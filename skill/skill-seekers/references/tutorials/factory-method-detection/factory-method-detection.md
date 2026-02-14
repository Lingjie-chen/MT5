# How To: Factory Method Detection

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test detection of create/make methods

## Prerequisites

**Required Modules:**
- `os`
- `sys`
- `unittest`
- `skill_seekers.cli.pattern_recognizer`


## Step-by-Step Guide

### Step 1: 'Test detection of create/make methods'

```python
'Test detection of create/make methods'
```

### Step 2: Assign code = "\nclass VehicleFactory:\n    def create(self, vehicle_type):\n        if vehicle_type == 'car':\n            return Car()\n        elif vehicle_type == 'truck':\n            return Truck()\n\n    def make_vehicle(self, specs):\n        return Vehicle(specs)\n"

```python
code = "\nclass VehicleFactory:\n    def create(self, vehicle_type):\n        if vehicle_type == 'car':\n            return Car()\n        elif vehicle_type == 'truck':\n            return Truck()\n\n    def make_vehicle(self, specs):\n        return Vehicle(specs)\n"
```

### Step 3: Assign report = self.recognizer.analyze_file(...)

```python
report = self.recognizer.analyze_file('test.py', code, 'Python')
```

### Step 4: Assign patterns = value

```python
patterns = [p for p in report.patterns if p.pattern_type == 'Factory']
```

### Step 5: Call self.assertGreater()

```python
self.assertGreater(len(patterns), 0)
```

### Step 6: Assign pattern = value

```python
pattern = patterns[0]
```

### Step 7: Call self.assertIn()

```python
self.assertIn('create', ' '.join(pattern.evidence).lower())
```


## Complete Example

```python
# Workflow
'Test detection of create/make methods'
code = "\nclass VehicleFactory:\n    def create(self, vehicle_type):\n        if vehicle_type == 'car':\n            return Car()\n        elif vehicle_type == 'truck':\n            return Truck()\n\n    def make_vehicle(self, specs):\n        return Vehicle(specs)\n"
report = self.recognizer.analyze_file('test.py', code, 'Python')
patterns = [p for p in report.patterns if p.pattern_type == 'Factory']
self.assertGreater(len(patterns), 0)
pattern = patterns[0]
self.assertIn('create', ' '.join(pattern.evidence).lower())
```

## Next Steps


---

*Source: test_pattern_recognizer.py:135 | Complexity: Intermediate | Last updated: 2026-02-14*