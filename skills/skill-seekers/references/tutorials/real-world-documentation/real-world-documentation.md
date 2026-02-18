# How To: Real World Documentation

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: workflow, integration

## Overview

Workflow: Test with realistic documentation content.

## Prerequisites

**Required Modules:**
- `pytest`
- `json`
- `skill_seekers.cli.rag_chunker`
- `langchain.schema`
- `llama_index.core.schema`


## Step-by-Step Guide

### Step 1: 'Test with realistic documentation content.'

```python
'Test with realistic documentation content.'
```

**Verification:**
```python
assert len(chunks) > 0
```

### Step 2: Assign chunker = RAGChunker(...)

```python
chunker = RAGChunker(chunk_size=512, chunk_overlap=50)
```

**Verification:**
```python
assert len(code_chunks) >= 1
```

### Step 3: Assign text = '\n        # React Hooks\n\n        React Hooks are functions that let you "hook into" React state and lifecycle features from function components.\n\n        ## useState\n\n        The `useState` Hook lets you add React state to function components.\n\n        ```javascript\n        import { useState } from \'react\';\n\n        function Example() {\n          const [count, setCount] = useState(0);\n\n          return (\n            <div>\n              <p>You clicked {count} times</p>\n              <button onClick={() => setCount(count + 1)}>\n                Click me\n              </button>\n            </div>\n          );\n        }\n        ```\n\n        ## useEffect\n\n        The `useEffect` Hook lets you perform side effects in function components.\n\n        ```javascript\n        import { useEffect } from \'react\';\n\n        function Example() {\n          useEffect(() => {\n            document.title = `You clicked ${count} times`;\n          });\n        }\n        ```\n\n        ## Best Practices\n\n        - Only call Hooks at the top level\n        - Only call Hooks from React functions\n        - Use multiple Hooks to separate concerns\n        '

```python
text = '\n        # React Hooks\n\n        React Hooks are functions that let you "hook into" React state and lifecycle features from function components.\n\n        ## useState\n\n        The `useState` Hook lets you add React state to function components.\n\n        ```javascript\n        import { useState } from \'react\';\n\n        function Example() {\n          const [count, setCount] = useState(0);\n\n          return (\n            <div>\n              <p>You clicked {count} times</p>\n              <button onClick={() => setCount(count + 1)}>\n                Click me\n              </button>\n            </div>\n          );\n        }\n        ```\n\n        ## useEffect\n\n        The `useEffect` Hook lets you perform side effects in function components.\n\n        ```javascript\n        import { useEffect } from \'react\';\n\n        function Example() {\n          useEffect(() => {\n            document.title = `You clicked ${count} times`;\n          });\n        }\n        ```\n\n        ## Best Practices\n\n        - Only call Hooks at the top level\n        - Only call Hooks from React functions\n        - Use multiple Hooks to separate concerns\n        '
```

**Verification:**
```python
assert chunk['metadata']['source'] == 'react-docs'
```

### Step 4: Assign metadata = value

```python
metadata = {'source': 'react-docs', 'category': 'hooks', 'url': 'https://react.dev/reference/react'}
```

**Verification:**
```python
assert chunk['metadata']['category'] == 'hooks'
```

### Step 5: Assign chunks = chunker.chunk_document(...)

```python
chunks = chunker.chunk_document(text, metadata)
```

**Verification:**
```python
assert chunk['metadata']['estimated_tokens'] > 0
```

### Step 6: Assign code_chunks = value

```python
code_chunks = [c for c in chunks if c['metadata']['has_code_block']]
```

**Verification:**
```python
assert len(code_chunks) >= 1
```


## Complete Example

```python
# Workflow
'Test with realistic documentation content.'
chunker = RAGChunker(chunk_size=512, chunk_overlap=50)
text = '\n        # React Hooks\n\n        React Hooks are functions that let you "hook into" React state and lifecycle features from function components.\n\n        ## useState\n\n        The `useState` Hook lets you add React state to function components.\n\n        ```javascript\n        import { useState } from \'react\';\n\n        function Example() {\n          const [count, setCount] = useState(0);\n\n          return (\n            <div>\n              <p>You clicked {count} times</p>\n              <button onClick={() => setCount(count + 1)}>\n                Click me\n              </button>\n            </div>\n          );\n        }\n        ```\n\n        ## useEffect\n\n        The `useEffect` Hook lets you perform side effects in function components.\n\n        ```javascript\n        import { useEffect } from \'react\';\n\n        function Example() {\n          useEffect(() => {\n            document.title = `You clicked ${count} times`;\n          });\n        }\n        ```\n\n        ## Best Practices\n\n        - Only call Hooks at the top level\n        - Only call Hooks from React functions\n        - Use multiple Hooks to separate concerns\n        '
metadata = {'source': 'react-docs', 'category': 'hooks', 'url': 'https://react.dev/reference/react'}
chunks = chunker.chunk_document(text, metadata)
assert len(chunks) > 0
code_chunks = [c for c in chunks if c['metadata']['has_code_block']]
assert len(code_chunks) >= 1
for chunk in chunks:
    assert chunk['metadata']['source'] == 'react-docs'
    assert chunk['metadata']['category'] == 'hooks'
    assert chunk['metadata']['estimated_tokens'] > 0
```

## Next Steps


---

*Source: test_rag_chunker.py:293 | Complexity: Intermediate | Last updated: 2026-02-14*