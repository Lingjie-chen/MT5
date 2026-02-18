# API Reference: test_analyze_command.py

**Language**: Python

**Source**: `tests\test_analyze_command.py`

---

## Classes

### TestAnalyzeSubcommand

Test analyze subcommand registration and argument parsing.

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

Create parser for testing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_subcommand_exists(self)

Test that analyze subcommand is registered.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_with_output_directory(self)

Test analyze with custom output directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_quick_preset_flag(self)

Test --quick preset flag parsing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_comprehensive_preset_flag(self)

Test --comprehensive preset flag parsing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_quick_and_comprehensive_mutually_exclusive(self)

Test that both flags can be parsed (mutual exclusion enforced at runtime).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_enhance_flag(self)

Test --enhance flag parsing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_skip_flags_passed_through(self)

Test that skip flags are recognized.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_all_skip_flags(self)

Test all skip flags are properly parsed.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_backward_compatible_depth_flag(self)

Test that deprecated --depth flag still works.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_depth_flag_choices(self)

Test that depth flag accepts correct values.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_languages_flag(self)

Test languages flag parsing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_file_patterns_flag(self)

Test file patterns flag parsing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_no_comments_flag(self)

Test no-comments flag parsing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_verbose_flag(self)

Test verbose flag parsing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_complex_command_combination(self)

Test complex command with multiple flags.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_directory_is_required(self)

Test that directory argument is required.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_default_output_directory(self)

Test default output directory value.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestAnalyzePresetBehavior

Test preset flag behavior and argument transformation.

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

Create parser for testing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_quick_preset_implies_surface_depth(self)

Test that --quick preset should trigger surface depth.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_comprehensive_preset_implies_full_depth(self)

Test that --comprehensive preset should trigger full depth.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_enhance_flag_standalone(self)

Test --enhance flag can be used without presets.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |



