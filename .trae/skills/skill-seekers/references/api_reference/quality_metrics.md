# API Reference: quality_metrics.py

**Language**: Python

**Source**: `src\skill_seekers\cli\quality_metrics.py`

---

## Classes

### MetricLevel

Metric severity level.

**Inherits from**: Enum



### QualityMetric

Individual quality metric.

**Inherits from**: (none)



### QualityScore

Overall quality score.

**Inherits from**: (none)



### QualityReport

Complete quality report.

**Inherits from**: (none)



### QualityAnalyzer

Analyze skill quality across multiple dimensions.

Provides comprehensive quality assessment and reporting.

**Inherits from**: (none)

#### Methods

##### __init__(self, skill_dir: Path)

Initialize quality analyzer.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| skill_dir | Path | - | - |


##### analyze_completeness(self) → float

Analyze skill completeness.

Checks for:
- SKILL.md exists and has content
- References directory exists
- Minimum documentation coverage

Returns:
    Completeness score (0-100)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `float`


##### analyze_accuracy(self) → float

Analyze skill accuracy.

Checks for:
- No broken links
- Valid JSON/YAML
- Consistent metadata
- No duplicate content

Returns:
    Accuracy score (0-100)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `float`


##### analyze_coverage(self) → float

Analyze documentation coverage.

Checks for:
- Multiple document types
- Code examples
- API references
- Getting started guide

Returns:
    Coverage score (0-100)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `float`


##### analyze_health(self) → float

Analyze skill health.

Checks for:
- File sizes reasonable
- No empty files
- Recent updates
- Proper structure

Returns:
    Health score (0-100)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `float`


##### calculate_statistics(self) → dict[str, Any]

Calculate skill statistics.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `dict[str, Any]`


##### calculate_overall_score(self, completeness: float, accuracy: float, coverage: float, health: float) → QualityScore

Calculate overall quality score.

Weighted average:
- Completeness: 30%
- Accuracy: 25%
- Coverage: 25%
- Health: 20%

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| completeness | float | - | - |
| accuracy | float | - | - |
| coverage | float | - | - |
| health | float | - | - |

**Returns**: `QualityScore`


##### generate_recommendations(self, score: QualityScore) → list[str]

Generate improvement recommendations.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| score | QualityScore | - | - |

**Returns**: `list[str]`


##### generate_report(self) → QualityReport

Generate comprehensive quality report.

Returns:
    Complete quality report

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `QualityReport`


##### format_report(self, report: QualityReport) → str

Format report as human-readable text.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| report | QualityReport | - | - |

**Returns**: `str`




## Functions

### main()

CLI entry point for quality metrics.

**Returns**: (none)


