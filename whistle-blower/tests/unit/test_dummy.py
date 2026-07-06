import pytest
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))
from app.mcp_server import (
    scan_oauth_apps,
    revoke_app_access,
    get_revocation_status,
    get_app_details,
    reset_demo_state,
    APPS_STORE,
)

@pytest.fixture(autouse=True, scope="function")
def fresh_state():
    reset_demo_state()
    yield

def test_scan_returns_all_apps_by_default():
    result = json.loads(scan_oauth_apps())
    assert result["total_scanned"] == 15
    assert len(result["apps"]) == 15

def test_revoke_removes_app_from_scan():
    revoke_app_access("sketchy-game-2023")
    result = json.loads(scan_oauth_apps())
    app_ids = [a["app_id"] for a in result["apps"]]
    assert "sketchy-game-2023" not in app_ids
    assert result["total_scanned"] == 14

def test_revoke_unknown_app_returns_error():
    result = revoke_app_access("nonexistent-app-xyz")
    assert "Error" in result

def test_revoke_already_revoked_returns_info():
    revoke_app_access("photo-editor-pro")
    result = revoke_app_access("photo-editor-pro")
    assert "Already revoked" in result

def test_get_revocation_status_updates_correctly():
    assert "connected" in get_revocation_status("photo-editor-pro")
    revoke_app_access("photo-editor-pro")
    assert "revoked" in get_revocation_status("photo-editor-pro")

def test_get_app_details_returns_scope_risk():
    result = json.loads(get_app_details("photo-editor-pro"))
    assert "scope_risk_profile" in result
    assert "overall_scope_risk" in result
    assert result["overall_scope_risk"] in ["Low", "Medium", "High", "Critical"]

def test_reset_restores_all_apps():
    revoke_app_access("sketchy-game-2023")
    revoke_app_access("photo-editor-pro")
    reset_demo_state()
    result = json.loads(scan_oauth_apps())
    assert result["total_scanned"] == 15
