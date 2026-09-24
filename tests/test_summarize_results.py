from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from summarize_results import summarize  # noqa: E402


class SummarizeResultsTests(unittest.TestCase):
    def test_summarizes_resolution_cost_and_repositories(self) -> None:
        rows = [
            {
                "repo": "owner/one",
                "resolved": True,
                "patch_submitted": True,
                "patch_size": 120,
                "agent_seconds": 10,
                "tool_calls": 4,
                "llm_turns": 5,
                "agent_error": "",
            },
            {
                "repo": "owner/one",
                "resolved": False,
                "patch_submitted": False,
                "patch_size": 0,
                "agent_seconds": 30,
                "tool_calls": 8,
                "llm_turns": 9,
                "agent_error": "time budget exhausted",
            },
            {
                "repo": "owner/two",
                "resolved": False,
                "patch_submitted": True,
                "patch_size": 40,
                "agent_seconds": 20,
                "tool_calls": 6,
                "llm_turns": 7,
                "agent_error": "",
            },
        ]

        result = summarize(rows)

        self.assertEqual(3, result["tasks"])
        self.assertEqual(1, result["resolved"])
        self.assertEqual(0.3333, result["resolution_rate"])
        self.assertEqual(1, result["empty_patches"])
        self.assertEqual(20.0, result["mean_agent_seconds"])
        self.assertEqual(1, result["error_categories"]["budget"])
        self.assertEqual(0.5, result["by_repo"]["owner/one"]["resolution_rate"])


if __name__ == "__main__":
    unittest.main()
