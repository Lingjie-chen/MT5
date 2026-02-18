# API Reference: test_analyze_e2e.py

**Language**: Python

**Source**: `tests\test_analyze_e2e.py`

---

## Classes

### TestAnalyzeCommandE2E

End-to-end tests for skill-seekers analyze command.

**Inherits from**: unittest.TestCase

#### Methods

##### setUpClass(cls)

Set up test fixtures once for all tests.

**Decorators**: `@classmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| cls | None | - | - |


##### tearDownClass(cls)

Clean up test directory.

**Decorators**: `@classmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| cls | None | - | - |


##### create_sample_codebase(cls)

Create a sample Python codebase for testing.

**Decorators**: `@classmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| cls | None | - | - |


##### run_command(self)

Run skill-seekers command and return result.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_help_shows_command(self)

Test that analyze command appears in main help.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_subcommand_help(self)

Test that analyze subcommand has proper help.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_quick_preset(self)

Test quick analysis preset (real execution).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_with_custom_output(self)

Test analysis with custom output directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_skip_flags_work(self)

Test that skip flags are properly handled.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_invalid_directory(self)

Test analysis with non-existent directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_missing_directory_arg(self)

Test that --directory is required.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_backward_compatibility_depth_flag(self)

Test that old --depth flag still works.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_generates_references(self)

Test that references directory is created.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_output_structure(self)

Test that output has expected structure.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestAnalyzeOldCommand

Test that old skill-seekers-codebase command still works.

**Inherits from**: unittest.TestCase

#### Methods

##### test_old_command_still_exists(self)

Test that skill-seekers-codebase still exists.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestAnalyzeIntegration

Integration tests for analyze command with other features.

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

Set up test directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### tearDown(self)

Clean up test directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_then_check_output(self)

Test analyzing and verifying output can be read.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_verbose_flag(self)

Test that verbose flag works.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |



