# API Reference: context_server.py

**Language**: Python

**Source**: `examples\continue-dev-universal\context_server.py`

---

## Functions

### load_framework_docs(framework: str) → str

Load framework documentation from Skill Seekers output.

Args:
    framework: Framework name (vue, react, django, etc.)

Returns:
    Documentation content as string

Raises:
    FileNotFoundError: If documentation not found

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| framework | str | - | - |

**Returns**: `str`



### root()

**Async function**

Root endpoint with server information.

**Returns**: (none)



### health()

**Async function**

Health check endpoint.

**Returns**: (none)



### list_frameworks() → Dict[str, List[str]]

**Async function**

List available frameworks.

Returns:
    Dictionary with available and missing frameworks

**Returns**: `Dict[str, List[str]]`



### get_framework_docs(framework: str, query: str = None) → JSONResponse

**Async function**

Get framework documentation as Continue.dev context items.

Args:
    framework: Framework name (vue, react, django, etc.)
    query: Optional search query for filtering (future feature)

Returns:
    JSON response with contextItems array for Continue.dev

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| framework | str | - | - |
| query | str | None | - |

**Returns**: `JSONResponse`



### get_project_conventions() → JSONResponse

**Async function**

Get project-specific conventions.

Returns:
    JSON response with project conventions

**Returns**: `JSONResponse`



### main()

**Returns**: (none)


