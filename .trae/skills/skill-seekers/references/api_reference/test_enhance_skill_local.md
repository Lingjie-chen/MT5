# API Reference: test_enhance_skill_local.py

**Language**: Python

**Source**: `tests\test_enhance_skill_local.py`

---

## Classes

### TestMultiAgentSupport

Test multi-agent enhancement support.

**Inherits from**: (none)

#### Methods

##### test_agent_presets_structure(self)

Verify AGENT_PRESETS has required fields.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_build_agent_command_claude(self, tmp_path)

Test Claude Code command building.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_build_agent_command_codex(self, tmp_path)

Test Codex CLI command building.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_build_agent_command_custom_with_placeholder(self, tmp_path, monkeypatch)

Test custom command with {prompt_file} placeholder.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |
| monkeypatch | None | - | - |


##### test_custom_agent_requires_command(self, tmp_path)

Test custom agent fails without --agent-cmd.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_invalid_agent_name(self, tmp_path)

Test invalid agent name raises error.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_agent_normalization(self, tmp_path)

Test agent name normalization (aliases).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_environment_variable_agent(self, tmp_path, monkeypatch)

Test SKILL_SEEKER_AGENT environment variable.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |
| monkeypatch | None | - | - |


##### test_environment_variable_custom_command(self, tmp_path, monkeypatch)

Test SKILL_SEEKER_AGENT_CMD environment variable.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |
| monkeypatch | None | - | - |


##### test_rejects_command_with_semicolon(self, tmp_path)

Test rejection of commands with shell metacharacters.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_rejects_command_with_pipe(self, tmp_path)

Test rejection of commands with pipe.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_rejects_command_with_background_job(self, tmp_path)

Test rejection of commands with background job operator.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_rejects_missing_executable(self, tmp_path, monkeypatch)

Test rejection when executable is not found on PATH.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |
| monkeypatch | None | - | - |




## Functions

### _make_skill_dir(tmp_path)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| tmp_path | None | - | - |

**Returns**: (none)



### _allow_executable(monkeypatch, name = 'my-agent')

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| monkeypatch | None | - | - |
| name | None | 'my-agent' | - |

**Returns**: (none)


