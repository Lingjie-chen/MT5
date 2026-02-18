# API Reference: framework.py

**Language**: Python

**Source**: `src\skill_seekers\benchmark\framework.py`

---

## Classes

### BenchmarkResult

Stores benchmark results during execution.

Examples:
    result = BenchmarkResult("test-benchmark")
    result.add_timing(...)
    result.add_memory(...)
    report = result.to_report()

**Inherits from**: (none)

#### Methods

##### __init__(self, name: str)

Initialize result collector.

Args:
    name: Benchmark name

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| name | str | - | - |


##### add_timing(self, result: TimingResult)

Add timing result.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| result | TimingResult | - | - |


##### add_memory(self, usage: MemoryUsage)

Add memory usage.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| usage | MemoryUsage | - | - |


##### add_metric(self, metric: Metric)

Add custom metric.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| metric | Metric | - | - |


##### add_recommendation(self, text: str)

Add optimization recommendation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |


##### set_system_info(self)

Collect system information.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### to_report(self) → BenchmarkReport

Generate final report.

Returns:
    Complete benchmark report

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `BenchmarkReport`




### Benchmark

Main benchmarking interface.

Provides context managers and decorators for timing and profiling.

Examples:
    # Create benchmark
    benchmark = Benchmark("scraping-test")

    # Time operations
    with benchmark.timer("scrape_pages"):
        scrape_docs(config)

    # Track memory
    with benchmark.memory("process_data"):
        process_large_dataset()

    # Generate report
    report = benchmark.report()
    print(report.summary)

**Inherits from**: (none)

#### Methods

##### __init__(self, name: str)

Initialize benchmark.

Args:
    name: Benchmark name

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| name | str | - | - |


##### timer(self, operation: str, iterations: int = 1)

Time an operation.

Args:
    operation: Operation name
    iterations: Number of iterations (for averaging)

Yields:
    None

Examples:
    with benchmark.timer("load_pages"):
        load_all_pages()

**Decorators**: `@contextmanager`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| operation | str | - | - |
| iterations | int | 1 | - |


##### memory(self, operation: str)

Track memory usage.

Args:
    operation: Operation name

Yields:
    None

Examples:
    with benchmark.memory("embed_docs"):
        generate_embeddings()

**Decorators**: `@contextmanager`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| operation | str | - | - |


##### measure(self, func: Callable) → Any

Measure function execution.

Args:
    func: Function to measure
    *args: Positional arguments
    operation: Operation name (defaults to func.__name__)
    track_memory: Whether to track memory
    **kwargs: Keyword arguments

Returns:
    Function result

Examples:
    result = benchmark.measure(
        scrape_all,
        config,
        operation="scrape_docs",
        track_memory=True
    )

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| func | Callable | - | - |

**Returns**: `Any`


##### timed(self, operation: str | None = None, track_memory: bool = False)

Decorator for timing functions.

Args:
    operation: Operation name (defaults to func.__name__)
    track_memory: Whether to track memory

Returns:
    Decorated function

Examples:
    @benchmark.timed("load_config")
    def load_config(path):
        return json.load(open(path))

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| operation | str | None | None | - |
| track_memory | bool | False | - |


##### metric(self, name: str, value: float, unit: str)

Record custom metric.

Args:
    name: Metric name
    value: Metric value
    unit: Unit of measurement

Examples:
    benchmark.metric("pages_per_sec", 12.5, "pages/sec")

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| name | str | - | - |
| value | float | - | - |
| unit | str | - | - |


##### recommend(self, text: str)

Add optimization recommendation.

Args:
    text: Recommendation text

Examples:
    if duration > 5.0:
        benchmark.recommend("Consider caching results")

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |


##### report(self) → BenchmarkReport

Generate final report.

Returns:
    Complete benchmark report

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `BenchmarkReport`


##### save(self, path: Path)

Save report to JSON file.

Args:
    path: Output file path

Examples:
    benchmark.save(Path("benchmarks/scraping_v2.json"))

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| path | Path | - | - |


##### analyze(self)

Analyze results and generate recommendations.

Automatically called by report(), but can be called manually.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




## Functions

### decorator(func: Callable) → Callable

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| func | Callable | - | - |

**Returns**: `Callable`



### wrapper()

**Returns**: (none)


