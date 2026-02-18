# API Reference: test_pdf_extractor.py

**Language**: Python

**Source**: `tests\test_pdf_extractor.py`

---

## Classes

### TestLanguageDetection

Test language detection with confidence scoring

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_python_with_confidence(self)

Test Python detection returns language and confidence

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_javascript_with_confidence(self)

Test JavaScript detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_cpp_with_confidence(self)

Test C++ detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_unknown_low_confidence(self)

Test unknown language returns low confidence

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_confidence_range(self)

Test confidence is always between 0 and 1

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_scss_with_confidence(self)

Test SCSS detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_dart_with_confidence(self)

Test Dart detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_scala_with_confidence(self)

Test Scala detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_sass_with_confidence(self)

Test SASS detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_elixir_with_confidence(self)

Test Elixir detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_lua_with_confidence(self)

Test Lua detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_perl_with_confidence(self)

Test Perl detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestSyntaxValidation

Test syntax validation for different languages

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_validate_python_valid(self)

Test valid Python syntax

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_validate_python_invalid_indentation(self)

Test invalid Python indentation

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_validate_python_unbalanced_brackets(self)

Test unbalanced brackets

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_validate_javascript_valid(self)

Test valid JavaScript syntax

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_validate_natural_language_fails(self)

Test natural language fails validation

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestQualityScoring

Test code quality scoring (0-10 scale)

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_quality_score_range(self)

Test quality score is between 0 and 10

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_high_quality_code(self)

Test high-quality code gets good score

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_low_quality_code(self)

Test low-quality code gets low score

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_quality_factors(self)

Test that quality considers multiple factors

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestChapterDetection

Test chapter/section detection

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_chapter_with_number(self)

Test chapter detection with number

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_chapter_uppercase(self)

Test chapter detection with uppercase

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_detect_section_heading(self)

Test section heading detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_not_chapter(self)

Test normal text is not detected as chapter

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestCodeBlockMerging

Test code block merging across pages

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_merge_continued_blocks(self)

Test merging code blocks split across pages

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_no_merge_different_languages(self)

Test blocks with different languages are not merged

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestCodeDetectionMethods

Test different code detection methods

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_pattern_based_detection(self)

Test pattern-based code detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_indent_based_detection(self)

Test indent-based code detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestQualityFiltering

Test quality-based filtering

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_filter_by_min_quality(self)

Test filtering code blocks by minimum quality

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestMarkdownExtractionFallback

Test markdown extraction fallback behavior for issue #267

**Inherits from**: unittest.TestCase

#### Methods

##### test_exception_types_in_fallback(self)

Test that fallback handles various exception types

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_fallback_text_extraction_logic(self)

Test that text extraction fallback produces valid output

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_markdown_fallback_on_assertion_error(self)

Test that AssertionError triggers fallback to text extraction

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_markdown_fallback_on_runtime_error(self)

Test that RuntimeError triggers fallback to text extraction

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_markdown_fallback_on_type_error(self)

Test that TypeError triggers fallback to text extraction

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_markdown_fallback_preserves_content_quality(self)

Test that fallback text extraction preserves content structure

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |



