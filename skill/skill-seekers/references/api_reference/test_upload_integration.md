# API Reference: test_upload_integration.py

**Language**: Python

**Source**: `tests\test_upload_integration.py`

---

## Classes

### TestChromaUploadBasics

Test ChromaDB upload basic functionality.

**Inherits from**: (none)

#### Methods

##### test_chroma_adaptor_exists(self)

Test that ChromaDB adaptor can be loaded.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_chroma_upload_without_chromadb_installed(self, sample_chroma_package)

Test upload fails gracefully without chromadb installed.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_chroma_package | None | - | - |


##### test_chroma_upload_api_signature(self, sample_chroma_package)

Test ChromaDB upload has correct API signature.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_chroma_package | None | - | - |




### TestWeaviateUploadBasics

Test Weaviate upload basic functionality.

**Inherits from**: (none)

#### Methods

##### test_weaviate_adaptor_exists(self)

Test that Weaviate adaptor can be loaded.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_weaviate_upload_without_weaviate_installed(self, sample_weaviate_package)

Test upload fails gracefully without weaviate-client installed.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_weaviate_package | None | - | - |


##### test_weaviate_upload_api_signature(self, sample_weaviate_package)

Test Weaviate upload has correct API signature.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_weaviate_package | None | - | - |




### TestPackageStructure

Test that packages are correctly structured for upload.

**Inherits from**: (none)

#### Methods

##### test_chroma_package_structure(self, sample_chroma_package)

Test ChromaDB package has required fields.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_chroma_package | None | - | - |


##### test_weaviate_package_structure(self, sample_weaviate_package)

Test Weaviate package has required fields.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| sample_weaviate_package | None | - | - |




### TestUploadCommandIntegration

Test upload command integration.

**Inherits from**: (none)

#### Methods

##### test_upload_skill_api_signature(self)

Test upload_skill_api has correct signature.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_upload_command_supports_chroma(self)

Test upload command recognizes chroma as target.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_upload_command_supports_weaviate(self)

Test upload command recognizes weaviate as target.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestErrorHandling

Test error handling in upload functionality.

**Inherits from**: (none)

#### Methods

##### test_chroma_handles_missing_file(self, tmp_path)

Test ChromaDB upload handles missing files gracefully.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_weaviate_handles_missing_file(self, tmp_path)

Test Weaviate upload handles missing files gracefully.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_chroma_handles_invalid_json(self, tmp_path)

Test ChromaDB upload handles invalid JSON gracefully.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_weaviate_handles_invalid_json(self, tmp_path)

Test Weaviate upload handles invalid JSON gracefully.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |




## Functions

### sample_chroma_package(tmp_path)

Create a sample ChromaDB package for testing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| tmp_path | None | - | - |

**Returns**: (none)



### sample_weaviate_package(tmp_path)

Create a sample Weaviate package for testing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| tmp_path | None | - | - |

**Returns**: (none)


