import json
import datetime
import uuid
from mcp.server.fastmcp import FastMCP

"""
WhistleBlower MCP Server
Tools: scan_oauth_apps | revoke_app_access | get_revocation_status |
       get_app_details | get_audit_log | save_scan_result | 
       get_scan_diff | reset_demo_state
"""

mcp = FastMCP("whistle-blower-mcp")

AUDIT_LOG_FILE = "audit_log.json"
SCAN_HISTORY_FILE = "scan_history.json"

SCOPE_RISK_REGISTRY = {
    "auth/gmail.readonly": ("High", "Can read all your Gmail messages"),
    "auth/gmail.send": ("Critical", "Can send emails as you"),
    "auth/drive": ("Critical", "Full access to all Google Drive files"),
    "auth/drive.file": ("Medium", "Access only to files the app created"),
    "auth/drive.readonly": ("High", "Can read all your Google Drive files"),
    "auth/calendar.events": ("Medium", "Can read and modify calendar events"),
    "auth/contacts.readonly": ("High", "Can read all your Google Contacts"),
    "auth/userinfo.profile": ("Low", "Can read your name and profile picture"),
    "auth/userinfo.email": ("Low", "Can read your email address"),
}

APPS_STORE = {
    # 4 HIGH risk: unverified=True, sensitive write scopes (gmail/drive/contacts), days_since_last_used > 300
    "datascraper-pro-2021": {
        "app_id": "datascraper-pro-2021",
        "name": "DataScraper Pro 2021",
        "scopes": ["https://www.googleapis.com/auth/contacts.readonly", "https://www.googleapis.com/auth/drive"],
        "days_since_last_used": 890,
        "verified": False,
        "revoked": False
    },
    "sketchy-game-2023": {
        "app_id": "sketchy-game-2023",
        "name": "Sketchy Game 2023",
        "scopes": ["https://www.googleapis.com/auth/contacts.readonly"],
        "days_since_last_used": 720,
        "verified": False,
        "revoked": False
    },
    "photo-editor-pro": {
        "app_id": "photo-editor-pro",
        "name": "Photo Editor Pro",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/drive.file"],
        "days_since_last_used": 450,
        "verified": False,
        "revoked": False
    },
    "external-mailer-bot": {
        "app_id": "external-mailer-bot",
        "name": "External Mailer Bot",
        "scopes": ["https://www.googleapis.com/auth/gmail.send"],
        "days_since_last_used": 350,
        "verified": False,
        "revoked": False
    },
    # 4 MEDIUM risk: verified=True but read-only sensitive scopes OR unused 90-200 days
    "quick-calendar-widget": {
        "app_id": "quick-calendar-widget",
        "name": "Quick Calendar Widget",
        "scopes": ["https://www.googleapis.com/auth/calendar.events"],
        "days_since_last_used": 5,
        "verified": True,
        "revoked": False
    },
    "drive-viewer-tool": {
        "app_id": "drive-viewer-tool",
        "name": "Drive Viewer Tool",
        "scopes": ["https://www.googleapis.com/auth/drive.readonly"],
        "days_since_last_used": 45,
        "verified": True,
        "revoked": False
    },
    "unused-notes-app": {
        "app_id": "unused-notes-app",
        "name": "Unused Notes App",
        "scopes": ["https://www.googleapis.com/auth/userinfo.profile"],
        "days_since_last_used": 150,
        "verified": True,
        "revoked": False
    },
    "stale-tracker": {
        "app_id": "stale-tracker",
        "name": "Stale Tracker",
        "scopes": ["https://www.googleapis.com/auth/userinfo.email"],
        "days_since_last_used": 180,
        "verified": True,
        "revoked": False
    },
    # 4 LOW risk: verified=True, only userinfo.profile/email scopes, used within 30 days
    "slack-integration": {
        "app_id": "slack-integration",
        "name": "Slack Integration",
        "scopes": ["https://www.googleapis.com/auth/userinfo.profile"],
        "days_since_last_used": 1,
        "verified": True,
        "revoked": False
    },
    "newsletter-signup": {
        "app_id": "newsletter-signup",
        "name": "Newsletter Signup",
        "scopes": ["https://www.googleapis.com/auth/userinfo.email"],
        "days_since_last_used": 10,
        "verified": True,
        "revoked": False
    },
    "trello-connector": {
        "app_id": "trello-connector",
        "name": "Trello Connector",
        "scopes": ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
        "days_since_last_used": 15,
        "verified": True,
        "revoked": False
    },
    "zoom-login": {
        "app_id": "zoom-login",
        "name": "Zoom Login",
        "scopes": ["https://www.googleapis.com/auth/userinfo.profile"],
        "days_since_last_used": 22,
        "verified": True,
        "revoked": False
    },
    # 2 FIRST PARTY: Google Docs and Google Calendar — verified=True, minimal scopes, days_since_last_used=0
    "google-docs": {
        "app_id": "google-docs",
        "name": "Google Docs",
        "scopes": ["https://www.googleapis.com/auth/userinfo.profile"],
        "days_since_last_used": 0,
        "verified": True,
        "revoked": False
    },
    "google-calendar": {
        "app_id": "google-calendar",
        "name": "Google Calendar",
        "scopes": ["https://www.googleapis.com/auth/userinfo.profile"],
        "days_since_last_used": 0,
        "verified": True,
        "revoked": False
    },
    # 1 TRICKY EDGE CASE: verified=True, auth/drive.readonly scope, days_since_last_used=2
    "tricky-edge-case": {
        "app_id": "tricky-edge-case",
        "name": "Tricky Edge Case App",
        "scopes": ["https://www.googleapis.com/auth/drive.readonly"],
        "days_since_last_used": 2,
        "verified": True,
        "revoked": False
    }
}

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

@mcp.tool()
def scan_oauth_apps() -> str:
    """Scan all connected OAuth applications and return them as a JSON list.
    Includes their app_id, name, scopes, verification status, and days since last used.
    """
    allowed_demo_apps = {
        "datascraper-pro-2021",
        "quick-calendar-widget",
        "slack-integration",
        "google-docs"
    }
    unrevoked_apps = []
    for app_id, app in APPS_STORE.items():
        if app_id in allowed_demo_apps and not app["revoked"]:
            unrevoked_apps.append({
                "app_id": app["app_id"],
                "name": app["name"],
                "scopes": app["scopes"],
                "days_since_last_used": app["days_since_last_used"],
                "verified": app["verified"]
            })
    
    result = {
        "total_scanned": len(unrevoked_apps),
        "scan_timestamp": datetime.datetime.now().isoformat(),
        "apps": unrevoked_apps
    }
    return json.dumps(result, indent=2)

@mcp.tool()
def revoke_app_access(app_id: str) -> str:
    """Revoke OAuth access for a specific application by its app_id.
    
    Args:
        app_id: The unique ID of the application to revoke.
    """
    if app_id not in APPS_STORE:
        return "Error: App not found."
    
    app = APPS_STORE[app_id]
    if app["revoked"]:
        return "Info: Already revoked."
    
    app["revoked"] = True
    msg = f"Success: Revoked access for '{app['name']}'. It no longer appears in scans."
    write_audit_entry("App Revocation", "INFO", msg)
    return msg

@mcp.tool()
def get_revocation_status(app_id: str) -> str:
    """Get the revocation status of a specific application.
    
    Args:
        app_id: The unique ID of the application.
    """
    if app_id not in APPS_STORE:
        return "Error: App not found."
    
    status = "revoked" if APPS_STORE[app_id]["revoked"] else "connected"
    write_audit_entry("Get Revocation Status", "INFO", f"Checked revocation status for {app_id}: {status}")
    return status

@mcp.tool()
def get_app_details(app_id: str) -> str:
    """Get detailed information about an application including scope risk profile.
    
    Args:
        app_id: The unique ID of the application.
    """
    if app_id not in APPS_STORE:
        return "Error: App not found."
    
    app = APPS_STORE[app_id]
    scope_risk_profile = []
    worst_risk = "Low"
    risk_order = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    
    for scope in app["scopes"]:
        matched_level = "Low"
        matched_desc = "Unknown scope"
        for registry_key, (risk, desc) in SCOPE_RISK_REGISTRY.items():
            if registry_key in scope:
                matched_level = risk
                matched_desc = desc
                break
        scope_risk_profile.append({
            "scope": scope,
            "risk_level": matched_level,
            "description": matched_desc
        })
        if risk_order[matched_level] > risk_order[worst_risk]:
            worst_risk = matched_level
            
    result = {
        "app_id": app["app_id"],
        "name": app["name"],
        "scopes": app["scopes"],
        "days_since_last_used": app["days_since_last_used"],
        "verified": app["verified"],
        "revoked": app["revoked"],
        "scope_risk_profile": scope_risk_profile,
        "overall_scope_risk": worst_risk
    }
    return json.dumps(result, indent=2)

@mcp.tool()
def reset_demo_state() -> str:
    """Reset the demo state by restoring all apps."""
    for app in APPS_STORE.values():
        app["revoked"] = False
    
    msg = "Demo state reset. All 15 apps restored."
    write_audit_entry("Demo Reset", "WARNING", msg)
    return msg

@mcp.tool()
def get_audit_log() -> str:
    """Get the digital hygiene audit log trail."""
    try:
        with open(AUDIT_LOG_FILE, "r") as f:
            logs = json.load(f)
        return json.dumps(logs, indent=2)
    except (FileNotFoundError, json.JSONDecodeError):
        return "[]"

@mcp.tool()
def save_scan_result(high_risk: int, medium_risk: int, low_risk: int, summary: str) -> str:
    """Save the summary statistics of a scan.
    
    Args:
        high_risk: Count of high risk apps.
        medium_risk: Count of medium risk apps.
        low_risk: Count of low risk apps.
        summary: Remediation plan summary text.
    """
    scan_id = str(uuid.uuid4())[:8]
    record = {
        "scan_id": scan_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "total": high_risk + medium_risk + low_risk,
        "summary": summary
    }
    try:
        try:
            with open(SCAN_HISTORY_FILE, "r") as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []
        history.append(record)
        with open(SCAN_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving scan history: {e}")
        
    return f"Scan saved with ID {scan_id}"

@mcp.tool()
def get_scan_diff() -> str:
    """Compare the latest two scans on high risk count."""
    try:
        with open(SCAN_HISTORY_FILE, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
        
    if len(history) < 2:
        return "No previous scan to compare. This is your first scan."
        
    previous = history[-2]
    current = history[-1]
    
    prev = previous["high_risk"]
    curr = current["high_risk"]
    date = previous["timestamp"]
    
    delta = curr - prev
    if delta < 0:
        msg = f"✅ Progress! High risk apps reduced from {prev} to {curr} since {date}."
    elif delta > 0:
        msg = f"⚠️ Risk increased. High risk apps grew from {prev} to {curr} since {date}."
    else:
        msg = f"No change in high risk count since your last scan on {date}."
        
    write_audit_entry("Scan Diff Computed", "INFO", msg)
    return msg

import http.server
import threading
import os

class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            status = json.dumps({
                "status": "ok",
                "service": "whistle-blower-mcp",
                "tools": 8,
                "apps_loaded": len(APPS_STORE),
                "timestamp": datetime.datetime.now().isoformat()
            })
            self.wfile.write(status.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress default HTTP logs

def start_health_server(port=8080):
    """Start a minimal health check HTTP server in a background thread."""
    server = http.server.HTTPServer(("0.0.0.0", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"[WhistleBlower] Health server running on port {port}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    start_health_server(port)
    mcp.run()
