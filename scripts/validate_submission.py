#!/usr/bin/env python3
"""Fast, offline preflight checks for the Kaggle submission directory.

This catches repository-local mistakes without claiming to replace the official
``adk_submission`` compiler distributed in the competition dataset.
"""

from __future__ import annotations

import argparse
import re
import stat
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only without dev deps
    raise SystemExit(
        "PyYAML is required for validation. Install requirements-dev.txt."
    ) from exc


MODEL = "gemma-4-31b-it-qat-w4a16-ct"
BUILTIN_TOOLS = {
    "run_command",
    "submit_patch",
    "get_status",
    "read_file",
    "edit_file",
    "write_file",
    "get_code_neighbors",
    "search_similar_code",
    "get_code_subgraph",
}
READ_ONLY_TOOLS = {
    "read_file",
    "get_code_neighbors",
    "search_similar_code",
    "get_code_subgraph",
}
ALLOWED_EXTENSIONS = {
    ".json",
    ".md",
    ".py",
    ".safetensors",
    ".txt",
    ".yaml",
    ".yml",
}
EXPECTED_PATHS = {
    "agent.yaml",
    "eval_config.yaml",
    "configs/sampling.yaml",
    "prompts/system.md",
    "prompts/analyzer.md",
    "sub_agents/code_analyzer.yaml",
    "skills/repo_navigation/SKILL.md",
}


class IncludeRef(str):
    """Marker value returned by the safe YAML loader for ``!include``."""


class SubmissionLoader(yaml.SafeLoader):
    """Safe YAML loader that preserves include paths for explicit validation."""


def _include(loader: SubmissionLoader, node: yaml.Node) -> IncludeRef:
    return IncludeRef(loader.construct_scalar(node))


SubmissionLoader.add_constructor("!include", _include)


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


class Validator:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.report = Report()
        self._validated_agents: set[Path] = set()

    def run(self) -> Report:
        if not self.root.is_dir():
            self.report.error(f"submission directory does not exist: {self.root}")
            return self.report

        self._validate_files()
        self._validate_expected_paths()
        self._validate_agent(self.root / "agent.yaml", is_root=True)
        self._validate_eval_config()
        self._validate_skills()
        self._validate_adapters()
        return self.report

    def _relative(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return str(path)

    def _inside_root(self, path: Path, context: str) -> Path | None:
        resolved = path.resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError:
            self.report.error(f"{context} escapes submission root: {path}")
            return None
        return resolved

    def _load_yaml(self, path: Path) -> dict[str, Any] | None:
        if not path.is_file():
            self.report.error(f"missing YAML file: {self._relative(path)}")
            return None
        try:
            data = yaml.load(path.read_text(encoding="utf-8"), Loader=SubmissionLoader)
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            self.report.error(f"invalid YAML {self._relative(path)}: {exc}")
            return None
        if not isinstance(data, dict):
            self.report.error(f"YAML root must be a mapping: {self._relative(path)}")
            return None
        return data

    def _resolve_include(
        self, value: Any, source: Path, *, expected_yaml: bool
    ) -> Any:
        if not isinstance(value, IncludeRef):
            return value
        if ".." in str(value).replace("\\", "/").split("/"):
            self.report.error(
                f"!include path traversal in {self._relative(source)}: {value}"
            )
            return None
        candidate = self._inside_root(source.parent / str(value), "!include")
        if candidate is None:
            return None
        if not candidate.is_file():
            self.report.error(
                f"missing include from {self._relative(source)}: {value}"
            )
            return None
        if candidate.suffix not in {".md", ".txt", ".yaml", ".yml"}:
            self.report.error(f"unsupported include extension: {self._relative(candidate)}")
            return None
        if expected_yaml:
            return self._load_yaml(candidate)
        try:
            return candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.report.error(f"cannot read include {self._relative(candidate)}: {exc}")
            return None

    def _validate_files(self) -> None:
        for path in self.root.rglob("*"):
            if path.is_symlink():
                self.report.error(f"symlinks are not allowed: {self._relative(path)}")
                continue
            if not path.is_file():
                continue
            relative = self._relative(path)
            if path.name == ".gitkeep":
                if relative != "adapters/.gitkeep":
                    self.report.error(f"unexpected repository marker: {relative}")
                continue
            if path.suffix.lower() not in ALLOWED_EXTENSIONS:
                self.report.error(f"unsupported submission file extension: {relative}")

    def _validate_expected_paths(self) -> None:
        present = {
            self._relative(path)
            for path in self.root.rglob("*")
            if path.is_file()
        }
        for expected in sorted(EXPECTED_PATHS - present):
            self.report.error(f"missing required starter file: {expected}")

    def _validate_agent(self, path: Path, *, is_root: bool) -> None:
        resolved = path.resolve()
        if resolved in self._validated_agents:
            self.report.error(f"cyclic or duplicate agent reference: {self._relative(path)}")
            return
        self._validated_agents.add(resolved)

        data = self._load_yaml(path)
        if data is None:
            return

        allowed_fields = {
            "agent_class",
            "name",
            "model",
            "adapter",
            "description",
            "instruction",
            "generate_content_config",
            "tools",
        }
        unknown = set(data) - allowed_fields
        if unknown:
            self.report.error(
                f"{self._relative(path)} has unsupported fields: {sorted(unknown)}"
            )

        if data.get("agent_class", "LlmAgent") != "LlmAgent":
            self.report.error(f"{self._relative(path)} must be an LlmAgent")
        if data.get("model") != MODEL:
            self.report.error(
                f"{self._relative(path)} must use model {MODEL!r}"
            )
        if not isinstance(data.get("name"), str) or not data["name"].strip():
            self.report.error(f"{self._relative(path)} needs a non-empty name")

        instruction = self._resolve_include(
            data.get("instruction"), path, expected_yaml=False
        )
        if not isinstance(instruction, str) or not instruction.strip():
            self.report.error(f"{self._relative(path)} needs a non-empty instruction")
        elif not is_root and path.name == "code_analyzer.yaml":
            reference = self.root / "prompts" / "analyzer.md"
            if reference.is_file():
                expected = " ".join(reference.read_text(encoding="utf-8").split())
                actual = " ".join(instruction.split())
                if actual != expected:
                    self.report.error(
                        "inline code_analyzer instruction drifted from "
                        "prompts/analyzer.md"
                    )

        generation = self._resolve_include(
            data.get("generate_content_config"), path, expected_yaml=True
        )
        self._validate_generation_config(generation, path)
        self._validate_tools(data.get("tools"), path, is_root=is_root)

    def _validate_generation_config(self, data: Any, source: Path) -> None:
        if not isinstance(data, dict):
            self.report.error(
                f"{self._relative(source)} needs a generation config mapping"
            )
            return
        allowed = {
            "temperature",
            "top_p",
            "top_k",
            "max_output_tokens",
            "thinking_config",
        }
        unknown = set(data) - allowed
        if unknown:
            self.report.error(
                f"generation config has unsupported fields: {sorted(unknown)}"
            )
        max_tokens = data.get("max_output_tokens")
        if not isinstance(max_tokens, int) or not 1 <= max_tokens <= 32768:
            self.report.error("max_output_tokens must be an integer in [1, 32768]")
        temperature = data.get("temperature")
        if not isinstance(temperature, (int, float)) or temperature < 0:
            self.report.error("temperature must be a non-negative number")
        top_p = data.get("top_p")
        if not isinstance(top_p, (int, float)) or not 0 <= top_p <= 1:
            self.report.error("top_p must be a number in [0, 1]")

        thinking = data.get("thinking_config")
        if not isinstance(thinking, dict):
            self.report.error("thinking_config must be a mapping")
            return
        unknown_thinking = set(thinking) - {
            "thinking_level",
            "thinking_budget",
            "include_thoughts",
        }
        if unknown_thinking:
            self.report.error(
                f"thinking_config has unsupported fields: {sorted(unknown_thinking)}"
            )
        if thinking.get("thinking_level") not in {"low", "medium", "high"}:
            self.report.error("thinking_level must be low, medium, or high")
        budget = thinking.get("thinking_budget")
        if not isinstance(budget, int) or not 1 <= budget <= 32768:
            self.report.error("thinking_budget must be an integer in [1, 32768]")
        if not isinstance(thinking.get("include_thoughts"), bool):
            self.report.error("include_thoughts must be a boolean")

    def _validate_tools(self, tools: Any, source: Path, *, is_root: bool) -> None:
        if not isinstance(tools, list) or not tools:
            self.report.error(f"{self._relative(source)} needs a non-empty tools list")
            return

        plain_tools: list[str] = []
        agent_tool_count = 0
        for entry in tools:
            if isinstance(entry, str):
                plain_tools.append(entry)
                if entry not in BUILTIN_TOOLS:
                    self.report.error(
                        f"{self._relative(source)} references unknown tool {entry!r}"
                    )
                continue
            if not isinstance(entry, dict) or set(entry) != {"agent_tool"}:
                self.report.error(
                    f"{self._relative(source)} has invalid tool entry: {entry!r}"
                )
                continue

            agent_tool_count += 1
            config = entry["agent_tool"]
            if not isinstance(config, dict):
                self.report.error("agent_tool must be a mapping")
                continue
            unknown = set(config) - {"config_path", "skip_summarization"}
            if unknown:
                self.report.error(
                    f"agent_tool has unsupported fields: {sorted(unknown)}"
                )
            config_path = config.get("config_path")
            if not isinstance(config_path, str) or not config_path:
                self.report.error("agent_tool requires config_path")
                continue
            if ".." in config_path.replace("\\", "/").split("/"):
                self.report.error(f"agent_tool path traversal: {config_path}")
                continue
            target = self._inside_root(source.parent / config_path, "agent_tool")
            if target is not None:
                self._validate_agent(target, is_root=False)
            if config.get("skip_summarization") is not True:
                self.report.warn(
                    "agent_tool skip_summarization should be true to isolate exploration"
                )

        if len(plain_tools) != len(set(plain_tools)):
            self.report.error(f"{self._relative(source)} contains duplicate tools")
        tool_set = set(plain_tools)
        if is_root:
            missing = BUILTIN_TOOLS - tool_set
            if missing:
                self.report.error(f"root agent is missing tools: {sorted(missing)}")
            if agent_tool_count > 1:
                self.report.error("root agent may declare at most one analyzer agent_tool")
        elif not tool_set <= READ_ONLY_TOOLS:
            self.report.error(
                f"sub-agent must remain read-only; found {sorted(tool_set - READ_ONLY_TOOLS)}"
            )

    def _validate_eval_config(self) -> None:
        path = self.root / "eval_config.yaml"
        data = self._load_yaml(path)
        if data is None:
            return
        if set(data) != {"evaluation"} or not isinstance(data["evaluation"], dict):
            self.report.error("eval_config.yaml must contain only an evaluation mapping")
            return
        evaluation = data["evaluation"]
        expected = {
            "timeout_seconds",
            "max_tool_calls",
            "max_time_minutes",
            "max_turns",
        }
        unknown = set(evaluation) - expected
        missing = expected - set(evaluation)
        if unknown:
            self.report.error(f"evaluation has unsupported fields: {sorted(unknown)}")
        if missing:
            self.report.error(f"evaluation is missing fields: {sorted(missing)}")
        for key in expected:
            value = evaluation.get(key)
            if not isinstance(value, int) or value <= 0:
                self.report.error(f"evaluation.{key} must be a positive integer")
        timeout = evaluation.get("timeout_seconds")
        minutes = evaluation.get("max_time_minutes")
        if isinstance(timeout, int) and isinstance(minutes, int):
            if timeout > minutes * 60:
                self.report.error(
                    "evaluation.timeout_seconds cannot exceed the task time budget"
                )

    def _validate_skills(self) -> None:
        for manifest in self.root.glob("skills/*/SKILL.md"):
            text = manifest.read_text(encoding="utf-8")
            match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
            if not match:
                self.report.error(
                    f"skill manifest lacks YAML frontmatter: {self._relative(manifest)}"
                )
                continue
            try:
                frontmatter = yaml.safe_load(match.group(1))
            except yaml.YAMLError as exc:
                self.report.error(
                    f"invalid skill frontmatter {self._relative(manifest)}: {exc}"
                )
                continue
            if not isinstance(frontmatter, dict):
                self.report.error(
                    f"skill frontmatter must be a mapping: {self._relative(manifest)}"
                )
                continue
            name = frontmatter.get("name")
            expected_name = manifest.parent.name
            if name != expected_name:
                self.report.error(
                    f"skill name {name!r} must match directory {expected_name!r}"
                )
            if not isinstance(name, str) or not re.fullmatch(
                r"[a-z0-9]+(?:[-_][a-z0-9]+)*", name
            ):
                self.report.error(f"invalid skill name: {name!r}")
            if not isinstance(frontmatter.get("description"), str):
                self.report.error(f"skill {name!r} needs a description")
            for script in (manifest.parent / "scripts").glob("*"):
                if script.is_file() and not script.stat().st_mode & stat.S_IXUSR:
                    self.report.error(
                        f"skill script is not executable: {self._relative(script)}"
                    )

    def _validate_adapters(self) -> None:
        adapters = self.root / "adapters"
        if not adapters.is_dir():
            self.report.error("missing adapters directory")
            return
        for child in adapters.iterdir():
            if child.name == ".gitkeep":
                continue
            if not child.is_dir():
                self.report.error(
                    f"adapter entries must be directories: {self._relative(child)}"
                )
                continue
            required = {"adapter_config.json", "adapter_model.safetensors"}
            present = {path.name for path in child.iterdir() if path.is_file()}
            missing = required - present
            if missing:
                self.report.error(
                    f"adapter {child.name!r} is incomplete; missing {sorted(missing)}"
                )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submission_dir", nargs="?", default="submission")
    parser.add_argument(
        "--strict", action="store_true", help="treat warnings as failures"
    )
    args = parser.parse_args()

    report = Validator(Path(args.submission_dir)).run()
    for warning in report.warnings:
        print(f"warning: {warning}")
    for error in report.errors:
        print(f"error: {error}", file=sys.stderr)

    if report.errors or (args.strict and report.warnings):
        print(
            f"validation failed: {len(report.errors)} error(s), "
            f"{len(report.warnings)} warning(s)",
            file=sys.stderr,
        )
        return 1
    print(f"validation passed: {args.submission_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
