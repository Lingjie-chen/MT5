# API Reference: test_preset_system.py

**Language**: Python

**Source**: `tests\test_preset_system.py`

---

## Classes

### TestPresetDefinitions

Test preset definitions are complete and valid.

**Inherits from**: (none)

#### Methods

##### test_all_presets_defined(self)

Test that all expected presets are defined.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_preset_structure(self)

Test that presets have correct structure.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_quick_preset(self)

Test quick preset configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_standard_preset(self)

Test standard preset configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_comprehensive_preset(self)

Test comprehensive preset configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestPresetManager

Test PresetManager functionality.

**Inherits from**: (none)

#### Methods

##### test_get_preset(self)

Test PresetManager.get_preset().

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_get_preset_invalid(self)

Test PresetManager.get_preset() with invalid name.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_list_presets(self)

Test PresetManager.list_presets().

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_format_preset_help(self)

Test PresetManager.format_preset_help().

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_get_default_preset(self)

Test PresetManager.get_default_preset().

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestPresetApplication

Test preset application logic.

**Inherits from**: (none)

#### Methods

##### test_apply_preset_quick(self)

Test applying quick preset.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_apply_preset_standard(self)

Test applying standard preset.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_apply_preset_comprehensive(self)

Test applying comprehensive preset.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_cli_overrides_preset(self)

Test that CLI args override preset defaults.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_apply_preset_preserves_args(self)

Test that apply_preset preserves existing args.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_apply_preset_invalid(self)

Test applying invalid preset raises error.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestDeprecationWarnings

Test deprecation warning functionality.

**Inherits from**: (none)

#### Methods

##### test_check_deprecated_flags_quick(self, capsys)

Test deprecation warning for --quick flag.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| capsys | None | - | - |


##### test_check_deprecated_flags_comprehensive(self, capsys)

Test deprecation warning for --comprehensive flag.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| capsys | None | - | - |


##### test_check_deprecated_flags_depth(self, capsys)

Test deprecation warning for --depth flag.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| capsys | None | - | - |


##### test_check_deprecated_flags_ai_mode(self, capsys)

Test deprecation warning for --ai-mode flag.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| capsys | None | - | - |


##### test_check_deprecated_flags_multiple(self, capsys)

Test deprecation warnings for multiple flags.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| capsys | None | - | - |


##### test_check_deprecated_flags_none(self, capsys)

Test no warnings when no deprecated flags used.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| capsys | None | - | - |




### TestBackwardCompatibility

Test backward compatibility with old flags.

**Inherits from**: (none)

#### Methods

##### test_old_flags_still_work(self)

Test that old flags still work (with warnings).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_preset_flag_preferred(self)

Test that --preset flag is the recommended way.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |



