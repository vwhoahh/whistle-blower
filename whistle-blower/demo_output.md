# WhistleBlower — Demo Session
*Run command: `adk run app`*

## 1. Security Checkpoint
```
[2026-07-05T23:45:00] [INFO] [security_checkpoint] Running security pre-checks...
[2026-07-05T23:45:01] [INFO] [security_checkpoint] PII check passed. (No user emails or phone numbers leaked)
[2026-07-05T23:45:01] [INFO] [security_checkpoint] Injection check passed. (No override/bypass keywords detected)
[2026-07-05T23:45:01] [INFO] [security_checkpoint] Security Check Passed: Input "Audit my connected apps" is safe.
```

## 2. Scan Output
```
[2026-07-05T23:45:02] [INFO] [mcp_server] Calling tool: scan_oauth_apps()
{
  "total_scanned": 15,
  "scan_timestamp": "2026-07-05T23:45:02.123456",
  "apps": [
    {
      "app_id": "datascraper-pro-2021",
      "name": "DataScraper Pro 2021",
      "scopes": ["https://www.googleapis.com/auth/contacts.readonly", "https://www.googleapis.com/auth/drive"],
      "days_since_last_used": 890,
      "verified": false
    },
    {
      "app_id": "sketchy-game-2023",
      "name": "Sketchy Game 2023",
      "scopes": ["https://www.googleapis.com/auth/contacts.readonly"],
      "days_since_last_used": 720,
      "verified": false
    },
    {
      "app_id": "photo-editor-pro",
      "name": "Photo Editor Pro",
      "scopes": ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/drive.file"],
      "days_since_last_used": 450,
      "verified": false
    },
    {
      "app_id": "external-mailer-bot",
      "name": "External Mailer Bot",
      "scopes": ["https://www.googleapis.com/auth/gmail.send"],
      "days_since_last_used": 350,
      "verified": false
    },
    {
      "app_id": "quick-calendar-widget",
      "name": "Quick Calendar Widget",
      "scopes": ["https://www.googleapis.com/auth/calendar.events"],
      "days_since_last_used": 5,
      "verified": true
    },
    {
      "app_id": "drive-viewer-tool",
      "name": "Drive Viewer Tool",
      "scopes": ["https://www.googleapis.com/auth/drive.readonly"],
      "days_since_last_used": 45,
      "verified": true
    },
    {
      "app_id": "unused-notes-app",
      "name": "Unused Notes App",
      "scopes": ["https://www.googleapis.com/auth/userinfo.profile"],
      "days_since_last_used": 150,
      "verified": true
    },
    {
      "app_id": "stale-tracker",
      "name": "Stale Tracker",
      "scopes": ["https://www.googleapis.com/auth/userinfo.email"],
      "days_since_last_used": 180,
      "verified": true
    },
    {
      "app_id": "slack-integration",
      "name": "Slack Integration",
      "scopes": ["https://www.googleapis.com/auth/userinfo.profile"],
      "days_since_last_used": 1,
      "verified": true
    },
    {
      "app_id": "newsletter-signup",
      "name": "Newsletter Signup",
      "scopes": ["https://www.googleapis.com/auth/userinfo.email"],
      "days_since_last_used": 10,
      "verified": true
    },
    {
      "app_id": "trello-connector",
      "name": "Trello Connector",
      "scopes": ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
      "days_since_last_used": 15,
      "verified": true
    },
    {
      "app_id": "zoom-login",
      "name": "Zoom Login",
      "scopes": ["https://www.googleapis.com/auth/userinfo.profile"],
      "days_since_last_used": 22,
      "verified": true
    },
    {
      "app_id": "google-docs",
      "name": "Google Docs",
      "scopes": ["https://www.googleapis.com/auth/userinfo.profile"],
      "days_since_last_used": 0,
      "verified": true
    },
    {
      "app_id": "google-calendar",
      "name": "Google Calendar",
      "scopes": ["https://www.googleapis.com/auth/userinfo.profile"],
      "days_since_last_used": 0,
      "verified": true
    },
    {
      "app_id": "tricky-edge-case",
      "name": "Tricky Edge Case App",
      "scopes": ["https://www.googleapis.com/auth/drive.readonly"],
      "days_since_last_used": 2,
      "verified": true
    }
  ]
}
```

## 3. get_app_details calls
```
[2026-07-05T23:45:03] [INFO] [mcp_server] Calling tool: get_app_details(app_id="photo-editor-pro")
{
  "app_id": "photo-editor-pro",
  "name": "Photo Editor Pro",
  "scopes": ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/drive.file"],
  "days_since_last_used": 450,
  "verified": false,
  "revoked": false,
  "scope_risk_profile": [
    {
      "scope": "https://www.googleapis.com/auth/gmail.readonly",
      "risk_level": "High",
      "description": "Can read all your Gmail messages"
    },
    {
      "scope": "https://www.googleapis.com/auth/drive.file",
      "risk_level": "Medium",
      "description": "Access only to files the app created"
    }
  ],
  "overall_scope_risk": "High"
}

[2026-07-05T23:45:03] [INFO] [mcp_server] Calling tool: get_app_details(app_id="quick-calendar-widget")
{
  "app_id": "quick-calendar-widget",
  "name": "Quick Calendar Widget",
  "scopes": ["https://www.googleapis.com/auth/calendar.events"],
  "days_since_last_used": 5,
  "verified": true,
  "revoked": false,
  "scope_risk_profile": [
    {
      "scope": "https://www.googleapis.com/auth/calendar.events",
      "risk_level": "Medium",
      "description": "Can read and modify calendar events"
    }
  ],
  "overall_scope_risk": "Medium"
}

[2026-07-05T23:45:04] [INFO] [mcp_server] Calling tool: get_app_details(app_id="slack-integration")
{
  "app_id": "slack-integration",
  "name": "Slack Integration",
  "scopes": ["https://www.googleapis.com/auth/userinfo.profile"],
  "days_since_last_used": 1,
  "verified": true,
  "revoked": false,
  "scope_risk_profile": [
    {
      "scope": "https://www.googleapis.com/auth/userinfo.profile",
      "risk_level": "Low",
      "description": "Can read your name and profile picture"
    }
  ],
  "overall_scope_risk": "Low"
}
```

## 4. Risk Analysis (risk_analyst_agent output)
```
[2026-07-05T23:45:06] [INFO] [risk_analyst_agent] Analysis complete. Returning RiskAnalysisReport.
{
  "analyses": [
    {
      "app_id": "datascraper-pro-2021",
      "name": "DataScraper Pro 2021",
      "risk_score": 10,
      "risk_rating": "High",
      "reason": "Unverified developer holding sensitive full Drive access and Contacts access, completely dormant for 890 days."
    },
    {
      "app_id": "sketchy-game-2023",
      "name": "Sketchy Game 2023",
      "risk_score": 8,
      "risk_rating": "High",
      "reason": "Unverified app with access to Google Contacts, unused for 720 days."
    },
    {
      "app_id": "photo-editor-pro",
      "name": "Photo Editor Pro",
      "risk_score": 9,
      "risk_rating": "High",
      "reason": "Unverified developer holding sensitive Gmail readonly access, unused for 450 days."
    },
    {
      "app_id": "external-mailer-bot",
      "name": "External Mailer Bot",
      "risk_score": 10,
      "risk_rating": "High",
      "reason": "Unverified developer holding critical Gmail Send scope, unused for 350 days."
    },
    {
      "app_id": "quick-calendar-widget",
      "name": "Quick Calendar Widget",
      "risk_score": 5,
      "risk_rating": "Medium",
      "reason": "Verified app holding Calendar events permissions, actively used 5 days ago."
    },
    {
      "app_id": "drive-viewer-tool",
      "name": "Drive Viewer Tool",
      "risk_score": 5,
      "risk_rating": "Medium",
      "reason": "Verified app holding High-risk Drive readonly scope, actively used 45 days ago."
    },
    {
      "app_id": "unused-notes-app",
      "name": "Unused Notes App",
      "risk_score": 4,
      "risk_rating": "Medium",
      "reason": "Verified app, low-risk scopes but dormant for 150 days."
    },
    {
      "app_id": "stale-tracker",
      "name": "Stale Tracker",
      "risk_score": 4,
      "risk_rating": "Medium",
      "reason": "Verified app, low-risk scopes but dormant for 180 days."
    },
    {
      "app_id": "slack-integration",
      "name": "Slack Integration",
      "risk_score": 1,
      "risk_rating": "Low",
      "reason": "Verified app, low-risk profile access, actively used 1 day ago."
    },
    {
      "app_id": "newsletter-signup",
      "name": "Newsletter Signup",
      "risk_score": 1,
      "risk_rating": "Low",
      "reason": "Verified app, low-risk email access, actively used 10 days ago."
    },
    {
      "app_id": "trello-connector",
      "name": "Trello Connector",
      "risk_score": 1,
      "risk_rating": "Low",
      "reason": "Verified app, profile and email access, actively used 15 days ago."
    },
    {
      "app_id": "zoom-login",
      "name": "Zoom Login",
      "risk_score": 1,
      "risk_rating": "Low",
      "reason": "Verified app, profile access, actively used 22 days ago."
    },
    {
      "app_id": "google-docs",
      "name": "Google Docs",
      "risk_score": 1,
      "risk_rating": "Low",
      "reason": "First-party Google app. Trusted ecosystem."
    },
    {
      "app_id": "google-calendar",
      "name": "Google Calendar",
      "risk_score": 1,
      "risk_rating": "Low",
      "reason": "First-party Google app. Trusted ecosystem."
    },
    {
      "app_id": "tricky-edge-case",
      "name": "Tricky Edge Case App",
      "risk_score": 4,
      "risk_rating": "Low",
      "reason": "Verified app, drive.readonly scope, used 2 days ago. Flagged for review, keep active for now."
    }
  ]
}
```

## 5. Remediation Plan (remediation_planner_agent output)
```
[2026-07-05T23:45:08] [INFO] [remediation_planner_agent] Planning complete. Returning RemediationPlan.
{
  "plan_items": [
    {"app_id": "datascraper-pro-2021", "name": "DataScraper Pro 2021", "action": "REVOKE", "reason": "Unverified app, extremely stale (890 days), holding full Drive read/write and Contacts access."},
    {"app_id": "sketchy-game-2023", "name": "Sketchy Game 2023", "action": "REVOKE", "reason": "Unverified game holding Contacts access, unused for almost 2 years."},
    {"app_id": "photo-editor-pro", "name": "Photo Editor Pro", "action": "REVOKE", "reason": "Unverified app, Gmail read access, unused for 450 days."},
    {"app_id": "external-mailer-bot", "name": "External Mailer Bot", "action": "REVOKE", "reason": "Unverified app holding Gmail send capability, unused for nearly a year."},
    {"app_id": "quick-calendar-widget", "name": "Quick Calendar Widget", "action": "KEEP", "reason": "Verified and recently used (5 days ago)."},
    {"app_id": "drive-viewer-tool", "name": "Drive Viewer Tool", "action": "KEEP", "reason": "Verified and recently used (45 days ago)."},
    {"app_id": "unused-notes-app", "name": "Unused Notes App", "action": "KEEP", "reason": "Verified app with minimal scope, although stale (150 days)."},
    {"app_id": "stale-tracker", "name": "Stale Tracker", "action": "KEEP", "reason": "Verified app with minimal scope, although stale (180 days)."},
    {"app_id": "slack-integration", "name": "Slack Integration", "action": "KEEP", "reason": "Highly active verified app with minimal scope."},
    {"app_id": "newsletter-signup", "name": "Newsletter Signup", "action": "KEEP", "reason": "Active verified app with minimal scope."},
    {"app_id": "trello-connector", "name": "Trello Connector", "action": "KEEP", "reason": "Active verified app with minimal scope."},
    {"app_id": "zoom-login", "name": "Zoom Login", "action": "KEEP", "reason": "Active verified app with minimal scope."},
    {"app_id": "google-docs", "name": "Google Docs", "action": "KEEP", "reason": "First-party Google app. Trusted ecosystem."},
    {"app_id": "google-calendar", "name": "Google Calendar", "action": "KEEP", "reason": "First-party Google app. Trusted ecosystem."},
    {"app_id": "tricky-edge-case", "name": "Tricky Edge Case App", "action": "KEEP", "reason": "Verified app with drive.readonly scope, used 2 days ago. Flagged for review but keep active for now."}
  ],
  "summary": "Our scan identified 15 connected apps. 4 unverified apps hold highly sensitive permissions (Gmail, Drive, Contacts) and have been dormant for over a year. We recommend immediately revoking access to these 4 apps. The remaining 11 apps are either first-party, low risk, or actively used, and should be kept."
}
```

## 6. Human Approval Gate
```
### 🛡️ WhistleBlower Risk Assessment Summary

Our scan identified 15 connected apps. 4 unverified apps hold highly sensitive permissions (Gmail, Drive, Contacts) and have been dormant for over a year. We recommend immediately revoking access to these 4 apps. The remaining 11 apps are either first-party, low risk, or actively used, and should be kept.

#### Proposed Actions:
- **DataScraper Pro 2021** (datascraper-pro-2021): 🛑 REVOKE — *Unverified app, extremely stale (890 days), holding full Drive read/write and Contacts access.*
- **Sketchy Game 2023** (sketchy-game-2023): 🛑 REVOKE — *Unverified game holding Contacts access, unused for almost 2 years.*
- **Photo Editor Pro** (photo-editor-pro): 🛑 REVOKE — *Unverified app, Gmail read access, unused for 450 days.*
- **External Mailer Bot** (external-mailer-bot): 🛑 REVOKE — *Unverified app holding Gmail send capability, unused for nearly a year.*
- **Quick Calendar Widget** (quick-calendar-widget): ✅ KEEP — *Verified and recently used (5 days ago).*
- **Drive Viewer Tool** (drive-viewer-tool): ✅ KEEP — *Verified and recently used (45 days ago).*
- **Unused Notes App** (unused-notes-app): ✅ KEEP — *Verified app with minimal scope, although stale (150 days).*
- **Stale Tracker** (stale-tracker): ✅ KEEP — *Verified app with minimal scope, although stale (180 days).*
- **Slack Integration** (slack-integration): ✅ KEEP — *Highly active verified app with minimal scope.*
- **Newsletter Signup** (newsletter-signup): ✅ KEEP — *Active verified app with minimal scope.*
- **Trello Connector** (trello-connector): ✅ KEEP — *Active verified app with minimal scope.*
- **Zoom Login** (zoom-login): ✅ KEEP — *Active verified app with minimal scope.*
- **Google Docs** (google-docs): ✅ KEEP — *First-party Google app. Trusted ecosystem.*
- **Google Calendar** (google-calendar): ✅ KEEP — *First-party Google app. Trusted ecosystem.*
- **Tricky Edge Case App** (tricky-edge-case): ✅ KEEP — *Verified app with drive.readonly scope, used 2 days ago. Flagged for review but keep active for now.*

⚠️ **WhistleBlower recommends revoking access to 4 app(s).** Do you want to proceed? (yes/no)
User: yes
```

## 7. Revocation Confirmation
```
[2026-07-05T23:45:20] [INFO] [mcp_server] Calling tool: revoke_app_access(app_id="datascraper-pro-2021")
Success: Revoked access for 'DataScraper Pro 2021'. It no longer appears in scans.

[2026-07-05T23:45:21] [INFO] [mcp_server] Calling tool: get_revocation_status(app_id="datascraper-pro-2021")
revoked

[2026-07-05T23:45:21] [INFO] [mcp_server] Calling tool: revoke_app_access(app_id="sketchy-game-2023")
Success: Revoked access for 'Sketchy Game 2023'. It no longer appears in scans.

[2026-07-05T23:45:22] [INFO] [mcp_server] Calling tool: get_revocation_status(app_id="sketchy-game-2023")
revoked

[2026-07-05T23:45:22] [INFO] [mcp_server] Calling tool: revoke_app_access(app_id="photo-editor-pro")
Success: Revoked access for 'Photo Editor Pro'. It no longer appears in scans.

[2026-07-05T23:45:23] [INFO] [mcp_server] Calling tool: get_revocation_status(app_id="photo-editor-pro")
revoked

[2026-07-05T23:45:23] [INFO] [mcp_server] Calling tool: revoke_app_access(app_id="external-mailer-bot")
Success: Revoked access for 'External Mailer Bot'. It no longer appears in scans.

[2026-07-05T23:45:24] [INFO] [mcp_server] Calling tool: get_revocation_status(app_id="external-mailer-bot")
revoked
```

## 8. Scan Diff
```
[2026-07-05T23:45:25] [INFO] [mcp_server] Calling tool: save_scan_result(high_risk=4, medium_risk=4, low_risk=7, summary="...")
Scan saved with ID a2b3c4d5

[2026-07-05T23:45:26] [INFO] [mcp_server] Calling tool: get_scan_diff()
No previous scan to compare. This is your first scan.
```

## 9. Final Summary
```
✅ **Revocation complete!** Access has been revoked for: DataScraper Pro 2021, Sketchy Game 2023, Photo Editor Pro, External Mailer Bot.

All actions have been logged to the audit trail.
```
