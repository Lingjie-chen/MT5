# API Reference: test_incremental_updates.py

**Language**: Python

**Source**: `tests\test_incremental_updates.py`

---

## Functions

### temp_skill_dir()

Create temporary skill directory for testing.

**Returns**: (none)



### test_initial_scan_all_added(temp_skill_dir)

Test first scan treats all files as added.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_no_changes_after_save(temp_skill_dir)

Test no changes detected after saving versions.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_detect_modified_file(temp_skill_dir)

Test detection of modified files.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_detect_added_file(temp_skill_dir)

Test detection of new files.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_detect_deleted_file(temp_skill_dir)

Test detection of deleted files.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_mixed_changes(temp_skill_dir)

Test detection of multiple types of changes.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_generate_update_package(temp_skill_dir)

Test update package generation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_diff_report_generation(temp_skill_dir)

Test diff report generation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_version_increment(temp_skill_dir)

Test version numbers increment correctly.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_apply_update_package(temp_skill_dir)

Test applying an update package.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_content_hash_consistency(temp_skill_dir)

Test content hash is consistent for same content.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| temp_skill_dir | None | - | - |

**Returns**: (none)



### test_empty_skill_directory()

Test handling empty skill directory.

**Returns**: (none)


