# API Reference: test_adaptor_benchmarks.py

**Language**: Python

**Source**: `tests\test_adaptor_benchmarks.py`

---

## Classes

### TestAdaptorBenchmarks

Performance benchmark suite for adaptors

**Inherits from**: unittest.TestCase

#### Methods

##### setUp(self)

Set up test environment

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### tearDown(self)

Clean up

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _create_skill_with_n_references(self, n: int, skill_name: str = 'benchmark') → Path

Create a skill directory with N reference files.

Args:
    n: Number of reference files to create
    skill_name: Name of the skill

Returns:
    Path to skill directory

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| n | int | - | - |
| skill_name | str | 'benchmark' | - |

**Returns**: `Path`


##### test_benchmark_format_skill_md_all_adaptors(self)

Benchmark format_skill_md across all adaptors

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_benchmark_package_operations(self)

Benchmark complete package operation

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_benchmark_scaling_with_reference_count(self)

Test how performance scales with reference count

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_benchmark_json_vs_zip_size_comparison(self)

Compare output sizes: JSON vs ZIP/tar.gz

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_benchmark_metadata_overhead(self)

Measure metadata processing overhead

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_benchmark_empty_vs_full_skill(self)

Compare performance: empty skill vs full skill

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |



