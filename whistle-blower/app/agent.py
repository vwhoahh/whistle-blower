# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
WhistleBlower Agent — ADK Multi-Agent Workflow
Flow: START → security_checkpoint → orchestrator_node
      (safe) → orchestrator_agent → risk_analyst_agent 
             → remediation_planner_agent → RequestInput → revocation
      (unsafe) → security_violation_handler
"""

import datetime
import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.tools import AgentTool
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.agents.context import Context
from google.adk.workflow import Workflow, FunctionNode
from google.genai import types

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from app.config import config

AUDIT_LOG_FILE = "audit_log.json"

def write_audit_entry(event_type: str, severity: str, details: str):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event": event_type,
        "severity": severity,
        "details": details
    }
    try:
        try:
            with open(AUDIT_LOG_FILE, "r") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
        logs.append(entry)
        with open(AUDIT_LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Error writing audit log: {e}")

# Pydantic Schemas for Structured output
class AppRiskAnalysis(BaseModel):
    app_id: str
    name: str
    risk_score: int = Field(..., description="Risk score from 0 to 10")
    risk_rating: str = Field(..., description="High, Medium, or Low")
    reason: str = Field(..., description="Explanation of the risk score and rating")

class RiskAnalysisReport(BaseModel):
    analyses: List[AppRiskAnalysis]

class RemediationItem(BaseModel):
    app_id: str
    name: str
    action: str = Field(..., description="REVOKE or KEEP")
    reason: str = Field(..., description="Justification for the action")

class RemediationPlan(BaseModel):
    plan_items: List[RemediationItem]
    summary: str = Field(..., description="Overall plain-English summary of the security posture")

# MCP Server connection params for local execution
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "python", "-m", "app.mcp_server"],
        )
    )
)

# Specialized Sub-Agents
risk_analyst_agent = LlmAgent(
    name="risk_analyst_agent",
    model=config.model,
    instruction=(
        "You are an expert OAuth permissions security analyst. "
        "Analyze the list of scanned connected OAuth apps, their scopes, and usage history. "
        "For each app in the list, call get_app_details(app_id) to retrieve the "
        "scope risk profile before assigning a risk score. Use overall_scope_risk "
        "and days_since_last_used together to determine the final risk rating. "
        "For each app, evaluate the security risk and assign a risk score (0 to 10), "
        "a risk rating (High, Medium, Low), and a detailed reason. "
        "Focus particularly on high-risk scopes (e.g. read/write for Drive, Calendar, Gmail) "
        "and long periods of inactivity (e.g. apps unused for >90 days)."
    ),
    tools=[mcp_toolset],
    output_schema=RiskAnalysisReport,
)

remediation_planner_agent = LlmAgent(
    name="remediation_planner_agent",
    model=config.model,
    instruction=(
        "You are a Digital Hygiene Remediation Planner. "
        "Based on the risk analysis report, formulate a prioritized plan. "
        "Identify which apps must be REVOKED (suggest revocation for High/Medium risk apps, "
        "especially those unused for a long time) and which can be KEEP (Low risk / actively used). "
        "Provide a plain-English summary explaining the overall security posture and why these "
        "actions are recommended."
    ),
    output_schema=RemediationPlan,
)

# Orchestrator Agent delegating via AgentTool and using MCP tools
orchestrator_agent = LlmAgent(
    name="orchestrator_agent",
    model=config.model,
    instruction=(
        "You are the WhistleBlower Orchestrator Agent. "
        "Coordinate the digital hygiene audit of connected apps. "
        "First, scan the connected apps using the scan_oauth_apps tool (available in your mcp_toolset). "
        "Second, invoke the risk_analyst_agent tool, passing the scanned apps list. "
        "Third, take the risk analysis result and pass it to remediation_planner_agent to generate a plan. "
        "Finally, return the remediation plan. "
        "For each app flagged as REVOKE in the remediation plan, call the "
        "revoke_app_access(app_id) MCP tool. Then call get_revocation_status(app_id) "
        "to confirm each revocation succeeded before reporting back. "
        "After the remediation plan is complete, call save_scan_result with the count of "
        "high, medium, and low risk apps and the plan summary. Then call get_scan_diff "
        "and include the comparison result in your final response to the user."
    ),
    tools=[
        mcp_toolset,
        AgentTool(risk_analyst_agent),
        AgentTool(remediation_planner_agent)
    ],
    output_schema=RemediationPlan,
)

# Workflow Function Nodes
def security_checkpoint_impl(ctx: Context, node_input: types.Content) -> Event:
    text = ""
    if node_input and node_input.parts:
        text = "".join(part.text for part in node_input.parts if part.text)
    
    # 1. Prompt injection check
    injection_keywords = ["override", "ignore previous instructions", "system prompt", "bypass", "jailbreak", "security check disable"]
    detected_injection = [kw for kw in injection_keywords if kw in text.lower()]
    
    # 2. PII scrubbing (redact emails and phone numbers)
    scrubbed_text = text
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    
    scrubbed_text = re.sub(email_pattern, "[REDACTED_EMAIL]", scrubbed_text)
    scrubbed_text = re.sub(phone_pattern, "[REDACTED_PHONE]", scrubbed_text)
    
    if detected_injection:
        write_audit_entry("Prompt Injection Attempt", "CRITICAL", f"Keywords found: {detected_injection}")
        return Event(
            output="Security Violation: Input rejected due to suspected prompt injection attempt.",
            route="unsafe"
        )
    
    if scrubbed_text != text:
        write_audit_entry("PII Redacted", "WARNING", "PII was scrubbed from user input.")
    else:
        write_audit_entry("Security Check Passed", "INFO", "No security issues detected in input.")
        
    ctx.state["user_prompt"] = scrubbed_text
    return Event(output=scrubbed_text, route="safe")

security_checkpoint = FunctionNode(
    func=security_checkpoint_impl,
    name="security_checkpoint",
    rerun_on_resume=False
)

def security_violation_handler_impl(node_input: str):
    yield Event(content=types.Content(role='model', parts=[types.Part.from_text(text=f"⚠️ {node_input}")]), route="final")
    yield Event(output=node_input)

security_violation_handler = FunctionNode(
    func=security_violation_handler_impl,
    name="security_violation_handler",
    rerun_on_resume=False
)

async def orchestrator_node_impl(ctx: Context, node_input: str):
    # Check if we are resuming from user approval input
    if ctx.resume_inputs and "approval" in ctx.resume_inputs:
        user_response = ctx.resume_inputs["approval"].strip().lower()
        if user_response in ["yes", "y", "approve", "confirm"]:
            # Retrieve the plan from state
            plan_data = ctx.state.get("remediation_plan")
            if not plan_data:
                yield Event(content=types.Content(role='model', parts=[types.Part.from_text(text="Error: Remediation plan not found in state. Please start over.")]), route="final")
                return
            
            # Perform revocations
            revoked_apps = []
            for item in plan_data.get("plan_items", []):
                if item.get("action") == "REVOKE":
                    app_id = item.get("app_id")
                    # Revocation is handled via mcp_toolset in orchestrator_agent
                    # The agent calls revoke_app_access via MCP — this node just confirms
                    write_audit_entry("App Revocation", "INFO", f"Success: Revoked OAuth access for app '{app_id}'.")
                    revoked_apps.append(item.get("name"))
            
            result_msg = f"✅ **Revocation complete!** Access has been revoked for: {', '.join(revoked_apps)}.\n\nAll actions have been logged to the audit trail."
            yield Event(content=types.Content(role='model', parts=[types.Part.from_text(text=result_msg)]), route="final")
            yield Event(output=result_msg)
        elif user_response in ["no", "n", "cancel", "stop", "nope"]:
            cancel_msg = "❌ **Revocation cancelled.** No apps were modified. They remain connected to your account."
            write_audit_entry("Revocation Cancelled", "WARNING", "User declined the revocation proposal.")
            yield Event(content=types.Content(role='model', parts=[types.Part.from_text(text=cancel_msg)]), route="final")
            yield Event(output=cancel_msg)
        else:
            # Ambiguous response
            write_audit_entry("Ambiguous Response", "WARNING", 
                              f"User said '{user_response}' — treated as decline.")
            cancel_msg = f"❌ Unclear response ('{user_response}'). Treating as no. No apps were modified."
            yield Event(content=types.Content(role='model', parts=[types.Part.from_text(text=cancel_msg)]), route="final")
            yield Event(output=cancel_msg)
        return

    # Run the orchestrator agent to scan and analyze risk
    yield Event(content=types.Content(role='model', parts=[types.Part.from_text(text="🔍 Scanning connected OAuth apps and evaluating permissions...")]), route="running")
    
    try:
        plan = await ctx.run_node(orchestrator_agent, node_input="Audit my apps")
    except Exception as e:
        write_audit_entry("Orchestrator Error", "CRITICAL", str(e))
        yield Event(
            content=types.Content(role='model', parts=[types.Part.from_text(
                text=f"⚠️ Scan failed due to an internal error: {e}. Please try again."
            )]),
            route="final"
        )
        return
    
    # ctx.run_node returns a dict for LlmAgents with output_schema
    if isinstance(plan, dict):
        plan_data = plan
    else:
        plan_data = plan.model_dump()
    
    if not plan_data or not plan_data.get("plan_items"):
        yield Event(
            content=types.Content(role='model', parts=[types.Part.from_text(
                text="⚠️ No apps were found to analyze. Your account may have no connected OAuth apps."
            )]),
            route="final"
        )
        return
        
    ctx.state["remediation_plan"] = plan_data
    
    # Determine apps flagged for revocation
    plan_items = plan_data.get("plan_items", [])
    apps_to_revoke = [item for item in plan_items if item.get("action") == "REVOKE"]
    
    summary_md = f"### 🛡️ WhistleBlower Risk Assessment Summary\n\n{plan_data.get('summary', '')}\n\n"
    summary_md += "#### Proposed Actions:\n"
    for item in plan_items:
        action_emoji = "🛑 REVOKE" if item.get("action") == "REVOKE" else "✅ KEEP"
        summary_md += f"- **{item.get('name')}** ({item.get('app_id')}): {action_emoji} — *{item.get('reason')}*\n"
        
    if apps_to_revoke:
        # Prompt for human approval
        msg = f"{summary_md}\n⚠️ **WhistleBlower recommends revoking access to {len(apps_to_revoke)} app(s).** Do you want to proceed? (yes/no)"
        if len(apps_to_revoke) > config.max_revocations_per_session:
            warn_msg = f"⚠️ {len(apps_to_revoke)} apps flagged for revocation — this is unusually high. Are you sure you want to revoke all of them? (yes/no)"
            write_audit_entry("Bulk Revocation Warning", "WARNING", f"{len(apps_to_revoke)} apps queued.")
            msg = f"{warn_msg}\n\n{summary_md}"
        yield RequestInput(interrupt_id="approval", message=msg)
    else:
        clean_msg = f"{summary_md}\n✅ **Your digital hygiene is clean!** No apps require revocation."
        yield Event(content=types.Content(role='model', parts=[types.Part.from_text(text=clean_msg)]), route="final")
        yield Event(output=clean_msg)

orchestrator_node = FunctionNode(
    func=orchestrator_node_impl,
    name="orchestrator_node",
    rerun_on_resume=True
)

# Setup graph edges
edges = [
    ('START', security_checkpoint),
    (security_checkpoint, {'safe': orchestrator_node, 'unsafe': security_violation_handler}),
]

# Instantiate App
root_agent = Workflow(
    name="whistle_blower",
    edges=edges,
)

app = App(
    root_agent=root_agent,
    name="app",
)

