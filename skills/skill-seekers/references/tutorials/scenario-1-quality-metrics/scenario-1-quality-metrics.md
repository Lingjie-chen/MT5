# How To: Scenario 1 Quality Metrics

**Difficulty**: Advanced
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test quality metrics meet architecture targets.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `pathlib`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.generate_router`
- `skill_seekers.cli.github_fetcher`
- `skill_seekers.cli.merge_sources`
- `skill_seekers.cli.unified_codebase_analyzer`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test quality metrics meet architecture targets.'

```python
'Test quality metrics meet architecture targets.'
```

**Verification:**
```python
assert len(lines) <= 200, f'Router too large: {len(lines)} lines (max 200)'
```

### Step 2: Assign router_md = '---\nname: fastmcp\ndescription: FastMCP framework overview\n---\n\n# FastMCP - Overview\n\n**Repository:** https://github.com/jlowin/fastmcp\n**Stars:** ⭐ 1,234 | **Language:** Python\n\n## Quick Start (from README)\n\nInstall with pip:\n```bash\npip install fastmcp\n```\n\n## Common Issues (from GitHub)\n\n1. **OAuth setup fails** (Issue #42, 15 comments)\n   - See `fastmcp-oauth` skill\n\n2. **Async tools not working** (Issue #38, 8 comments)\n   - See `fastmcp-async` skill\n\n## Choose Your Path\n\n**OAuth?** → Use `fastmcp-oauth` skill\n**Async?** → Use `fastmcp-async` skill\n'

```python
router_md = '---\nname: fastmcp\ndescription: FastMCP framework overview\n---\n\n# FastMCP - Overview\n\n**Repository:** https://github.com/jlowin/fastmcp\n**Stars:** ⭐ 1,234 | **Language:** Python\n\n## Quick Start (from README)\n\nInstall with pip:\n```bash\npip install fastmcp\n```\n\n## Common Issues (from GitHub)\n\n1. **OAuth setup fails** (Issue #42, 15 comments)\n   - See `fastmcp-oauth` skill\n\n2. **Async tools not working** (Issue #38, 8 comments)\n   - See `fastmcp-async` skill\n\n## Choose Your Path\n\n**OAuth?** → Use `fastmcp-oauth` skill\n**Async?** → Use `fastmcp-async` skill\n'
```

**Verification:**
```python
assert github_lines >= 3, f'GitHub overhead too small: {github_lines} lines'
```

### Step 3: Assign lines = router_md.strip.split(...)

```python
lines = router_md.strip().split('\n')
```

**Verification:**
```python
assert github_lines <= 60, f'GitHub overhead too large: {github_lines} lines'
```

### Step 4: Assign github_lines = 0

```python
github_lines = 0
```

**Verification:**
```python
assert 'Issue #42' in router_md, 'Missing issue references'
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test quality metrics meet architecture targets.'
router_md = '---\nname: fastmcp\ndescription: FastMCP framework overview\n---\n\n# FastMCP - Overview\n\n**Repository:** https://github.com/jlowin/fastmcp\n**Stars:** ⭐ 1,234 | **Language:** Python\n\n## Quick Start (from README)\n\nInstall with pip:\n```bash\npip install fastmcp\n```\n\n## Common Issues (from GitHub)\n\n1. **OAuth setup fails** (Issue #42, 15 comments)\n   - See `fastmcp-oauth` skill\n\n2. **Async tools not working** (Issue #38, 8 comments)\n   - See `fastmcp-async` skill\n\n## Choose Your Path\n\n**OAuth?** → Use `fastmcp-oauth` skill\n**Async?** → Use `fastmcp-async` skill\n'
lines = router_md.strip().split('\n')
assert len(lines) <= 200, f'Router too large: {len(lines)} lines (max 200)'
github_lines = 0
if 'Repository:' in router_md:
    github_lines += 1
if 'Stars:' in router_md or '⭐' in router_md:
    github_lines += 1
if 'Common Issues' in router_md:
    github_lines += router_md.count('Issue #')
assert github_lines >= 3, f'GitHub overhead too small: {github_lines} lines'
assert github_lines <= 60, f'GitHub overhead too large: {github_lines} lines'
assert 'Issue #42' in router_md, 'Missing issue references'
assert '⭐' in router_md or 'Stars:' in router_md, 'Missing GitHub metadata'
assert 'Quick Start' in router_md or 'README' in router_md, 'Missing README content'
```

## Next Steps


---

*Source: test_architecture_scenarios.py:427 | Complexity: Advanced | Last updated: 2026-02-14*