# API Reference: ai_enhancer.py

**Language**: Python

**Source**: `src\skill_seekers\cli\ai_enhancer.py`

---

## Classes

### AIAnalysis

AI analysis result for patterns or examples

**Inherits from**: (none)



### AIEnhancer

Base class for AI enhancement

**Inherits from**: (none)

#### Methods

##### __init__(self, api_key: str | None = None, enabled: bool = True, mode: str = 'auto')

Initialize AI enhancer.

Args:
    api_key: Anthropic API key (uses ANTHROPIC_API_KEY env if None)
    enabled: Enable AI enhancement (default: True)
    mode: Enhancement mode - "auto" (default), "api", or "local"
          - "auto": Use API if key available, otherwise fall back to LOCAL
          - "api": Force API mode (fails if no key)
          - "local": Use Claude Code CLI (no API key needed)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| api_key | str | None | None | - |
| enabled | bool | True | - |
| mode | str | 'auto' | - |


##### _check_claude_cli(self) → bool

Check if Claude Code CLI is available

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`


##### _call_claude(self, prompt: str, max_tokens: int = 1000) → str | None

Call Claude (API or LOCAL mode) with error handling

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |
| max_tokens | int | 1000 | - |

**Returns**: `str | None`


##### _call_claude_api(self, prompt: str, max_tokens: int = 1000) → str | None

Call Claude API

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |
| max_tokens | int | 1000 | - |

**Returns**: `str | None`


##### _call_claude_local(self, prompt: str) → str | None

Call Claude using LOCAL mode (Claude Code CLI)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |

**Returns**: `str | None`




### PatternEnhancer

Enhance design pattern detection with AI analysis

**Inherits from**: AIEnhancer

#### Methods

##### enhance_patterns(self, patterns: list[dict]) → list[dict]

Enhance detected patterns with AI analysis.

Args:
    patterns: List of detected pattern instances

Returns:
    Enhanced patterns with AI analysis

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| patterns | list[dict] | - | - |

**Returns**: `list[dict]`


##### _enhance_patterns_parallel(self, batches: list[list[dict]], workers: int) → list[dict]

Process pattern batches in parallel using ThreadPoolExecutor.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| batches | list[list[dict]] | - | - |
| workers | int | - | - |

**Returns**: `list[dict]`


##### _enhance_pattern_batch(self, patterns: list[dict]) → list[dict]

Enhance a batch of patterns

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| patterns | list[dict] | - | - |

**Returns**: `list[dict]`




### TestExampleEnhancer

Enhance test examples with AI analysis

**Inherits from**: AIEnhancer

#### Methods

##### enhance_examples(self, examples: list[dict]) → list[dict]

Enhance test examples with AI context and explanations.

Args:
    examples: List of extracted test examples

Returns:
    Enhanced examples with AI analysis

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| examples | list[dict] | - | - |

**Returns**: `list[dict]`


##### _enhance_examples_parallel(self, batches: list[list[dict]], workers: int) → list[dict]

Process example batches in parallel using ThreadPoolExecutor.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| batches | list[list[dict]] | - | - |
| workers | int | - | - |

**Returns**: `list[dict]`


##### _enhance_example_batch(self, examples: list[dict]) → list[dict]

Enhance a batch of examples

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| examples | list[dict] | - | - |

**Returns**: `list[dict]`


##### generate_tutorials(self, examples: list[dict]) → dict[str, list[dict]]

Group enhanced examples into tutorial sections.

Args:
    examples: Enhanced examples with AI analysis

Returns:
    Dictionary mapping tutorial groups to examples

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| examples | list[dict] | - | - |

**Returns**: `dict[str, list[dict]]`



