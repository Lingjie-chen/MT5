# How To: Build With Ai Enhancement Api Mode Mocked

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, unittest, workflow, integration

## Overview

Workflow: Test building guides WITH AI enhancement in API mode (mocked)

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

**Required Fixtures:**
- `api_client` fixture

**Setup Required:**
```python
self.temp_dir = tempfile.mkdtemp()
```

## Step-by-Step Guide

### Step 1: 'Test building guides WITH AI enhancement in API mode (mocked)'

```python
'Test building guides WITH AI enhancement in API mode (mocked)'
```

### Step 2: Assign examples = value

```python
examples = [{'example_id': 'test_002', 'test_name': 'test_data_scraping', 'category': 'workflow', 'code': '\ndef test_data_scraping():\n    scraper = DocumentationScraper()\n    result = scraper.scrape("https://example.com/docs")\n    assert result.pages > 0\n                ', 'language': 'python', 'file_path': 'tests/test_scraper.py', 'line_start': 20, 'tags': ['scraping', 'documentation'], 'ai_analysis': {'tutorial_group': 'Data Collection', 'best_practices': ['Handle rate limiting'], 'common_mistakes': ['Not handling SSL errors']}}]
```

### Step 3: Assign builder = HowToGuideBuilder(...)

```python
builder = HowToGuideBuilder()
```

### Step 4: Assign output_dir = value

```python
output_dir = Path(self.temp_dir) / 'guides_enhanced'
```

### Step 5: Assign mock_enhancer = value

```python
mock_enhancer = MockEnhancer.return_value
```

### Step 6: Assign mock_enhancer.mode = 'api'

```python
mock_enhancer.mode = 'api'
```

### Step 7: Assign mock_enhancer.enhance_guide = mock_enhance_guide

```python
mock_enhancer.enhance_guide = mock_enhance_guide
```

### Step 8: Assign collection = builder.build_guides_from_examples(...)

```python
collection = builder.build_guides_from_examples(examples=examples, grouping_strategy='ai-tutorial-group', output_dir=output_dir, enhance_with_ai=True, ai_mode='api')
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
MockEnhancer.assert_called_once_with(mode='api')
```

### Step 12: Assign enhanced = guide_data.copy(...)

```python
enhanced = guide_data.copy()
```

### Step 13: Assign unknown = value

```python
enhanced['step_enhancements'] = [StepEnhancement(step_index=0, explanation='Test explanation', variations=[])]
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
'Test building guides WITH AI enhancement in API mode (mocked)'
from unittest.mock import patch
examples = [{'example_id': 'test_002', 'test_name': 'test_data_scraping', 'category': 'workflow', 'code': '\ndef test_data_scraping():\n    scraper = DocumentationScraper()\n    result = scraper.scrape("https://example.com/docs")\n    assert result.pages > 0\n                ', 'language': 'python', 'file_path': 'tests/test_scraper.py', 'line_start': 20, 'tags': ['scraping', 'documentation'], 'ai_analysis': {'tutorial_group': 'Data Collection', 'best_practices': ['Handle rate limiting'], 'common_mistakes': ['Not handling SSL errors']}}]
builder = HowToGuideBuilder()
output_dir = Path(self.temp_dir) / 'guides_enhanced'
with patch('skill_seekers.cli.guide_enhancer.GuideEnhancer') as MockEnhancer:
    mock_enhancer = MockEnhancer.return_value
    mock_enhancer.mode = 'api'

    def mock_enhance_guide(guide_data):
        enhanced = guide_data.copy()
        enhanced['step_enhancements'] = [StepEnhancement(step_index=0, explanation='Test explanation', variations=[])]
        enhanced['troubleshooting_detailed'] = []
        enhanced['prerequisites_detailed'] = []
        enhanced['next_steps_detailed'] = []
        enhanced['use_cases'] = []
        return enhanced
    mock_enhancer.enhance_guide = mock_enhance_guide
    collection = builder.build_guides_from_examples(examples=examples, grouping_strategy='ai-tutorial-group', output_dir=output_dir, enhance_with_ai=True, ai_mode='api')
    self.assertIsInstance(collection, GuideCollection)
    self.assertGreater(collection.total_guides, 0)
    MockEnhancer.assert_called_once_with(mode='api')
```

## Next Steps


---

*Source: test_how_to_guide_builder.py:698 | Complexity: Advanced | Last updated: 2026-02-14*