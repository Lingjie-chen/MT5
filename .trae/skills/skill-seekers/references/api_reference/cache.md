# API Reference: cache.py

**Language**: Python

**Source**: `src\skill_seekers\embedding\cache.py`

---

## Classes

### EmbeddingCache

SQLite-based cache for embeddings.

Stores embeddings with their text hashes to avoid regeneration.
Supports TTL (time-to-live) for cache entries.

Examples:
    cache = EmbeddingCache("/path/to/cache.db")

    # Store embedding
    cache.set("hash123", [0.1, 0.2, 0.3], model="text-embedding-3-small")

    # Retrieve embedding
    embedding = cache.get("hash123")

    # Check if cached
    if cache.has("hash123"):
        print("Embedding is cached")

**Inherits from**: (none)

#### Methods

##### __init__(self, db_path: str = ':memory:', ttl_days: int = 30)

Initialize embedding cache.

Args:
    db_path: Path to SQLite database (":memory:" for in-memory)
    ttl_days: Time-to-live for cache entries in days

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| db_path | str | ':memory:' | - |
| ttl_days | int | 30 | - |


##### _init_db(self)

Initialize database schema.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### set(self, hash_key: str, embedding: list[float], model: str) → None

Store embedding in cache.

Args:
    hash_key: Hash of text+model
    embedding: Embedding vector
    model: Model name

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| hash_key | str | - | - |
| embedding | list[float] | - | - |
| model | str | - | - |

**Returns**: `None`


##### get(self, hash_key: str) → list[float] | None

Retrieve embedding from cache.

Args:
    hash_key: Hash of text+model

Returns:
    Embedding vector if cached and not expired, None otherwise

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| hash_key | str | - | - |

**Returns**: `list[float] | None`


##### get_batch(self, hash_keys: list[str]) → tuple[list[list[float] | None], list[bool]]

Retrieve multiple embeddings from cache.

Args:
    hash_keys: List of hashes

Returns:
    Tuple of (embeddings list, cached flags)
    embeddings list contains None for cache misses

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| hash_keys | list[str] | - | - |

**Returns**: `tuple[list[list[float] | None], list[bool]]`


##### has(self, hash_key: str) → bool

Check if embedding is cached and not expired.

Args:
    hash_key: Hash of text+model

Returns:
    True if cached and not expired, False otherwise

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| hash_key | str | - | - |

**Returns**: `bool`


##### delete(self, hash_key: str) → None

Delete embedding from cache.

Args:
    hash_key: Hash of text+model

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| hash_key | str | - | - |

**Returns**: `None`


##### clear(self, model: str | None = None) → int

Clear cache entries.

Args:
    model: If provided, only clear entries for this model

Returns:
    Number of entries deleted

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| model | str | None | None | - |

**Returns**: `int`


##### clear_expired(self) → int

Clear expired cache entries.

Returns:
    Number of entries deleted

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `int`


##### size(self) → int

Get number of cached embeddings.

Returns:
    Number of cache entries

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `int`


##### stats(self) → dict

Get cache statistics.

Returns:
    Dictionary with cache stats

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `dict`


##### close(self)

Close database connection.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### __enter__(self)

Context manager entry.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### __exit__(self, exc_type, exc_val, exc_tb)

Context manager exit.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| exc_type | None | - | - |
| exc_val | None | - | - |
| exc_tb | None | - | - |



