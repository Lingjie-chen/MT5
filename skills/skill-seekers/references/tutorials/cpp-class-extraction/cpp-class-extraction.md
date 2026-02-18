# How To: Cpp Class Extraction

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: unittest, workflow, integration

## Overview

Workflow: Test C++ class extraction with inheritance.

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `os`
- `sys`
- `unittest`
- `skill_seekers.cli.code_analyzer`

**Setup Required:**
```python
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')
```

## Step-by-Step Guide

### Step 1: 'Test C++ class extraction with inheritance.'

```python
'Test C++ class extraction with inheritance.'
```

### Step 2: Assign code = '\nclass Animal {\npublic:\n    virtual void makeSound() = 0;\n};\n\nclass Dog : public Animal {\npublic:\n    void makeSound() override;\n    void bark();\nprivate:\n    std::string breed;\n};\n'

```python
code = '\nclass Animal {\npublic:\n    virtual void makeSound() = 0;\n};\n\nclass Dog : public Animal {\npublic:\n    void makeSound() override;\n    void bark();\nprivate:\n    std::string breed;\n};\n'
```

### Step 3: Assign result = self.analyzer.analyze_file(...)

```python
result = self.analyzer.analyze_file('test.h', code, 'C++')
```

### Step 4: Call self.assertIn()

```python
self.assertIn('classes', result)
```

### Step 5: Call self.assertEqual()

```python
self.assertEqual(len(result['classes']), 2)
```

### Step 6: Assign animal_class = value

```python
animal_class = result['classes'][0]
```

### Step 7: Call self.assertEqual()

```python
self.assertEqual(animal_class['name'], 'Animal')
```

### Step 8: Assign dog_class = value

```python
dog_class = result['classes'][1]
```

### Step 9: Call self.assertEqual()

```python
self.assertEqual(dog_class['name'], 'Dog')
```

### Step 10: Call self.assertIn()

```python
self.assertIn('Animal', dog_class['base_classes'])
```


## Complete Example

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

# Workflow
'Test C++ class extraction with inheritance.'
code = '\nclass Animal {\npublic:\n    virtual void makeSound() = 0;\n};\n\nclass Dog : public Animal {\npublic:\n    void makeSound() override;\n    void bark();\nprivate:\n    std::string breed;\n};\n'
result = self.analyzer.analyze_file('test.h', code, 'C++')
self.assertIn('classes', result)
self.assertEqual(len(result['classes']), 2)
animal_class = result['classes'][0]
self.assertEqual(animal_class['name'], 'Animal')
dog_class = result['classes'][1]
self.assertEqual(dog_class['name'], 'Dog')
self.assertIn('Animal', dog_class['base_classes'])
```

## Next Steps


---

*Source: test_code_analyzer.py:376 | Complexity: Advanced | Last updated: 2026-02-14*