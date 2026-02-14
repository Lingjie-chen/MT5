# How To: Swift Vs Similar Languages

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test Swift doesn't false-positive for similar syntax in other languages.

Critical for avoiding misclassification of:
- Go: 'func', ':=' short declaration
- Rust: 'fn', 'let mut', struct
- TypeScript: 'let', 'const', type annotations with ':'

These languages share keywords or syntax patterns with Swift,
so detection must use unique Swift patterns (guard let, @State, etc.)

## Prerequisites

**Required Modules:**
- `pytest`
- `bs4`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.swift_patterns`
- `skill_seekers.cli.swift_patterns`
- `skill_seekers.cli.swift_patterns`
- `unittest.mock`
- `skill_seekers.cli.language_detector`
- `sys`
- `unittest.mock`
- `unittest.mock`
- `skill_seekers.cli.language_detector`
- `inspect`
- `skill_seekers.cli`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`
- `skill_seekers.cli.language_detector`


## Step-by-Step Guide

### Step 1: "\n        Test Swift doesn't false-positive for similar syntax in other languages.\n\n        Critical for avoiding misclassification of:\n        - Go: 'func', ':=' short declaration\n        - Rust: 'fn', 'let mut', struct\n        - TypeScript: 'let', 'const', type annotations with ':'\n\n        These languages share keywords or syntax patterns with Swift,\n        so detection must use unique Swift patterns (guard let, @State, etc.)\n        "

```python
"\n        Test Swift doesn't false-positive for similar syntax in other languages.\n\n        Critical for avoiding misclassification of:\n        - Go: 'func', ':=' short declaration\n        - Rust: 'fn', 'let mut', struct\n        - TypeScript: 'let', 'const', type annotations with ':'\n\n        These languages share keywords or syntax patterns with Swift,\n        so detection must use unique Swift patterns (guard let, @State, etc.)\n        "
```

**Verification:**
```python
assert lang == 'go', f"Expected 'go', got '{lang}'"
```

### Step 2: Assign detector = LanguageDetector(...)

```python
detector = LanguageDetector()
```

**Verification:**
```python
assert lang == 'rust', f"Expected 'rust', got '{lang}'"
```

### Step 3: Assign go_code = '\n        package main\n\n        func main() {\n            message := "Hello"\n            fmt.Println(message)\n        }\n        '

```python
go_code = '\n        package main\n\n        func main() {\n            message := "Hello"\n            fmt.Println(message)\n        }\n        '
```

**Verification:**
```python
assert lang == 'typescript', f"Expected 'typescript', got '{lang}'"
```

### Step 4: Assign unknown = detector.detect_from_code(...)

```python
lang, _ = detector.detect_from_code(go_code)
```

**Verification:**
```python
assert lang == 'go', f"Expected 'go', got '{lang}'"
```

### Step 5: Assign rust_code = '\n        fn main() {\n            let mut x = 5;\n            println!("Value: {}", x);\n        }\n        '

```python
rust_code = '\n        fn main() {\n            let mut x = 5;\n            println!("Value: {}", x);\n        }\n        '
```

### Step 6: Assign unknown = detector.detect_from_code(...)

```python
lang, _ = detector.detect_from_code(rust_code)
```

**Verification:**
```python
assert lang == 'rust', f"Expected 'rust', got '{lang}'"
```

### Step 7: Assign ts_code = "\n        interface User {\n            name: string;\n            age: number;\n        }\n\n        const greet = (user: User): string => {\n            return `Hello, ${user.name}`;\n        }\n\n        export type Status = 'active' | 'inactive';\n        "

```python
ts_code = "\n        interface User {\n            name: string;\n            age: number;\n        }\n\n        const greet = (user: User): string => {\n            return `Hello, ${user.name}`;\n        }\n\n        export type Status = 'active' | 'inactive';\n        "
```

### Step 8: Assign unknown = detector.detect_from_code(...)

```python
lang, _ = detector.detect_from_code(ts_code)
```

**Verification:**
```python
assert lang == 'typescript', f"Expected 'typescript', got '{lang}'"
```


## Complete Example

```python
# Workflow
"\n        Test Swift doesn't false-positive for similar syntax in other languages.\n\n        Critical for avoiding misclassification of:\n        - Go: 'func', ':=' short declaration\n        - Rust: 'fn', 'let mut', struct\n        - TypeScript: 'let', 'const', type annotations with ':'\n\n        These languages share keywords or syntax patterns with Swift,\n        so detection must use unique Swift patterns (guard let, @State, etc.)\n        "
detector = LanguageDetector()
go_code = '\n        package main\n\n        func main() {\n            message := "Hello"\n            fmt.Println(message)\n        }\n        '
lang, _ = detector.detect_from_code(go_code)
assert lang == 'go', f"Expected 'go', got '{lang}'"
rust_code = '\n        fn main() {\n            let mut x = 5;\n            println!("Value: {}", x);\n        }\n        '
lang, _ = detector.detect_from_code(rust_code)
assert lang == 'rust', f"Expected 'rust', got '{lang}'"
ts_code = "\n        interface User {\n            name: string;\n            age: number;\n        }\n\n        const greet = (user: User): string => {\n            return `Hello, ${user.name}`;\n        }\n\n        export type Status = 'active' | 'inactive';\n        "
lang, _ = detector.detect_from_code(ts_code)
assert lang == 'typescript', f"Expected 'typescript', got '{lang}'"
```

## Next Steps


---

*Source: test_swift_detection.py:1004 | Complexity: Advanced | Last updated: 2026-02-14*