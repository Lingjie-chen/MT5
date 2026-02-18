# API Reference: test_url_conversion.py

**Language**: Python

**Source**: `tests\test_url_conversion.py`

---

## Classes

### TestConvertToMdUrls

Test suite for _convert_to_md_urls method

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

Set up test converter instance

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_strips_anchor_fragments(self)

Test that anchor fragments (#anchor) are properly stripped from URLs

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_deduplicates_multiple_anchors_same_url(self)

Test that multiple anchors on the same URL are deduplicated

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_preserves_md_extension_urls(self)

Test that URLs already ending with .md are preserved

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_md_extension_with_anchor_fragments(self)

Test that .md URLs with anchors are handled correctly

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_does_not_match_md_in_path(self)

Test that URLs containing 'md' in path (but not ending with .md) are converted

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_removes_trailing_slashes(self)

Test that trailing slashes are removed before appending /index.html.md

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_mixed_urls_with_and_without_anchors(self)

Test mixed URLs with various formats

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_empty_url_list(self)

Test that empty URL list returns empty result

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_real_world_mikro_orm_case(self)

Test the exact URLs from issue #277 (MikroORM case)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_preserves_query_parameters(self)

Test that query parameters are preserved (only anchors stripped)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_complex_anchor_formats(self)

Test various anchor formats (encoded, with dashes, etc.)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_url_order_preservation(self)

Test that first occurrence of base URL is preserved

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |



