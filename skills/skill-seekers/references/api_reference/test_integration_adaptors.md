# API Reference: test_integration_adaptors.py

**Language**: Python

**Source**: `tests\test_integration_adaptors.py`

---

## Classes

### TestWeaviateIntegration

Integration tests with real Weaviate instance.

**Inherits from**: (none)

#### Methods

##### test_complete_workflow_with_weaviate(self, sample_skill_dir, tmp_path)

Test: package → upload to Weaviate → query → verify.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_skill_dir | None | - | - |
| tmp_path | None | - | - |


##### test_weaviate_metadata_preservation(self, sample_skill_dir, tmp_path)

Test that metadata is correctly stored and retrieved.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_skill_dir | None | - | - |
| tmp_path | None | - | - |




### TestChromaIntegration

Integration tests with ChromaDB.

**Inherits from**: (none)

#### Methods

##### test_complete_workflow_with_chroma(self, sample_skill_dir, tmp_path)

Test: package → upload to Chroma → query → verify.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_skill_dir | None | - | - |
| tmp_path | None | - | - |


##### test_chroma_query_filtering(self, sample_skill_dir, tmp_path)

Test metadata filtering in ChromaDB queries.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_skill_dir | None | - | - |
| tmp_path | None | - | - |




### TestQdrantIntegration

Integration tests with Qdrant.

**Inherits from**: (none)

#### Methods

##### test_complete_workflow_with_qdrant(self, sample_skill_dir, tmp_path)

Test: package → upload to Qdrant → query → verify.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_skill_dir | None | - | - |
| tmp_path | None | - | - |


##### test_qdrant_payload_filtering(self, sample_skill_dir, tmp_path)

Test payload filtering in Qdrant.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_skill_dir | None | - | - |
| tmp_path | None | - | - |




## Functions

### sample_skill_dir(tmp_path)

Create a sample skill for integration testing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| tmp_path | None | - | - |

**Returns**: (none)



### check_service_available(url: str, timeout: int = 5) → bool

Check if a service is available.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| url | str | - | - |
| timeout | int | 5 | - |

**Returns**: `bool`


