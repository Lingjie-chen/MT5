# API Reference: test_quality_metrics.py

**Language**: Python

**Source**: `tests\test_quality_metrics.py`

---

## Functions

### complete_skill_dir()

Create complete skill directory.

**Returns**: (none)



### minimal_skill_dir()

Create minimal skill directory.

**Returns**: (none)



### test_completeness_full(complete_skill_dir)

Test completeness analysis with complete skill.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| complete_skill_dir | None | - | - |

**Returns**: (none)



### test_completeness_minimal(minimal_skill_dir)

Test completeness analysis with minimal skill.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| minimal_skill_dir | None | - | - |

**Returns**: (none)



### test_accuracy_clean()

Test accuracy analysis with clean content.

**Returns**: (none)



### test_accuracy_with_todos()

Test accuracy detects TODO markers.

**Returns**: (none)



### test_accuracy_with_placeholder()

Test accuracy detects placeholder text.

**Returns**: (none)



### test_coverage_high(complete_skill_dir)

Test coverage analysis with good coverage.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| complete_skill_dir | None | - | - |

**Returns**: (none)



### test_coverage_low()

Test coverage analysis with low coverage.

**Returns**: (none)



### test_health_good()

Test health analysis with healthy skill.

**Returns**: (none)



### test_health_empty_files()

Test health detects empty files.

**Returns**: (none)



### test_calculate_statistics(complete_skill_dir)

Test statistics calculation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| complete_skill_dir | None | - | - |

**Returns**: (none)



### test_overall_score_calculation()

Test overall score calculation.

**Returns**: (none)



### test_grade_assignment()

Test grade assignment based on score.

**Returns**: (none)



### test_generate_recommendations()

Test recommendation generation.

**Returns**: (none)



### test_generate_report(complete_skill_dir)

Test full report generation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| complete_skill_dir | None | - | - |

**Returns**: (none)



### test_format_report(complete_skill_dir)

Test report formatting.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| complete_skill_dir | None | - | - |

**Returns**: (none)



### test_metric_levels()

Test metric level assignment.

**Returns**: (none)



### test_empty_skill_directory()

Test handling empty skill directory.

**Returns**: (none)



### test_metric_suggestions()

Test metrics include suggestions.

**Returns**: (none)


