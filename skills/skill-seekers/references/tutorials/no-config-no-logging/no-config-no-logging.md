# How To: No Config No Logging

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: mock, unittest, workflow, integration

## Overview

Workflow: Test that default mode doesn't log exclude_dirs messages.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `unittest`
- `unittest.mock`
- `skill_seekers.cli.github_scraper`

**Setup Required:**
```python
# Fixtures: mock_logger, _mock_github
```

## Step-by-Step Guide

### Step 1: "Test that default mode doesn't log exclude_dirs messages."

```python
"Test that default mode doesn't log exclude_dirs messages."
```

### Step 2: Assign config = value

```python
config = {'repo': 'owner/repo'}
```

### Step 3: Assign _scraper = GitHubScraper(...)

```python
_scraper = GitHubScraper(config)
```

### Step 4: Assign info_calls = value

```python
info_calls = [str(call) for call in mock_logger.info.call_args_list]
```

### Step 5: Assign warning_calls = value

```python
warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
```

### Step 6: Assign exclude_info = value

```python
exclude_info = [c for c in info_calls if 'directory exclusion' in c]
```

### Step 7: Assign exclude_warnings = value

```python
exclude_warnings = [c for c in warning_calls if 'directory exclusion' in c]
```

### Step 8: Call self.assertEqual()

```python
self.assertEqual(len(exclude_info), 0)
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(len(exclude_warnings), 0)
```


## Complete Example

```python
# Setup
# Fixtures: mock_logger, _mock_github

# Workflow
"Test that default mode doesn't log exclude_dirs messages."
config = {'repo': 'owner/repo'}
_scraper = GitHubScraper(config)
info_calls = [str(call) for call in mock_logger.info.call_args_list]
warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
exclude_info = [c for c in info_calls if 'directory exclusion' in c]
exclude_warnings = [c for c in warning_calls if 'directory exclusion' in c]
self.assertEqual(len(exclude_info), 0)
self.assertEqual(len(exclude_warnings), 0)
```

## Next Steps


---

*Source: test_excluded_dirs_config.py:299 | Complexity: Advanced | Last updated: 2026-02-14*