# API Reference: 3_query_example.py

**Language**: Python

**Source**: `examples\weaviate-example\3_query_example.py`

---

## Functions

### connect_to_weaviate(url: str, api_key: str = None)

Connect to Weaviate instance.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| url | str | - | - |
| api_key | str | None | - |

**Returns**: (none)



### hybrid_search_example(client, class_name: str = 'React')

Example 1: Hybrid Search (keyword + vector).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| client | None | - | - |
| class_name | str | 'React' | - |

**Returns**: (none)



### keyword_only_search(client, class_name: str = 'React')

Example 2: Keyword-Only Search (alpha=0).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| client | None | - | - |
| class_name | str | 'React' | - |

**Returns**: (none)



### filtered_search(client, class_name: str = 'React')

Example 3: Search with Metadata Filter.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| client | None | - | - |
| class_name | str | 'React' | - |

**Returns**: (none)



### semantic_search(client, class_name: str = 'React')

Example 4: Pure Semantic Search (alpha=1).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| client | None | - | - |
| class_name | str | 'React' | - |

**Returns**: (none)



### get_statistics(client, class_name: str = 'React')

Show database statistics.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| client | None | - | - |
| class_name | str | 'React' | - |

**Returns**: (none)



### main()

**Returns**: (none)


