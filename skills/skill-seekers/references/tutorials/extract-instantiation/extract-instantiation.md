# How To: Extract Instantiation

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test extraction of object instantiation patterns

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

### Step 1: 'Test extraction of object instantiation patterns'

```python
'Test extraction of object instantiation patterns'
```

### Step 2: Assign code = '\nimport unittest\n\nclass TestDatabase(unittest.TestCase):\n    def test_connection(self):\n        """Test database connection"""\n        db = Database(host="localhost", port=5432, user="admin")\n        self.assertTrue(db.connect())\n'

```python
code = '\nimport unittest\n\nclass TestDatabase(unittest.TestCase):\n    def test_connection(self):\n        """Test database connection"""\n        db = Database(host="localhost", port=5432, user="admin")\n        self.assertTrue(db.connect())\n'
```

### Step 3: Assign examples = self.analyzer.extract(...)

```python
examples = self.analyzer.extract('test_db.py', code)
```

### Step 4: Assign instantiations = value

```python
instantiations = [ex for ex in examples if ex.category == 'instantiation']
```

### Step 5: Call self.assertGreater()

```python
self.assertGreater(len(instantiations), 0)
```

### Step 6: Assign inst = value

```python
inst = instantiations[0]
```

### Step 7: Call self.assertIn()

```python
self.assertIn('Database', inst.code)
```

### Step 8: Call self.assertIn()

```python
self.assertIn('host', inst.code)
```

### Step 9: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(inst.confidence, 0.7)
```


## Complete Example

```python
# Workflow
'Test extraction of object instantiation patterns'
code = '\nimport unittest\n\nclass TestDatabase(unittest.TestCase):\n    def test_connection(self):\n        """Test database connection"""\n        db = Database(host="localhost", port=5432, user="admin")\n        self.assertTrue(db.connect())\n'
examples = self.analyzer.extract('test_db.py', code)
instantiations = [ex for ex in examples if ex.category == 'instantiation']
self.assertGreater(len(instantiations), 0)
inst = instantiations[0]
self.assertIn('Database', inst.code)
self.assertIn('host', inst.code)
self.assertGreaterEqual(inst.confidence, 0.7)
```

## Next Steps


---

*Source: test_test_example_extractor.py:40 | Complexity: Advanced | Last updated: 2026-02-14*