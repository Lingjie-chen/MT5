# How To: Extract Method Call With Assertion

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test extraction of method calls followed by assertions

## Prerequisites

**Required Modules:**
- `os`
- `shutil`
- `sys`
- `tempfile`
- `unittest`
- `pathlib`
- `skill_seekers.cli.test_example_extractor`


## Step-by-Step Guide

### Step 1: 'Test extraction of method calls followed by assertions'

```python
'Test extraction of method calls followed by assertions'
```

### Step 2: Assign code = '\nimport unittest\n\nclass TestAPI(unittest.TestCase):\n    def test_api_response(self):\n        """Test API returns correct status"""\n        response = self.client.get("/users/1")\n        self.assertEqual(response.status_code, 200)\n'

```python
code = '\nimport unittest\n\nclass TestAPI(unittest.TestCase):\n    def test_api_response(self):\n        """Test API returns correct status"""\n        response = self.client.get("/users/1")\n        self.assertEqual(response.status_code, 200)\n'
```

### Step 3: Assign examples = self.analyzer.extract(...)

```python
examples = self.analyzer.extract('test_api.py', code)
```

### Step 4: Call self.assertGreater()

```python
self.assertGreater(len(examples), 0)
```

### Step 5: Assign method_calls = value

```python
method_calls = [ex for ex in examples if ex.category == 'method_call']
```

### Step 6: Assign call = value

```python
call = method_calls[0]
```

### Step 7: Call self.assertIn()

```python
self.assertIn('get', call.code)
```

### Step 8: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(call.confidence, 0.7)
```


## Complete Example

```python
# Workflow
'Test extraction of method calls followed by assertions'
code = '\nimport unittest\n\nclass TestAPI(unittest.TestCase):\n    def test_api_response(self):\n        """Test API returns correct status"""\n        response = self.client.get("/users/1")\n        self.assertEqual(response.status_code, 200)\n'
examples = self.analyzer.extract('test_api.py', code)
self.assertGreater(len(examples), 0)
method_calls = [ex for ex in examples if ex.category == 'method_call']
if method_calls:
    call = method_calls[0]
    self.assertIn('get', call.code)
    self.assertGreaterEqual(call.confidence, 0.7)
```

## Next Steps


---

*Source: test_test_example_extractor.py:62 | Complexity: Advanced | Last updated: 2026-02-14*