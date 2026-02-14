# API Reference: test_qdrant_adaptor.py

**Language**: Python

**Source**: `tests\test_adaptors\test_qdrant_adaptor.py`

---

## Classes

### TestQdrantAdaptor

Test suite for QdrantAdaptor class.

**Inherits from**: (none)

#### Methods

##### test_adaptor_registration(self)

Test that Qdrant adaptor is registered.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_format_skill_md(self, tmp_path)

Test formatting SKILL.md as Qdrant points.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_package_creates_json(self, tmp_path)

Test packaging skill into JSON file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_package_output_filename(self, tmp_path)

Test package output filename generation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_upload_returns_message(self, tmp_path)

Test upload returns instructions (no actual upload).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_validate_api_key_returns_false(self)

Test that API key validation returns False (no API needed).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_get_env_var_name_returns_empty(self)

Test that env var name is QDRANT_API_KEY (optional for Qdrant Cloud).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_supports_enhancement_returns_false(self)

Test that enhancement is not supported.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_enhance_returns_false(self, tmp_path)

Test that enhance returns False.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_empty_skill_directory(self, tmp_path)

Test handling of empty skill directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_references_only(self, tmp_path)

Test skill with references but no SKILL.md.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |



