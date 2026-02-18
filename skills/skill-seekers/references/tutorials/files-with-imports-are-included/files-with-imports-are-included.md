# How To: Files With Imports Are Included

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test that files with only imports are included in analysis (Issue #239).

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

### Step 1: 'Test that files with only imports are included in analysis (Issue #239).'

```python
'Test that files with only imports are included in analysis (Issue #239).'
```

### Step 2: Call unknown.write_text()

```python
(self.test_project / 'imports_only.py').write_text('import django\nfrom flask import Flask\nimport requests')
```

### Step 3: Assign old_argv = value

```python
old_argv = sys.argv
```

### Step 4: Assign code_analysis = value

```python
code_analysis = self.output_dir / 'code_analysis.json'
```

### Step 5: Call self.assertTrue()

```python
self.assertTrue(code_analysis.exists(), 'Code analysis file should exist')
```

### Step 6: Call self.assertGreater()

```python
self.assertGreater(len(analysis_data['files']), 0, 'Files with imports should be included')
```

### Step 7: Assign import_file = next(...)

```python
import_file = next((f for f in analysis_data['files'] if 'imports_only.py' in f['file']), None)
```

### Step 8: Call self.assertIsNotNone()

```python
self.assertIsNotNone(import_file, 'Import-only file should be in analysis')
```

### Step 9: Call self.assertIn()

```python
self.assertIn('imports', import_file, 'Imports should be extracted')
```

### Step 10: Call self.assertGreater()

```python
self.assertGreater(len(import_file['imports']), 0, 'Should have captured imports')
```

### Step 11: Call self.assertIn()

```python
self.assertIn('django', import_file['imports'], 'Django import should be captured')
```

### Step 12: Call self.assertIn()

```python
self.assertIn('flask', import_file['imports'], 'Flask import should be captured')
```

### Step 13: Assign sys.argv = value

```python
sys.argv = ['skill-seekers-codebase', '--directory', str(self.test_project), '--output', str(self.output_dir), '--depth', 'deep', '--ai-mode', 'none']
```

### Step 14: Call scraper_main()

```python
scraper_main()
```

### Step 15: Assign sys.argv = old_argv

```python
sys.argv = old_argv
```

### Step 16: Assign analysis_data = json.load(...)

```python
analysis_data = json.load(f)
```


## Complete Example

```python
# Workflow
'Test that files with only imports are included in analysis (Issue #239).'
(self.test_project / 'imports_only.py').write_text('import django\nfrom flask import Flask\nimport requests')
from skill_seekers.cli.codebase_scraper import main as scraper_main
import sys
old_argv = sys.argv
try:
    sys.argv = ['skill-seekers-codebase', '--directory', str(self.test_project), '--output', str(self.output_dir), '--depth', 'deep', '--ai-mode', 'none']
    scraper_main()
finally:
    sys.argv = old_argv
code_analysis = self.output_dir / 'code_analysis.json'
self.assertTrue(code_analysis.exists(), 'Code analysis file should exist')
with open(code_analysis) as f:
    analysis_data = json.load(f)
self.assertGreater(len(analysis_data['files']), 0, 'Files with imports should be included')
import_file = next((f for f in analysis_data['files'] if 'imports_only.py' in f['file']), None)
self.assertIsNotNone(import_file, 'Import-only file should be in analysis')
self.assertIn('imports', import_file, 'Imports should be extracted')
self.assertGreater(len(import_file['imports']), 0, 'Should have captured imports')
self.assertIn('django', import_file['imports'], 'Django import should be captured')
self.assertIn('flask', import_file['imports'], 'Flask import should be captured')
```

## Next Steps


---

*Source: test_framework_detection.py:87 | Complexity: Advanced | Last updated: 2026-02-14*