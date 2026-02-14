# How To: Mock Github Repo

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, pytest, workflow, integration

## Overview

Workflow: Create mock GitHub repository structure.

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

### Step 1: 'Create mock GitHub repository structure.'

```python
'Create mock GitHub repository structure.'
```

### Step 2: Assign repo_dir = value

```python
repo_dir = tmp_path / 'fastmcp'
```

### Step 3: Call repo_dir.mkdir()

```python
repo_dir.mkdir()
```

### Step 4: Assign src_dir = value

```python
src_dir = repo_dir / 'src'
```

### Step 5: Call src_dir.mkdir()

```python
src_dir.mkdir()
```

### Step 6: Call unknown.write_text()

```python
(src_dir / 'auth.py').write_text("\n# OAuth authentication\ndef google_provider(client_id, client_secret):\n    '''Google OAuth provider'''\n    return Provider('google', client_id, client_secret)\n\ndef azure_provider(tenant_id, client_id):\n    '''Azure OAuth provider'''\n    return Provider('azure', tenant_id, client_id)\n")
```

### Step 7: Call unknown.write_text()

```python
(src_dir / 'async_tools.py').write_text('\nimport asyncio\n\nasync def async_tool():\n    \'\'\'Async tool decorator\'\'\'\n    await asyncio.sleep(1)\n    return "result"\n')
```

### Step 8: Assign tests_dir = value

```python
tests_dir = repo_dir / 'tests'
```

### Step 9: Call tests_dir.mkdir()

```python
tests_dir.mkdir()
```

### Step 10: Call unknown.write_text()

```python
(tests_dir / 'test_auth.py').write_text("\ndef test_google_provider():\n    provider = google_provider('id', 'secret')\n    assert provider.name == 'google'\n\ndef test_azure_provider():\n    provider = azure_provider('tenant', 'id')\n    assert provider.name == 'azure'\n")
```

### Step 11: Call unknown.write_text()

```python
(repo_dir / 'README.md').write_text('\n# FastMCP\n\nFastMCP is a Python framework for building MCP servers.\n\n## Quick Start\n\nInstall with pip:\n```bash\npip install fastmcp\n```\n\n## Features\n- OAuth authentication (Google, Azure, GitHub)\n- Async/await support\n- Easy testing with pytest\n')
```

### Step 12: Call unknown.write_text()

```python
(repo_dir / 'CONTRIBUTING.md').write_text('\n# Contributing\n\nPlease follow these guidelines when contributing.\n')
```

### Step 13: Assign docs_dir = value

```python
docs_dir = repo_dir / 'docs'
```

### Step 14: Call docs_dir.mkdir()

```python
docs_dir.mkdir()
```

### Step 15: Call unknown.write_text()

```python
(docs_dir / 'oauth.md').write_text('\n# OAuth Guide\n\nHow to set up OAuth providers.\n')
```

### Step 16: Call unknown.write_text()

```python
(docs_dir / 'async.md').write_text('\n# Async Guide\n\nHow to use async tools.\n')
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Create mock GitHub repository structure.'
repo_dir = tmp_path / 'fastmcp'
repo_dir.mkdir()
src_dir = repo_dir / 'src'
src_dir.mkdir()
(src_dir / 'auth.py').write_text("\n# OAuth authentication\ndef google_provider(client_id, client_secret):\n    '''Google OAuth provider'''\n    return Provider('google', client_id, client_secret)\n\ndef azure_provider(tenant_id, client_id):\n    '''Azure OAuth provider'''\n    return Provider('azure', tenant_id, client_id)\n")
(src_dir / 'async_tools.py').write_text('\nimport asyncio\n\nasync def async_tool():\n    \'\'\'Async tool decorator\'\'\'\n    await asyncio.sleep(1)\n    return "result"\n')
tests_dir = repo_dir / 'tests'
tests_dir.mkdir()
(tests_dir / 'test_auth.py').write_text("\ndef test_google_provider():\n    provider = google_provider('id', 'secret')\n    assert provider.name == 'google'\n\ndef test_azure_provider():\n    provider = azure_provider('tenant', 'id')\n    assert provider.name == 'azure'\n")
(repo_dir / 'README.md').write_text('\n# FastMCP\n\nFastMCP is a Python framework for building MCP servers.\n\n## Quick Start\n\nInstall with pip:\n```bash\npip install fastmcp\n```\n\n## Features\n- OAuth authentication (Google, Azure, GitHub)\n- Async/await support\n- Easy testing with pytest\n')
(repo_dir / 'CONTRIBUTING.md').write_text('\n# Contributing\n\nPlease follow these guidelines when contributing.\n')
docs_dir = repo_dir / 'docs'
docs_dir.mkdir()
(docs_dir / 'oauth.md').write_text('\n# OAuth Guide\n\nHow to set up OAuth providers.\n')
(docs_dir / 'async.md').write_text('\n# Async Guide\n\nHow to use async tools.\n')
return repo_dir
```

## Next Steps


---

*Source: test_architecture_scenarios.py:65 | Complexity: Advanced | Last updated: 2026-02-14*