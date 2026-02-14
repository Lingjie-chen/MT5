# How To: Observer Triplet Detection

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test classic attach/detach/notify triplet

## Prerequisites

**Required Modules:**
- `os`
- `sys`
- `unittest`
- `skill_seekers.cli.pattern_recognizer`


## Step-by-Step Guide

### Step 1: 'Test classic attach/detach/notify triplet'

```python
'Test classic attach/detach/notify triplet'
```

### Step 2: Assign code = '\nclass Subject:\n    def __init__(self):\n        self.observers = []\n\n    def attach(self, observer):\n        self.observers.append(observer)\n\n    def detach(self, observer):\n        self.observers.remove(observer)\n\n    def notify(self):\n        for observer in self.observers:\n            observer.update()\n'

```python
code = '\nclass Subject:\n    def __init__(self):\n        self.observers = []\n\n    def attach(self, observer):\n        self.observers.append(observer)\n\n    def detach(self, observer):\n        self.observers.remove(observer)\n\n    def notify(self):\n        for observer in self.observers:\n            observer.update()\n'
```

### Step 3: Assign report = self.recognizer.analyze_file(...)

```python
report = self.recognizer.analyze_file('test.py', code, 'Python')
```

### Step 4: Assign patterns = value

```python
patterns = [p for p in report.patterns if p.pattern_type == 'Observer']
```

### Step 5: Call self.assertGreater()

```python
self.assertGreater(len(patterns), 0)
```

### Step 6: Assign pattern = value

```python
pattern = patterns[0]
```

### Step 7: Call self.assertGreaterEqual()

```python
self.assertGreaterEqual(pattern.confidence, 0.8)
```

### Step 8: Assign evidence_str = unknown.join.lower(...)

```python
evidence_str = ' '.join(pattern.evidence).lower()
```

### Step 9: Call self.assertTrue()

```python
self.assertTrue('attach' in evidence_str and 'detach' in evidence_str and ('notify' in evidence_str))
```


## Complete Example

```python
# Workflow
'Test classic attach/detach/notify triplet'
code = '\nclass Subject:\n    def __init__(self):\n        self.observers = []\n\n    def attach(self, observer):\n        self.observers.append(observer)\n\n    def detach(self, observer):\n        self.observers.remove(observer)\n\n    def notify(self):\n        for observer in self.observers:\n            observer.update()\n'
report = self.recognizer.analyze_file('test.py', code, 'Python')
patterns = [p for p in report.patterns if p.pattern_type == 'Observer']
self.assertGreater(len(patterns), 0)
pattern = patterns[0]
self.assertGreaterEqual(pattern.confidence, 0.8)
evidence_str = ' '.join(pattern.evidence).lower()
self.assertTrue('attach' in evidence_str and 'detach' in evidence_str and ('notify' in evidence_str))
```

## Next Steps


---

*Source: test_pattern_recognizer.py:199 | Complexity: Advanced | Last updated: 2026-02-14*