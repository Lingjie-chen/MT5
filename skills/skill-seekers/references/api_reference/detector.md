# API Reference: detector.py

**Language**: Python

**Source**: `src\skill_seekers\sync\detector.py`

---

## Classes

### ChangeDetector

Detects changes in documentation pages.

Uses multiple strategies:
1. Content hashing (SHA-256)
2. Last-Modified headers
3. ETag headers
4. Content diffing

Examples:
    detector = ChangeDetector()

    # Check single page
    change = detector.check_page(
        url="https://react.dev/learn",
        old_hash="abc123"
    )

    # Generate diff
    diff = detector.generate_diff(old_content, new_content)

    # Check multiple pages
    changes = detector.check_pages(urls, previous_state)

**Inherits from**: (none)

#### Methods

##### __init__(self, timeout: int = 30)

Initialize change detector.

Args:
    timeout: Request timeout in seconds

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| timeout | int | 30 | - |


##### compute_hash(self, content: str) → str

Compute SHA-256 hash of content.

Args:
    content: Page content

Returns:
    Hexadecimal hash string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| content | str | - | - |

**Returns**: `str`


##### fetch_page(self, url: str) → tuple[str, dict[str, str]]

Fetch page content and metadata.

Args:
    url: Page URL

Returns:
    Tuple of (content, metadata)
    metadata includes: last-modified, etag, content-type

Raises:
    requests.RequestException: If fetch fails

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| url | str | - | - |

**Returns**: `tuple[str, dict[str, str]]`


##### check_page(self, url: str, old_hash: str | None = None, generate_diff: bool = False, old_content: str | None = None) → PageChange

Check if page has changed.

Args:
    url: Page URL
    old_hash: Previous content hash
    generate_diff: Whether to generate diff
    old_content: Previous content (for diff generation)

Returns:
    PageChange object

Raises:
    requests.RequestException: If fetch fails

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| url | str | - | - |
| old_hash | str | None | None | - |
| generate_diff | bool | False | - |
| old_content | str | None | None | - |

**Returns**: `PageChange`


##### check_pages(self, urls: list[str], previous_hashes: dict[str, str], generate_diffs: bool = False) → ChangeReport

Check multiple pages for changes.

Args:
    urls: List of URLs to check
    previous_hashes: URL -> hash mapping from previous state
    generate_diffs: Whether to generate diffs

Returns:
    ChangeReport with all detected changes

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| urls | list[str] | - | - |
| previous_hashes | dict[str, str] | - | - |
| generate_diffs | bool | False | - |

**Returns**: `ChangeReport`


##### generate_diff(self, old_content: str, new_content: str) → str

Generate unified diff between old and new content.

Args:
    old_content: Original content
    new_content: New content

Returns:
    Unified diff string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| old_content | str | - | - |
| new_content | str | - | - |

**Returns**: `str`


##### generate_summary_diff(self, old_content: str, new_content: str) → str

Generate human-readable diff summary.

Args:
    old_content: Original content
    new_content: New content

Returns:
    Summary string with added/removed line counts

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| old_content | str | - | - |
| new_content | str | - | - |

**Returns**: `str`


##### check_header_changes(self, url: str, old_modified: str | None = None, old_etag: str | None = None) → bool

Quick check using HTTP headers (no content download).

Args:
    url: Page URL
    old_modified: Previous Last-Modified header
    old_etag: Previous ETag header

Returns:
    True if headers indicate change, False otherwise

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| url | str | - | - |
| old_modified | str | None | None | - |
| old_etag | str | None | None | - |

**Returns**: `bool`


##### batch_check_headers(self, urls: list[str], previous_metadata: dict[str, dict[str, str]]) → list[str]

Batch check URLs using headers only.

Args:
    urls: URLs to check
    previous_metadata: URL -> metadata mapping

Returns:
    List of URLs that likely changed

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| urls | list[str] | - | - |
| previous_metadata | dict[str, dict[str, str]] | - | - |

**Returns**: `list[str]`



