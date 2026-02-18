# API Reference: codebase_scraper.py

**Language**: Python

**Source**: `src\skill_seekers\cli\codebase_scraper.py`

---

## Functions

### detect_language(file_path: Path) → str

Detect programming language from file extension.

Args:
    file_path: Path to source file

Returns:
    Language name or 'Unknown'

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| file_path | Path | - | - |

**Returns**: `str`



### load_gitignore(directory: Path) → pathspec.PathSpec | None

Load .gitignore file and create pathspec matcher.

Args:
    directory: Root directory to search for .gitignore

Returns:
    PathSpec object if .gitignore found, None otherwise

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| directory | Path | - | - |

**Returns**: `pathspec.PathSpec | None`



### should_exclude_dir(dir_name: str, excluded_dirs: set) → bool

Check if directory should be excluded from analysis.

Args:
    dir_name: Directory name
    excluded_dirs: Set of directory names to exclude

Returns:
    True if directory should be excluded

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| dir_name | str | - | - |
| excluded_dirs | set | - | - |

**Returns**: `bool`



### walk_directory(root: Path, patterns: list[str] | None = None, gitignore_spec: pathspec.PathSpec | None = None, excluded_dirs: set | None = None) → list[Path]

Walk directory tree and collect source files.

Args:
    root: Root directory to walk
    patterns: Optional file patterns to include (e.g., ['*.py', '*.js'])
    gitignore_spec: Optional PathSpec object for .gitignore rules
    excluded_dirs: Set of directory names to exclude

Returns:
    List of source file paths

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| root | Path | - | - |
| patterns | list[str] | None | None | - |
| gitignore_spec | pathspec.PathSpec | None | None | - |
| excluded_dirs | set | None | None | - |

**Returns**: `list[Path]`



### walk_markdown_files(root: Path, gitignore_spec: pathspec.PathSpec | None = None, excluded_dirs: set | None = None) → list[Path]

Walk directory tree and collect markdown documentation files.

Args:
    root: Root directory to walk
    gitignore_spec: Optional PathSpec object for .gitignore rules
    excluded_dirs: Set of directory names to exclude

Returns:
    List of markdown file paths

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| root | Path | - | - |
| gitignore_spec | pathspec.PathSpec | None | None | - |
| excluded_dirs | set | None | None | - |

**Returns**: `list[Path]`



### categorize_markdown_file(file_path: Path, root: Path) → str

Categorize a markdown file based on its location and filename.

Args:
    file_path: Path to the markdown file
    root: Root directory of the project

Returns:
    Category name (e.g., 'overview', 'guides', 'architecture')

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| file_path | Path | - | - |
| root | Path | - | - |

**Returns**: `str`



### extract_markdown_structure(content: str) → dict[str, Any]

Extract structure from markdown content (headers, code blocks, links).

Args:
    content: Markdown file content

Returns:
    Dictionary with extracted structure

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| content | str | - | - |

**Returns**: `dict[str, Any]`



### generate_markdown_summary(content: str, structure: dict[str, Any], max_length: int = 500) → str

Generate a summary of markdown content.

Args:
    content: Full markdown content
    structure: Extracted structure from extract_markdown_structure()
    max_length: Maximum summary length

Returns:
    Summary string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| content | str | - | - |
| structure | dict[str, Any] | - | - |
| max_length | int | 500 | - |

**Returns**: `str`



### process_markdown_docs(directory: Path, output_dir: Path, depth: str = 'deep', gitignore_spec: pathspec.PathSpec | None = None, enhance_with_ai: bool = False, ai_mode: str = 'none') → dict[str, Any]

Process all markdown documentation files in a directory.

Args:
    directory: Root directory to scan
    output_dir: Output directory for processed docs
    depth: Processing depth ('surface', 'deep', 'full')
    gitignore_spec: Optional .gitignore spec
    enhance_with_ai: Whether to use AI enhancement
    ai_mode: AI mode ('none', 'auto', 'api', 'local')

Returns:
    Dictionary with processed documentation data

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| directory | Path | - | - |
| output_dir | Path | - | - |
| depth | str | 'deep' | - |
| gitignore_spec | pathspec.PathSpec | None | None | - |
| enhance_with_ai | bool | False | - |
| ai_mode | str | 'none' | - |

**Returns**: `dict[str, Any]`



### _enhance_docs_with_ai(docs: list[dict], ai_mode: str) → list[dict]

Enhance documentation analysis with AI.

Args:
    docs: List of processed document dictionaries
    ai_mode: AI mode ('api' or 'local')

Returns:
    Enhanced document list

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| docs | list[dict] | - | - |
| ai_mode | str | - | - |

**Returns**: `list[dict]`



### _enhance_docs_api(docs: list[dict], api_key: str) → list[dict]

Enhance docs using Claude API.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| docs | list[dict] | - | - |
| api_key | str | - | - |

**Returns**: `list[dict]`



### _enhance_docs_local(docs: list[dict]) → list[dict]

Enhance docs using Claude Code CLI (LOCAL mode).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| docs | list[dict] | - | - |

**Returns**: `list[dict]`



### analyze_codebase(directory: Path, output_dir: Path, depth: str = 'deep', languages: list[str] | None = None, file_patterns: list[str] | None = None, build_api_reference: bool = True, extract_comments: bool = True, build_dependency_graph: bool = True, detect_patterns: bool = True, extract_test_examples: bool = True, build_how_to_guides: bool = True, extract_config_patterns: bool = True, extract_docs: bool = True, enhance_level: int = 0) → dict[str, Any]

Analyze local codebase and extract code knowledge.

Args:
    directory: Directory to analyze
    output_dir: Output directory for results
    depth: Analysis depth (surface, deep, full)
    languages: Optional list of languages to analyze
    file_patterns: Optional file patterns to include
    build_api_reference: Generate API reference markdown
    extract_comments: Extract inline comments
    build_dependency_graph: Generate dependency graph and detect circular dependencies
    detect_patterns: Detect design patterns (Singleton, Factory, Observer, etc.)
    extract_test_examples: Extract usage examples from test files
    build_how_to_guides: Build how-to guides from workflow examples (C3.3)
    extract_config_patterns: Extract configuration patterns from config files (C3.4)
    extract_docs: Extract and process markdown documentation files (default: True)
    enhance_level: AI enhancement level (0=off, 1=SKILL.md only, 2=+config+arch+docs, 3=full)

Returns:
    Analysis results dictionary

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| directory | Path | - | - |
| output_dir | Path | - | - |
| depth | str | 'deep' | - |
| languages | list[str] | None | None | - |
| file_patterns | list[str] | None | None | - |
| build_api_reference | bool | True | - |
| extract_comments | bool | True | - |
| build_dependency_graph | bool | True | - |
| detect_patterns | bool | True | - |
| extract_test_examples | bool | True | - |
| build_how_to_guides | bool | True | - |
| extract_config_patterns | bool | True | - |
| extract_docs | bool | True | - |
| enhance_level | int | 0 | - |

**Returns**: `dict[str, Any]`



### _generate_skill_md(output_dir: Path, directory: Path, results: dict[str, Any], depth: str, build_api_reference: bool, build_dependency_graph: bool, detect_patterns: bool, extract_test_examples: bool, extract_config_patterns: bool, extract_docs: bool = True, docs_data: dict[str, Any] | None = None)

Generate rich SKILL.md from codebase analysis results.

Creates a 300+ line skill file with:
- Front matter (name, description)
- Repository info (path, languages, file count)
- When to Use section
- Quick Reference (patterns, languages, stats)
- Code Examples (from test files)
- API Reference (from code analysis)
- Architecture Overview
- Configuration Patterns
- Available References

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| output_dir | Path | - | - |
| directory | Path | - | - |
| results | dict[str, Any] | - | - |
| depth | str | - | - |
| build_api_reference | bool | - | - |
| build_dependency_graph | bool | - | - |
| detect_patterns | bool | - | - |
| extract_test_examples | bool | - | - |
| extract_config_patterns | bool | - | - |
| extract_docs | bool | True | - |
| docs_data | dict[str, Any] | None | None | - |

**Returns**: (none)



### _get_language_stats(files: list[dict]) → dict[str, int]

Count files by language from analysis results.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| files | list[dict] | - | - |

**Returns**: `dict[str, int]`



### _format_patterns_section(output_dir: Path) → str

Format design patterns section from patterns/detected_patterns.json.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| output_dir | Path | - | - |

**Returns**: `str`



### _format_examples_section(output_dir: Path) → str

Format code examples section from test_examples/test_examples.json.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| output_dir | Path | - | - |

**Returns**: `str`



### _format_api_section(output_dir: Path) → str

Format API reference section.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| output_dir | Path | - | - |

**Returns**: `str`



### _format_architecture_section(output_dir: Path) → str

Format architecture section from architecture/architectural_patterns.json.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| output_dir | Path | - | - |

**Returns**: `str`



### _format_config_section(output_dir: Path) → str

Format configuration patterns section.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| output_dir | Path | - | - |

**Returns**: `str`



### _format_signal_flow_section(output_dir: Path, results: dict[str, Any]) → str

Format signal flow analysis section (C3.10 - Godot projects).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| output_dir | Path | - | - |
| results | dict[str, Any] | - | - |

**Returns**: `str`



### _format_documentation_section(_output_dir: Path, docs_data: dict[str, Any]) → str

Format project documentation section from extracted markdown files.

Note: output_dir parameter is unused but kept for consistency with other _format_* functions.
Documentation data is provided via docs_data parameter.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| _output_dir | Path | - | - |
| docs_data | dict[str, Any] | - | - |

**Returns**: `str`



### _generate_references(output_dir: Path)

Generate references/ directory structure by symlinking analysis output.

Creates a clean references/ directory that links to all analysis outputs.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| output_dir | Path | - | - |

**Returns**: (none)



### _check_deprecated_flags(args)

Check for deprecated flags and show migration warnings.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| args | None | - | - |

**Returns**: (none)



### main()

Command-line interface for codebase analysis.

**Returns**: (none)


