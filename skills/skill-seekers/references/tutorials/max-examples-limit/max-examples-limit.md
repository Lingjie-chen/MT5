# How To: Max Examples Limit

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test max examples per file limit

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

### Step 1: 'Test max examples per file limit'

```python
'Test max examples per file limit'
```

### Step 2: Assign test_file = value

```python
test_file = self.temp_dir / 'test_many.py'
```

### Step 3: Assign test_code = 'import unittest\n\nclass TestSuite(unittest.TestCase):\n'

```python
test_code = 'import unittest\n\nclass TestSuite(unittest.TestCase):\n'
```

### Step 4: Call test_file.write_text()

```python
test_file.write_text(test_code)
```

### Step 5: Assign limited_extractor = TestExampleExtractor(...)

```python
limited_extractor = TestExampleExtractor(max_per_file=5)
```

### Step 6: Assign examples = limited_extractor.extract_from_file(...)

```python
examples = limited_extractor.extract_from_file(test_file)
```

### Step 7: Call self.assertLessEqual()

```python
self.assertLessEqual(len(examples), 5)
```


## Complete Example

```python
# Setup
self.temp_dir = Path(tempfile.mkdtemp())
self.extractor = TestExampleExtractor(min_confidence=0.5, max_per_file=10)

# Workflow
'Test max examples per file limit'
test_file = self.temp_dir / 'test_many.py'
test_code = 'import unittest\n\nclass TestSuite(unittest.TestCase):\n'
for i in range(20):
    test_code += f'\n    def test_example_{i}(self):\n        """Test {i}"""\n        obj = MyClass(id={i}, name="test_{i}")\n        self.assertIsNotNone(obj)\n'
test_file.write_text(test_code)
limited_extractor = TestExampleExtractor(max_per_file=5)
examples = limited_extractor.extract_from_file(test_file)
self.assertLessEqual(len(examples), 5)
```

## Next Steps


---

*Source: test_test_example_extractor.py:649 | Complexity: Intermediate | Last updated: 2026-02-14*