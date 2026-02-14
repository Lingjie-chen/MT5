# API Reference: 2_upload_to_weaviate.py

**Language**: Python

**Source**: `examples\weaviate-example\2_upload_to_weaviate.py`

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



### load_skill_data(filepath: str = 'output/react-weaviate.json')

Load the Weaviate-format skill JSON.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| filepath | str | 'output/react-weaviate.json' | - |

**Returns**: (none)



### create_schema(client, schema: dict)

Create Weaviate schema (class + properties).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| client | None | - | - |
| schema | dict | - | - |

**Returns**: (none)



### upload_objects(client, class_name: str, objects: list)

Batch upload objects to Weaviate.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| client | None | - | - |
| class_name | str | - | - |
| objects | list | - | - |

**Returns**: (none)



### verify_upload(client, class_name: str)

Verify objects were uploaded correctly.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| client | None | - | - |
| class_name | str | - | - |

**Returns**: (none)



### main()

**Returns**: (none)


