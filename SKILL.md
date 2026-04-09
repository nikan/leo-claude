---
name: leo-claude
description: Declarative workflow engine that drives a CLI-only GitHub issue lifecycle — implementation, review, merge, translation follow-up, and documentation follow-up — using configurable agent roles and commands.
---

# Leo Claude

Declarative workflow engine driven by `workflow.yml`. The YAML file is the single source of truth — changing it changes the skill behavior.

## How to use

Read and parse `workflow.yml` before doing anything else. Every setting, stage, role, branch rule, handoff field, completion criterion, and failure rule is defined there.

## Execution rules

1. **Parse `workflow.yml`** at the start of every invocation. Do not cache or assume prior values.
2. **Re-read `workflow.yml` before every stage transition.** As context fills up, earlier instructions drift out of working memory. Before starting any new stage, re-read the file to confirm: (a) which role owns the stage, (b) which binary/CLI to invoke, (c) what steps and rules apply, (d) what handoff context to pass. Never rely on memory of the initial parse.
3. **Walk the `stages` list in order.** Each stage has an `id`, optional `role`, optional `condition`, `steps`, and `rules`.
4. **Resolve roles** from the `roles` map. Use the configured `bin` and `args` to invoke each role's CLI binary.
5. **Resolve branches** using `branches.pattern`, substituting the appropriate prefix from `branches.prefixes`.
6. **Evaluate `condition`** on conditional stages. Skip the stage if the condition is not met.
7. **Follow `on_failure`** directives: `halt` stops the workflow; `goto <stage_id>` loops back.
8. **Enforce `max_iterations`** on looping stages. If a `review_limits` input is provided (comma-separated: `dev,translation,docs`), parse it and override the defaults from the `review_limits` section. Track iteration count per looping stage; halt with `failure.review_limit_exceeded` when the limit is reached.
9. **Pass handoff context** listed in the `handoff` array to every role at every stage transition.
10. **Check `completion`** criteria at the end. The workflow is done only when all listed conditions are satisfied.
11. **On any failure**, follow the matching rule from the `failure` map. If no rule matches, use `failure.unknown`.

## Inputs

Defined under `inputs` in `workflow.yml`. Currently:

- `issue` (required) — GitHub issue number or full URL
- `target_branch` (optional) — overrides `branches.target_base`; pass it as `target_branch=<branch>`
- `review_limits` (optional) — comma-separated max review iterations for development, translation, and documentation (e.g. `"6,3,2"`). Defaults are defined in the `review_limits` section of `workflow.yml` (development: 5, translation: 3, documentation: 3). Pass it as `review_limits=6,3,2`.

### Invocation examples

```
/leo-claude #123
/leo-claude #123 review_limits=6,3,2
/leo-claude #123 target_branch=release/1.2 review_limits=6,3,2
```

## Preflight

The `preflight` section lists `required_tools` and `checks` scripts. Run all checks before any stage. Any failure is a hard stop.

## Extending the workflow

To add a stage, append an entry to the `stages` list in `workflow.yml`. To add a role, add it to the `roles` map and reference it from a stage. To change branch naming, edit `branches.pattern` or `branches.prefixes`. No other files need to change.
