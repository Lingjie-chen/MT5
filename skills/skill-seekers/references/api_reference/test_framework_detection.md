# API Reference: test_framework_detection.py

**Language**: Python

**Source**: `tests\test_framework_detection.py`

---

## Classes

### TestFrameworkDetection

Tests for Issue #239 - Framework detection with import-only files

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

Create temporary directory for testing.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### tearDown(self)

Clean up temporary directory.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_flask_framework_detection_from_imports(self)

Test that Flask is detected from import statements (Issue #239).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_files_with_imports_are_included(self)

Test that files with only imports are included in analysis (Issue #239).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_no_false_positive_frameworks(self)

Test that framework detection doesn't produce false positives (Issue #239).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |



