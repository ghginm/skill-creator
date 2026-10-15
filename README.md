# Skill Creator

A repository of two upstream skill-creation toolkits, kept under distinct names so an agent can use either or combine them. This is an authoring toolbox, not an application, a skill registry, or an automatic installer.

**Agents: start with [AGENTS.md](AGENTS.md), then follow the [skill creation guide](docs/skill-creation.md).**

## Choose a toolkit

| Need | Start here |
| --- | --- |
| Understand skill structure, scaffold a skill, or generate Codex UI metadata | [OpenAI creator](skills/skill-creator-openai/SKILL.md) |
| Draft and improve skills through test prompts, baselines, grading, and human review | [Anthropic creator](skills/skill-creator-anthropic/SKILL.md) |
| Create a skill with both scaffolding and evaluation | OpenAI initialization, then Anthropic evaluation; use the guide's repository-root commands |

Both are instructions plus executable helpers. Read the selected `SKILL.md` before using its tools. Provider-specific commands are not automatically portable to other agents.

## Quick start

Run from this repository's root in a POSIX shell with Python 3.10+:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install PyYAML
export PYTHONDONTWRITEBYTECODE=1
export REPO_ROOT="$PWD"
export SKILL_OUTPUT_ROOT="$(dirname "$REPO_ROOT")/authored-skills"

python "$REPO_ROOT/skills/skill-creator-openai/scripts/init_skill.py" example-skill \
  --path "$SKILL_OUTPUT_ROOT" \
  --resources scripts,references \
  --interface 'display_name=Example Skill' \
  --interface 'short_description=Create and validate example task outputs' \
  --interface 'default_prompt=Use $example-skill to complete the example workflow.'
```

This creates a **draft**, not a finished skill. Replace the frontmatter description and all TODOs, implement only needed resources, and run:

```bash
python "$REPO_ROOT/skills/skill-creator-openai/scripts/quick_validate.py" \
  "$SKILL_OUTPUT_ROOT/example-skill"
python "$REPO_ROOT/skills/skill-creator-anthropic/scripts/quick_validate.py" \
  "$SKILL_OUTPUT_ROOT/example-skill"
```

Then exercise the skill on real prompts. The [full guide](docs/skill-creation.md) covers authoring, validation limits, evaluation, packaging, and handoff. Output is deliberately outside this checkout: it is not committed or installed automatically.

## Repository map

```text
AGENTS.md                              Agent entry point and repository boundaries
README.md                              Overview and quick start
docs/skill-creation.md                  End-to-end authoring workflow
scripts/sync_skill_creators.py          Destructive refresh of the two vendored toolkits
.github/workflows/update-skill-creators.yml
                                       Scheduled/manual upstream-update PR workflow
skills/skill-creator-openai/            OpenAI authoring instructions and helpers
skills/skill-creator-anthropic/         Anthropic authoring/evaluation instructions and helpers
```

Each toolkit includes `LICENSE.txt` and `.upstream.json`. The latter records the upstream repository, source path, selected directory's Git tree SHA, and local name change. See the bundled licenses before redistributing upstream material; they do not establish a license for skills you author.

## Upstream maintenance

**Do not put authored skills or local documentation inside either managed toolkit directory.** The sync script deletes and replaces both directories, including untracked files inside them. It fetches each upstream repository's `main`, renames the skill's frontmatter `name` for coexistence, adds a notice, and records provenance. It is not a dry run and has no command-line options or rollback across both sources.

Only when intentionally updating the vendored toolkits:

```bash
python3 scripts/sync_skill_creators.py
git diff --stat
git diff -- skills/skill-creator-openai skills/skill-creator-anthropic
```

Sync needs Git, Python 3.9+, and network access. Review executable-script changes and run both bundled validators on the refreshed toolkits before committing.

The configured GitHub Actions workflow runs Mondays at 07:23 UTC or via manual dispatch. It proposes updates on `automation/update-skill-creators`; it does not automatically merge them or validate authored skills. Its commit convention is `chore(skills): sync skill-creators from upstream`.

## Contributing

Keep repository-specific guidance in root docs or `docs/`, not in vendored files. Use focused branches such as `docs/agent-skill-creation-guide` and Conventional Commit messages such as `docs: explain the agent skill creation workflow`. Stage only intended files; leave local environments, generated skills, evaluation outputs, and Python caches out of commits. There is no repository-wide test suite or dependency manifest; verify documented commands using an external scratch skill before changing the guide.
