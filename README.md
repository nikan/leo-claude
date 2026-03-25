# Leo Claude

Declarative workflow engine that drives a CLI-only GitHub issue lifecycle — implementation, review, merge, translation follow-up, and documentation follow-up — using configurable agent roles and commands.

## How It Works

Give Leo Claude a GitHub issue number and it runs a multi-stage pipeline:

1. **Preflight** — validates tools, auth, and role binaries
2. **Context** — reads the issue and resolves sub-issues via `gh`
3. **Branch** — creates a working branch from the target base
4. **Implement** — hands off to the implementer role
5. **Review** — hands off to the reviewer role; loops back if issues are found
6. **Merge** — squash-merges, closes issues, deletes the branch
7. **Translate** — follow-up branch for i18n if needed
8. **Document** — follow-up branch for docs if needed

Each stage is executed by a configurable CLI agent binary (e.g. `claude`, `codex`, `vibe`).

## Prerequisites

- `git`
- `gh` (GitHub CLI, authenticated)
- `rg` (ripgrep)
- At least one AI coding CLI installed (`claude`, `codex`, `vibe`, or `copilot`)

## Installation

### Claude Code

```bash
git clone https://github.com/nikan/leo-claude.git ~/.claude/skills/leo-claude
```

Then invoke with `/leo-claude` inside Claude Code.

### OpenAI Codex CLI

```bash
git clone https://github.com/nikan/leo-claude.git ~/.codex/skills/leo-claude
```

Or use the built-in skill installer:

```
Install skill from https://github.com/nikan/leo-claude
```

### Vibe

```bash
git clone https://github.com/nikan/leo-claude.git ~/.vibe/skills/leo-claude
```

### GitHub Copilot CLI

Copilot does not have a skill system. Instead, copy the repo into your project and Copilot will pick up instructions from `AGENTS.md`:

```bash
git clone https://github.com/nikan/leo-claude.git
cp leo-claude/AGENTS.md /path/to/your/project/AGENTS.md
```

### Multi-platform (shared install)

To share a single copy across all tools, clone once and symlink:

```bash
git clone https://github.com/nikan/leo-claude.git ~/.agents/skills/leo-claude

ln -s ~/.agents/skills/leo-claude ~/.claude/skills/leo-claude
ln -s ~/.agents/skills/leo-claude ~/.codex/skills/leo-claude
ln -s ~/.agents/skills/leo-claude ~/.vibe/skills/leo-claude
```

## Configuration

Edit `workflow.yml` to change the workflow. It is the single source of truth for branches, roles, stages, and failure rules.

### Branch and merge settings

```yaml
branches:
  target_base: develop
  merge_method: squash        # merge | squash | rebase
  prefixes:
    issue: issue
    translation: issue-i18n
    documentation: issue-docs
  pattern: "{prefix}/{issue-number}-{short-slug}"
```

### Role binaries

Each workflow stage is assigned to a CLI binary. Change these to match your setup:

```yaml
roles:
  implementer:
    bin: claude               # writes the code
  reviewer:
    bin: codex                # reviews the diff
  translator:
    bin: vibe                 # handles i18n follow-up
  documentor:
    bin: vibe                 # handles docs follow-up
```

Any CLI that accepts a prompt can be used as a role binary.

### Override the workflow file

Set `WORKFLOW_FILE` to point to a different workflow definition:

```bash
export WORKFLOW_FILE=/path/to/custom-workflow.yml
```

## Verifying the setup

Run the preflight checks before first use:

```bash
scripts/preflight.sh
```

This validates Python 3 and PyYAML availability (with platform-specific install hints if missing), then runs the full environment check: CLI dependencies, GitHub auth, vibe auth, config values, and role binaries.

## Platform Compatibility

| Feature | Claude Code | Codex CLI | Vibe | Copilot CLI |
|---------|-------------|-----------|------|-------------|
| Skill auto-discovery | `SKILL.md` | `SKILL.md` | `SKILL.md` | N/A |
| UI metadata | ignored | `agents/openai.yaml` | ignored | N/A |
| Project instructions | `CLAUDE.md` | `AGENTS.md` | `VIBE.md` / `AGENTS.md` | `AGENTS.md` |
| Slash-command invocation | `/leo-claude` | `$leo-claude` | `/leo-claude` | N/A |

## License

MIT
