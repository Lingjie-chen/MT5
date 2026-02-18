# API Reference: test_config_fetcher.py

**Language**: Python

**Source**: `tests\test_config_fetcher.py`

---

## Classes

### TestFetchConfigFromApi

Tests for fetch_config_from_api function.

**Inherits from**: (none)

#### Methods

##### test_successful_fetch(self, mock_client_class, tmp_path)

Test successful config download from API.

**Decorators**: `@patch('skill_seekers.cli.config_fetcher.httpx.Client')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| mock_client_class | None | - | - |
| tmp_path | None | - | - |


##### test_config_not_found(self, mock_client_class)

Test handling of 404 response.

**Decorators**: `@patch('skill_seekers.cli.config_fetcher.httpx.Client')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| mock_client_class | None | - | - |


##### test_no_download_url(self, mock_client_class)

Test handling of missing download_url.

**Decorators**: `@patch('skill_seekers.cli.config_fetcher.httpx.Client')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| mock_client_class | None | - | - |


##### test_http_error(self, mock_client_class)

Test handling of HTTP errors.

**Decorators**: `@patch('skill_seekers.cli.config_fetcher.httpx.Client')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| mock_client_class | None | - | - |


##### test_json_decode_error(self, mock_client_class)

Test handling of invalid JSON response.

**Decorators**: `@patch('skill_seekers.cli.config_fetcher.httpx.Client')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| mock_client_class | None | - | - |


##### test_normalize_config_name(self, tmp_path)

Test config name normalization (remove .json, remove configs/ prefix).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |




### TestListAvailableConfigs

Tests for list_available_configs function.

**Inherits from**: (none)

#### Methods

##### test_successful_list(self, mock_client_class)

Test successful config listing.

**Decorators**: `@patch('skill_seekers.cli.config_fetcher.httpx.Client')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| mock_client_class | None | - | - |


##### test_category_filter(self, mock_client_class)

Test listing with category filter.

**Decorators**: `@patch('skill_seekers.cli.config_fetcher.httpx.Client')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| mock_client_class | None | - | - |


##### test_api_error(self, mock_client_class)

Test handling of API errors.

**Decorators**: `@patch('skill_seekers.cli.config_fetcher.httpx.Client')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| mock_client_class | None | - | - |




### TestResolveConfigPath

Tests for resolve_config_path function.

**Inherits from**: (none)

#### Methods

##### test_exact_path_exists(self, tmp_path)

Test resolution when exact path exists.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_with_configs_prefix(self, tmp_path)

Test resolution with configs/ prefix.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_auto_fetch_disabled(self)

Test that auto-fetch doesn't run when disabled.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_auto_fetch_enabled(self, mock_fetch, tmp_path)

Test that auto-fetch runs when enabled.

**Decorators**: `@patch('skill_seekers.cli.config_fetcher.fetch_config_from_api')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| mock_fetch | None | - | - |
| tmp_path | None | - | - |


##### test_auto_fetch_failed(self, mock_fetch)

Test handling when auto-fetch fails.

**Decorators**: `@patch('skill_seekers.cli.config_fetcher.fetch_config_from_api')`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| mock_fetch | None | - | - |


##### test_config_name_normalization(self, tmp_path)

Test various config name formats.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |




### TestConfigFetcherIntegration

Integration tests that hit real API (marked as integration).

**Inherits from**: (none)

#### Methods

##### test_fetch_real_config(self, tmp_path)

Test fetching a real config from API.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_list_real_configs(self)

Test listing real configs from API.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




## Functions

### get_side_effect(url)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| url | None | - | - |

**Returns**: (none)



### get_side_effect(url)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| url | None | - | - |

**Returns**: (none)


