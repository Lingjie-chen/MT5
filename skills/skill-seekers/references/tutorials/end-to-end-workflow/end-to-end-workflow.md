# How To: End To End Workflow

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test complete extraction workflow

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `os`
- `shutil`
- `sys`
- `tempfile`
- `unittest`
- `pathlib`
- `skill_seekers.cli.test_example_extractor`

**Setup Required:**
```python
self.temp_dir = Path(tempfile.mkdtemp())
self.extractor = TestExampleExtractor(min_confidence=0.5, max_per_file=10)
```

## Step-by-Step Guide

### Step 1: 'Test complete extraction workflow'

```python
'Test complete extraction workflow'
```

### Step 2: Call unknown.mkdir()

```python
(self.temp_dir / 'tests').mkdir()
```

### Step 3: Call unknown.write_text()

```python
(self.temp_dir / 'tests' / 'test_unit.py').write_text('\nimport unittest\n\nclass TestAPI(unittest.TestCase):\n    def test_connection(self):\n        """Test API connection"""\n        api = APIClient(url="https://api.example.com", timeout=30)\n        self.assertTrue(api.connect())\n')
```

### Step 4: Call unknown.write_text()

```python
(self.temp_dir / 'tests' / 'test_integration.py').write_text('\ndef test_workflow():\n    """Test complete workflow"""\n    user = User(name="John", email="john@example.com")\n    user.save()\n    user.verify()\n    assert user.is_active\n')
```

### Step 5: Assign report = self.extractor.extract_from_directory(...)

```python
report = self.extractor.extract_from_directory(self.temp_dir / 'tests')
```

### Step 6: Call self.assertGreater()

```python
self.assertGreater(report.total_examples, 0)
```

### Step 7: Call self.assertIsInstance()

```python
self.assertIsInstance(report.examples_by_category, dict)
```

### Step 8: Call self.assertIsInstance()

```python
self.assertIsInstance(report.examples_by_language, dict)
```

### Step 9: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(report.avg_complexity, 0.0)
```

### Step 10: Call self.assertLessEqual()

```python
self.assertLessEqual(report.avg_complexity, 1.0)
```

### Step 11: Call self.assertGreater()

```python
self.assertGreater(len(report.examples_by_category), 0)
```

### Step 12: Call self.assertIsNotNone()

```python
self.assertIsNotNone(example.example_id)
```

### Step 13: Call self.assertIsNotNone()

```python
self.assertIsNotNone(example.test_name)
```

### Step 14: Call self.assertIsNotNone()

```python
self.assertIsNotNone(example.category)
```

### Step 15: Call self.assertIsNotNone()

```python
self.assertIsNotNone(example.code)
```

### Step 16: Call self.assertIsNotNone()

```python
self.assertIsNotNone(example.language)
```

### Step 17: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(example.confidence, 0.0)
```

### Step 18: Call self.assertLessEqual()

```python
self.assertLessEqual(example.confidence, 1.0)
```


## Complete Example

```python
# Setup
self.temp_dir = Path(tempfile.mkdtemp())
self.extractor = TestExampleExtractor(min_confidence=0.5, max_per_file=10)

# Workflow
'Test complete extraction workflow'
(self.temp_dir / 'tests').mkdir()
(self.temp_dir / 'tests' / 'test_unit.py').write_text('\nimport unittest\n\nclass TestAPI(unittest.TestCase):\n    def test_connection(self):\n        """Test API connection"""\n        api = APIClient(url="https://api.example.com", timeout=30)\n        self.assertTrue(api.connect())\n')
(self.temp_dir / 'tests' / 'test_integration.py').write_text('\ndef test_workflow():\n    """Test complete workflow"""\n    user = User(name="John", email="john@example.com")\n    user.save()\n    user.verify()\n    assert user.is_active\n')
report = self.extractor.extract_from_directory(self.temp_dir / 'tests')
self.assertGreater(report.total_examples, 0)
self.assertIsInstance(report.examples_by_category, dict)
self.assertIsInstance(report.examples_by_language, dict)
self.assertGreaterEqual(report.avg_complexity, 0.0)
self.assertLessEqual(report.avg_complexity, 1.0)
self.assertGreater(len(report.examples_by_category), 0)
for example in report.examples:
    self.assertIsNotNone(example.example_id)
    self.assertIsNotNone(example.test_name)
    self.assertIsNotNone(example.category)
    self.assertIsNotNone(example.code)
    self.assertIsNotNone(example.language)
    self.assertGreaterEqual(example.confidence, 0.0)
    self.assertLessEqual(example.confidence, 1.0)
```

## Next Steps


---

*Source: test_test_example_extractor.py:670 | Complexity: Advanced | Last updated: 2026-02-14*