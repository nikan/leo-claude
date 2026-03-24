# Leo Claude

Declarative workflow engine for CLI-only GitHub issue lifecycle management.

## Instructions

This skill is driven by `workflow.yml`. Read and parse it before doing anything else. The YAML is the single source of truth for stages, roles, branches, handoff context, completion criteria, and failure rules.

When the user provides a GitHub issue number or URL:

1. Parse `workflow.yml`.
2. Walk the `stages` list in order.
3. For each stage, resolve the assigned `role` from the `roles` map and invoke its `bin`.
4. Resolve branch names using `branches.pattern` and the appropriate `branches.prefixes` entry.
5. Evaluate `condition` on conditional stages — skip if not met.
6. Follow `on_failure` directives: `halt` stops the workflow; `goto <stage_id>` loops back.
7. Pass every field listed in `handoff` to each role at each stage transition.
8. Check all `completion` criteria at the end.
9. On failure, follow the matching rule from the `failure` map.

## Extending

Add stages to the `stages` list, roles to the `roles` map, or branch prefixes to `branches.prefixes` — all in `workflow.yml`. No other files need to change.
