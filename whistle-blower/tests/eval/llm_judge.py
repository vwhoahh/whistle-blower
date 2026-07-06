"""
LLM-as-Judge evaluation for WhistleBlower.
A separate Claude judge model scores WhistleBlower's agent outputs against
a correctness rubric, returning a numeric score and rationale per case.
"""

import json
import os
import sys
import datetime
from dataclasses import dataclass, field

JUDGE_RUBRIC = """
You are an expert judge evaluating a security AI agent called WhistleBlower.
WhistleBlower audits OAuth permissions and recommends revocations.

Score the agent's response on a scale of 1-10 for each of these 3 criteria:
1. Correctness: Did the agent identify the right risk level for the app described?
2. Completeness: Did the agent explain WHY the app is risky (scopes + inactivity)?
3. Clarity: Is the explanation understandable to a non-technical user?

Respond ONLY with a valid JSON object (no markdown, no preamble):
{
  "correctness": <1-10>,
  "completeness": <1-10>,
  "clarity": <1-10>,
  "overall": <average of the three, rounded to 1 decimal>,
  "rationale": "<one sentence explaining the scores>"
}
"""


@dataclass
class JudgeCase:
    case_id: str
    agent_input: str
    agent_output: str
    expected_keywords: list
    expected_action: str


class LLMJudge:
    def __init__(self):
        from anthropic import Anthropic

        self.client = Anthropic()
        # Uses ANTHROPIC_API_KEY env var automatically
        self.model = "claude-haiku-4-5"  # Fast + cheap for eval runs
        self.results = []

    def score(self, case: JudgeCase) -> dict:
        """Send agent output to Claude judge and get a structured score."""
        prompt = f"""
The WhistleBlower agent was asked: "{case.agent_input}"

The agent responded with:
---
{case.agent_output}
---

Expected action: {case.expected_action}
Expected keywords that should appear: {case.expected_keywords}

{JUDGE_RUBRIC}
"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        try:
            scores = json.loads(raw)
        except json.JSONDecodeError:
            scores = {
                "correctness": 5,
                "completeness": 5,
                "clarity": 5,
                "overall": 5.0,
                "rationale": "Parse error — defaulting to 5",
            }
        scores["case_id"] = case.case_id
        scores["expected_action"] = case.expected_action
        scores["keyword_match"] = all(
            kw.lower() in case.agent_output.lower() for kw in case.expected_keywords
        )
        self.results.append(scores)
        return scores

    def run_all(self, cases: list) -> dict:
        """Run judge on all cases, print results table, return summary."""
        print("\n" + "=" * 60)
        print("WhistleBlower LLM-as-Judge Evaluation")
        print("=" * 60)

        for case in cases:
            result = self.score(case)
            if result["overall"] >= 7.0:
                status = "PASS"
            elif result["overall"] >= 5.0:
                status = "WARN"
            else:
                status = "FAIL"
            print(
                f"{status} [{case.case_id}] Overall: {result['overall']}/10 — {result['rationale']}"
            )

        avg_overall = sum(r["overall"] for r in self.results) / len(self.results)
        keyword_pass = sum(1 for r in self.results if r["keyword_match"])

        summary = {
            "total_cases": len(self.results),
            "average_overall_score": round(avg_overall, 2),
            "keyword_match_rate": f"{keyword_pass}/{len(self.results)}",
            "pass_rate": f"{sum(1 for r in self.results if r['overall'] >= 7.0)}/{len(self.results)}",
            "timestamp": datetime.datetime.now().isoformat(),
            "detailed_results": self.results,
        }

        # Write results to file
        with open("tests/eval/judge_results.json", "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\n{'=' * 60}")
        print(f"Average Score: {avg_overall:.1f}/10")
        print(f"Keyword Match: {keyword_pass}/{len(self.results)}")
        print(f"Results saved to tests/eval/judge_results.json")
        return summary
