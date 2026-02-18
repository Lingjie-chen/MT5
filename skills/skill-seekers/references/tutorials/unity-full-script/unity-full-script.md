# How To: Unity Full Script

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test complete Unity script (high confidence expected)

## Prerequisites

**Required Modules:**
- `pytest`
- `bs4`
- `skill_seekers.cli.language_detector`


## Step-by-Step Guide

### Step 1: 'Test complete Unity script (high confidence expected)'

```python
'Test complete Unity script (high confidence expected)'
```

**Verification:**
```python
assert lang == 'csharp'
```

### Step 2: Assign detector = LanguageDetector(...)

```python
detector = LanguageDetector()
```

**Verification:**
```python
assert confidence >= 0.9
```

### Step 3: Assign code = '\n        using UnityEngine;\n        using System.Collections;\n\n        public class PlayerController : MonoBehaviour\n        {\n            [SerializeField]\n            private float speed = 5.0f;\n\n            [SerializeField]\n            private Rigidbody rb;\n\n            void Awake()\n            {\n                rb = GetComponent<Rigidbody>();\n            }\n\n            void Update()\n            {\n                float moveH = Input.GetAxis("Horizontal");\n                float moveV = Input.GetAxis("Vertical");\n\n                Vector3 movement = new Vector3(moveH, 0, moveV);\n                rb.AddForce(movement * speed);\n            }\n\n            IEnumerator DashCoroutine()\n            {\n                speed *= 2;\n                yield return new WaitForSeconds(0.5f);\n                speed /= 2;\n            }\n        }\n        '

```python
code = '\n        using UnityEngine;\n        using System.Collections;\n\n        public class PlayerController : MonoBehaviour\n        {\n            [SerializeField]\n            private float speed = 5.0f;\n\n            [SerializeField]\n            private Rigidbody rb;\n\n            void Awake()\n            {\n                rb = GetComponent<Rigidbody>();\n            }\n\n            void Update()\n            {\n                float moveH = Input.GetAxis("Horizontal");\n                float moveV = Input.GetAxis("Vertical");\n\n                Vector3 movement = new Vector3(moveH, 0, moveV);\n                rb.AddForce(movement * speed);\n            }\n\n            IEnumerator DashCoroutine()\n            {\n                speed *= 2;\n                yield return new WaitForSeconds(0.5f);\n                speed /= 2;\n            }\n        }\n        '
```

### Step 4: Assign unknown = detector.detect_from_code(...)

```python
lang, confidence = detector.detect_from_code(code)
```

**Verification:**
```python
assert lang == 'csharp'
```


## Complete Example

```python
# Workflow
'Test complete Unity script (high confidence expected)'
detector = LanguageDetector()
code = '\n        using UnityEngine;\n        using System.Collections;\n\n        public class PlayerController : MonoBehaviour\n        {\n            [SerializeField]\n            private float speed = 5.0f;\n\n            [SerializeField]\n            private Rigidbody rb;\n\n            void Awake()\n            {\n                rb = GetComponent<Rigidbody>();\n            }\n\n            void Update()\n            {\n                float moveH = Input.GetAxis("Horizontal");\n                float moveV = Input.GetAxis("Vertical");\n\n                Vector3 movement = new Vector3(moveH, 0, moveV);\n                rb.AddForce(movement * speed);\n            }\n\n            IEnumerator DashCoroutine()\n            {\n                speed *= 2;\n                yield return new WaitForSeconds(0.5f);\n                speed /= 2;\n            }\n        }\n        '
lang, confidence = detector.detect_from_code(code)
assert lang == 'csharp'
assert confidence >= 0.9
```

## Next Steps


---

*Source: test_language_detector.py:256 | Complexity: Intermediate | Last updated: 2026-02-14*