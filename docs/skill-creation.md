# Create a skill with this repository

## Contents

1. [Choose a workflow](#1-choose-a-workflow)
2. [Prepare the environment and output location](#2-prepare-the-environment-and-output-location)
3. [Initialize a new skill](#3-initialize-a-new-skill)
4. [Write the skill](#4-write-the-skill)
5. [Validate structure and resources](#5-validate-structure-and-resources)
6. [Test behavior and iterate](#6-test-behavior-and-iterate)
7. [Package and hand off](#7-package-and-hand-off)
8. [Troubleshooting](#troubleshooting)

## 1. Choose a workflow

Use the OpenAI creator for scaffolding and Codex metadata. Use the Anthropic creator for its draft → test → review → improve process. They can be combined: there is no requirement to author with the provider whose agent will eventually consume the skill.

Read the selected creator's `SKILL.md` first:

- [OpenAI creator](../skills/skill-creator-openai/SKILL.md)
- [Anthropic creator](../skills/skill-creator-anthropic/SKILL.md)

Capture the task, expected inputs and outputs, required tools, realistic trigger phrases, near-miss requests that should not trigger, and success criteria. Use information already provided; ask only for missing decisions that affect the result. Confirm the target agent/harness and whether installation or packaging is wanted.

For an existing skill, work on a writable copy, preserve its identifier, and snapshot the original outside the skill before editing. Skip initialization. Use the original as the baseline when evaluating an improvement.

## 2. Prepare the environment and output location

The examples below use a POSIX shell. Start at the repository root. Python 3.10+ covers the bundled evaluation helpers' type syntax; PyYAML is needed by initialization, metadata generation, and validation. No project dependency manifest is provided.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install PyYAML
export PYTHONDONTWRITEBYTECODE=1
export REPO_ROOT="$PWD"
export OPENAI_CREATOR="$REPO_ROOT/skills/skill-creator-openai"
export ANTHROPIC_CREATOR="$REPO_ROOT/skills/skill-creator-anthropic"
export SKILL_OUTPUT_ROOT="$(dirname "$REPO_ROOT")/authored-skills"
export SKILL_NAME="example-skill"
export SKILL_DIR="$SKILL_OUTPUT_ROOT/$SKILL_NAME"
```

If the user supplies a different output location, set `SKILL_OUTPUT_ROOT` to that parent directory instead. The sibling directory is a safe default, not a required installation location. A `.venv` created here is local-only; do not stage it.

Do not create output inside either vendored creator. Upstream sync replaces those directories. Setup, initialization, validation, aggregation, review generation, and packaging do **not** require running sync.

## 3. Initialize a new skill

After reading the OpenAI creator, use its initializer even if you intend to evaluate with the Anthropic workflow:

```bash
python "$OPENAI_CREATOR/scripts/init_skill.py" "$SKILL_NAME" \
  --path "$SKILL_OUTPUT_ROOT" \
  --resources scripts,references \
  --interface 'display_name=Example Skill' \
  --interface 'short_description=Create and validate example task outputs' \
  --interface 'default_prompt=Use $example-skill to complete the example workflow.'
```

Replace the example values for a real task. Keep the default prompt's `$skill-name` literal; single quotes prevent shell expansion. Only request resource directories that are useful. `assets` is also supported; omit `--resources` for a text-only skill. `--examples` adds placeholder files, not working task implementations.

The initializer creates:

```text
example-skill/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
└── references/
```

It refuses an existing destination. It also normalizes names to lowercase hyphen-case; choose a valid name deliberately and inspect the reported output path. Keep the folder and frontmatter name identical, at most 64 characters, with no leading/trailing or repeated hyphens.

**The generated template is incomplete.** Its TODO description is not a finished string value, and initialization success is not validation success.

## 4. Write the skill

Replace the generated TODOs and remove the template's structure-selection instructions. Start with minimal frontmatter:

```yaml
---
name: example-skill
description: "Create and validate example task outputs. Use when the user asks to run or adapt the example workflow and needs a checked output artifact."
---
```

For the real description, explain the capability and triggering contexts in user language. Keep it nonempty, at most 1,024 characters, and without angle brackets. Put use conditions in the description, not only in the body: agents use metadata to decide whether to load the body.

Write concise, executable instructions covering:

- Required inputs and prerequisite/tool checks.
- The action sequence and decisions that require user input.
- Exact output formats and where to save artifacts.
- Failure handling and boundaries for destructive or external actions.
- Verification steps and what evidence to report.
- Direct pointers to bundled references, with when to read each one.

Prefer a body under 500 lines. Put detailed knowledge in `references/`, reusable deterministic code in `scripts/`, and copyable output templates in `assets/`. Keep resource links directly discoverable from `SKILL.md`. Delete unused empty directories and example files. Do not add a README or changelog inside the skill merely to explain its creation; keep development notes outside the deliverable.

For Codex UI metadata, read [the bundled field reference](../skills/skill-creator-openai/references/openai_yaml.md). Regenerate after finalizing the skill text:

```bash
python "$OPENAI_CREATOR/scripts/generate_openai_yaml.py" "$SKILL_DIR" \
  --interface 'display_name=Example Skill' \
  --interface 'short_description=Create and validate example task outputs' \
  --interface 'default_prompt=Use $example-skill to complete the example workflow.'
```

The short description must be 25–64 characters. This file is product-specific UI metadata, not a substitute for `SKILL.md`, and is not necessarily used by other harnesses.

## 5. Validate structure and resources

Run both validators for a skill intended to work with both toolkits:

```bash
python "$OPENAI_CREATOR/scripts/quick_validate.py" "$SKILL_DIR"
python "$ANTHROPIC_CREATOR/scripts/quick_validate.py" "$SKILL_DIR"
```

These check basic frontmatter shape, required fields, name syntax/length, and description type/length. They are **not** full correctness checks: among other limitations, empty string values can pass, and they do not enforce folder/name equality, resolve resource links, detect every placeholder, or test task behavior.

The checked-in validators disagree about `compatibility`: Anthropic accepts it; OpenAI rejects it. For the shared path, use only `name` and `description` unless extra fields are required and deliberately checked against the target. Do not edit the vendored validator to make your skill pass. A target-specific field is a portability decision to report, not a reason to silently remove required information.

Before calling the skill ready:

- Check that name and description are nonempty strings and the name matches the directory.
- Remove all TODOs, placeholder resources, and accidental credentials or machine-specific paths.
- Resolve every resource pointer and execute new scripts against representative inputs, including a failure case.
- Inspect `agents/openai.yaml` against the final text when it is part of the deliverable.
- Confirm that the skill can be used independently of this toolbox checkout.

## 6. Test behavior and iterate

A metadata pass does not show that an agent can accomplish the task. Start with 2–3 realistic prompts and check the resulting artifacts, not just the agent's explanation. Include an edge/failure case. Record prompts, inputs, outputs, assertions, and limitations.

For the full Anthropic workflow, read its test/evaluation sections and load resources only as needed:

- [Schemas](../skills/skill-creator-anthropic/references/schemas.md): eval definitions, grading, timing, benchmark, and feedback formats.
- [Grader](../skills/skill-creator-anthropic/agents/grader.md): evidence-based grading.
- [Analyzer](../skills/skill-creator-anthropic/agents/analyzer.md): interpretation of results and variance.
- [Comparator](../skills/skill-creator-anthropic/agents/comparator.md): optional blind comparison.

Store eval definitions at `$SKILL_DIR/evals/evals.json`. Keep generated run artifacts in a sibling workspace:

```bash
export WORKSPACE="$SKILL_OUTPUT_ROOT/$SKILL_NAME-workspace"
export ITERATION="$WORKSPACE/iteration-1"
```

For each prompt, run fresh-context agents with the skill and without it (or with the original version for an update). Provide identical inputs and output requirements. If fresh agents are unavailable, perform a manual sanity run and explicitly say there is no independent baseline; do not manufacture a benchmark.

Use numbered `run-*` directories when aggregation is needed. The checked-in aggregator looks for this extra level, even though some upstream prose examples omit it:

```text
example-skill-workspace/iteration-1/
└── eval-1-basic-task/
    ├── eval_metadata.json
    ├── with_skill/
    │   └── run-1/
    │       ├── outputs/
    │       ├── grading.json
    │       └── timing.json
    └── without_skill/
        └── run-1/
            ├── outputs/
            ├── grading.json
            └── timing.json
```

Keep `eval_id`, prompt, and assertions in the eval-level `eval_metadata.json` for aggregation. Also copy that metadata into each `run-*` directory: the review viewer looks only in the run directory and its immediate parent, not the eval grandparent. Grading entries in `expectations` use `text`, `passed`, and `evidence`; the summary contains actual counts and pass rate. Save real timing/token data when the harness supplies it. Do not treat missing metrics or the aggregator's fallback values as measured token usage. Upstream prose uses both “assertions” and “expectations”; consult the linked schemas and consuming helper before writing JSON.

After producing and grading actual outputs, aggregate and generate a static review page:

```bash
(
  cd "$ANTHROPIC_CREATOR"
  python -m scripts.aggregate_benchmark "$ITERATION" --skill-name "$SKILL_NAME"
)
python "$ANTHROPIC_CREATOR/eval-viewer/generate_review.py" "$ITERATION" \
  --skill-name "$SKILL_NAME" \
  --benchmark "$ITERATION/benchmark.json" \
  --static "$ITERATION/review.html"
```

The subshell preserves your original working directory and makes the toolkit's `scripts.*` imports resolve. The aggregator writes `benchmark.json` and `benchmark.md`. Open the static page for human review; “Submit All Reviews” downloads `feedback.json`, which must be placed into the iteration directory. Improve the skill and rerun into a new iteration. Use `--previous-workspace` on the review generator to compare iterations.

### Optional: description triggering tests

Task-output evals and trigger evals are different. The Anthropic trigger scripts require an installed, authenticated `claude` CLI and access to an appropriate Claude model. Python and PyYAML alone are insufficient. They invoke `claude -p`, incur model usage, and temporarily write command files under a discovered `.claude/commands/` project directory. Inspect that context and obtain approval for usage before launching them.

Prepare a separate trigger-eval JSON array of objects with `query` and `should_trigger`. After checking CLI availability/authentication, set `CLAUDE_MODEL` to an available Claude model ID, then run:

```bash
(
  cd "$ANTHROPIC_CREATOR"
  python -m scripts.run_eval \
    --eval-set "$WORKSPACE/trigger-evals.json" \
    --skill-path "$SKILL_DIR" \
    --model "$CLAUDE_MODEL"
)
```

For iterative description improvement, inspect `python -m scripts.run_loop --help` from the same toolkit directory and follow the creator's optimization section. Do not pass an OpenAI or other provider's session model ID merely because upstream says to use the current model. Trigger scores in Claude do not establish trigger behavior in another harness.

## 7. Package and hand off

If an archive is wanted, run the Anthropic packager as a module, not as a directly executed script:

```bash
(
  cd "$ANTHROPIC_CREATOR"
  python -m scripts.package_skill "$SKILL_DIR" "$WORKSPACE/dist"
)
```

It validates with the Anthropic validator and writes `$WORKSPACE/dist/$SKILL_NAME.skill`, a ZIP archive containing the skill directory. It excludes root-level `evals/`, Python caches, `node_modules`, and certain OS/build files; it is not a general secret or development-artifact filter. Inspect archive contents before handing it off:

```bash
python -m zipfile -l "$WORKSPACE/dist/$SKILL_NAME.skill"
```

Deliver the directory/archive path, the use case and triggering description, the checks actually run, and any missing dependencies or untested harness behavior. Keep the output directory independently usable and retain any licenses needed by copied resources.

This repository does not implement installation. Use the target harness's documented destination or installer only when requested; do not assume the archive installs itself or overwrite an existing installed skill.

## Troubleshooting

| Symptom | Check / action |
| --- | --- |
| `ModuleNotFoundError: yaml` | Activate the intended environment and install PyYAML with that interpreter's `python -m pip`. |
| `ModuleNotFoundError: scripts` | Run Anthropic package/module helpers via `python -m scripts.<name>` from the Anthropic creator directory. |
| Freshly initialized skill fails validation | Replace the TODO description with a YAML string and finish the scaffold; initialization is not completion. |
| Destination already exists | For an update, skip initialization and work on a copy; do not delete the existing skill to force initialization. |
| `compatibility` rejected | This is a known difference between the bundled validators; choose fields for the target and report the portability limit. |
| Empty benchmark / no runs found | Verify real `grading.json` files under `eval-*/<configuration>/run-*`, plus outputs for the viewer. |
| Static review does not persist feedback into the workspace | Move the downloaded `feedback.json` into the iteration directory. |
| `claude` missing or not authenticated | Skip automatic trigger optimization; use available manual testing and report the limitation. |
| Local edits disappear after sync | Sync replaces both vendored directories. Keep authored skills and local documentation outside them. |
