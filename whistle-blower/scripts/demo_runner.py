"""
WhistleBlower Animated Demo Script.
Simulates a live agent run with animated terminal output.
Designed to be recorded with asciinema or QuickTime for submission.
"""

import time
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
from app.mcp_server import (
    scan_oauth_apps,
    revoke_app_access,
    get_app_details,
    get_revocation_status,
    reset_demo_state,
    APPS_STORE,
)


def slow_print(text, delay=0.03):
    for char in text:
        try:
            print(char, end="", flush=True)
        except UnicodeEncodeError:
            print("?", end="", flush=True)
        time.sleep(delay)
    print()


def section(title):
    print(f"\n{'=' * 60}")
    slow_print(f"  {title}")
    print("=" * 60)


reset_demo_state()

section("WhistleBlower -- Autonomous Digital Hygiene Agent")
slow_print("  Initialising security checkpoint...")
time.sleep(0.5)
slow_print("  [OK] PII scrubbing: ACTIVE")
slow_print("  [OK] Injection detection: ACTIVE")
slow_print("  [OK] Audit trail: ACTIVE")

section("STEP 1: Scanning OAuth Apps")
time.sleep(0.8)
result = json.loads(scan_oauth_apps())
slow_print(f"  Found {result['total_scanned']} connected apps.")
slow_print(f"  Scan timestamp: {result['scan_timestamp'][:19]}")

section("STEP 2: Analysing Risk (get_app_details)")
risky_apps = ["photo-editor-pro", "datascraper-pro-2021", "slack-integration"]
for app_id in risky_apps:
    time.sleep(0.4)
    details = json.loads(get_app_details(app_id))
    slow_print(f"  [{details['name']}]")
    slow_print(f"    Overall Risk: {details['overall_scope_risk']}")
    slow_print(f"    Days Unused:  {details['days_since_last_used']}")
    slow_print(f"    Verified:     {details['verified']}")

section("STEP 3: Remediation Plan")
time.sleep(0.5)
revoke_list = [
    "photo-editor-pro",
    "datascraper-pro-2021",
    "sketchy-game-2023",
    "external-mailer-bot",
]
keep_list = ["slack-integration", "google-docs", "trello-connector"]
slow_print("  REVOKE (4 apps):")
for a in revoke_list:
    slow_print(f"    - {APPS_STORE[a]['name']}")
slow_print("  KEEP (11 apps):")
for a in keep_list:
    slow_print(f"    - {APPS_STORE[a]['name']}")

section("STEP 4: Human Approval Gate")
slow_print("  WhistleBlower requires your explicit approval before revoking.")
slow_print("  Revoking 4 apps. Do you confirm? (yes/no): ", delay=0.05)
time.sleep(1.5)
slow_print("yes", delay=0.1)

section("STEP 5: Executing Revocations")
for app_id in revoke_list:
    time.sleep(0.5)
    result = revoke_app_access(app_id)
    slow_print(f"  {result}")
    status = get_revocation_status(app_id)
    slow_print(f"    -> Status: {status}")

section("STEP 6: Post-Revocation Scan")
time.sleep(0.5)
final = json.loads(scan_oauth_apps())
slow_print(f"  Apps remaining: {final['total_scanned']} (was 15)")
slow_print(f"  Attack surface reduced by: {round((4 / 15) * 100)}%")

section("STEP 7: Audit Trail")
slow_print("  Last 4 entries in audit_log.json:")
try:
    with open("audit_log.json") as f:
        logs = json.load(f)
    for entry in logs[-4:]:
        slow_print(
            f"  [{entry['severity']}] {entry['event']} -- {entry['timestamp'][:19]}"
        )
except Exception:
    slow_print("  (Run from project root to see audit log)")

section("WhistleBlower Demo Complete")
slow_print("  Track: Concierge Agents | Kaggle 2026")
