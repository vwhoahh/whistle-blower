"""
Entry point for WhistleBlower LLM-as-Judge evaluation.
Defines test cases and runs the Claude judge scorer.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from tests.eval.llm_judge import LLMJudge, JudgeCase

JUDGE_CASES = [
    JudgeCase(
        case_id="high_risk_unverified_stale",
        agent_input="Audit DataScraper Pro 2021 — unverified, contacts+drive access, 890 days unused",
        agent_output=(
            "DataScraper Pro 2021 presents a HIGH risk. This unverified app holds "
            "full Google Drive access and Contacts access but has not been used in 890 days "
            "(nearly 2.5 years). Recommendation: REVOKE immediately."
        ),
        expected_keywords=["HIGH", "REVOKE", "unverified", "890"],
        expected_action="REVOKE",
    ),
    JudgeCase(
        case_id="first_party_keep",
        agent_input="Should Google Docs be revoked?",
        agent_output=(
            "Google Docs is a first-party Google application with low-risk "
            "profile scope only. It is actively used and verified. Recommendation: KEEP."
        ),
        expected_keywords=["KEEP", "first-party", "verified"],
        expected_action="KEEP",
    ),
    JudgeCase(
        case_id="tricky_edge_verified_recent",
        agent_input="Assess Tricky Edge Case App — verified, drive.readonly, used 2 days ago",
        agent_output=(
            "Tricky Edge Case App holds drive.readonly scope which carries "
            "High inherent risk, but it is verified and was actively used 2 days ago. "
            "Current risk score: 4/10. Recommendation: KEEP but flag for periodic review."
        ),
        expected_keywords=["KEEP", "verified", "drive.readonly"],
        expected_action="KEEP",
    ),
    JudgeCase(
        case_id="medium_risk_stale",
        agent_input="Evaluate Stale Tracker — verified, email scope, 180 days unused",
        agent_output=(
            "Stale Tracker is a verified app requesting only email access. "
            "However, it has been dormant for 180 days. Risk score: 4/10, Medium. "
            "Recommendation: KEEP but consider revoking if not needed."
        ),
        expected_keywords=["Medium", "180", "verified"],
        expected_action="KEEP",
    ),
    JudgeCase(
        case_id="critical_scope_gmail_send",
        agent_input="Assess External Mailer Bot — unverified, gmail.send scope, 350 days unused",
        agent_output=(
            "External Mailer Bot holds a CRITICAL scope: gmail.send allows "
            "the app to send emails on your behalf. The app is unverified and has not "
            "been used in 350 days. This is an extreme risk. Recommendation: REVOKE immediately."
        ),
        expected_keywords=["CRITICAL", "REVOKE", "gmail.send", "350"],
        expected_action="REVOKE",
    ),
    JudgeCase(
        case_id="low_risk_active",
        agent_input="Assess Slack Integration — verified, profile scope, used 1 day ago",
        agent_output=(
            "Slack Integration is a verified app with only profile access, "
            "used as recently as yesterday. Risk score: 1/10. Recommendation: KEEP."
        ),
        expected_keywords=["KEEP", "verified", "1"],
        expected_action="KEEP",
    ),
]


if __name__ == "__main__":
    judge = LLMJudge()
    summary = judge.run_all(JUDGE_CASES)
    # Exit with error code if average score below 6.5
    if summary["average_overall_score"] < 6.5:
        print("FAIL: Eval failed — average score below threshold (6.5)")
        sys.exit(1)
    else:
        print("PASS: Eval passed!")
        sys.exit(0)
