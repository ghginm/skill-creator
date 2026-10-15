# Agent instructions

## Start here

This repo vendors two skill-creation toolkits. It is not the destination for a new skill unless the user explicitly asks to store one here.

1. Read [README.md](README.md) for the layout and setup.
2. Read [docs/skill-creation.md](docs/skill-creation.md) for commands and acceptance criteria.
3. Choose and read the relevant creator:
   - [OpenAI](skills/skill-creator-openai/SKILL.md): structure, initialization, Codex metadata.
   - [Anthropic](skills/skill-creator-anthropic/SKILL.md): drafting, evals, baselines, grading, review, iteration.
   - For both, initialize with OpenAI and evaluate with Anthropic. Do not read every reference upfront; load the resources for the current phase.

## Boundaries

- Treat `skills/skill-creator-openai/` and `skills/skill-creator-anthropic/` as upstream-managed. Do not edit them for an ordinary authoring or documentation task. Their contents are replaced by sync.
- Do not run `scripts/sync_skill_creators.py` to set up skill creation. Run it only for an explicitly requested upstream refresh; it deletes and replaces both managed directories.
- Use a user-specified output path. Otherwise use an `authored-skills/` sibling of this checkout, as in the guide. Keep eval workspaces beside the authored skill and archives outside it.
- Do not install into a harness, overwrite an installed skill, or alter global agent configuration without user authorization. A `.skill` archive is not an installation.
- Keep this repo's onboarding docs outside the vendored directories. Preserve provenance files and bundled licenses.
- Inspect `git status` before edits. Preserve unrelated changes and untracked files; stage explicit paths rather than `git add .`.

## Execution and verification

- Use Python 3.10+ and PyYAML for the combined authoring/evaluation workflow. The sync script alone needs only Python 3.9+ and Git.
- Run OpenAI helpers by script path. Run Anthropic helpers that import `scripts.*` as modules from the Anthropic toolkit directory; see the guide's subshell examples.
- Upstream instructions use toolkit-relative paths and sometimes assume Claude-specific tools. Translate paths using the guide; do not invent unavailable tools or pass another provider's model ID to `claude`.
- The bundled validators differ: OpenAI rejects `compatibility`, while Anthropic accepts it. Start with `name` and `description` for skills intended to pass both.
- A validator pass proves basic metadata validity, not behavior, resource-link correctness, security, or installation. Remove TODOs, inspect resources, execute bundled scripts, and test realistic prompts separately.
- Preserve real evidence. Report unavailable baselines, missing timing data, or missing CLI authentication as limitations, not successful evals.

## Definition of done

Deliver the completed skill directory (and archive if requested), validation results, actual test evidence, and any remaining limitations. For repository documentation changes, exercise the documented local command path on an external scratch skill, check links and `git diff --check`, and report exactly what was verified.

Use focused branches (`docs/<topic>`, `feat/<topic>`, `fix/<topic>`) and Conventional Commits (`docs: ...`, `feat: ...`, `fix: ...`). Commit and push only when requested; never merge or rewrite history implicitly. Verify the remote branch's SHA after pushing. If authentication blocks a push, report the local commit and the blocker rather than claiming publication.
