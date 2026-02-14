# API Reference: 2_upload_to_chroma.py

**Language**: Python

**Source**: `examples\chroma-example\2_upload_to_chroma.py`

---

## Functions

### create_client(persist_directory: str = None)

Create ChromaDB client.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| persist_directory | str | None | - |

**Returns**: (none)



### load_skill_data(filepath: str = 'output/vue-chroma.json')

Load the ChromaDB-format skill JSON.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| filepath | str | 'output/vue-chroma.json' | - |

**Returns**: (none)



### create_collection(client, collection_name: str, reset: bool = False)

Create ChromaDB collection.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| client | None | - | - |
| collection_name | str | - | - |
| reset | bool | False | - |

**Returns**: (none)



### upload_documents(collection, data: dict)

Add documents to collection.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| collection | None | - | - |
| data | dict | - | - |

**Returns**: (none)



### verify_upload(collection)

Verify documents were uploaded correctly.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| collection | None | - | - |

**Returns**: (none)



### main()

**Returns**: (none)


