# API Reference: signal_flow_analyzer.py

**Language**: Python

**Source**: `src\skill_seekers\cli\signal_flow_analyzer.py`

---

## Classes

### SignalFlowAnalyzer

Analyzes signal flow patterns in Godot projects.

**Inherits from**: (none)

#### Methods

##### __init__(self, analysis_results: dict[str, Any])

Initialize with code analysis results.

Args:
    analysis_results: Dict containing analyzed files with signal data

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| analysis_results | dict[str, Any] | - | - |


##### analyze(self) → dict[str, Any]

Perform signal flow analysis.

Returns:
    Dict containing signal flow analysis results

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `dict[str, Any]`


##### _extract_signals(self)

Extract all signal declarations.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _extract_connections(self)

Extract all signal connections (.connect() calls).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _extract_emissions(self)

Extract all signal emissions (.emit() calls).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _build_flow_chains(self)

Build signal flow chains (A emits -> B connects).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _detect_patterns(self)

Detect common signal usage patterns.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _calculate_statistics(self) → dict[str, Any]

Calculate signal usage statistics.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `dict[str, Any]`


##### generate_signal_flow_diagram(self) → str

Generate a Mermaid diagram of signal flow.

Returns:
    Mermaid diagram as string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### extract_signal_usage_patterns(self) → list[dict[str, Any]]

Extract common signal usage patterns for how-to guide generation.

Returns:
    List of signal usage patterns with connect/emit/handle examples

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `list[dict[str, Any]]`


##### generate_how_to_guides(self, output_dir: Path, ai_mode: str = 'LOCAL') → str

Generate signal-based how-to guides using AI.

Args:
    output_dir: Directory to save guides
    ai_mode: "LOCAL" (Claude Code) or "API" (Anthropic API)

Returns:
    Path to generated guide file

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| output_dir | Path | - | - |
| ai_mode | str | 'LOCAL' | - |

**Returns**: `str`


##### _generate_signal_guide(self, pattern: dict[str, Any], ai_mode: str) → str

Generate a how-to guide for a single signal using AI.

Args:
    pattern: Signal usage pattern data
    ai_mode: "LOCAL" or "API"

Returns:
    Markdown guide content

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| pattern | dict[str, Any] | - | - |
| ai_mode | str | - | - |

**Returns**: `str`


##### save_analysis(self, output_dir: Path, ai_mode: str = 'LOCAL')

Save signal flow analysis to files.

Args:
    output_dir: Directory to save analysis results

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| output_dir | Path | - | - |
| ai_mode | str | 'LOCAL' | - |


##### _generate_signal_reference(self, output_dir: Path, analysis: dict)

Generate human-readable signal reference.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| output_dir | Path | - | - |
| analysis | dict | - | - |



