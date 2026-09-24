from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_submission import Validator  # noqa: E402


class SubmissionValidatorTests(unittest.TestCase):
    def copy_submission(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        target = Path(temporary.name) / "submission"
        shutil.copytree(ROOT / "submission", target)
        return temporary, target

    def test_repository_submission_passes(self) -> None:
        report = Validator(ROOT / "submission").run()
        self.assertEqual([], report.errors)
        self.assertEqual([], report.warnings)

    def test_rejects_wrong_subagent_model(self) -> None:
        temporary, target = self.copy_submission()
        self.addCleanup(temporary.cleanup)
        config = target / "sub_agents" / "code_analyzer.yaml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                "gemma-4-31b-it-qat-w4a16-ct", "some-other-model"
            ),
            encoding="utf-8",
        )

        report = Validator(target).run()

        self.assertTrue(any("must use model" in error for error in report.errors))

    def test_rejects_write_access_on_analyzer(self) -> None:
        temporary, target = self.copy_submission()
        self.addCleanup(temporary.cleanup)
        config = target / "sub_agents" / "code_analyzer.yaml"
        config.write_text(
            config.read_text(encoding="utf-8") + "\n  - write_file\n",
            encoding="utf-8",
        )

        report = Validator(target).run()

        self.assertTrue(
            any("must remain read-only" in error for error in report.errors)
        )

    def test_rejects_unknown_evaluation_key(self) -> None:
        temporary, target = self.copy_submission()
        self.addCleanup(temporary.cleanup)
        config = target / "eval_config.yaml"
        config.write_text(
            config.read_text(encoding="utf-8") + "  context_compaction: true\n",
            encoding="utf-8",
        )

        report = Validator(target).run()

        self.assertTrue(
            any("unsupported fields" in error for error in report.errors)
        )

    def test_rejects_parent_include_even_when_it_resolves_inside_root(self) -> None:
        temporary, target = self.copy_submission()
        self.addCleanup(temporary.cleanup)
        config = target / "agent.yaml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                "!include prompts/system.md",
                "!include prompts/../prompts/system.md",
            ),
            encoding="utf-8",
        )

        report = Validator(target).run()

        self.assertTrue(
            any("!include path traversal" in error for error in report.errors)
        )


if __name__ == "__main__":
    unittest.main()
