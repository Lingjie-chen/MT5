# API Reference: multilang_support.py

**Language**: Python

**Source**: `src\skill_seekers\cli\multilang_support.py`

---

## Classes

### LanguageInfo

Language information for a document.

**Inherits from**: (none)



### TranslationStatus

Translation status for a document.

**Inherits from**: (none)



### LanguageDetector

Detect document language using heuristics.

Uses character patterns, common words, and script detection.

**Inherits from**: (none)

#### Methods

##### detect(self, text: str, sample_size: int = 2000) → LanguageInfo

Detect language of text.

Args:
    text: Text to analyze
    sample_size: Number of characters to sample

Returns:
    LanguageInfo with detected language

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| sample_size | int | 2000 | - |

**Returns**: `LanguageInfo`


##### detect_from_filename(self, filename: str) → str | None

Detect language from filename pattern.

Supports patterns like:
- file.en.md
- file_en.md
- en/file.md
- file-en.md

Args:
    filename: Filename to analyze

Returns:
    ISO 639-1 language code or None

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| filename | str | - | - |

**Returns**: `str | None`




### MultiLanguageManager

Manages multi-language documentation structure.

Organizes documents by language and tracks translations.

**Inherits from**: (none)

#### Methods

##### __init__(self)

Initialize multi-language manager.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### add_document(self, file_path: str, content: str, metadata: dict | None = None, force_language: str | None = None) → None

Add document with language detection.

Args:
    file_path: Path to document
    content: Document content
    metadata: Additional metadata
    force_language: Override language detection

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| file_path | str | - | - |
| content | str | - | - |
| metadata | dict | None | None | - |
| force_language | str | None | None | - |

**Returns**: `None`


##### get_languages(self) → list[str]

Get list of detected languages.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `list[str]`


##### get_document_count(self, language: str | None = None) → int

Get document count for a language.

Args:
    language: Language code (None for all)

Returns:
    Number of documents

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| language | str | None | None | - |

**Returns**: `int`


##### get_translation_status(self, base_language: str | None = None) → TranslationStatus

Get translation status.

Args:
    base_language: Base language (None for primary)

Returns:
    Translation status summary

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| base_language | str | None | None | - |

**Returns**: `TranslationStatus`


##### export_by_language(self, output_dir: Path) → dict[str, Path]

Export documents organized by language.

Args:
    output_dir: Output directory

Returns:
    Dictionary mapping language codes to output paths

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| output_dir | Path | - | - |

**Returns**: `dict[str, Path]`


##### generate_translation_report(self) → str

Generate human-readable translation report.

Returns:
    Formatted report string

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`




## Functions

### main()

CLI entry point for multi-language support.

**Returns**: (none)


