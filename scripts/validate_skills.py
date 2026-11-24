#!/usr/bin/env python3
"""Validate all skills in this repository against the agentskills.io specification.

Checks:
  1. Flat layout only: skills/<name>/SKILL.md (fails if nested SKILL.md files exist).
  2. Strict YAML frontmatter: only the 6 agentskills.io keys allowed
     (name, description, license, compatibility, metadata, allowed-tools).
  3. Field constraints:
       - name: required, matches folder name, ^[a-z0-9]+(-[a-z0-9]+)*$, <= 64 chars
       - description: required, non-empty, <= 1024 chars
       - compatibility: optional, <= 500 chars
  4. Line budget: warns > 400 lines, fails > 500 lines.
  5. Relative markdown links in SKILL.md resolve to real files/directories.
  6. Portability: fails on hardcoded /home/nithish/ or ~/.claude/skills/ paths
     in SKILL.md, references/, and scripts/.
  7. Python syntax: runs py_compile on every .py file under skills/ and scripts/.
"""

from __future__ import annotations

import argparse
import py_compile
import re
import sys
from pathlib import Path

ALLOWED_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HARDCODED_PATTERNS = [
    (re.compile(r"/home/nithish(?:/|\b)"), "hardcoded /home/nithish path"),
    (re.compile(r"~/\.claude/skills(?:/|\b)"), "hardcoded ~/.claude/skills path"),
    (re.compile(r"~/\.gemini/config/skills(?:/|\b)"), "hardcoded ~/.gemini/config/skills path"),
]


def parse_frontmatter(text: str) -> tuple[dict[str, object] | None, str, str | None]:
    """Parse YAML frontmatter without requiring PyYAML.

    Returns (fields_dict, body_text, error_message).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, "missing opening '---' YAML frontmatter delimiter"

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return None, text, "missing closing '---' YAML frontmatter delimiter"

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])

    # Try PyYAML first if installed, otherwise use our strict stdlib parser.
    try:
        import yaml  # type: ignore

        data = yaml.safe_load("\n".join(fm_lines))
        if not isinstance(data, dict):
            return None, body, "YAML frontmatter must be a mapping"
        return data, body, None
    except ImportError:
        pass
    except Exception as exc:
        return None, body, f"invalid YAML frontmatter: {exc}"

    fields: dict[str, object] = {}
    i = 0
    while i < len(fm_lines):
        raw = fm_lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        if raw.startswith((" ", "\t")):
            return None, body, f"unexpected indentation in frontmatter line {i + 2}: {raw!r}"
        if ":" not in raw:
            return None, body, f"malformed frontmatter line {i + 2}: {raw!r}"

        key, rest = raw.split(":", 1)
        key = key.strip()
        val = rest.strip()

        if val in (">", "|", ">-", "|-"):
            fold = val.startswith(">")
            block: list[str] = []
            i += 1
            while i < len(fm_lines):
                nxt = fm_lines[i]
                if nxt.strip() == "":
                    block.append("")
                    i += 1
                elif nxt.startswith((" ", "\t")):
                    block.append(nxt.strip())
                    i += 1
                else:
                    break
            fields[key] = (" ".join(b for b in block if b) if fold else "\n".join(block)).strip()
            continue

        if val == "":
            # Nested map (e.g. metadata:) or empty scalar
            nested: dict[str, str] = {}
            i += 1
            while i < len(fm_lines):
                nxt = fm_lines[i]
                if not nxt.strip() or nxt.lstrip().startswith("#"):
                    i += 1
                    continue
                if nxt.startswith((" ", "\t")):
                    if ":" in nxt:
                        nk, nv = nxt.strip().split(":", 1)
                        nested[nk.strip()] = nv.strip().strip('"').strip("'")
                    i += 1
                else:
                    break
            fields[key] = nested if nested else ""
            continue

        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        fields[key] = val
        i += 1

    return fields, body, None


def strip_code_fences(md: str) -> str:
    """Remove fenced code blocks so example snippets don't trigger link checks."""
    out: list[str] = []
    in_fence = False
    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def check_hardcoded_paths(path: Path, repo_root: Path, errors: list[str]) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return
    rel = path.relative_to(repo_root)
    for lineno, line in enumerate(text.splitlines(), 1):
        for pat, label in HARDCODED_PATTERNS:
            if pat.search(line):
                errors.append(f"{rel}:{lineno}: {label}")


def validate_repo(repo_root: Path, strict: bool = False) -> int:
    skills_dir = repo_root / "skills"
    errors: list[str] = []
    warnings: list[str] = []

    if not skills_dir.is_dir():
        print(f"FAIL: skills directory not found at {skills_dir}", file=sys.stderr)
        return 1

    skill_files = sorted(skills_dir.rglob("SKILL.md"))
    if not skill_files:
        errors.append("no SKILL.md files found under skills/")

    validated_skills: list[str] = []

    for skill_md in skill_files:
        rel_skill = skill_md.relative_to(repo_root)
        skill_dir = skill_md.parent

        # 1. Flat layout check
        if skill_dir.parent != skills_dir:
            errors.append(
                f"{rel_skill}: nested sub-skill is forbidden by agentskills.io flat layout "
                f"(must be skills/<name>/SKILL.md)"
            )
            continue

        folder_name = skill_dir.name
        validated_skills.append(folder_name)
        text = skill_md.read_text(encoding="utf-8")
        lines = text.splitlines()

        # 2. Frontmatter check
        fm, body, fm_err = parse_frontmatter(text)
        if fm_err or fm is None:
            errors.append(f"{rel_skill}: {fm_err}")
            continue

        extra_keys = sorted(set(fm.keys()) - ALLOWED_KEYS)
        if extra_keys:
            errors.append(
                f"{rel_skill}: disallowed frontmatter key(s): {', '.join(extra_keys)} "
                f"(allowed: {', '.join(sorted(ALLOWED_KEYS))})"
            )

        # 3. Field constraints
        name = fm.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{rel_skill}: missing required frontmatter key 'name'")
        else:
            name = name.strip()
            if name != folder_name:
                errors.append(f"{rel_skill}: frontmatter name '{name}' != folder name '{folder_name}'")
            if len(name) > 64:
                errors.append(f"{rel_skill}: name '{name}' exceeds 64 chars ({len(name)})")
            if not NAME_RE.match(name):
                errors.append(f"{rel_skill}: name '{name}' must match ^[a-z0-9]+(-[a-z0-9]+)*$")

        desc = fm.get("description")
        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{rel_skill}: missing required frontmatter key 'description'")
        elif len(desc.strip()) > 1024:
            errors.append(f"{rel_skill}: description exceeds 1024 chars ({len(desc.strip())})")

        compat = fm.get("compatibility")
        if compat is not None and isinstance(compat, str) and len(compat.strip()) > 500:
            errors.append(f"{rel_skill}: compatibility exceeds 500 chars ({len(compat.strip())})")

        # 4. Line budget
        if len(lines) > 500:
            errors.append(f"{rel_skill}: exceeds 500-line budget ({len(lines)} lines)")
        elif len(lines) > 400:
            warnings.append(f"{rel_skill}: approaching 500-line budget ({len(lines)} lines)")

        # 5. Relative markdown links in SKILL.md
        clean_body = strip_code_fences(body)
        for match in MD_LINK_RE.finditer(clean_body):
            raw_target = match.group(1).strip()
            if not raw_target or raw_target.startswith(("http://", "https://", "mailto:", "#", "<")):
                continue
            # Strip optional title or anchor fragment
            target = raw_target.split()[0].split("#", 1)[0]
            if not target or "<" in target or ">" in target:
                continue
            resolved = (skill_dir / target).resolve()
            if not resolved.exists():
                errors.append(f"{rel_skill}: broken relative link -> {target}")

        # 6. Portability checks across SKILL.md, references/, scripts/
        check_hardcoded_paths(skill_md, repo_root, errors)
        for sub in ("references", "scripts"):
            sub_dir = skill_dir / sub
            if sub_dir.is_dir():
                for f in sorted(sub_dir.rglob("*")):
                    if f.is_file() and "__pycache__" not in f.parts and f.suffix in (".md", ".py", ".sh", ".txt", ".json"):
                        check_hardcoded_paths(f, repo_root, errors)

    # 7. py_compile on all Python scripts under skills/ and scripts/
    py_files: list[Path] = []
    for base in (skills_dir, repo_root / "scripts"):
        if base.is_dir():
            for py in sorted(base.rglob("*.py")):
                if "__pycache__" in py.parts:
                    continue
                py_files.append(py)
                try:
                    py_compile.compile(str(py), doraise=True)
                except py_compile.PyCompileError as exc:
                    errors.append(f"{py.relative_to(repo_root)}: py_compile failed: {exc.msg}")

    # Report
    print(f"Validated {len(validated_skills)} skill(s) and {len(py_files)} Python script(s).")
    if validated_skills:
        print("Skills:", ", ".join(validated_skills))

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"FAIL: {e}")

    if errors or (strict and warnings):
        print(f"\nResult: FAILED ({len(errors)} error(s), {len(warnings)} warning(s))")
        return 1

    print(f"\nResult: PASSED (0 errors, {len(warnings)} warning(s))")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate agentskills.io compliance for this repo.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Path to repository root (default: parent of scripts/).",
    )
    args = parser.parse_args()
    return validate_repo(args.repo.resolve(), strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
