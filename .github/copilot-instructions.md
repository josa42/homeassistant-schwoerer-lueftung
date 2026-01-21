# GitHub Copilot Instructions

## Commit Workflow

### Always Commit Changes

When completing tasks that modify files:
- **Always commit changes** - Don't leave uncommitted work
- Use clear, descriptive commit messages
- Include the co-author attribution (see below)

### Amending Commits

When it makes sense to amend (refine, fix typos, add forgotten files):
- **DO amend** commits that haven't been pushed yet
- **NEVER amend** commits that have already been pushed
- Use `git commit --amend` for local-only commits

Example when to amend:
- ✅ Just committed, then realized a typo in the commit message
- ✅ Just committed, but forgot to add a file that belongs to the same change
- ✅ Just committed, but need to adjust formatting in the same logical change
- ❌ Commit was already pushed to remote
- ❌ Commit is more than a few minutes old and work has moved on

## Commit Message Format

Always include a co-author attribution in commit messages:

```
Co-authored-by: GitHub Copilot <github-copilot@github.com>
```

### Example

```
Fix MODEL undefined error in platform files

- Import MODEL_WGT and MODEL_WRT from const in all platform files
- Add dynamic model computation based on coordinator.has_heating()
- Replace undefined MODEL with computed model variable
- Fixes NameError in binary_sensor, number, select, sensor, and switch platforms

Co-authored-by: GitHub Copilot <github-copilot@github.com>
```

## Guidelines

- Add the co-author line as the last line of every commit message
- Separate the co-author line from the commit body with a blank line
- Use the exact format: `Co-authored-by: GitHub Copilot <github-copilot@github.com>`
- Always commit completed work - don't leave changes uncommitted
- Amend local commits when it makes sense, but never amend pushed commits
