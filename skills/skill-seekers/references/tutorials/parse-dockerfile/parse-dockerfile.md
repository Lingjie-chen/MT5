# How To: Parse Dockerfile

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test parsing Dockerfile for ENV vars

## Prerequisites

**Required Modules:**
- `json`
- `os`
- `sys`
- `tempfile`
- `unittest`
- `pathlib`
- `skill_seekers.cli.config_extractor`
- `shutil`
- `shutil`
- `shutil`
- `shutil`


## Step-by-Step Guide

### Step 1: 'Test parsing Dockerfile for ENV vars'

```python
'Test parsing Dockerfile for ENV vars'
```

### Step 2: Assign dockerfile_content = '\nFROM python:3.10\nENV DATABASE_URL=postgresql://localhost:5432/db\nENV API_KEY=secret\nWORKDIR /app\n'

```python
dockerfile_content = '\nFROM python:3.10\nENV DATABASE_URL=postgresql://localhost:5432/db\nENV API_KEY=secret\nWORKDIR /app\n'
```

### Step 3: Assign config_file = ConfigFile(...)

```python
config_file = ConfigFile(file_path=str(Path(self.temp_dir) / 'Dockerfile'), relative_path='Dockerfile', config_type='dockerfile', purpose='unknown')
```

### Step 4: Assign file_path = value

```python
file_path = Path(self.temp_dir) / 'Dockerfile'
```

### Step 5: Call file_path.write_text()

```python
file_path.write_text(dockerfile_content)
```

### Step 6: Call self.parser.parse_config_file()

```python
self.parser.parse_config_file(config_file)
```

### Step 7: Assign env_settings = value

```python
env_settings = [s for s in config_file.settings if s.env_var]
```

### Step 8: Call self.assertGreater()

```python
self.assertGreater(len(env_settings), 0)
```


## Complete Example

```python
# Workflow
'Test parsing Dockerfile for ENV vars'
dockerfile_content = '\nFROM python:3.10\nENV DATABASE_URL=postgresql://localhost:5432/db\nENV API_KEY=secret\nWORKDIR /app\n'
config_file = ConfigFile(file_path=str(Path(self.temp_dir) / 'Dockerfile'), relative_path='Dockerfile', config_type='dockerfile', purpose='unknown')
file_path = Path(self.temp_dir) / 'Dockerfile'
file_path.write_text(dockerfile_content)
self.parser.parse_config_file(config_file)
env_settings = [s for s in config_file.settings if s.env_var]
self.assertGreater(len(env_settings), 0)
```

## Next Steps


---

*Source: test_config_extractor.py:242 | Complexity: Advanced | Last updated: 2026-02-14*