# How To: Build With Ai Enhancement Local Mode Mocked

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, unittest, workflow, integration

## Overview

Workflow: Test building guides WITH AI enhancement in LOCAL mode (mocked)

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `os`
- `shutil`
- `sys`
- `tempfile`
- `unittest`
- `pathlib`
- `skill_seekers.cli.guide_enhancer`
- `skill_seekers.cli.how_to_guide_builder`
- `unittest.mock`
- `unittest.mock`
- `unittest.mock`
- `unittest.mock`
- `ast`
- `ast`

**Setup Required:**
```python
self.temp_dir = tempfile.mkdtemp()
```

## Step-by-Step Guide

### Step 1: 'Test building guides WITH AI enhancement in LOCAL mode (mocked)'

```python
'Test building guides WITH AI enhancement in LOCAL mode (mocked)'
```

### Step 2: Assign examples = value

```python
examples = [{'example_id': 'test_003', 'test_name': 'test_api_integration', 'category': 'workflow', 'code': '\ndef test_api_integration():\n    client = APIClient(base_url="https://api.example.com")\n    response = client.get("/users")\n    assert response.status_code == 200\n                ', 'language': 'python', 'file_path': 'tests/test_api.py', 'line_start': 30, 'tags': ['api', 'integration'], 'ai_analysis': {'tutorial_group': 'API Testing', 'best_practices': ['Use environment variables'], 'common_mistakes': ['Hardcoded credentials']}}]
```

### Step 3: Assign builder = HowToGuideBuilder(...)

```python
builder = HowToGuideBuilder()
```

### Step 4: Assign output_dir = value

```python
output_dir = Path(self.temp_dir) / 'guides_local'
```

### Step 5: Assign mock_enhancer = value

```python
mock_enhancer = MockEnhancer.return_value
```

### Step 6: Assign mock_enhancer.mode = 'local'

```python
mock_enhancer.mode = 'local'
```

### Step 7: Assign mock_enhancer.enhance_guide = mock_enhance_guide

```python
mock_enhancer.enhance_guide = mock_enhance_guide
```

### Step 8: Assign collection = builder.build_guides_from_examples(...)

```python
collection = builder.build_guides_from_examples(examples=examples, grouping_strategy='ai-tutorial-group', output_dir=output_dir, enhance_with_ai=True, ai_mode='local')
```

### Step 9: Call self.assertIsInstance()

```python
self.assertIsInstance(collection, GuideCollection)
```

### Step 10: Call self.assertGreater()

```python
self.assertGreater(collection.total_guides, 0)
```

### Step 11: Call MockEnhancer.assert_called_once_with()

```python
MockEnhancer.assert_called_once_with(mode='local')
```

### Step 12: Assign enhanced = guide_data.copy(...)

```python
enhanced = guide_data.copy()
```

### Step 13: Assign unknown = value

```python
enhanced['step_enhancements'] = []
```

### Step 14: Assign unknown = value

```python
enhanced['troubleshooting_detailed'] = []
```

### Step 15: Assign unknown = value

```python
enhanced['prerequisites_detailed'] = []
```

### Step 16: Assign unknown = value

```python
enhanced['next_steps_detailed'] = []
```

### Step 17: Assign unknown = value

```python
enhanced['use_cases'] = []
```


## Complete Example

```python
# Setup
self.temp_dir = tempfile.mkdtemp()

# Workflow
'Test building guides WITH AI enhancement in LOCAL mode (mocked)'
from unittest.mock import patch
examples = [{'example_id': 'test_003', 'test_name': 'test_api_integration', 'category': 'workflow', 'code': '\ndef test_api_integration():\n    client = APIClient(base_url="https://api.example.com")\n    response = client.get("/users")\n    assert response.status_code == 200\n                ', 'language': 'python', 'file_path': 'tests/test_api.py', 'line_start': 30, 'tags': ['api', 'integration'], 'ai_analysis': {'tutorial_group': 'API Testing', 'best_practices': ['Use environment variables'], 'common_mistakes': ['Hardcoded credentials']}}]
builder = HowToGuideBuilder()
output_dir = Path(self.temp_dir) / 'guides_local'
with patch('skill_seekers.cli.guide_enhancer.GuideEnhancer') as MockEnhancer:
    mock_enhancer = MockEnhancer.return_value
    mock_enhancer.mode = 'local'

    def mock_enhance_guide(guide_data):
        enhanced = guide_data.copy()
        enhanced['step_enhancements'] = []
        enhanced['troubleshooting_detailed'] = []
        enhanced['prerequisites_detailed'] = []
        enhanced['next_steps_detailed'] = []
        enhanced['use_cases'] = []
        return enhanced
    mock_enhancer.enhance_guide = mock_enhance_guide
    collection = builder.build_guides_from_examples(examples=examples, grouping_strategy='ai-tutorial-group', output_dir=output_dir, enhance_with_ai=True, ai_mode='local')
    self.assertIsInstance(collection, GuideCollection)
    self.assertGreater(collection.total_guides, 0)
    MockEnhancer.assert_called_once_with(mode='local')
```

## Next Steps


---

*Source: test_how_to_guide_builder.py:764 | Complexity: Advanced | Last updated: 2026-02-14*