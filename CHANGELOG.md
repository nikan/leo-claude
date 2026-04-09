# Changelog

All notable changes to leo-claude are documented in this file.

## [0.5.0] - 2026-04-09

### Added
- Configurable review iteration limits per stage (development: 5, translation: 3, documentation: 3 by default).
- `review_limits` input for CLI override via `key=value` syntax (e.g. `review_limits=6,3,2`).
- `max_iterations` field on review, translate, and document stages.
- `review_limit_exceeded` failure rule — halts workflow when a review loop exceeds its limit.
- Explicit `set: review_limits` resolution step in the context stage.

## [0.4.0] - 2026-03-28

### Added
- Execution rule requiring re-read of `workflow.yml` before every stage transition, preventing context drift from collapsing multi-role orchestration into single-agent execution.

## [0.3.0] - 2026-03-27

### Added
- Orchestrator role definition — the invoking Claude Code session owns preflight, context, branch, and merge stages.
- Preflight validation for `github.dev_user` and `github.review_user` configuration.
- `reviewer_mode` handoff field (`comments` | `change_request`) set once in context stage based on whether dev and review users match.

### Changed
- Enhanced workflow stages with explicit validation checks and GitHub account switching.
- Improved issue closure process with linked issue resolution from PR body keywords, commit message keywords, and sub-issues — all three sources deduplicated before closing.

## [0.2.0] - 2026-03-26

### Fixed
- Vibe invocation failure caused by unwritable log directory.

## [0.1.0] - 2026-03-25

Initial release.

### Added
- Declarative workflow engine driven by `workflow.yml`.
- Seven-stage lifecycle: preflight, context, branch, implement, review, translate, document.
- Role system mapping stages to CLI binaries (claude, codex, vibe-wrapper.sh).
- Prompt templates for implementer, reviewer, translator, and documentor roles.
- Preflight scripts rewritten in Python for cross-platform support.
- Sub-issue resolution via GitHub native sub-issues and task-list body references.
- Bulk issue closing script.
- Handoff contract passing context between roles at each stage transition.
- Conditional stages for translation and documentation follow-ups.
- Branch naming with configurable prefixes and patterns.

[0.5.0]: https://github.com/nikan/leo-claude/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/nikan/leo-claude/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/nikan/leo-claude/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/nikan/leo-claude/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/nikan/leo-claude/releases/tag/v0.1.0
