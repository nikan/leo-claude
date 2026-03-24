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
2. **Walk the `stages` list in order.** Each stage has an `id`, optional `role`, optional `condition`, `steps`, and `rules`.
3. **Resolve roles** from the `roles` map. Use the configured `bin` and `args` to invoke each role's CLI binary.
4. **Resolve branches** using `branches.pattern`, substituting the appropriate prefix from `branches.prefixes`.
5. **Evaluate `condition`** on conditional stages. Skip the stage if the condition is not met.
6. **Follow `on_failure`** directives: `halt` stops the workflow; `goto <stage_id>` loops back.
7. **Pass handoff context** listed in the `handoff` array to every role at every stage transition.
8. **Check `completion`** criteria at the end. The workflow is done only when all listed conditions are satisfied.
9. **On any failure**, follow the matching rule from the `failure` map. If no rule matches, use `failure.unknown`.

## Inputs

Defined under `inputs` in `workflow.yml`. Currently:

- `issue` (required) — GitHub issue number or full URL
- `target_branch` (optional) — overrides `branches.target_base`

## Preflight

The `preflight` section lists `required_tools` and `checks` scripts. Run all checks before any stage. Any failure is a hard stop.

## Extending the workflow

To add a stage, append an entry to the `stages` list in `workflow.yml`. To add a role, add it to the `roles` map and reference it from a stage. To change branch naming, edit `branches.pattern` or `branches.prefixes`. No other files need to change.
