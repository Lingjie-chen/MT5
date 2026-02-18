---
name: skill-seekers
description: Generate LLM skills from documentation, codebases, and GitHub repositories
---

# Skill Seekers

## Prerequisites

```bash
pip install skill-seekers
# Or: uv pip install skill-seekers
```

## Commands

| Source | Command |
|--------|---------|
| Local code | `skill-seekers analyze --directory ./path` |
| Docs URL | `skill-seekers scrape --url https://...` |
| GitHub | `skill-seekers github --repo owner/repo` |
| PDF | `skill-seekers pdf --file doc.pdf` |

## Quick Start

```bash
# Analyze local codebase
skill-seekers analyze --directory /path/to/project --output output/my-skill/

# Package for Claude
yes | skill-seekers package output/my-skill/ --no-open
```

## Options

| Flag | Description |
|------|-------------|
| `--depth surface/deep/full` | Analysis depth |
| `--skip-patterns` | Skip pattern detection |
| `--skip-test-examples` | Skip test extraction |
| `--ai-mode none/api/local` | AI enhancement |

---



# Skill_Seekers Codebase

## Description

Local codebase analysis and documentation generated from code analysis.

**Path:** `C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers`
**Files Analyzed:** 263
**Languages:** Python, TypeScript
**Analysis Depth:** deep

## When to Use This Skill

Use this skill when you need to:
- Understand the codebase architecture and design patterns
- Find implementation examples and usage patterns
- Review API documentation extracted from code
- Check configuration patterns and best practices
- Explore test examples and real-world usage
- Navigate the codebase structure efficiently

## ⚡ Quick Reference

### Codebase Statistics

**Languages:**
- **Python**: 261 files (99.2%)
- **TypeScript**: 2 files (0.8%)

**Analysis Performed:**
- ✅ API Reference (C2.5)
- ✅ Dependency Graph (C2.6)
- ✅ Design Patterns (C3.1)
- ✅ Test Examples (C3.2)
- ✅ Configuration Patterns (C3.4)
- ✅ Architectural Analysis (C3.7)
- ✅ Project Documentation (C3.9)

## 📝 Code Examples

*High-quality examples extracted from test files (C3.2)*

**Workflow: Test ScrapeParser has correct arguments.** (complexity: 1.00)

```python
'Test ScrapeParser has correct arguments.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers(dest='command')
scrape_parser = ScrapeParser()
scrape_parser.create_parser(subparsers)
args = main_parser.parse_args(['scrape', '--config', 'test.json'])
assert args.command == 'scrape'
assert args.config == 'test.json'
args = main_parser.parse_args(['scrape', '--config', 'test.json', '--max-pages', '100'])
assert args.max_pages == 100
args = main_parser.parse_args(['scrape', '--enhance'])
assert args.enhance is True
```

**Workflow: Test GitHubParser has correct arguments.** (complexity: 1.00)

```python
'Test GitHubParser has correct arguments.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers(dest='command')
github_parser = GitHubParser()
github_parser.create_parser(subparsers)
args = main_parser.parse_args(['github', '--repo', 'owner/repo'])
assert args.command == 'github'
assert args.repo == 'owner/repo'
args = main_parser.parse_args(['github', '--repo', 'owner/repo', '--non-interactive'])
assert args.non_interactive is True
```

**Workflow: Test PackageParser has correct arguments.** (complexity: 1.00)

```python
'Test PackageParser has correct arguments.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers(dest='command')
package_parser = PackageParser()
package_parser.create_parser(subparsers)
args = main_parser.parse_args(['package', 'output/test/'])
assert args.command == 'package'
assert args.skill_directory == 'output/test/'
args = main_parser.parse_args(['package', 'output/test/', '--target', 'gemini'])
assert args.target == 'gemini'
args = main_parser.parse_args(['package', 'output/test/', '--no-open'])
assert args.no_open is True
```

**Workflow: Test AnalyzeParser has correct arguments.** (complexity: 1.00)

```python
'Test AnalyzeParser has correct arguments.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers(dest='command')
from skill_seekers.cli.parsers.analyze_parser import AnalyzeParser
analyze_parser = AnalyzeParser()
analyze_parser.create_parser(subparsers)
args = main_parser.parse_args(['analyze', '--directory', '.'])
assert args.command == 'analyze'
assert args.directory == '.'
args = main_parser.parse_args(['analyze', '--directory', '.', '--quick'])
assert args.quick is True
args = main_parser.parse_args(['analyze', '--directory', '.', '--comprehensive'])
assert args.comprehensive is True
args = main_parser.parse_args(['analyze', '--directory', '.', '--skip-patterns'])
assert args.skip_patterns is True
```

**Workflow: Test that Flask is detected from import statements (Issue #239).** (complexity: 1.00)

```python
'Test that Flask is detected from import statements (Issue #239).'
app_dir = self.test_project / 'app'
app_dir.mkdir()
(app_dir / '__init__.py').write_text('from flask import Flask\napp = Flask(__name__)')
(app_dir / 'routes.py').write_text("from flask import render_template\nfrom app import app\n\n@app.route('/')\ndef index():\n    return render_template('index.html')\n")
from skill_seekers.cli.codebase_scraper import main as scraper_main
import sys
old_argv = sys.argv
try:
    sys.argv = ['skill-seekers-codebase', '--directory', str(self.test_project), '--output', str(self.output_dir), '--depth', 'deep', '--ai-mode', 'none', '--skip-patterns', '--skip-test-examples', '--skip-how-to-guides', '--skip-config-patterns', '--skip-docs']
    scraper_main()
finally:
    sys.argv = old_argv
arch_file = self.output_dir / 'references' / 'architecture' / 'architectural_patterns.json'
self.assertTrue(arch_file.exists(), 'Architecture file should be created')
with open(arch_file) as f:
    arch_data = json.load(f)
self.assertIn('frameworks_detected', arch_data)
self.assertIn('Flask', arch_data['frameworks_detected'], 'Flask should be detected from imports')
```

**Workflow: Test that files with only imports are included in analysis (Issue #239).** (complexity: 1.00)

```python
'Test that files with only imports are included in analysis (Issue #239).'
(self.test_project / 'imports_only.py').write_text('import django\nfrom flask import Flask\nimport requests')
from skill_seekers.cli.codebase_scraper import main as scraper_main
import sys
old_argv = sys.argv
try:
    sys.argv = ['skill-seekers-codebase', '--directory', str(self.test_project), '--output', str(self.output_dir), '--depth', 'deep', '--ai-mode', 'none']
    scraper_main()
finally:
    sys.argv = old_argv
code_analysis = self.output_dir / 'code_analysis.json'
self.assertTrue(code_analysis.exists(), 'Code analysis file should exist')
with open(code_analysis) as f:
    analysis_data = json.load(f)
self.assertGreater(len(analysis_data['files']), 0, 'Files with imports should be included')
import_file = next((f for f in analysis_data['files'] if 'imports_only.py' in f['file']), None)
self.assertIsNotNone(import_file, 'Import-only file should be in analysis')
self.assertIn('imports', import_file, 'Imports should be extracted')
self.assertGreater(len(import_file['imports']), 0, 'Should have captured imports')
self.assertIn('django', import_file['imports'], 'Django import should be captured')
self.assertIn('flask', import_file['imports'], 'Flask import should be captured')
```

**Workflow: Test that framework detection doesn't produce false positives (Issue #239).** (complexity: 1.00)

```python
"Test that framework detection doesn't produce false positives (Issue #239)."
app_dir = self.test_project / 'app'
app_dir.mkdir()
(app_dir / 'utils.py').write_text("def my_function():\n    return 'hello'\n")
from skill_seekers.cli.codebase_scraper import main as scraper_main
import sys
old_argv = sys.argv
try:
    sys.argv = ['skill-seekers-codebase', '--directory', str(self.test_project), '--output', str(self.output_dir), '--depth', 'deep', '--ai-mode', 'none']
    scraper_main()
finally:
    sys.argv = old_argv
arch_file = self.output_dir / 'references' / 'architecture' / 'architectural_patterns.json'
if arch_file.exists():
    with open(arch_file) as f:
        arch_data = json.load(f)
    frameworks = arch_data.get('frameworks_detected', [])
    self.assertNotIn('Flask', frameworks, 'Should not detect Flask without imports')
    for fw in ['ASP.NET', 'Rails', 'Laravel']:
        self.assertNotIn(fw, frameworks, f'Should not detect {fw} without real evidence')
```

**Workflow: Test that Flask is detected from import statements (Issue #239).** (complexity: 1.00)

```python
'Test that Flask is detected from import statements (Issue #239).'
app_dir = self.test_project / 'app'
app_dir.mkdir()
(app_dir / '__init__.py').write_text('from flask import Flask\napp = Flask(__name__)')
(app_dir / 'routes.py').write_text("from flask import render_template\nfrom app import app\n\n@app.route('/')\ndef index():\n    return render_template('index.html')\n")
from skill_seekers.cli.codebase_scraper import main as scraper_main
import sys
old_argv = sys.argv
try:
    sys.argv = ['skill-seekers-codebase', '--directory', str(self.test_project), '--output', str(self.output_dir), '--depth', 'deep', '--ai-mode', 'none', '--skip-patterns', '--skip-test-examples', '--skip-how-to-guides', '--skip-config-patterns', '--skip-docs']
    scraper_main()
finally:
    sys.argv = old_argv
arch_file = self.output_dir / 'references' / 'architecture' / 'architectural_patterns.json'
self.assertTrue(arch_file.exists(), 'Architecture file should be created')
with open(arch_file) as f:
    arch_data = json.load(f)
self.assertIn('frameworks_detected', arch_data)
self.assertIn('Flask', arch_data['frameworks_detected'], 'Flask should be detected from imports')
```

**Workflow: Test that files with only imports are included in analysis (Issue #239).** (complexity: 1.00)

```python
'Test that files with only imports are included in analysis (Issue #239).'
(self.test_project / 'imports_only.py').write_text('import django\nfrom flask import Flask\nimport requests')
from skill_seekers.cli.codebase_scraper import main as scraper_main
import sys
old_argv = sys.argv
try:
    sys.argv = ['skill-seekers-codebase', '--directory', str(self.test_project), '--output', str(self.output_dir), '--depth', 'deep', '--ai-mode', 'none']
    scraper_main()
finally:
    sys.argv = old_argv
code_analysis = self.output_dir / 'code_analysis.json'
self.assertTrue(code_analysis.exists(), 'Code analysis file should exist')
with open(code_analysis) as f:
    analysis_data = json.load(f)
self.assertGreater(len(analysis_data['files']), 0, 'Files with imports should be included')
import_file = next((f for f in analysis_data['files'] if 'imports_only.py' in f['file']), None)
self.assertIsNotNone(import_file, 'Import-only file should be in analysis')
self.assertIn('imports', import_file, 'Imports should be extracted')
self.assertGreater(len(import_file['imports']), 0, 'Should have captured imports')
self.assertIn('django', import_file['imports'], 'Django import should be captured')
self.assertIn('flask', import_file['imports'], 'Flask import should be captured')
```

**Workflow: Test that framework detection doesn't produce false positives (Issue #239).** (complexity: 1.00)

```python
"Test that framework detection doesn't produce false positives (Issue #239)."
app_dir = self.test_project / 'app'
app_dir.mkdir()
(app_dir / 'utils.py').write_text("def my_function():\n    return 'hello'\n")
from skill_seekers.cli.codebase_scraper import main as scraper_main
import sys
old_argv = sys.argv
try:
    sys.argv = ['skill-seekers-codebase', '--directory', str(self.test_project), '--output', str(self.output_dir), '--depth', 'deep', '--ai-mode', 'none']
    scraper_main()
finally:
    sys.argv = old_argv
arch_file = self.output_dir / 'references' / 'architecture' / 'architectural_patterns.json'
if arch_file.exists():
    with open(arch_file) as f:
        arch_data = json.load(f)
    frameworks = arch_data.get('frameworks_detected', [])
    self.assertNotIn('Flask', frameworks, 'Should not detect Flask without imports')
    for fw in ['ASP.NET', 'Rails', 'Laravel']:
        self.assertNotIn(fw, frameworks, f'Should not detect {fw} without real evidence')
```

*See `references/test_examples/` for all extracted examples*

## ⚙️ Configuration Patterns

*From C3.4 configuration analysis*

**Configuration Files Analyzed:** 51
**Total Settings:** 3718
**Patterns Detected:** 0

**Configuration Types:**
- unknown: 51 files

*See `references/config_patterns/` for detailed configuration analysis*

## 📖 Project Documentation

*Extracted from markdown files in the project (C3.9)*

**Total Documentation Files:** 152
**Categories:** 10

### Overview

- **AGENTS.md - Skill Seekers**: **AGENTS.md - Skill Seekers**
- **RAG & CLI Improvements (v2.11.0) - All Phases Complete**: **RAG & CLI Improvements (v2.11.0) - All Phases Complete**
- **Bulletproof Quick Start Guide**: **Bulletproof Quick Start Guide**
- **CLAUDE.md**: **CLAUDE.md**
- **Comprehensive QA Report - v2.11.0**: **Comprehensive QA Report - v2.11.0**
- *...and 28 more*

### Architecture

- **Architecture Verification Report**: **Architecture Verification Report**
- **HTTPX Skill Quality Analysis - Ultra-Deep Grading**: **HTTPX Skill Quality Analysis - Ultra-Deep Grading**
- **Three-Stream GitHub Architecture - Implementation Summary**: **Three-Stream GitHub Architecture - Implementation Summary**
- **Local Repository Extraction Test - deck_deck_go**: **Local Repository Extraction Test - deck_deck_go**
- **Skill Quality Fix Plan**: **Skill Quality Fix Plan**
- *...and 9 more*

### Guides

- **HTTP Transport for FastMCP Server**: **HTTP Transport for FastMCP Server**
- **Complete MCP Setup Guide - MCP 2025 (v2.7.0)**: **Complete MCP Setup Guide - MCP 2025 (v2.7.0)**
- **Migration Guide**: **Migration Guide**
- **Multi-Agent Auto-Configuration Guide**: **Multi-Agent Auto-Configuration Guide**
- **Setup Quick Reference Card**: **Setup Quick Reference Card**
- *...and 3 more*

### Features

- **Bootstrap Skill - Self-Hosting (v2.7.0)**: **Bootstrap Skill - Self-Hosting (v2.7.0)**
- **Bootstrap Skill - Technical Deep Dive**: **Bootstrap Skill - Technical Deep Dive**
- **AI-Powered SKILL.md Enhancement**: **AI-Powered SKILL.md Enhancement**
- **Enhancement Modes Guide**: **Enhancement Modes Guide**
- **How-To Guide Generation (C3.3)**: **How-To Guide Generation (C3.3)**
- *...and 7 more*

### Api

- **Skill Seekers Config API**: **Skill Seekers Config API**
- **AI Skill Standards & Best Practices (2026)**: **AI Skill Standards & Best Practices (2026)**
- **API Reference - Programmatic Usage**: **API Reference - Programmatic Usage**
- **C3.x Router Architecture - Ultra-Detailed Technical Specification**: **C3.x Router Architecture - Ultra-Detailed Technical Specification**
- **CLAUDE.md**: **CLAUDE.md**
- *...and 6 more*

### Examples

- **ChromaDB Vector Database Example**: **ChromaDB Vector Database Example**
- **Cline + Django Assistant Example**: **Cline + Django Assistant Example**
- **Continue.dev + Universal Context Example**: **Continue.dev + Universal Context Example**
- **Example React Project for Cursor**: **Example React Project for Cursor**
- **Cursor + React Skill Example**: **Cursor + React Skill Example**
- *...and 8 more*

*See `references/documentation/` for all project documentation*

## 📚 Available References

This skill includes detailed reference documentation:

- **API Reference**: `references/api_reference/` - Complete API documentation
- **Dependencies**: `references/dependencies/` - Dependency graph and analysis
- **Patterns**: `references/patterns/` - Detected design patterns
- **Examples**: `references/test_examples/` - Usage examples from tests
- **Configuration**: `references/config_patterns/` - Configuration patterns
- **Architecture**: `references/architecture/` - Architectural patterns
- **Documentation**: `references/documentation/` - Project documentation

---

**Generated by Skill Seeker** | Codebase Analyzer with C3.x Analysis
