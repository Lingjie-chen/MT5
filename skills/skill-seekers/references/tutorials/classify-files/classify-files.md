# How To: Classify Files

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test classify_files separates code and docs correctly.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `pathlib`
- `unittest.mock`
- `pytest`
- `skill_seekers.cli.github_fetcher`

**Setup Required:**
```python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: 'Test classify_files separates code and docs correctly.'

```python
'Test classify_files separates code and docs correctly.'
```

**Verification:**
```python
assert 'main.py' in code_paths
```

### Step 2: Call unknown.mkdir()

```python
(tmp_path / 'src').mkdir()
```

**Verification:**
```python
assert 'utils.js' in code_paths
```

### Step 3: Call unknown.write_text()

```python
(tmp_path / 'src' / 'main.py').write_text("print('hello')")
```

**Verification:**
```python
assert 'lib.js' not in code_paths
```

### Step 4: Call unknown.write_text()

```python
(tmp_path / 'src' / 'utils.js').write_text('function(){}')
```

**Verification:**
```python
assert 'README.md' in doc_paths
```

### Step 5: Call unknown.mkdir()

```python
(tmp_path / 'docs').mkdir()
```

**Verification:**
```python
assert 'guide.md' in doc_paths
```

### Step 6: Call unknown.write_text()

```python
(tmp_path / 'README.md').write_text('# README')
```

**Verification:**
```python
assert 'api.rst' in doc_paths
```

### Step 7: Call unknown.write_text()

```python
(tmp_path / 'docs' / 'guide.md').write_text('# Guide')
```

### Step 8: Call unknown.write_text()

```python
(tmp_path / 'docs' / 'api.rst').write_text('API')
```

### Step 9: Call unknown.mkdir()

```python
(tmp_path / 'node_modules').mkdir()
```

### Step 10: Call unknown.write_text()

```python
(tmp_path / 'node_modules' / 'lib.js').write_text('// should be excluded')
```

### Step 11: Assign fetcher = GitHubThreeStreamFetcher(...)

```python
fetcher = GitHubThreeStreamFetcher('https://github.com/test/repo')
```

### Step 12: Assign unknown = fetcher.classify_files(...)

```python
code_files, doc_files = fetcher.classify_files(tmp_path)
```

### Step 13: Assign code_paths = value

```python
code_paths = [f.name for f in code_files]
```

**Verification:**
```python
assert 'main.py' in code_paths
```

### Step 14: Assign doc_paths = value

```python
doc_paths = [f.name for f in doc_files]
```

**Verification:**
```python
assert 'README.md' in doc_paths
```


## Complete Example

```python
# Setup
# Fixtures: tmp_path

# Workflow
'Test classify_files separates code and docs correctly.'
(tmp_path / 'src').mkdir()
(tmp_path / 'src' / 'main.py').write_text("print('hello')")
(tmp_path / 'src' / 'utils.js').write_text('function(){}')
(tmp_path / 'docs').mkdir()
(tmp_path / 'README.md').write_text('# README')
(tmp_path / 'docs' / 'guide.md').write_text('# Guide')
(tmp_path / 'docs' / 'api.rst').write_text('API')
(tmp_path / 'node_modules').mkdir()
(tmp_path / 'node_modules' / 'lib.js').write_text('// should be excluded')
fetcher = GitHubThreeStreamFetcher('https://github.com/test/repo')
code_files, doc_files = fetcher.classify_files(tmp_path)
code_paths = [f.name for f in code_files]
assert 'main.py' in code_paths
assert 'utils.js' in code_paths
assert 'lib.js' not in code_paths
doc_paths = [f.name for f in doc_files]
assert 'README.md' in doc_paths
assert 'guide.md' in doc_paths
assert 'api.rst' in doc_paths
```

## Next Steps


---

*Source: test_github_fetcher.py:105 | Complexity: Advanced | Last updated: 2026-02-14*