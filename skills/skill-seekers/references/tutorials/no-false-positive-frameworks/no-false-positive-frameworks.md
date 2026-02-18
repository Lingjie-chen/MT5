# How To: No False Positive Frameworks

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that framework detection doesn't produce false positives (Issue #239).

## Prerequisites

**Required Modules:**
- `json`
- `os`
- `shutil`
- `tempfile`
- `unittest`
- `pathlib`
- `skill_seekers.cli.codebase_scraper`
- `sys`
- `skill_seekers.cli.codebase_scraper`
- `sys`
- `skill_seekers.cli.codebase_scraper`
- `sys`


## Step-by-Step Guide

### Step 1: "Test that framework detection doesn't produce false positives (Issue #239)."

```python
"Test that framework detection doesn't produce false positives (Issue #239)."
```

### Step 2: Assign app_dir = value

```python
app_dir = self.test_project / 'app'
```

### Step 3: Call app_dir.mkdir()

```python
app_dir.mkdir()
```

### Step 4: Call unknown.write_text()

```python
(app_dir / 'utils.py').write_text("def my_function():\n    return 'hello'\n")
```

### Step 5: Assign old_argv = value

```python
old_argv = sys.argv
```

### Step 6: Assign arch_file = value

```python
arch_file = self.output_dir / 'references' / 'architecture' / 'architectural_patterns.json'
```

### Step 7: Assign sys.argv = value

```python
sys.argv = ['skill-seekers-codebase', '--directory', str(self.test_project), '--output', str(self.output_dir), '--depth', 'deep', '--ai-mode', 'none']
```

### Step 8: Call scraper_main()

```python
scraper_main()
```

### Step 9: Assign sys.argv = old_argv

```python
sys.argv = old_argv
```

### Step 10: Assign frameworks = arch_data.get(...)

```python
frameworks = arch_data.get('frameworks_detected', [])
```

### Step 11: Call self.assertNotIn()

```python
self.assertNotIn('Flask', frameworks, 'Should not detect Flask without imports')
```

### Step 12: Assign arch_data = json.load(...)

```python
arch_data = json.load(f)
```

### Step 13: Call self.assertNotIn()

```python
self.assertNotIn(fw, frameworks, f'Should not detect {fw} without real evidence')
```


## Complete Example

```python
# Workflow
"Test that framework detection doesn't produce false positives (Issue #239)."
app_dir = self.test_project / 'app'
app_dir.mkdir()
(app_dir / 'utils.py').write_text("def my_function():\n    return 'hello'\n")
from skill_seekers.cli.codebase_scraper import main as scraper_main
import sys
old_argv = sys.argv
try:
    sys.argv = ['skill-seekers-codebase', '--directory', str(self.test_project), '--output', str(self.output_dir), '--depth', 'deep', '--ai-mode', 'none']
    scraper_main()
finally:
    sys.argv = old_argv
arch_file = self.output_dir / 'references' / 'architecture' / 'architectural_patterns.json'
if arch_file.exists():
    with open(arch_file) as f:
        arch_data = json.load(f)
    frameworks = arch_data.get('frameworks_detected', [])
    self.assertNotIn('Flask', frameworks, 'Should not detect Flask without imports')
    for fw in ['ASP.NET', 'Rails', 'Laravel']:
        self.assertNotIn(fw, frameworks, f'Should not detect {fw} without real evidence')
```

## Next Steps


---

*Source: test_framework_detection.py:137 | Complexity: Advanced | Last updated: 2026-02-14*