# How To: Detect Lua With Confidence

**Difficulty**: Intermediate
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test Lua detection

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `sys`
- `unittest`
- `pathlib`
- `fitz`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.pdf_extractor_poc`
- `skill_seekers.cli.pdf_extractor_poc`
- `fitz`
- `unittest.mock`
- `fitz`
- `unittest.mock`
- `fitz`
- `unittest.mock`
- `fitz`
- `unittest.mock`
- `fitz`

**Setup Required:**
```python
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor
```

## Step-by-Step Guide

### Step 1: 'Test Lua detection'

```python
'Test Lua detection'
```

### Step 2: Assign extractor = self.PDFExtractor.__new__(...)

```python
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
```

### Step 3: Assign extractor.language_detector = LanguageDetector(...)

```python
extractor.language_detector = LanguageDetector(min_confidence=0.15)
```

### Step 4: Assign code = '\n        local function calculate_sum(numbers)\n          local total = 0\n          for i = 1, #numbers do\n            total = total + numbers[i]\n          end\n          return total\n        end\n\n        local items = {1, 2, 3, 4, 5}\n        local result = calculate_sum(items)\n        print("Sum: " .. result)\n        '

```python
code = '\n        local function calculate_sum(numbers)\n          local total = 0\n          for i = 1, #numbers do\n            total = total + numbers[i]\n          end\n          return total\n        end\n\n        local items = {1, 2, 3, 4, 5}\n        local result = calculate_sum(items)\n        print("Sum: " .. result)\n        '
```

### Step 5: Assign unknown = extractor.detect_language_from_code(...)

```python
language, confidence = extractor.detect_language_from_code(code)
```

### Step 6: Call self.assertEqual()

```python
self.assertEqual(language, 'lua')
```

### Step 7: Call self.assertGreater()

```python
self.assertGreater(confidence, 0.7)
```


## Complete Example

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

# Workflow
'Test Lua detection'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = '\n        local function calculate_sum(numbers)\n          local total = 0\n          for i = 1, #numbers do\n            total = total + numbers[i]\n          end\n          return total\n        end\n\n        local items = {1, 2, 3, 4, 5}\n        local result = calculate_sum(items)\n        print("Sum: " .. result)\n        '
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'lua')
self.assertGreater(confidence, 0.7)
```

## Next Steps


---

*Source: test_pdf_extractor.py:252 | Complexity: Intermediate | Last updated: 2026-02-14*