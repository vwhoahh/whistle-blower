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

import contextlib
import os
from collections.abc import AsyncIterator

import google.auth
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from google.cloud import logging as google_cloud_logging

from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.reasoning_engine_adapter import (
    attach_reasoning_engine_routes,
)
from app.app_utils.telemetry import (
    setup_agent_engine_telemetry,
    setup_telemetry,
)
from app.app_utils.typing import Feedback

load_dotenv()
setup_telemetry()
# Must run before get_fast_api_app to set the tracer provider resource.
setup_agent_engine_telemetry()
try:
    _, project_id = google.auth.default()
    logging_client = google_cloud_logging.Client()
    logger = logging_client.logger(__name__)
except Exception as e:
    import logging as py_logging
    py_logging.warning(f"GCP Credentials not found. Falling back to local logging. Error: {e}")
    class LocalLogger:
        def log_struct(self, data, severity="INFO"):
            py_logging.info(f"[{severity}] {data}")
    logger = LocalLogger()
    project_id = "local-dev"
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Runner for the A2A path, sharing the same session/artifact services as the
    # adk_api and reasoning_engine paths (see services.py). Imported here so the
    # agent is built after env/telemetry setup.
    from app.agent import app as adk_app
    from app.agent import root_agent

    runner = Runner(
        app=adk_app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        auto_create_session=True,
    )
    # Shared by the A2A path and the reasoning_engine adapter routes.
    app.state.runner = runner
    app.state.agent_app_name = adk_app.name
    await attach_a2a_routes(
        app,
        agent=root_agent,
        runner=runner,
        task_store=InMemoryTaskStore(),
        rpc_path=f"/a2a/{adk_app.name}",
    )
    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=services.ARTIFACT_SERVICE_URI,
    allow_origins=allow_origins,
    session_service_uri=services.SESSION_SERVICE_URI,
    otel_to_cloud=False,
    lifespan=lifespan,
)
app.title = "whistle-blower"
app.description = "API for interacting with the Agent whistle-blower"


# Proxy routes so the Vertex AI Console Playground (reasoning_engine SDK) can
# talk to this agent alongside the native adk_api routes.
attach_reasoning_engine_routes(app)


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


from fastapi.responses import HTMLResponse
import json

@app.get("/dashboard", response_class=HTMLResponse)
def get_cyber_dashboard():
    """Serve the WhistleBlower premium cybersecurity hackathon dashboard."""
    dashboard_path = os.path.join(AGENT_DIR, "dashboard", "index.html")
    with open(dashboard_path, "r", encoding="utf-8") as f:
        return f.read()


from app.mcp_server import (
    scan_oauth_apps,
    get_app_details,
    revoke_app_access,
    get_audit_log,
    reset_demo_state,
)

@app.get("/api/apps")
def api_get_apps():
    """Get the current list of OAuth apps from the live database."""
    apps_data = json.loads(scan_oauth_apps())
    return apps_data

@app.get("/api/app-details/{app_id}")
def api_get_app_details(app_id: str):
    """Get detailed risk profile for a specific app."""
    details = json.loads(get_app_details(app_id))
    return details

@app.post("/api/revoke/{app_id}")
def api_post_revoke(app_id: str):
    """Revoke access for a specific app."""
    msg = revoke_app_access(app_id)
    return {"status": "success", "message": msg}

@app.get("/api/audit-log")
def api_get_audit_log():
    """Get the live digital hygiene audit logs."""
    logs = json.loads(get_audit_log())
    return logs

@app.post("/api/reset")
def api_post_reset():
    """Reset the database state and restore all apps."""
    msg = reset_demo_state()
    return {"status": "success", "message": msg}


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
