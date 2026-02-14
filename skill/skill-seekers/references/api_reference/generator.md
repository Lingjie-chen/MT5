# API Reference: generator.py

**Language**: Python

**Source**: `src\skill_seekers\embedding\generator.py`

---

## Classes

### EmbeddingGenerator

Generate embeddings using multiple model providers.

Supported providers:
- OpenAI (text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002)
- Sentence Transformers (all-MiniLM-L6-v2, all-mpnet-base-v2, etc.)
- Anthropic/Voyage AI (voyage-2, voyage-large-2)

Examples:
    # OpenAI embeddings
    generator = EmbeddingGenerator()
    embedding = generator.generate("Hello world", model="text-embedding-3-small")

    # Sentence transformers (local, no API)
    embedding = generator.generate("Hello world", model="all-MiniLM-L6-v2")

    # Batch generation
    embeddings = generator.generate_batch(
        ["text1", "text2", "text3"],
        model="text-embedding-3-small"
    )

**Inherits from**: (none)

#### Methods

##### __init__(self, api_key: str | None = None, voyage_api_key: str | None = None, cache_dir: str | None = None)

Initialize embedding generator.

Args:
    api_key: API key for OpenAI
    voyage_api_key: API key for Voyage AI (Anthropic's recommended embeddings)
    cache_dir: Directory for caching models (sentence-transformers)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| api_key | str | None | None | - |
| voyage_api_key | str | None | None | - |
| cache_dir | str | None | None | - |


##### get_model_info(self, model: str) → dict

Get information about a model.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| model | str | - | - |

**Returns**: `dict`


##### list_models(self) → list[dict]

List all available models.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `list[dict]`


##### generate(self, text: str, model: str = 'text-embedding-3-small', normalize: bool = True) → list[float]

Generate embedding for a single text.

Args:
    text: Text to embed
    model: Model name
    normalize: Whether to normalize to unit length

Returns:
    Embedding vector

Raises:
    ValueError: If model is not supported
    Exception: If embedding generation fails

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| model | str | 'text-embedding-3-small' | - |
| normalize | bool | True | - |

**Returns**: `list[float]`


##### generate_batch(self, texts: list[str], model: str = 'text-embedding-3-small', normalize: bool = True, batch_size: int = 32) → tuple[list[list[float]], int]

Generate embeddings for multiple texts.

Args:
    texts: List of texts to embed
    model: Model name
    normalize: Whether to normalize to unit length
    batch_size: Batch size for processing

Returns:
    Tuple of (embeddings list, dimensions)

Raises:
    ValueError: If model is not supported
    Exception: If embedding generation fails

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| texts | list[str] | - | - |
| model | str | 'text-embedding-3-small' | - |
| normalize | bool | True | - |
| batch_size | int | 32 | - |

**Returns**: `tuple[list[list[float]], int]`


##### _generate_openai(self, text: str, model: str, normalize: bool) → list[float]

Generate embedding using OpenAI API.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| model | str | - | - |
| normalize | bool | - | - |

**Returns**: `list[float]`


##### _generate_openai_batch(self, texts: list[str], model: str, normalize: bool, batch_size: int) → tuple[list[list[float]], int]

Generate embeddings using OpenAI API in batches.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| texts | list[str] | - | - |
| model | str | - | - |
| normalize | bool | - | - |
| batch_size | int | - | - |

**Returns**: `tuple[list[list[float]], int]`


##### _generate_voyage(self, text: str, model: str, normalize: bool) → list[float]

Generate embedding using Voyage AI API.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| model | str | - | - |
| normalize | bool | - | - |

**Returns**: `list[float]`


##### _generate_voyage_batch(self, texts: list[str], model: str, normalize: bool, batch_size: int) → tuple[list[list[float]], int]

Generate embeddings using Voyage AI API in batches.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| texts | list[str] | - | - |
| model | str | - | - |
| normalize | bool | - | - |
| batch_size | int | - | - |

**Returns**: `tuple[list[list[float]], int]`


##### _generate_sentence_transformer(self, text: str, model: str, normalize: bool) → list[float]

Generate embedding using sentence-transformers.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| model | str | - | - |
| normalize | bool | - | - |

**Returns**: `list[float]`


##### _generate_sentence_transformer_batch(self, texts: list[str], model: str, normalize: bool, batch_size: int) → tuple[list[list[float]], int]

Generate embeddings using sentence-transformers in batches.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| texts | list[str] | - | - |
| model | str | - | - |
| normalize | bool | - | - |
| batch_size | int | - | - |

**Returns**: `tuple[list[list[float]], int]`


##### _normalize(embedding: list[float]) → list[float]

Normalize embedding to unit length.

**Decorators**: `@staticmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| embedding | list[float] | - | - |

**Returns**: `list[float]`


##### compute_hash(text: str, model: str) → str

Compute cache key for text and model.

**Decorators**: `@staticmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| text | str | - | - |
| model | str | - | - |

**Returns**: `str`



