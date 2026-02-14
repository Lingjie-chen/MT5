# API Reference: runner.py

**Language**: Python

**Source**: `src\skill_seekers\benchmark\runner.py`

---

## Classes

### BenchmarkRunner

Run and compare benchmarks.

Examples:
    runner = BenchmarkRunner()

    # Run single benchmark
    report = runner.run("scraping-v2", scraping_benchmark)

    # Compare with baseline
    comparison = runner.compare(
        baseline_path="benchmarks/v1.json",
        current_path="benchmarks/v2.json"
    )

    # Run suite
    reports = runner.run_suite({
        "scraping": scraping_benchmark,
        "embedding": embedding_benchmark,
    })

**Inherits from**: (none)

#### Methods

##### __init__(self, output_dir: Path | None = None)

Initialize runner.

Args:
    output_dir: Directory for benchmark results

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| output_dir | Path | None | None | - |


##### run(self, name: str, benchmark_func: Callable[[Benchmark], None], save: bool = True) → BenchmarkReport

Run single benchmark.

Args:
    name: Benchmark name
    benchmark_func: Function that performs benchmark
    save: Whether to save results

Returns:
    Benchmark report

Examples:
    def scraping_benchmark(bench):
        with bench.timer("scrape"):
            scrape_docs(config)

    report = runner.run("scraping-v2", scraping_benchmark)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| name | str | - | - |
| benchmark_func | Callable[[Benchmark], None] | - | - |
| save | bool | True | - |

**Returns**: `BenchmarkReport`


##### run_suite(self, benchmarks: dict[str, Callable[[Benchmark], None]], save: bool = True) → dict[str, BenchmarkReport]

Run multiple benchmarks.

Args:
    benchmarks: Dict of name -> benchmark function
    save: Whether to save results

Returns:
    Dict of name -> report

Examples:
    reports = runner.run_suite({
        "scraping": scraping_benchmark,
        "embedding": embedding_benchmark,
    })

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| benchmarks | dict[str, Callable[[Benchmark], None]] | - | - |
| save | bool | True | - |

**Returns**: `dict[str, BenchmarkReport]`


##### compare(self, baseline_path: Path, current_path: Path) → ComparisonReport

Compare two benchmark reports.

Args:
    baseline_path: Path to baseline report
    current_path: Path to current report

Returns:
    Comparison report

Examples:
    comparison = runner.compare(
        baseline_path=Path("benchmarks/v1.json"),
        current_path=Path("benchmarks/v2.json")
    )

    print(comparison.overall_improvement)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| baseline_path | Path | - | - |
| current_path | Path | - | - |

**Returns**: `ComparisonReport`


##### list_benchmarks(self) → list[dict[str, Any]]

List saved benchmarks.

Returns:
    List of benchmark metadata

Examples:
    benchmarks = runner.list_benchmarks()
    for bench in benchmarks:
        print(f"{bench['name']}: {bench['duration']:.1f}s")

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `list[dict[str, Any]]`


##### get_latest(self, name: str) → Path | None

Get path to latest benchmark with given name.

Args:
    name: Benchmark name

Returns:
    Path to latest report, or None

Examples:
    latest = runner.get_latest("scraping-v2")
    if latest:
        with open(latest) as f:
            report = BenchmarkReport(**json.load(f))

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| name | str | - | - |

**Returns**: `Path | None`


##### cleanup_old(self, keep_latest: int = 5)

Remove old benchmark files.

Args:
    keep_latest: Number of latest benchmarks to keep per name

Examples:
    runner.cleanup_old(keep_latest=3)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| keep_latest | int | 5 | - |



