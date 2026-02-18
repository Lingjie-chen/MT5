# API Reference: embedding_pipeline.py

**Language**: Python

**Source**: `src\skill_seekers\cli\embedding_pipeline.py`

---

## Classes

### EmbeddingConfig

Configuration for embedding generation.

**Inherits from**: (none)



### EmbeddingResult

Result of embedding generation.

**Inherits from**: (none)



### CostTracker

Track embedding generation costs.

**Inherits from**: (none)

#### Methods

##### add_request(self, token_count: int, cost: float, from_cache: bool = False)

Add a request to tracking.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| token_count | int | - | - |
| cost | float | - | - |
| from_cache | bool | False | - |


##### get_stats(self) → dict[str, Any]

Get statistics.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `dict[str, Any]`




### EmbeddingProvider

Abstract base class for embedding providers.

**Inherits from**: ABC

#### Methods

##### generate_embeddings(self, texts: list[str]) → list[list[float]]

Generate embeddings for texts.

**Decorators**: `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| texts | list[str] | - | - |

**Returns**: `list[list[float]]`


##### get_dimension(self) → int

Get embedding dimension.

**Decorators**: `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `int`


##### estimate_cost(self, token_count: int) → float

Estimate cost for token count.

**Decorators**: `@abstractmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| token_count | int | - | - |

**Returns**: `float`




### OpenAIEmbeddingProvider

OpenAI embedding provider.

**Inherits from**: EmbeddingProvider

#### Methods

##### __init__(self, model: str = 'text-embedding-ada-002', api_key: str | None = None)

Initialize OpenAI provider.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| model | str | 'text-embedding-ada-002' | - |
| api_key | str | None | None | - |


##### _get_client(self)

Lazy load OpenAI client.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### generate_embeddings(self, texts: list[str]) → list[list[float]]

Generate embeddings using OpenAI.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| texts | list[str] | - | - |

**Returns**: `list[list[float]]`


##### get_dimension(self) → int

Get embedding dimension.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `int`


##### estimate_cost(self, token_count: int) → float

Estimate cost.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| token_count | int | - | - |

**Returns**: `float`




### LocalEmbeddingProvider

Local embedding provider (simulated).

**Inherits from**: EmbeddingProvider

#### Methods

##### __init__(self, dimension: int = 384)

Initialize local provider.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| dimension | int | 384 | - |


##### generate_embeddings(self, texts: list[str]) → list[list[float]]

Generate embeddings using local model (simulated).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| texts | list[str] | - | - |

**Returns**: `list[list[float]]`


##### get_dimension(self) → int

Get embedding dimension.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `int`


##### estimate_cost(self, token_count: int) → float

Local models are free.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| token_count | int | - | - |

**Returns**: `float`




### EmbeddingCache

Cache for embeddings to avoid recomputation.

**Inherits from**: (none)

#### Methods

##### __init__(self, cache_dir: Path | None = None)

Initialize cache.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| cache_dir | Path | None | None | - |


##### _compute_hash(self, text: str, model: str) → str

Compute cache key.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| model | str | - | - |

**Returns**: `str`


##### get(self, text: str, model: str) → list[float] | None

Get embedding from cache.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| model | str | - | - |

**Returns**: `list[float] | None`


##### set(self, text: str, model: str, embedding: list[float]) → None

Store embedding in cache.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| model | str | - | - |
| embedding | list[float] | - | - |

**Returns**: `None`




### EmbeddingPipeline

Flexible embedding generation pipeline.

Supports multiple providers, batch processing, caching, and cost tracking.

**Inherits from**: (none)

#### Methods

##### __init__(self, config: EmbeddingConfig)

Initialize pipeline.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| config | EmbeddingConfig | - | - |


##### _create_provider(self) → EmbeddingProvider

Create provider based on config.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `EmbeddingProvider`


##### _estimate_tokens(self, text: str) → int

Estimate token count (rough approximation).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |

**Returns**: `int`


##### generate_batch(self, texts: list[str], show_progress: bool = True) → EmbeddingResult

Generate embeddings for batch of texts.

Args:
    texts: List of texts to embed
    show_progress: Show progress output

Returns:
    EmbeddingResult with embeddings and metadata

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| texts | list[str] | - | - |
| show_progress | bool | True | - |

**Returns**: `EmbeddingResult`


##### validate_dimensions(self, embeddings: list[list[float]]) → bool

Validate embedding dimensions.

Args:
    embeddings: List of embeddings to validate

Returns:
    True if valid

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| embeddings | list[list[float]] | - | - |

**Returns**: `bool`


##### get_cost_stats(self) → dict[str, Any]

Get cost tracking statistics.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `dict[str, Any]`




## Functions

### example_usage()

Example usage of embedding pipeline.

**Returns**: (none)


