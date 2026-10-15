#!/usr/bin/env python3
"""Sync only two upstream skill-creator directories into this repository.

Runs from any working directory. Requires Git and Python 3.9+.
It intentionally REPLACES local contents of both managed skill directories.
"""

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    (
        "https://github.com/anthropics/skills.git",
        "skills/skill-creator",
        "skill-creator-anthropic",
    ),
    (
        "https://github.com/openai/skills.git",
        "skills/.system/skill-creator",
        "skill-creator-openai",
    ),
)


def git(*args: str) -> str:
    return subprocess.check_output(("git", *map(str, args)), text=True).strip()


def sync_one(url: str, source_path: str, target_name: str, temp: Path) -> None:
    checkout = temp / f"checkout-{target_name}"
    subprocess.run(
        [
            "git", "clone", "--quiet", "--depth=1", "--filter=blob:none",
            "--sparse", "--branch", "main", url, str(checkout),
        ],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(checkout), "sparse-checkout", "set", source_path],
        check=True,
    )

    source = checkout / source_path
    if not (source / "SKILL.md").is_file():
        raise RuntimeError(f"Expected SKILL.md missing from {url}/{source_path}")
    if not (source / "LICENSE.txt").is_file():
        raise RuntimeError(f"Expected LICENSE.txt missing from {url}/{source_path}")

    stage = temp / f"stage-{target_name}"
    shutil.copytree(source, stage, symlinks=True)

    # Both upstream skills are named 'skill-creator'. Give them distinct IDs
    # so they can coexist in the same agent skills directory.
    skill_file = stage / "SKILL.md"
    raw = skill_file.read_bytes().decode("utf-8")
    fm = re.match(r"\A---\n(.*?)\n---\n", raw, re.DOTALL)
    if not fm:
        raise RuntimeError(f"Unexpected SKILL.md frontmatter in {url}")
    patched_front, count = re.subn(
        r"(?m)^name:[ \t]*skill-creator[ \t]*$",
        f"name: {target_name}",
        fm.group(1),
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"Upstream skill name changed in {url}; review manually")
    notice = (
        f"<!-- Downstream modification: frontmatter name changed from "
        f"skill-creator to {target_name} to avoid an ID collision. -->\n"
    )
    patched = f"---\n{patched_front}\n---\n{notice}" + raw[fm.end():]
    skill_file.write_bytes(patched.encode("utf-8"))

    # Git tree ID identifies the exact selected folder. It won't change if
    # upstream changes unrelated files elsewhere in its large repository.
    tree_sha = git("-C", str(checkout), "rev-parse", f"HEAD:{source_path}")
    (stage / ".upstream.json").write_text(
        json.dumps(
            {
                "repository": url,
                "path": source_path,
                "git_tree_sha": tree_sha,
                "local_change": "SKILL.md frontmatter name renamed for coexistence",
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    destination = ROOT / "skills" / target_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.move(str(stage), str(destination))
    print(f"Synced {target_name} (tree {tree_sha[:12]})")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="skill-creators-") as tmp:
        for url, upstream_path, local_name in SOURCES:
            sync_one(url, upstream_path, local_name, Path(tmp))


if __name__ == "__main__":
    main()
