# How To: Chain Dependencies

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test chain of dependencies.

## Prerequisites

**Required Modules:**
- `shutil`
- `tempfile`
- `unittest`
- `skill_seekers.cli.dependency_analyzer`


## Step-by-Step Guide

### Step 1: 'Test chain of dependencies.'

```python
'Test chain of dependencies.'
```

### Step 2: Call self.analyzer.analyze_file()

```python
self.analyzer.analyze_file('main.py', 'import utils', 'Python')
```

### Step 3: Call self.analyzer.analyze_file()

```python
self.analyzer.analyze_file('utils.py', 'import helpers', 'Python')
```

### Step 4: Call self.analyzer.analyze_file()

```python
self.analyzer.analyze_file('helpers.py', '', 'Python')
```

### Step 5: Assign graph = self.analyzer.build_graph(...)

```python
graph = self.analyzer.build_graph()
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(graph.number_of_nodes(), 3)
```


## Complete Example

```python
# Workflow
'Test chain of dependencies.'
self.analyzer.analyze_file('main.py', 'import utils', 'Python')
self.analyzer.analyze_file('utils.py', 'import helpers', 'Python')
self.analyzer.analyze_file('helpers.py', '', 'Python')
graph = self.analyzer.build_graph()
self.assertEqual(graph.number_of_nodes(), 3)
```

## Next Steps


---

*Source: test_dependency_analyzer.py:208 | Complexity: Intermediate | Last updated: 2026-02-14*