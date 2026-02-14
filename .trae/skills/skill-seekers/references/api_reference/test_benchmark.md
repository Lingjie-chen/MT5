# API Reference: test_benchmark.py

**Language**: Python

**Source**: `tests\test_benchmark.py`

---

## Classes

### TestBenchmarkResult

Test BenchmarkResult class.

**Inherits from**: (none)

#### Methods

##### test_result_initialization(self)

Test result initialization.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_add_timing(self)

Test adding timing result.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_add_memory(self)

Test adding memory usage.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_add_metric(self)

Test adding custom metric.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_add_recommendation(self)

Test adding recommendation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_set_system_info(self)

Test collecting system info.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_to_report(self)

Test report generation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestBenchmark

Test Benchmark class.

**Inherits from**: (none)

#### Methods

##### test_benchmark_initialization(self)

Test benchmark initialization.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_timer_context_manager(self)

Test timer context manager.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_timer_with_iterations(self)

Test timer with iterations.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_memory_context_manager(self)

Test memory context manager.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_measure_function(self)

Test measure function.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_measure_with_memory_tracking(self)

Test measure with memory tracking.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_timed_decorator(self)

Test timed decorator.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_timed_decorator_with_memory(self)

Test timed decorator with memory tracking.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_metric_recording(self)

Test metric recording.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_recommendation_recording(self)

Test recommendation recording.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_report_generation(self)

Test report generation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_save_report(self, tmp_path)

Test saving report to file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_analyze_bottlenecks(self)

Test bottleneck analysis.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_high_memory(self)

Test high memory usage detection.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestBenchmarkRunner

Test BenchmarkRunner class.

**Inherits from**: (none)

#### Methods

##### test_runner_initialization(self, tmp_path)

Test runner initialization.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_run_benchmark(self, tmp_path)

Test running single benchmark.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_run_benchmark_no_save(self, tmp_path)

Test running benchmark without saving.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_run_suite(self, tmp_path)

Test running benchmark suite.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_compare_benchmarks(self, tmp_path)

Test comparing benchmarks.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_list_benchmarks(self, tmp_path)

Test listing benchmarks.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_get_latest(self, tmp_path)

Test getting latest benchmark.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_get_latest_not_found(self, tmp_path)

Test getting latest when benchmark doesn't exist.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |


##### test_cleanup_old(self, tmp_path)

Test cleaning up old benchmarks.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| tmp_path | None | - | - |




### TestBenchmarkModels

Test benchmark model classes.

**Inherits from**: (none)

#### Methods

##### test_timing_result_model(self)

Test TimingResult model.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_memory_usage_model(self)

Test MemoryUsage model.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_metric_model(self)

Test Metric model.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_benchmark_report_summary(self)

Test BenchmarkReport summary property.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_comparison_report_has_regressions(self)

Test ComparisonReport has_regressions property.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_comparison_report_overall_improvement(self)

Test ComparisonReport overall_improvement property.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




## Functions

### slow_function(x)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| x | None | - | - |

**Returns**: (none)



### allocate_memory()

**Returns**: (none)



### my_function(x)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| x | None | - | - |

**Returns**: (none)



### allocate()

**Returns**: (none)



### test_benchmark(bench)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| bench | None | - | - |

**Returns**: (none)



### test_benchmark(bench)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| bench | None | - | - |

**Returns**: (none)



### bench1(bench)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| bench | None | - | - |

**Returns**: (none)



### bench2(bench)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| bench | None | - | - |

**Returns**: (none)



### baseline_bench(bench)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| bench | None | - | - |

**Returns**: (none)



### improved_bench(bench)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| bench | None | - | - |

**Returns**: (none)



### test_bench(bench)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| bench | None | - | - |

**Returns**: (none)



### test_bench(bench)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| bench | None | - | - |

**Returns**: (none)


