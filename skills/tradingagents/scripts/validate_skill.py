#!/usr/bin/env python3
"""Validate the repository-local TradingAgents skill's static contracts."""

import json
import re
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_FILE = SKILL_ROOT / "SKILL.md"
EVALS_FILE = SKILL_ROOT / "evals" / "evals.json"
REFERENCE_FILE = SKILL_ROOT / "references" / "maintenance-map.md"


def fail(message: str) -> None:
    raise SystemExit(f"skill validation failed: {message}")


def main() -> None:
    if not SKILL_FILE.is_file():
        fail(f"missing {SKILL_FILE.relative_to(SKILL_ROOT)}")
    if not REFERENCE_FILE.is_file():
        fail(f"missing {REFERENCE_FILE.relative_to(SKILL_ROOT)}")
    if not EVALS_FILE.is_file():
        fail(f"missing {EVALS_FILE.relative_to(SKILL_ROOT)}")

    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", skill_text, re.DOTALL)
    if frontmatter is None:
        fail("SKILL.md must start with YAML frontmatter")
    frontmatter_text = frontmatter.group(1)
    for field in ("name", "description"):
        if not re.search(rf"^{field}:\s*\S+", frontmatter_text, re.MULTILINE):
            fail(f"frontmatter is missing {field}")
    if not re.search(r"^name:\s*tradingagents\s*$", frontmatter_text, re.MULTILINE):
        fail("frontmatter name must be tradingagents")

    if "tradingagents analyze" in skill_text:
        fail("SKILL.md contains obsolete 'tradingagents analyze' syntax")
    required_sections = (
        "## First Checks",
        "## Persistence And Recovery",
        "## Response Contract",
        "## References",
    )
    for section in required_sections:
        if section not in skill_text:
            fail(f"SKILL.md is missing {section}")
    for path in ("feature_list.json", "progress.md", "./init.sh", "session-handoff.md"):
        if path not in skill_text:
            fail(f"SKILL.md does not mention {path}")

    try:
        data = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid eval JSON: {exc}")
    if data.get("skill_name") != "tradingagents":
        fail("eval skill_name must be tradingagents")
    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        fail("evals must be a non-empty list")
    ids = []
    for index, item in enumerate(evals, start=1):
        if not isinstance(item, dict):
            fail(f"eval {index} must be an object")
        eval_id = item.get("id")
        if not isinstance(eval_id, int) or isinstance(eval_id, bool):
            fail(f"eval {index} must have an integer id")
        ids.append(eval_id)
        for field in ("prompt", "expected_output", "expectations", "assertions"):
            if not item.get(field):
                fail(f"eval {eval_id} is missing non-empty {field}")
        if not isinstance(item["expectations"], list) or not all(
            isinstance(value, str) and value.strip() for value in item["expectations"]
        ):
            fail(f"eval {eval_id} expectations must be non-empty strings")
        if not isinstance(item["assertions"], list) or not all(
            isinstance(value, str) and value.strip() for value in item["assertions"]
        ):
            fail(f"eval {eval_id} assertions must be non-empty strings")
    if len(ids) != len(set(ids)):
        fail("eval ids must be unique")

    print(f"TradingAgents skill validation passed ({len(evals)} evals).")


if __name__ == "__main__":
    main()
