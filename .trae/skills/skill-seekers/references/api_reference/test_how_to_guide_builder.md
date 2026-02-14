# API Reference: test_how_to_guide_builder.py

**Language**: Python

**Source**: `tests\test_how_to_guide_builder.py`

---

## Classes

### TestWorkflowAnalyzer

Tests for WorkflowAnalyzer - Extract steps from workflows

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_python_workflow(self)

Test analysis of Python workflow with multiple steps

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_prerequisites(self)

Test detection of prerequisites from imports and fixtures

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_find_verification_points(self)

Test finding verification/assertion points in workflow

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_calculate_complexity(self)

Test complexity level calculation

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_extract_steps_python_ast(self)

Test Python AST-based step extraction

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_extract_steps_heuristic(self)

Test heuristic-based step extraction for non-Python languages

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestWorkflowGrouper

Tests for WorkflowGrouper - Group related workflows

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_group_by_file_path(self)

Test grouping workflows by file path

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_group_by_test_name(self)

Test grouping workflows by test name patterns

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_group_by_complexity(self)

Test grouping workflows by complexity level

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_group_by_ai_tutorial_group(self)

Test AI-based tutorial grouping (or fallback if no AI)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestGuideGenerator

Tests for GuideGenerator - Generate markdown guides

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_generate_guide_markdown(self)

Test generation of complete markdown guide

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_create_header(self)

Test header generation with metadata

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_create_steps_section(self)

Test steps section generation

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_create_complete_example(self)

Test complete example generation

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_create_index(self)

Test index generation for guide collection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestHowToGuideBuilder

Tests for HowToGuideBuilder - Main orchestrator

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### tearDown(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_extract_workflow_examples(self)

Test extraction of workflow examples from mixed examples

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_create_guide_from_workflows(self)

Test guide creation from grouped workflows

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_create_collection(self)

Test guide collection creation with metadata

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_save_guides_to_files(self)

Test saving guides to markdown files

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_build_guides_from_examples(self)

Test full guide building workflow

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestEndToEnd

End-to-end integration test

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### tearDown(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_full_workflow(self)

Test complete workflow from examples to guides

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestAIEnhancementIntegration

Tests for AI Enhancement integration with HowToGuideBuilder (C3.3)

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### tearDown(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_build_with_ai_enhancement_disabled(self)

Test building guides WITHOUT AI enhancement (backward compatibility)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_build_with_ai_enhancement_api_mode_mocked(self)

Test building guides WITH AI enhancement in API mode (mocked)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_build_with_ai_enhancement_local_mode_mocked(self)

Test building guides WITH AI enhancement in LOCAL mode (mocked)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_build_with_ai_enhancement_auto_mode(self)

Test building guides WITH AI enhancement in AUTO mode

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_graceful_fallback_when_ai_fails(self)

Test graceful fallback when AI enhancement fails

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestExpandedWorkflowDetection

Tests for expanded workflow detection (issue #242)

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_empty_examples_returns_empty_collection(self)

Test that empty examples returns valid empty GuideCollection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_non_workflow_examples_returns_empty_collection(self)

Test that non-workflow examples returns empty collection with diagnostics

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_workflow_example_detected(self)

Test that workflow category examples are detected

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_guide_collection_always_valid(self)

Test that GuideCollection is always returned, never None

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_heuristic_detection_4_assignments_3_calls(self)

Test heuristic detection: 4+ assignments and 3+ calls

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_new_workflow_keywords_detection(self)

Test that new workflow keywords are detected (issue #242)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_heuristic_does_not_match_simple_tests(self)

Test that simple tests don't match heuristic (< 4 assignments or < 3 calls)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_keyword_case_insensitive_matching(self)

Test that workflow keyword matching works regardless of case

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




## Functions

### mock_enhance_guide(guide_data)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| guide_data | None | - | - |

**Returns**: (none)



### mock_enhance_guide(guide_data)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| guide_data | None | - | - |

**Returns**: (none)



### mock_enhance_guide(guide_data)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| guide_data | None | - | - |

**Returns**: (none)


