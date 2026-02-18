# Test Example Extraction Report

**Total Examples**: 912  
**High Value Examples** (confidence > 0.7): 912  
**Average Complexity**: 0.48  

## Examples by Category

- **config**: 10
- **instantiation**: 301
- **method_call**: 240
- **workflow**: 361

## Examples by Language

- **Python**: 912

## Extracted Examples

### test_chain_dependencies

**Category**: workflow  
**Description**: Workflow: Test chain of dependencies.  
**Expected**: self.assertEqual(graph.number_of_nodes(), 3)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not ANALYZER_AVAILABLE:
    self.skipTest('dependency_analyzer not available')
self.analyzer = DependencyAnalyzer()

'Test chain of dependencies.'
self.analyzer.analyze_file('main.py', 'import utils', 'Python')
self.analyzer.analyze_file('utils.py', 'import helpers', 'Python')
self.analyzer.analyze_file('helpers.py', '', 'Python')
graph = self.analyzer.build_graph()
self.assertEqual(graph.number_of_nodes(), 3)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_dependency_analyzer.py:208*

### test_chain_dependencies

**Category**: workflow  
**Description**: Workflow: Test chain of dependencies.  
**Expected**: self.assertEqual(graph.number_of_nodes(), 3)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test chain of dependencies.'
self.analyzer.analyze_file('main.py', 'import utils', 'Python')
self.analyzer.analyze_file('utils.py', 'import helpers', 'Python')
self.analyzer.analyze_file('helpers.py', '', 'Python')
graph = self.analyzer.build_graph()
self.assertEqual(graph.number_of_nodes(), 3)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_dependency_analyzer.py:208*

### test_scrape_parser_creates_subparser

**Category**: workflow  
**Description**: Workflow: Test that ScrapeParser creates valid subparser.  
**Expected**: assert scrape_parser.help == 'Scrape documentation website'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that ScrapeParser creates valid subparser.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers()
scrape_parser = ScrapeParser()
subparser = scrape_parser.create_parser(subparsers)
assert subparser is not None
assert scrape_parser.name == 'scrape'
assert scrape_parser.help == 'Scrape documentation website'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_parsers.py:72*

### test_github_parser_creates_subparser

**Category**: workflow  
**Description**: Workflow: Test that GitHubParser creates valid subparser.  
**Expected**: assert github_parser.name == 'github'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that GitHubParser creates valid subparser.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers()
github_parser = GitHubParser()
subparser = github_parser.create_parser(subparsers)
assert subparser is not None
assert github_parser.name == 'github'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_parsers.py:84*

### test_package_parser_creates_subparser

**Category**: workflow  
**Description**: Workflow: Test that PackageParser creates valid subparser.  
**Expected**: assert package_parser.name == 'package'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that PackageParser creates valid subparser.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers()
package_parser = PackageParser()
subparser = package_parser.create_parser(subparsers)
assert subparser is not None
assert package_parser.name == 'package'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_parsers.py:95*

### test_register_parsers_creates_all_subcommands

**Category**: workflow  
**Description**: Workflow: Test that register_parsers creates all 19 subcommands.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that register_parsers creates all 19 subcommands.'
main_parser = argparse.ArgumentParser()
subparsers = main_parser.add_subparsers(dest='command')
register_parsers(subparsers)
test_commands = ['config --show', 'scrape --config test.json', 'github --repo owner/repo', 'package output/test/', 'upload test.zip', 'analyze --directory .', 'enhance output/test/', 'estimate test.json']
for cmd in test_commands:
    args = main_parser.parse_args(cmd.split())
    assert args.command is not None
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_parsers.py:106*

### test_scrape_parser_arguments

**Category**: workflow  
**Description**: Workflow: Test ScrapeParser has correct arguments.  
**Expected**: assert args.enhance is True  
**Confidence**: 0.90  
**Tags**: workflow, integration  

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

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_parsers.py:134*

### test_github_parser_arguments

**Category**: workflow  
**Description**: Workflow: Test GitHubParser has correct arguments.  
**Expected**: assert args.non_interactive is True  
**Confidence**: 0.90  
**Tags**: workflow, integration  

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

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_parsers.py:153*

### test_package_parser_arguments

**Category**: workflow  
**Description**: Workflow: Test PackageParser has correct arguments.  
**Expected**: assert args.no_open is True  
**Confidence**: 0.90  
**Tags**: workflow, integration  

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

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_parsers.py:168*

### test_analyze_parser_arguments

**Category**: workflow  
**Description**: Workflow: Test AnalyzeParser has correct arguments.  
**Expected**: assert args.skip_patterns is True  
**Confidence**: 0.90  
**Tags**: workflow, integration  

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

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_parsers.py:186*

### test_init_loads_data

**Category**: workflow  
**Description**: Workflow: Test that converter loads data file on initialization  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
if not PYGITHUB_AVAILABLE:
    self.skipTest('PyGithub not installed')
from skill_seekers.cli.github_scraper import GitHubToSkillConverter
self.GitHubToSkillConverter = GitHubToSkillConverter
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir)
self.data_file = self.output_dir / 'test_github_data.json'
self.mock_data = {'repo_info': {'name': 'react', 'full_name': 'facebook/react', 'description': 'A JavaScript library', 'stars': 200000, 'language': 'JavaScript'}, 'readme': '# React\n\nA JavaScript library for building user interfaces.', 'languages': {'JavaScript': {'bytes': 8000, 'percentage': 80.0}, 'TypeScript': {'bytes': 2000, 'percentage': 20.0}}, 'issues': [{'number': 123, 'title': 'Bug in useState', 'state': 'open', 'labels': ['bug'], 'milestone': 'v18.0', 'created_at': '2023-01-01T10:00:00', 'updated_at': '2023-01-02T10:00:00', 'closed_at': None, 'url': 'https://github.com/facebook/react/issues/123', 'body': 'Issue description'}], 'changelog': '# Changelog\n\n## v18.0.0\n- New features', 'releases': [{'tag_name': 'v18.0.0', 'name': 'React 18.0.0', 'body': 'Release notes', 'published_at': '2023-03-01T10:00:00', 'prerelease': False, 'draft': False, 'url': 'https://github.com/facebook/react/releases/tag/v18.0.0'}]}
with open(self.data_file, 'w') as f:
    json.dump(self.mock_data, f)

'Test that converter loads data file on initialization'
config = {'repo': 'facebook/react', 'name': 'test', 'description': 'Test skill'}
with patch('skill_seekers.cli.github_scraper.GitHubToSkillConverter.__init__') as mock_init:
    mock_init.return_value = None
    converter = self.GitHubToSkillConverter(config)
    converter.data_file = str(self.data_file)
    converter.data = converter._load_data()
    self.assertIn('repo_info', converter.data)
    self.assertEqual(converter.data['repo_info']['name'], 'react')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_scraper.py:596*

### test_build_skill_creates_directory_structure

**Category**: workflow  
**Description**: Workflow: Test that build_skill creates proper directory structure  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
if not PYGITHUB_AVAILABLE:
    self.skipTest('PyGithub not installed')
from skill_seekers.cli.github_scraper import GitHubToSkillConverter
self.GitHubToSkillConverter = GitHubToSkillConverter
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir)
self.data_file = self.output_dir / 'test_github_data.json'
self.mock_data = {'repo_info': {'name': 'react', 'full_name': 'facebook/react', 'description': 'A JavaScript library', 'stars': 200000, 'language': 'JavaScript'}, 'readme': '# React\n\nA JavaScript library for building user interfaces.', 'languages': {'JavaScript': {'bytes': 8000, 'percentage': 80.0}, 'TypeScript': {'bytes': 2000, 'percentage': 20.0}}, 'issues': [{'number': 123, 'title': 'Bug in useState', 'state': 'open', 'labels': ['bug'], 'milestone': 'v18.0', 'created_at': '2023-01-01T10:00:00', 'updated_at': '2023-01-02T10:00:00', 'closed_at': None, 'url': 'https://github.com/facebook/react/issues/123', 'body': 'Issue description'}], 'changelog': '# Changelog\n\n## v18.0.0\n- New features', 'releases': [{'tag_name': 'v18.0.0', 'name': 'React 18.0.0', 'body': 'Release notes', 'published_at': '2023-03-01T10:00:00', 'prerelease': False, 'draft': False, 'url': 'https://github.com/facebook/react/releases/tag/v18.0.0'}]}
with open(self.data_file, 'w') as f:
    json.dump(self.mock_data, f)

'Test that build_skill creates proper directory structure'
data_file_path = self.output_dir / 'test_github_data.json'
with open(data_file_path, 'w') as f:
    json.dump(self.mock_data, f)
config = {'repo': 'facebook/react', 'name': 'test', 'description': 'Test skill'}
with patch('skill_seekers.cli.github_scraper.GitHubToSkillConverter._load_data') as mock_load:
    mock_load.return_value = self.mock_data
    converter = self.GitHubToSkillConverter(config)
    converter.skill_dir = str(self.output_dir / 'test_skill')
    converter.data = self.mock_data
    converter.build_skill()
    skill_dir = Path(converter.skill_dir)
    self.assertTrue(skill_dir.exists())
    self.assertTrue((skill_dir / 'SKILL.md').exists())
    self.assertTrue((skill_dir / 'references').exists())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_scraper.py:610*

### test_invalid_repo_name

**Category**: workflow  
**Description**: Workflow: Test handling of invalid repository name  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
if not PYGITHUB_AVAILABLE:
    self.skipTest('PyGithub not installed')
from skill_seekers.cli.github_scraper import GitHubScraper
self.GitHubScraper = GitHubScraper

'Test handling of invalid repository name'
config = {'repo': 'invalid_repo_format', 'name': 'test', 'github_token': None}
with patch('skill_seekers.cli.github_scraper.Github'):
    scraper = self.GitHubScraper(config)
    scraper.repo = None
    scraper.github.get_repo = Mock(side_effect=GithubException(404, 'Not found'))
    with self.assertRaises(ValueError) as context:
        scraper._fetch_repository()
    self.assertIn('Repository not found', str(context.exception))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_scraper.py:980*

### test_init_loads_data

**Category**: workflow  
**Description**: Workflow: Test that converter loads data file on initialization  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
'Test that converter loads data file on initialization'
config = {'repo': 'facebook/react', 'name': 'test', 'description': 'Test skill'}
with patch('skill_seekers.cli.github_scraper.GitHubToSkillConverter.__init__') as mock_init:
    mock_init.return_value = None
    converter = self.GitHubToSkillConverter(config)
    converter.data_file = str(self.data_file)
    converter.data = converter._load_data()
    self.assertIn('repo_info', converter.data)
    self.assertEqual(converter.data['repo_info']['name'], 'react')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_scraper.py:596*

### test_build_skill_creates_directory_structure

**Category**: workflow  
**Description**: Workflow: Test that build_skill creates proper directory structure  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
'Test that build_skill creates proper directory structure'
data_file_path = self.output_dir / 'test_github_data.json'
with open(data_file_path, 'w') as f:
    json.dump(self.mock_data, f)
config = {'repo': 'facebook/react', 'name': 'test', 'description': 'Test skill'}
with patch('skill_seekers.cli.github_scraper.GitHubToSkillConverter._load_data') as mock_load:
    mock_load.return_value = self.mock_data
    converter = self.GitHubToSkillConverter(config)
    converter.skill_dir = str(self.output_dir / 'test_skill')
    converter.data = self.mock_data
    converter.build_skill()
    skill_dir = Path(converter.skill_dir)
    self.assertTrue(skill_dir.exists())
    self.assertTrue((skill_dir / 'SKILL.md').exists())
    self.assertTrue((skill_dir / 'references').exists())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_scraper.py:610*

### test_invalid_repo_name

**Category**: workflow  
**Description**: Workflow: Test handling of invalid repository name  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
'Test handling of invalid repository name'
config = {'repo': 'invalid_repo_format', 'name': 'test', 'github_token': None}
with patch('skill_seekers.cli.github_scraper.Github'):
    scraper = self.GitHubScraper(config)
    scraper.repo = None
    scraper.github.get_repo = Mock(side_effect=GithubException(404, 'Not found'))
    with self.assertRaises(ValueError) as context:
        scraper._fetch_repository()
    self.assertIn('Repository not found', str(context.exception))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_scraper.py:980*

### test_github_workflows_reference_correct_paths

**Category**: workflow  
**Description**: Workflow: Test that GitHub workflows reference correct MCP paths  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that GitHub workflows reference correct MCP paths'
workflow_file = Path('.github/workflows/tests.yml')
if workflow_file.exists():
    with open(workflow_file) as f:
        content = f.read()
    assert 'mcp/requirements.txt' not in content or 'skill_seeker_mcp/requirements.txt' in content, 'GitHub workflow should use correct MCP paths'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_setup_scripts.py:200*

### test_flask_framework_detection_from_imports

**Category**: workflow  
**Description**: Workflow: Test that Flask is detected from import statements (Issue #239).  
**Expected**: self.assertIn('Flask', arch_data['frameworks_detected'], 'Flask should be detected from imports')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Create temporary directory for testing.'
self.temp_dir = tempfile.mkdtemp()
self.test_project = Path(self.temp_dir) / 'test_project'
self.test_project.mkdir()
self.output_dir = Path(self.temp_dir) / 'output'

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

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_framework_detection.py:31*

### test_files_with_imports_are_included

**Category**: workflow  
**Description**: Workflow: Test that files with only imports are included in analysis (Issue #239).  
**Expected**: self.assertIn('flask', import_file['imports'], 'Flask import should be captured')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Create temporary directory for testing.'
self.temp_dir = tempfile.mkdtemp()
self.test_project = Path(self.temp_dir) / 'test_project'
self.test_project.mkdir()
self.output_dir = Path(self.temp_dir) / 'output'

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

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_framework_detection.py:87*

### test_no_false_positive_frameworks

**Category**: workflow  
**Description**: Workflow: Test that framework detection doesn't produce false positives (Issue #239).  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Create temporary directory for testing.'
self.temp_dir = tempfile.mkdtemp()
self.test_project = Path(self.temp_dir) / 'test_project'
self.test_project.mkdir()
self.output_dir = Path(self.temp_dir) / 'output'

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

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_framework_detection.py:137*

### test_flask_framework_detection_from_imports

**Category**: workflow  
**Description**: Workflow: Test that Flask is detected from import statements (Issue #239).  
**Expected**: self.assertIn('Flask', arch_data['frameworks_detected'], 'Flask should be detected from imports')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

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

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_framework_detection.py:31*

### test_files_with_imports_are_included

**Category**: workflow  
**Description**: Workflow: Test that files with only imports are included in analysis (Issue #239).  
**Expected**: self.assertIn('flask', import_file['imports'], 'Flask import should be captured')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

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

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_framework_detection.py:87*

### test_no_false_positive_frameworks

**Category**: workflow  
**Description**: Workflow: Test that framework detection doesn't produce false positives (Issue #239).  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

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

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_framework_detection.py:137*

### test_detect_unified_format

**Category**: workflow  
**Description**: Workflow: Test unified format detection and legacy rejection  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test unified format detection and legacy rejection'
import json
import tempfile
unified_config = {'name': 'test', 'description': 'Test skill', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com'}]}
legacy_config = {'name': 'test', 'description': 'Test skill', 'base_url': 'https://example.com'}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(unified_config, f)
    config_path = f.name
try:
    validator = ConfigValidator(config_path)
    assert validator.is_unified
    validator.validate()
finally:
    os.unlink(config_path)
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(legacy_config, f)
    config_path = f.name
try:
    validator = ConfigValidator(config_path)
    assert validator.is_unified
    with pytest.raises(ValueError, match='LEGACY CONFIG FORMAT DETECTED'):
        validator.validate()
finally:
    os.unlink(config_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified.py:29*

### test_needs_api_merge

**Category**: workflow  
**Description**: Workflow: Test API merge detection  
**Expected**: assert not validator.needs_api_merge()  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test API merge detection'
config_needs_merge = {'name': 'test', 'description': 'Test', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com', 'extract_api': True}, {'type': 'github', 'repo': 'user/repo', 'include_code': True}]}
validator = ConfigValidator(config_needs_merge)
assert validator.needs_api_merge()
config_no_merge = {'name': 'test', 'description': 'Test', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com'}]}
validator = ConfigValidator(config_no_merge)
assert not validator.needs_api_merge()
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified.py:99*

### test_detect_missing_in_docs

**Category**: workflow  
**Description**: Workflow: Test detection of APIs missing in documentation  
**Expected**: assert any((c.api_name == 'undocumented_func' for c in conflicts))  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test detection of APIs missing in documentation'
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'documented_func', 'parameters': [{'name': 'x', 'type': 'int'}], 'return_type': 'str'}]}]}
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'undocumented_func', 'parameters': [{'name': 'y', 'type_hint': 'float'}], 'return_type': 'bool'}]}]}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector._find_missing_in_docs()
assert len(conflicts) > 0
assert any((c.type == 'missing_in_docs' for c in conflicts))
assert any((c.api_name == 'undocumented_func' for c in conflicts))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified.py:152*

### test_detect_missing_in_code

**Category**: workflow  
**Description**: Workflow: Test detection of APIs missing in code  
**Expected**: assert any((c.api_name == 'obsolete_func' for c in conflicts))  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test detection of APIs missing in code'
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'obsolete_func', 'parameters': [{'name': 'x', 'type': 'int'}], 'return_type': 'str'}]}]}
github_data = {'code_analysis': {'analyzed_files': []}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector._find_missing_in_code()
assert len(conflicts) > 0
assert any((c.type == 'missing_in_code' for c in conflicts))
assert any((c.api_name == 'obsolete_func' for c in conflicts))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified.py:193*

### test_detect_signature_mismatch

**Category**: workflow  
**Description**: Workflow: Test detection of signature mismatches  
**Expected**: assert any((c.api_name == 'func' for c in conflicts))  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test detection of signature mismatches'
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'func', 'parameters': [{'name': 'x', 'type': 'int'}], 'return_type': 'str'}]}]}
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'func', 'parameters': [{'name': 'x', 'type_hint': 'int'}, {'name': 'y', 'type_hint': 'bool', 'default': 'False'}], 'return_type': 'str'}]}]}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector._find_signature_mismatches()
assert len(conflicts) > 0
assert any((c.type == 'signature_mismatch' for c in conflicts))
assert any((c.api_name == 'func' for c in conflicts))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified.py:220*

### test_rule_based_merge_docs_only

**Category**: workflow  
**Description**: Workflow: Test rule-based merge for docs-only APIs  
**Expected**: assert merged['apis']['docs_only_api']['status'] == 'docs_only'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test rule-based merge for docs-only APIs'
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'docs_only_api', 'parameters': [{'name': 'x', 'type': 'int'}], 'return_type': 'str'}]}]}
github_data = {'code_analysis': {'analyzed_files': []}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector.detect_all_conflicts()
merger = RuleBasedMerger(docs_data, github_data, conflicts)
merged = merger.merge_all()
assert 'apis' in merged
assert 'docs_only_api' in merged['apis']
assert merged['apis']['docs_only_api']['status'] == 'docs_only'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified.py:294*

### test_rule_based_merge_code_only

**Category**: workflow  
**Description**: Workflow: Test rule-based merge for code-only APIs  
**Expected**: assert merged['apis']['code_only_api']['status'] == 'code_only'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test rule-based merge for code-only APIs'
docs_data = {'pages': []}
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'code_only_api', 'parameters': [{'name': 'y', 'type_hint': 'float'}], 'return_type': 'bool'}]}]}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector.detect_all_conflicts()
merger = RuleBasedMerger(docs_data, github_data, conflicts)
merged = merger.merge_all()
assert 'apis' in merged
assert 'code_only_api' in merged['apis']
assert merged['apis']['code_only_api']['status'] == 'code_only'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified.py:324*

### test_rule_based_merge_matched

**Category**: workflow  
**Description**: Workflow: Test rule-based merge for matched APIs  
**Expected**: assert merged['apis']['matched_api']['status'] == 'matched'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test rule-based merge for matched APIs'
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'matched_api', 'parameters': [{'name': 'x', 'type': 'int'}], 'return_type': 'str'}]}]}
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'matched_api', 'parameters': [{'name': 'x', 'type_hint': 'int'}], 'return_type': 'str'}]}]}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector.detect_all_conflicts()
merger = RuleBasedMerger(docs_data, github_data, conflicts)
merged = merger.merge_all()
assert 'apis' in merged
assert 'matched_api' in merged['apis']
assert merged['apis']['matched_api']['status'] == 'matched'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified.py:355*

### test_merge_summary

**Category**: workflow  
**Description**: Workflow: Test merge summary statistics  
**Expected**: assert merged['summary']['code_only'] == 1  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test merge summary statistics'
docs_data = {'pages': [{'url': 'https://example.com/api', 'apis': [{'name': 'api1', 'parameters': [], 'return_type': 'str'}, {'name': 'api2', 'parameters': [], 'return_type': 'int'}]}]}
github_data = {'code_analysis': {'analyzed_files': [{'functions': [{'name': 'api3', 'parameters': [], 'return_type': 'bool'}]}]}}
detector = ConflictDetector(docs_data, github_data)
conflicts = detector.detect_all_conflicts()
merger = RuleBasedMerger(docs_data, github_data, conflicts)
merged = merger.merge_all()
assert 'summary' in merged
assert merged['summary']['total_apis'] == 3
assert merged['summary']['docs_only'] == 2
assert merged['summary']['code_only'] == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified.py:399*

### test_skill_builder_basic

**Category**: workflow  
**Description**: Workflow: Test basic skill building  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test basic skill building'
config = {'name': 'test_skill', 'description': 'Test skill description', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com'}]}
scraped_data = {'documentation': {'pages': [], 'data_file': '/tmp/test.json'}}
with tempfile.TemporaryDirectory() as tmpdir:
    builder = UnifiedSkillBuilder(config, scraped_data)
    builder.skill_dir = tmpdir
    builder._generate_skill_md()
    skill_md = Path(tmpdir) / 'SKILL.md'
    assert skill_md.exists()
    content = skill_md.read_text()
    assert 'test_skill' in content.lower()
    assert 'Test skill description' in content
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified.py:438*

### test_format_skill_md

**Category**: workflow  
**Description**: Workflow: Test formatting SKILL.md as LangChain Documents.  
**Expected**: assert 'getting started' in categories or 'api' in categories  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test formatting SKILL.md as LangChain Documents.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
skill_md = skill_dir / 'SKILL.md'
skill_md.write_text('# Test Skill\n\nThis is a test skill for LangChain format.')
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start.')
(refs_dir / 'api.md').write_text('# API Reference\n\nAPI docs.')
adaptor = get_adaptor('langchain')
metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
documents_json = adaptor.format_skill_md(skill_dir, metadata)
documents = json.loads(documents_json)
assert len(documents) == 3
for doc in documents:
    assert 'page_content' in doc
    assert 'metadata' in doc
    assert doc['metadata']['source'] == 'test_skill'
    assert doc['metadata']['version'] == '1.0.0'
    assert 'category' in doc['metadata']
    assert 'file' in doc['metadata']
    assert 'type' in doc['metadata']
categories = {doc['metadata']['category'] for doc in documents}
assert 'overview' in categories
assert 'getting started' in categories or 'api' in categories
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_langchain_adaptor.py:23*

### test_package_creates_json

**Category**: workflow  
**Description**: Workflow: Test packaging skill into JSON file.  
**Expected**: assert 'metadata' in documents[0]  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test packaging skill into JSON file.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('langchain')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.exists()
assert output_path.suffix == '.json'
assert 'langchain' in output_path.name
with open(output_path) as f:
    documents = json.load(f)
assert isinstance(documents, list)
assert len(documents) > 0
assert 'page_content' in documents[0]
assert 'metadata' in documents[0]
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_langchain_adaptor.py:65*

### test_package_output_filename

**Category**: workflow  
**Description**: Workflow: Test package output filename generation.  
**Expected**: assert 'langchain' in output_path.name  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test package output filename generation.'
skill_dir = tmp_path / 'react'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# React\n\nReact docs.')
adaptor = get_adaptor('langchain')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.name == 'react-langchain.json'
output_path = adaptor.package(skill_dir, tmp_path / 'test.zip')
assert output_path.suffix == '.json'
assert 'langchain' in output_path.name
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_langchain_adaptor.py:90*

### test_empty_skill_directory

**Category**: workflow  
**Description**: Workflow: Test handling of empty skill directory.  
**Expected**: assert documents == []  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test handling of empty skill directory.'
skill_dir = tmp_path / 'empty_skill'
skill_dir.mkdir()
adaptor = get_adaptor('langchain')
metadata = SkillMetadata(name='empty_skill', description='Empty', version='1.0.0')
documents_json = adaptor.format_skill_md(skill_dir, metadata)
documents = json.loads(documents_json)
assert documents == []
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_langchain_adaptor.py:146*

### test_references_only

**Category**: workflow  
**Description**: Workflow: Test skill with references but no SKILL.md.  
**Expected**: assert documents[0]['metadata']['type'] == 'reference'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test skill with references but no SKILL.md.'
skill_dir = tmp_path / 'refs_only'
skill_dir.mkdir()
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'test.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('langchain')
metadata = SkillMetadata(name='refs_only', description='Refs only', version='1.0.0')
documents_json = adaptor.format_skill_md(skill_dir, metadata)
documents = json.loads(documents_json)
assert len(documents) == 1
assert documents[0]['metadata']['category'] == 'test'
assert documents[0]['metadata']['type'] == 'reference'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_langchain_adaptor.py:160*

### temp_git_repo

**Category**: workflow  
**Description**: Workflow: Create a temporary git repository with sample configs.  
**Confidence**: 0.90  
**Tags**: pytest, workflow, integration  

```python
'Create a temporary git repository with sample configs.'
repo_dir = tempfile.mkdtemp(prefix='ss_repo_')
repo = git.Repo.init(repo_dir)
configs = {'react.json': {'name': 'react', 'description': 'React framework for UIs', 'base_url': 'https://react.dev/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre code'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {'getting_started': ['learn', 'start'], 'api': ['reference', 'api']}, 'rate_limit': 0.5, 'max_pages': 100}, 'vue.json': {'name': 'vue', 'description': 'Vue.js progressive framework', 'base_url': 'https://vuejs.org/', 'selectors': {'main_content': 'main', 'title': 'h1'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}, 'rate_limit': 0.5, 'max_pages': 50}, 'django.json': {'name': 'django', 'description': 'Django web framework', 'base_url': 'https://docs.djangoproject.com/', 'selectors': {'main_content': "div[role='main']", 'title': 'h1'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}, 'rate_limit': 0.5, 'max_pages': 200}}
for filename, config_data in configs.items():
    config_path = Path(repo_dir) / filename
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)
repo.index.add(['*.json'])
repo.index.commit('Initial commit with sample configs')
yield (repo_dir, repo)
shutil.rmtree(repo_dir, ignore_errors=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_sources_e2e.py:51*

### test_e2e_workflow_direct_git_url

**Category**: workflow  
**Description**: Workflow: E2E Test 1: Direct git URL workflow (no source registration)

Steps:
1. Clone repository via direct git URL
2. List available configs
3. Fetch specific config
4. Verify config content  
**Expected**: assert config['max_pages'] == 100  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

'\n        E2E Test 1: Direct git URL workflow (no source registration)\n\n        Steps:\n        1. Clone repository via direct git URL\n        2. List available configs\n        3. Fetch specific config\n        4. Verify config content\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
git_repo = GitConfigRepo(cache_dir=cache_dir)
repo_path = git_repo.clone_or_pull(source_name='test-direct', git_url=git_url, branch='master')
assert repo_path.exists()
assert (repo_path / '.git').exists()
configs = git_repo.find_configs(repo_path)
assert len(configs) == 3
config_names = [c.stem for c in configs]
assert set(config_names) == {'react', 'vue', 'django'}
config = git_repo.get_config(repo_path, 'react')
assert config['name'] == 'react'
assert config['description'] == 'React framework for UIs'
assert config['base_url'] == 'https://react.dev/'
assert 'selectors' in config
assert 'categories' in config
assert config['max_pages'] == 100
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_sources_e2e.py:107*

### test_e2e_workflow_with_source_registration

**Category**: workflow  
**Description**: Workflow: E2E Test 2: Complete workflow with source registration

Steps:
1. Add source to registry
2. List sources
3. Get source details
4. Clone via source name
5. Fetch config
6. Update source (re-add with different priority)
7. Remove source
8. Verify removal  
**Expected**: assert len(sources) == 0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

'\n        E2E Test 2: Complete workflow with source registration\n\n        Steps:\n        1. Add source to registry\n        2. List sources\n        3. Get source details\n        4. Clone via source name\n        5. Fetch config\n        6. Update source (re-add with different priority)\n        7. Remove source\n        8. Verify removal\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
source_manager = SourceManager(config_dir=config_dir)
source = source_manager.add_source(name='team-configs', git_url=git_url, source_type='custom', branch='master', priority=10)
assert source['name'] == 'team-configs'
assert source['git_url'] == git_url
assert source['type'] == 'custom'
assert source['branch'] == 'master'
assert source['priority'] == 10
assert source['enabled'] is True
sources = source_manager.list_sources()
assert len(sources) == 1
assert sources[0]['name'] == 'team-configs'
retrieved_source = source_manager.get_source('team-configs')
assert retrieved_source['git_url'] == git_url
git_repo = GitConfigRepo(cache_dir=cache_dir)
repo_path = git_repo.clone_or_pull(source_name=source['name'], git_url=source['git_url'], branch=source['branch'])
assert repo_path.exists()
config = git_repo.get_config(repo_path, 'vue')
assert config['name'] == 'vue'
assert config['base_url'] == 'https://vuejs.org/'
updated_source = source_manager.add_source(name='team-configs', git_url=git_url, source_type='custom', branch='master', priority=5)
assert updated_source['priority'] == 5
removed = source_manager.remove_source('team-configs')
assert removed is True
sources = source_manager.list_sources()
assert len(sources) == 0
with pytest.raises(KeyError, match="Source 'team-configs' not found"):
    source_manager.get_source('team-configs')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_sources_e2e.py:150*

### test_e2e_multiple_sources_priority_resolution

**Category**: workflow  
**Description**: Workflow: E2E Test 3: Multiple sources with priority resolution

Steps:
1. Add multiple sources with different priorities
2. Verify sources are sorted by priority
3. Enable/disable sources
4. List enabled sources only  
**Expected**: assert 'high-priority' not in [s['name'] for s in enabled_sources]  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

'\n        E2E Test 3: Multiple sources with priority resolution\n\n        Steps:\n        1. Add multiple sources with different priorities\n        2. Verify sources are sorted by priority\n        3. Enable/disable sources\n        4. List enabled sources only\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
source_manager = SourceManager(config_dir=config_dir)
source_manager.add_source(name='low-priority', git_url=git_url, priority=100)
source_manager.add_source(name='high-priority', git_url=git_url, priority=1)
source_manager.add_source(name='medium-priority', git_url=git_url, priority=50)
sources = source_manager.list_sources()
assert len(sources) == 3
assert sources[0]['name'] == 'high-priority'
assert sources[1]['name'] == 'medium-priority'
assert sources[2]['name'] == 'low-priority'
source_manager.add_source(name='high-priority', git_url=git_url, priority=1, enabled=False)
enabled_sources = source_manager.list_sources(enabled_only=True)
assert len(enabled_sources) == 2
assert all((s['enabled'] for s in enabled_sources))
assert 'high-priority' not in [s['name'] for s in enabled_sources]
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_sources_e2e.py:225*

### test_e2e_pull_existing_repository

**Category**: workflow  
**Description**: Workflow: E2E Test 4: Pull updates from existing repository

Steps:
1. Clone repository
2. Add new commit to original repo
3. Pull updates
4. Verify new config is available  
**Expected**: assert fastapi_config['max_pages'] == 150  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

'\n        E2E Test 4: Pull updates from existing repository\n\n        Steps:\n        1. Clone repository\n        2. Add new commit to original repo\n        3. Pull updates\n        4. Verify new config is available\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
git_repo = GitConfigRepo(cache_dir=cache_dir)
repo_path = git_repo.clone_or_pull(source_name='test-pull', git_url=git_url, branch='master')
initial_configs = git_repo.find_configs(repo_path)
assert len(initial_configs) == 3
new_config = {'name': 'fastapi', 'description': 'FastAPI framework', 'base_url': 'https://fastapi.tiangolo.com/', 'selectors': {'main_content': 'article'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}, 'rate_limit': 0.5, 'max_pages': 150}
new_config_path = Path(repo_dir) / 'fastapi.json'
with open(new_config_path, 'w') as f:
    json.dump(new_config, f, indent=2)
repo.index.add(['fastapi.json'])
repo.index.commit('Add FastAPI config')
updated_repo_path = git_repo.clone_or_pull(source_name='test-pull', git_url=git_url, branch='master', force_refresh=False)
updated_configs = git_repo.find_configs(updated_repo_path)
assert len(updated_configs) == 4
fastapi_config = git_repo.get_config(updated_repo_path, 'fastapi')
assert fastapi_config['name'] == 'fastapi'
assert fastapi_config['max_pages'] == 150
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_sources_e2e.py:262*

### test_e2e_force_refresh

**Category**: workflow  
**Description**: Workflow: E2E Test 5: Force refresh (delete and re-clone)

Steps:
1. Clone repository
2. Modify local cache manually
3. Force refresh
4. Verify cache was reset  
**Expected**: assert len(configs) == 3  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

'\n        E2E Test 5: Force refresh (delete and re-clone)\n\n        Steps:\n        1. Clone repository\n        2. Modify local cache manually\n        3. Force refresh\n        4. Verify cache was reset\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
git_repo = GitConfigRepo(cache_dir=cache_dir)
repo_path = git_repo.clone_or_pull(source_name='test-refresh', git_url=git_url, branch='master')
corrupt_file = repo_path / 'CORRUPTED.txt'
with open(corrupt_file, 'w') as f:
    f.write('This file should not exist after refresh')
assert corrupt_file.exists()
refreshed_repo_path = git_repo.clone_or_pull(source_name='test-refresh', git_url=git_url, branch='master', force_refresh=True)
assert not corrupt_file.exists()
configs = git_repo.find_configs(refreshed_repo_path)
assert len(configs) == 3
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_sources_e2e.py:321*

### test_e2e_config_not_found

**Category**: workflow  
**Description**: Workflow: E2E Test 6: Error handling - config not found

Steps:
1. Clone repository
2. Try to fetch non-existent config
3. Verify helpful error message with suggestions  
**Expected**: assert 'django' in error_msg  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

'\n        E2E Test 6: Error handling - config not found\n\n        Steps:\n        1. Clone repository\n        2. Try to fetch non-existent config\n        3. Verify helpful error message with suggestions\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
git_repo = GitConfigRepo(cache_dir=cache_dir)
repo_path = git_repo.clone_or_pull(source_name='test-not-found', git_url=git_url, branch='master')
with pytest.raises(FileNotFoundError) as exc_info:
    git_repo.get_config(repo_path, 'nonexistent')
error_msg = str(exc_info.value)
assert 'nonexistent.json' in error_msg
assert 'not found' in error_msg
assert 'react' in error_msg
assert 'vue' in error_msg
assert 'django' in error_msg
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_sources_e2e.py:362*

### test_e2e_invalid_git_url

**Category**: workflow  
**Description**: Workflow: E2E Test 7: Error handling - invalid git URL

Steps:
1. Try to clone with invalid URL
2. Verify validation error  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_dirs

'\n        E2E Test 7: Error handling - invalid git URL\n\n        Steps:\n        1. Try to clone with invalid URL\n        2. Verify validation error\n        '
cache_dir, config_dir = temp_dirs
git_repo = GitConfigRepo(cache_dir=cache_dir)
invalid_urls = ['', 'not-a-url', 'ftp://invalid.com/repo.git', "javascript:alert('xss')"]
for invalid_url in invalid_urls:
    with pytest.raises(ValueError, match='Invalid git URL'):
        git_repo.clone_or_pull(source_name='test-invalid', git_url=invalid_url, branch='master')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_sources_e2e.py:394*

### test_e2e_source_name_validation

**Category**: workflow  
**Description**: Workflow: E2E Test 8: Error handling - invalid source names

Steps:
1. Try to add sources with invalid names
2. Verify validation errors  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_dirs

'\n        E2E Test 8: Error handling - invalid source names\n\n        Steps:\n        1. Try to add sources with invalid names\n        2. Verify validation errors\n        '
cache_dir, config_dir = temp_dirs
source_manager = SourceManager(config_dir=config_dir)
invalid_names = ['', 'name with spaces', 'name/with/slashes', 'name@with@symbols', 'name.with.dots', '123-only-numbers-start-is-ok', 'name!exclamation']
valid_git_url = 'https://github.com/test/repo.git'
for invalid_name in invalid_names[:-2]:
    if invalid_name == '123-only-numbers-start-is-ok':
        continue
    with pytest.raises(ValueError, match='Invalid source name'):
        source_manager.add_source(name=invalid_name, git_url=valid_git_url)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_sources_e2e.py:414*

### test_e2e_registry_persistence

**Category**: workflow  
**Description**: Workflow: E2E Test 9: Registry persistence across instances

Steps:
1. Add source with one SourceManager instance
2. Create new SourceManager instance
3. Verify source persists
4. Modify source with new instance
5. Verify changes persist  
**Expected**: assert source['priority'] == 50  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_dirs, temp_git_repo

'\n        E2E Test 9: Registry persistence across instances\n\n        Steps:\n        1. Add source with one SourceManager instance\n        2. Create new SourceManager instance\n        3. Verify source persists\n        4. Modify source with new instance\n        5. Verify changes persist\n        '
cache_dir, config_dir = temp_dirs
repo_dir, repo = temp_git_repo
git_url = f'file://{repo_dir}'
manager1 = SourceManager(config_dir=config_dir)
manager1.add_source(name='persistent-source', git_url=git_url, priority=25)
manager2 = SourceManager(config_dir=config_dir)
sources = manager2.list_sources()
assert len(sources) == 1
assert sources[0]['name'] == 'persistent-source'
assert sources[0]['priority'] == 25
manager2.add_source(name='persistent-source', git_url=git_url, priority=50)
manager3 = SourceManager(config_dir=config_dir)
source = manager3.get_source('persistent-source')
assert source['priority'] == 50
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_sources_e2e.py:444*

### test_with_configs_prefix

**Category**: workflow  
**Description**: Workflow: Test resolution with configs/ prefix.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test resolution with configs/ prefix.'
configs_dir = tmp_path / 'configs'
configs_dir.mkdir()
config_file = configs_dir / 'test.json'
config_file.write_text('{"name": "test"}')
import os
original_cwd = os.getcwd()
try:
    os.chdir(tmp_path)
    result = resolve_config_path('test.json', auto_fetch=False)
    assert result is not None
    assert result.exists()
    assert result.name == 'test.json'
finally:
    os.chdir(original_cwd)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_fetcher.py:239*

### test_config_name_normalization

**Category**: workflow  
**Description**: Workflow: Test various config name formats.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test various config name formats.'
configs_dir = tmp_path / 'configs'
configs_dir.mkdir()
config_file = configs_dir / 'react.json'
config_file.write_text('{"name": "react"}')
import os
original_cwd = os.getcwd()
try:
    os.chdir(tmp_path)
    test_cases = ['react.json', 'configs/react.json']
    for config_name in test_cases:
        result = resolve_config_path(config_name, auto_fetch=False)
        assert result is not None, f'Failed for {config_name}'
        assert result.exists()
        assert result.name == 'react.json'
finally:
    os.chdir(original_cwd)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_fetcher.py:290*

### test_classify_files

**Category**: workflow  
**Description**: Workflow: Test classify_files separates code and docs correctly.  
**Expected**: assert 'api.rst' in doc_paths  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test classify_files separates code and docs correctly.'
(tmp_path / 'src').mkdir()
(tmp_path / 'src' / 'main.py').write_text("print('hello')")
(tmp_path / 'src' / 'utils.js').write_text('function(){}')
(tmp_path / 'docs').mkdir()
(tmp_path / 'README.md').write_text('# README')
(tmp_path / 'docs' / 'guide.md').write_text('# Guide')
(tmp_path / 'docs' / 'api.rst').write_text('API')
(tmp_path / 'node_modules').mkdir()
(tmp_path / 'node_modules' / 'lib.js').write_text('// should be excluded')
fetcher = GitHubThreeStreamFetcher('https://github.com/test/repo')
code_files, doc_files = fetcher.classify_files(tmp_path)
code_paths = [f.name for f in code_files]
assert 'main.py' in code_paths
assert 'utils.js' in code_paths
assert 'lib.js' not in code_paths
doc_paths = [f.name for f in doc_files]
assert 'README.md' in doc_paths
assert 'guide.md' in doc_paths
assert 'api.rst' in doc_paths
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_fetcher.py:105*

### test_detect_python_with_confidence

**Category**: workflow  
**Description**: Workflow: Test Python detection returns language and confidence  
**Expected**: self.assertLessEqual(confidence, 1.0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

'Test Python detection returns language and confidence'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = "def hello():\n    print('world')\n    return True"
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'python')
self.assertGreater(confidence, 0.4)
self.assertLessEqual(confidence, 1.0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_extractor.py:40*

### test_detect_javascript_with_confidence

**Category**: workflow  
**Description**: Workflow: Test JavaScript detection  
**Expected**: self.assertGreater(confidence, 0.5)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

'Test JavaScript detection'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = "const handleClick = () => {\n  console.log('clicked');\n};"
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'javascript')
self.assertGreater(confidence, 0.5)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_extractor.py:56*

### test_detect_cpp_with_confidence

**Category**: workflow  
**Description**: Workflow: Test C++ detection  
**Expected**: self.assertGreater(confidence, 0.5)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

'Test C++ detection'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = '#include <iostream>\nint main() {\n  std::cout << "Hello";\n}'
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'cpp')
self.assertGreater(confidence, 0.5)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_extractor.py:71*

### test_detect_unknown_low_confidence

**Category**: workflow  
**Description**: Workflow: Test unknown language returns low confidence  
**Expected**: self.assertLess(confidence, 0.3)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

'Test unknown language returns low confidence'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = 'this is not code at all just plain text'
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'unknown')
self.assertLess(confidence, 0.3)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_extractor.py:86*

### test_detect_scss_with_confidence

**Category**: workflow  
**Description**: Workflow: Test SCSS detection  
**Expected**: self.assertGreater(confidence, 0.8)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

'Test SCSS detection'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = '\n        $primary-color: #3498db;\n\n        @mixin border-radius($radius) {\n          border-radius: $radius;\n        }\n\n        .button {\n          color: $primary-color;\n          @include border-radius(5px);\n\n          &:hover {\n            background: darken($primary-color, 10%);\n          }\n        }\n        '
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'scss')
self.assertGreater(confidence, 0.8)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_extractor.py:122*

### test_detect_dart_with_confidence

**Category**: workflow  
**Description**: Workflow: Test Dart detection  
**Expected**: self.assertGreater(confidence, 0.6)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

'Test Dart detection'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = "\n        import 'package:flutter/material.dart';\n\n        class MyApp extends StatelessWidget {\n          @override\n          Widget build(BuildContext context) {\n            return MaterialApp(\n              home: Text('Hello'),\n            );\n          }\n        }\n        "
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'dart')
self.assertGreater(confidence, 0.6)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_extractor.py:150*

### test_detect_scala_with_confidence

**Category**: workflow  
**Description**: Workflow: Test Scala detection  
**Expected**: self.assertGreater(confidence, 0.7)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

'Test Scala detection'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = '\n        case class Person(name: String, age: Int)\n\n        object Main extends App {\n          val person = Person("Alice", 30)\n          person match {\n            case Person(n, a) if a >= 18 => println(s"Adult: $n")\n            case _ => println("Minor")\n          }\n        }\n        '
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'scala')
self.assertGreater(confidence, 0.7)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_extractor.py:174*

### test_detect_sass_with_confidence

**Category**: workflow  
**Description**: Workflow: Test SASS detection  
**Expected**: self.assertGreater(confidence, 0.8)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

'Test SASS detection'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = '\n        $primary-color: #3498db\n\n        =border-radius($radius)\n          border-radius: $radius\n\n        .button\n          color: $primary-color\n          +border-radius(5px)\n\n          &:hover\n            background: darken($primary-color, 10%)\n        '
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'sass')
self.assertGreater(confidence, 0.8)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_extractor.py:197*

### test_detect_elixir_with_confidence

**Category**: workflow  
**Description**: Workflow: Test Elixir detection  
**Expected**: self.assertGreater(confidence, 0.8)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

'Test Elixir detection'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = '\n        defmodule MyApp.User do\n          def greet(name) do\n            "Hello, #{name}"\n          end\n\n          defp calculate_age(birth_year) do\n            2024 - birth_year\n          end\n\n          def process(data) do\n            data\n            |> String.trim()\n            |> String.downcase()\n            |> String.split(",")\n          end\n        end\n        '
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'elixir')
self.assertGreater(confidence, 0.8)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_extractor.py:222*

### test_detect_lua_with_confidence

**Category**: workflow  
**Description**: Workflow: Test Lua detection  
**Expected**: self.assertGreater(confidence, 0.7)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor

'Test Lua detection'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
from skill_seekers.cli.language_detector import LanguageDetector
extractor.language_detector = LanguageDetector(min_confidence=0.15)
code = '\n        local function calculate_sum(numbers)\n          local total = 0\n          for i = 1, #numbers do\n            total = total + numbers[i]\n          end\n          return total\n        end\n\n        local items = {1, 2, 3, 4, 5}\n        local result = calculate_sum(items)\n        print("Sum: " .. result)\n        '
language, confidence = extractor.detect_language_from_code(code)
self.assertEqual(language, 'lua')
self.assertGreater(confidence, 0.7)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_extractor.py:252*

### test_router_generator_init

**Category**: workflow  
**Description**: Workflow: Test router generator initialization.  
**Expected**: assert generator.github_streams is None  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test router generator initialization.'
config1 = {'name': 'test-oauth', 'description': 'OAuth authentication', 'base_url': 'https://example.com', 'categories': {'authentication': ['auth', 'oauth']}}
config2 = {'name': 'test-async', 'description': 'Async operations', 'base_url': 'https://example.com', 'categories': {'async': ['async', 'await']}}
config_path1 = tmp_path / 'config1.json'
config_path2 = tmp_path / 'config2.json'
with open(config_path1, 'w') as f:
    json.dump(config1, f)
with open(config_path2, 'w') as f:
    json.dump(config2, f)
generator = RouterGenerator([str(config_path1), str(config_path2)])
assert generator.router_name == 'test'
assert len(generator.configs) == 2
assert generator.github_streams is None
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_generate_router_github.py:20*

### test_infer_router_name

**Category**: workflow  
**Description**: Workflow: Test router name inference from sub-skill names.  
**Expected**: assert generator.router_name == 'fastmcp'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test router name inference from sub-skill names.'
config1 = {'name': 'fastmcp-oauth', 'base_url': 'https://example.com'}
config2 = {'name': 'fastmcp-async', 'base_url': 'https://example.com'}
config_path1 = tmp_path / 'config1.json'
config_path2 = tmp_path / 'config2.json'
with open(config_path1, 'w') as f:
    json.dump(config1, f)
with open(config_path2, 'w') as f:
    json.dump(config2, f)
generator = RouterGenerator([str(config_path1), str(config_path2)])
assert generator.router_name == 'fastmcp'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_generate_router_github.py:51*

### test_extract_routing_keywords_basic

**Category**: workflow  
**Description**: Workflow: Test basic keyword extraction without GitHub.  
**Expected**: assert 'oauth' in keywords  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test basic keyword extraction without GitHub.'
config = {'name': 'test-oauth', 'base_url': 'https://example.com', 'categories': {'authentication': ['auth', 'oauth'], 'tokens': ['token', 'jwt']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
generator = RouterGenerator([str(config_path)])
routing = generator.extract_routing_keywords()
assert 'test-oauth' in routing
keywords = routing['test-oauth']
assert 'authentication' in keywords
assert 'tokens' in keywords
assert 'oauth' in keywords
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_generate_router_github.py:68*

### test_router_with_github_metadata

**Category**: workflow  
**Description**: Workflow: Test router generator with GitHub metadata.  
**Expected**: assert generator.github_issues is not None  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test router generator with GitHub metadata.'
config = {'name': 'test-oauth', 'description': 'OAuth skill', 'base_url': 'https://github.com/test/repo', 'categories': {'oauth': ['oauth', 'auth']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# Test Project\n\nA test OAuth library.', contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={'stars': 1234, 'forks': 56, 'language': 'Python', 'description': 'OAuth helper'}, common_problems=[{'title': 'OAuth fails on redirect', 'number': 42, 'state': 'open', 'comments': 15, 'labels': ['bug', 'oauth']}], known_solutions=[], top_labels=[{'label': 'oauth', 'count': 20}, {'label': 'bug', 'count': 10}])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
assert generator.github_metadata is not None
assert generator.github_metadata['stars'] == 1234
assert generator.github_docs is not None
assert generator.github_docs['readme'].startswith('# Test Project')
assert generator.github_issues is not None
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_generate_router_github.py:93*

### test_extract_keywords_with_github_labels

**Category**: workflow  
**Description**: Workflow: Test keyword extraction with GitHub issue labels (2x weight).  
**Expected**: assert oauth_count >= 4  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test keyword extraction with GitHub issue labels (2x weight).'
config = {'name': 'test-oauth', 'base_url': 'https://example.com', 'categories': {'oauth': ['oauth', 'auth']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme=None, contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={}, common_problems=[], known_solutions=[], top_labels=[{'label': 'oauth', 'count': 50}, {'label': 'authentication', 'count': 30}, {'label': 'bug', 'count': 20}])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
routing = generator.extract_routing_keywords()
keywords = routing['test-oauth']
oauth_count = keywords.count('oauth')
assert oauth_count >= 4
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_generate_router_github.py:141*

### test_generate_skill_md_with_github

**Category**: workflow  
**Description**: Workflow: Test SKILL.md generation with GitHub metadata.  
**Expected**: assert 'how do i handle redirect uri mismatch' in skill_md.lower() or 'how do i fix redirect uri mismatch' in skill_md.lower()  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test SKILL.md generation with GitHub metadata.'
config = {'name': 'test-oauth', 'description': 'OAuth authentication skill', 'base_url': 'https://github.com/test/oauth', 'categories': {'oauth': ['oauth']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# OAuth Library\n\nQuick start: Install with pip install oauth', contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={'stars': 5000, 'forks': 200, 'language': 'Python', 'description': 'OAuth 2.0 library'}, common_problems=[{'title': 'Redirect URI mismatch', 'number': 100, 'state': 'open', 'comments': 25, 'labels': ['bug', 'oauth']}, {'title': 'Token refresh fails', 'number': 95, 'state': 'open', 'comments': 18, 'labels': ['oauth']}], known_solutions=[], top_labels=[])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
skill_md = generator.generate_skill_md()
assert '⭐ 5,000' in skill_md
assert 'Python' in skill_md
assert 'OAuth 2.0 library' in skill_md
assert '## Quick Start' in skill_md
assert 'OAuth Library' in skill_md
assert '## Common Issues' in skill_md or '## Examples' in skill_md
assert 'how do i handle redirect uri mismatch' in skill_md.lower() or 'how do i fix redirect uri mismatch' in skill_md.lower()
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_generate_router_github.py:176*

### test_generate_skill_md_without_github

**Category**: workflow  
**Description**: Workflow: Test SKILL.md generation without GitHub (backward compat).  
**Expected**: assert 'How It Works' in skill_md  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test SKILL.md generation without GitHub (backward compat).'
config = {'name': 'test-oauth', 'description': 'OAuth skill', 'base_url': 'https://example.com', 'categories': {'oauth': ['oauth']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
generator = RouterGenerator([str(config_path)])
skill_md = generator.generate_skill_md()
assert '⭐' not in skill_md
assert 'Repository Info' not in skill_md
assert 'Quick Start (from README)' not in skill_md
assert 'Common Issues (from GitHub)' not in skill_md
assert 'When to Use This Skill' in skill_md
assert 'How It Works' in skill_md
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_generate_router_github.py:244*

### test_generate_subskill_issues_section

**Category**: workflow  
**Description**: Workflow: Test generation of issues section for sub-skills.  
**Expected**: assert '✅' in issues_section  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test generation of issues section for sub-skills.'
config = {'name': 'test-oauth', 'base_url': 'https://example.com', 'categories': {'oauth': ['oauth']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme=None, contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={}, common_problems=[{'title': 'OAuth redirect fails', 'number': 50, 'state': 'open', 'comments': 20, 'labels': ['oauth', 'bug']}, {'title': 'Token expiration issue', 'number': 45, 'state': 'open', 'comments': 15, 'labels': ['oauth']}], known_solutions=[{'title': 'Fixed OAuth flow', 'number': 40, 'state': 'closed', 'comments': 10, 'labels': ['oauth']}], top_labels=[])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
issues_section = generator.generate_subskill_issues_section('test-oauth', ['oauth'])
assert 'Common Issues (from GitHub)' in issues_section
assert 'OAuth redirect fails' in issues_section
assert 'Issue #50' in issues_section
assert '20 comments' in issues_section
assert '🔴' in issues_section
assert '✅' in issues_section
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_generate_router_github.py:275*

### test_generate_subskill_issues_no_matches

**Category**: workflow  
**Description**: Workflow: Test issues section when no issues match the topic.  
**Expected**: assert 'OAuth fails' in issues_section  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test issues section when no issues match the topic.'
config = {'name': 'test-async', 'base_url': 'https://example.com', 'categories': {'async': ['async']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme=None, contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={}, common_problems=[{'title': 'OAuth fails', 'number': 1, 'state': 'open', 'comments': 5, 'labels': ['oauth']}], known_solutions=[], top_labels=[])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator = RouterGenerator([str(config_path)], github_streams=github_streams)
issues_section = generator.generate_subskill_issues_section('test-async', ['async'])
assert 'Common Issues (from GitHub)' in issues_section
assert 'Other' in issues_section
assert 'OAuth fails' in issues_section
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_generate_router_github.py:334*

### test_creates_subdirectory_per_source

**Category**: workflow  
**Description**: Workflow: Test that each doc source gets its own subdirectory.  
**Expected**: self.assertTrue(os.path.exists(os.path.join(docs_dir, 'source_b')))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

'Test that each doc source gets its own subdirectory.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
refs_dir1 = os.path.join(self.temp_dir, 'refs1')
refs_dir2 = os.path.join(self.temp_dir, 'refs2')
os.makedirs(refs_dir1)
os.makedirs(refs_dir2)
config = {'name': 'test_docs_refs', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [{'source_id': 'source_a', 'base_url': 'https://a.com', 'total_pages': 5, 'refs_dir': refs_dir1}, {'source_id': 'source_b', 'base_url': 'https://b.com', 'total_pages': 3, 'refs_dir': refs_dir2}], 'github': [], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_docs_references(scraped_data['documentation'])
docs_dir = os.path.join(builder.skill_dir, 'references', 'documentation')
self.assertTrue(os.path.exists(os.path.join(docs_dir, 'source_a')))
self.assertTrue(os.path.exists(os.path.join(docs_dir, 'source_b')))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multi_source.py:103*

### test_creates_index_per_source

**Category**: workflow  
**Description**: Workflow: Test that each source subdirectory has its own index.md.  
**Expected**: self.assertTrue(os.path.exists(source_index))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

'Test that each source subdirectory has its own index.md.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
refs_dir = os.path.join(self.temp_dir, 'refs')
os.makedirs(refs_dir)
config = {'name': 'test_source_index', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [{'source_id': 'my_source', 'base_url': 'https://example.com', 'total_pages': 10, 'refs_dir': refs_dir}], 'github': [], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_docs_references(scraped_data['documentation'])
source_index = os.path.join(builder.skill_dir, 'references', 'documentation', 'my_source', 'index.md')
self.assertTrue(os.path.exists(source_index))
with open(source_index) as f:
    content = f.read()
    self.assertIn('my_source', content)
    self.assertIn('https://example.com', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multi_source.py:141*

### test_creates_main_index_listing_all_sources

**Category**: workflow  
**Description**: Workflow: Test that main index.md lists all documentation sources.  
**Expected**: self.assertTrue(os.path.exists(main_index))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

'Test that main index.md lists all documentation sources.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
refs_dir1 = os.path.join(self.temp_dir, 'refs1')
refs_dir2 = os.path.join(self.temp_dir, 'refs2')
os.makedirs(refs_dir1)
os.makedirs(refs_dir2)
config = {'name': 'test_main_index', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [{'source_id': 'docs_one', 'base_url': 'https://one.com', 'total_pages': 10, 'refs_dir': refs_dir1}, {'source_id': 'docs_two', 'base_url': 'https://two.com', 'total_pages': 20, 'refs_dir': refs_dir2}], 'github': [], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_docs_references(scraped_data['documentation'])
main_index = os.path.join(builder.skill_dir, 'references', 'documentation', 'index.md')
self.assertTrue(os.path.exists(main_index))
with open(main_index) as f:
    content = f.read()
    self.assertIn('docs_one', content)
    self.assertIn('docs_two', content)
    self.assertIn('2 documentation sources', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multi_source.py:176*

### test_copies_reference_files_to_source_dir

**Category**: workflow  
**Description**: Workflow: Test that reference files are copied to source subdirectory.  
**Expected**: self.assertTrue(os.path.exists(os.path.join(source_dir, 'guide.md')))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

'Test that reference files are copied to source subdirectory.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
refs_dir = os.path.join(self.temp_dir, 'refs')
os.makedirs(refs_dir)
with open(os.path.join(refs_dir, 'api.md'), 'w') as f:
    f.write('# API Reference')
with open(os.path.join(refs_dir, 'guide.md'), 'w') as f:
    f.write('# User Guide')
config = {'name': 'test_copy_refs', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [{'source_id': 'test_source', 'base_url': 'https://test.com', 'total_pages': 5, 'refs_dir': refs_dir}], 'github': [], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_docs_references(scraped_data['documentation'])
source_dir = os.path.join(builder.skill_dir, 'references', 'documentation', 'test_source')
self.assertTrue(os.path.exists(os.path.join(source_dir, 'api.md')))
self.assertTrue(os.path.exists(os.path.join(source_dir, 'guide.md')))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multi_source.py:218*

### test_creates_subdirectory_per_repo

**Category**: workflow  
**Description**: Workflow: Test that each GitHub repo gets its own subdirectory.  
**Expected**: self.assertTrue(os.path.exists(os.path.join(github_dir, 'org_repo2')))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

'Test that each GitHub repo gets its own subdirectory.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
config = {'name': 'test_github_refs', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [], 'github': [{'repo': 'org/repo1', 'repo_id': 'org_repo1', 'data': {'readme': '# Repo 1', 'issues': [], 'releases': [], 'repo_info': {}}}, {'repo': 'org/repo2', 'repo_id': 'org_repo2', 'data': {'readme': '# Repo 2', 'issues': [], 'releases': [], 'repo_info': {}}}], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_github_references(scraped_data['github'])
github_dir = os.path.join(builder.skill_dir, 'references', 'github')
self.assertTrue(os.path.exists(os.path.join(github_dir, 'org_repo1')))
self.assertTrue(os.path.exists(os.path.join(github_dir, 'org_repo2')))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multi_source.py:269*

### test_creates_readme_per_repo

**Category**: workflow  
**Description**: Workflow: Test that README.md is created for each repo.  
**Expected**: self.assertTrue(os.path.exists(readme_path))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

'Test that README.md is created for each repo.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
config = {'name': 'test_readme', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [], 'github': [{'repo': 'test/myrepo', 'repo_id': 'test_myrepo', 'data': {'readme': '# My Repository\n\nDescription here.', 'issues': [], 'releases': [], 'repo_info': {}}}], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_github_references(scraped_data['github'])
readme_path = os.path.join(builder.skill_dir, 'references', 'github', 'test_myrepo', 'README.md')
self.assertTrue(os.path.exists(readme_path))
with open(readme_path) as f:
    content = f.read()
    self.assertIn('test/myrepo', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multi_source.py:299*

### test_creates_issues_file_when_issues_exist

**Category**: workflow  
**Description**: Workflow: Test that issues.md is created when repo has issues.  
**Expected**: self.assertTrue(os.path.exists(issues_path))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

'Test that issues.md is created when repo has issues.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
config = {'name': 'test_issues', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [], 'github': [{'repo': 'test/repo', 'repo_id': 'test_repo', 'data': {'readme': '# Repo', 'issues': [{'number': 1, 'title': 'Bug report', 'state': 'open', 'labels': ['bug'], 'url': 'https://github.com/test/repo/issues/1'}, {'number': 2, 'title': 'Feature request', 'state': 'closed', 'labels': ['enhancement'], 'url': 'https://github.com/test/repo/issues/2'}], 'releases': [], 'repo_info': {}}}], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_github_references(scraped_data['github'])
issues_path = os.path.join(builder.skill_dir, 'references', 'github', 'test_repo', 'issues.md')
self.assertTrue(os.path.exists(issues_path))
with open(issues_path) as f:
    content = f.read()
    self.assertIn('Bug report', content)
    self.assertIn('Feature request', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multi_source.py:334*

### test_creates_main_index_listing_all_repos

**Category**: workflow  
**Description**: Workflow: Test that main index.md lists all GitHub repositories.  
**Expected**: self.assertTrue(os.path.exists(main_index))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

'Test that main index.md lists all GitHub repositories.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
config = {'name': 'test_github_index', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [], 'github': [{'repo': 'org/first', 'repo_id': 'org_first', 'data': {'readme': '#', 'issues': [], 'releases': [], 'repo_info': {'stars': 100}}}, {'repo': 'org/second', 'repo_id': 'org_second', 'data': {'readme': '#', 'issues': [], 'releases': [], 'repo_info': {'stars': 50}}}], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_github_references(scraped_data['github'])
main_index = os.path.join(builder.skill_dir, 'references', 'github', 'index.md')
self.assertTrue(os.path.exists(main_index))
with open(main_index) as f:
    content = f.read()
    self.assertIn('org/first', content)
    self.assertIn('org/second', content)
    self.assertIn('2 GitHub repositories', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multi_source.py:385*

### test_creates_pdf_index_with_count

**Category**: workflow  
**Description**: Workflow: Test that PDF index shows correct document count.  
**Expected**: self.assertTrue(os.path.exists(pdf_index))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test fixtures.'
self.temp_dir = tempfile.mkdtemp()
self.original_dir = os.getcwd()
os.chdir(self.temp_dir)

'Test that PDF index shows correct document count.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
config = {'name': 'test_pdf', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [], 'github': [], 'pdf': [{'path': '/path/to/doc1.pdf'}, {'path': '/path/to/doc2.pdf'}, {'path': '/path/to/doc3.pdf'}]}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_pdf_references(scraped_data['pdf'])
pdf_index = os.path.join(builder.skill_dir, 'references', 'pdf', 'index.md')
self.assertTrue(os.path.exists(pdf_index))
with open(pdf_index) as f:
    content = f.read()
    self.assertIn('3 PDF document', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multi_source.py:446*

### test_creates_subdirectory_per_source

**Category**: workflow  
**Description**: Workflow: Test that each doc source gets its own subdirectory.  
**Expected**: self.assertTrue(os.path.exists(os.path.join(docs_dir, 'source_b')))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test that each doc source gets its own subdirectory.'
from skill_seekers.cli.unified_skill_builder import UnifiedSkillBuilder
refs_dir1 = os.path.join(self.temp_dir, 'refs1')
refs_dir2 = os.path.join(self.temp_dir, 'refs2')
os.makedirs(refs_dir1)
os.makedirs(refs_dir2)
config = {'name': 'test_docs_refs', 'description': 'Test', 'sources': []}
scraped_data = {'documentation': [{'source_id': 'source_a', 'base_url': 'https://a.com', 'total_pages': 5, 'refs_dir': refs_dir1}, {'source_id': 'source_b', 'base_url': 'https://b.com', 'total_pages': 3, 'refs_dir': refs_dir2}], 'github': [], 'pdf': []}
builder = UnifiedSkillBuilder(config, scraped_data)
builder._generate_docs_references(scraped_data['documentation'])
docs_dir = os.path.join(builder.skill_dir, 'references', 'documentation')
self.assertTrue(os.path.exists(os.path.join(docs_dir, 'source_a')))
self.assertTrue(os.path.exists(os.path.join(docs_dir, 'source_b')))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multi_source.py:103*

### test_bootstrap_script_runs

**Category**: workflow  
**Description**: Workflow: Test that bootstrap script runs successfully.

Note: This test is slow as it runs full codebase analysis.
Run with: pytest -m slow  
**Expected**: assert 'pip install skill-seekers' in content, 'SKILL.md should have install instructions'  
**Confidence**: 0.90  
**Tags**: pytest, workflow, integration  

```python
# Setup
# Fixtures: project_root

'Test that bootstrap script runs successfully.\n\n        Note: This test is slow as it runs full codebase analysis.\n        Run with: pytest -m slow\n        '
script = project_root / 'scripts' / 'bootstrap_skill.sh'
result = subprocess.run(['bash', str(script)], cwd=project_root, capture_output=True, text=True, timeout=600)
assert result.returncode == 0, f'Script failed: {result.stderr}'
output_dir = project_root / 'output' / 'skill-seekers'
assert output_dir.exists(), 'Output directory should be created'
skill_md = output_dir / 'SKILL.md'
assert skill_md.exists(), 'SKILL.md should be created'
content = skill_md.read_text()
assert '## Prerequisites' in content, 'SKILL.md should have header prepended'
assert 'pip install skill-seekers' in content, 'SKILL.md should have install instructions'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_bootstrap_skill.py:54*

### test_deduplicate_urls

**Category**: workflow  
**Description**: Workflow: Test that duplicate URLs are removed.  
**Expected**: self.assertEqual(count, 1)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test that duplicate URLs are removed.'
from skill_seekers.cli.llms_txt_parser import LlmsTxtParser
content = '\n- [Doc 1](https://example.com/doc.md)\n- [Doc 2](https://example.com/doc.md)\nhttps://example.com/doc.md\n'
parser = LlmsTxtParser(content)
urls = parser.extract_urls()
count = sum((1 for u in urls if u == 'https://example.com/doc.md'))
self.assertEqual(count, 1)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_markdown_parsing.py:273*

### test_deduplicate_urls

**Category**: workflow  
**Description**: Workflow: Test that duplicate URLs are removed.  
**Expected**: self.assertEqual(count, 1)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test that duplicate URLs are removed.'
from skill_seekers.cli.llms_txt_parser import LlmsTxtParser
content = '\n- [Doc 1](https://example.com/doc.md)\n- [Doc 2](https://example.com/doc.md)\nhttps://example.com/doc.md\n'
parser = LlmsTxtParser(content)
urls = parser.extract_urls()
count = sum((1 for u in urls if u == 'https://example.com/doc.md'))
self.assertEqual(count, 1)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_markdown_parsing.py:273*

### test_cache_set_and_get

**Category**: workflow  
**Description**: Workflow: Test setting and getting cached values  
**Expected**: self.assertEqual(cached, test_data)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor
self.temp_dir = tempfile.mkdtemp()

'Test setting and getting cached values'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = True
test_data = {'page': 1, 'text': 'cached content'}
extractor.set_cached('page_1', test_data)
cached = extractor.get_cached('page_1')
self.assertEqual(cached, test_data)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_advanced_features.py:339*

### test_cache_miss

**Category**: workflow  
**Description**: Workflow: Test cache miss returns None  
**Expected**: self.assertIsNone(cached)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor
self.temp_dir = tempfile.mkdtemp()

'Test cache miss returns None'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = True
cached = extractor.get_cached('nonexistent_key')
self.assertIsNone(cached)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_advanced_features.py:354*

### test_cache_disabled

**Category**: workflow  
**Description**: Workflow: Test caching can be disabled  
**Expected**: self.assertIsNone(cached)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor
self.temp_dir = tempfile.mkdtemp()

'Test caching can be disabled'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = False
extractor.set_cached('page_1', {'data': 'test'})
self.assertEqual(len(extractor._cache), 0)
cached = extractor.get_cached('page_1')
self.assertIsNone(cached)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_advanced_features.py:364*

### test_cache_overwrite

**Category**: workflow  
**Description**: Workflow: Test cache can be overwritten  
**Expected**: self.assertEqual(cached['version'], 2)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor
self.temp_dir = tempfile.mkdtemp()

'Test cache can be overwritten'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = True
extractor.set_cached('page_1', {'version': 1})
extractor.set_cached('page_1', {'version': 2})
cached = extractor.get_cached('page_1')
self.assertEqual(cached['version'], 2)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_advanced_features.py:380*

### test_cache_set_and_get

**Category**: workflow  
**Description**: Workflow: Test setting and getting cached values  
**Expected**: self.assertEqual(cached, test_data)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test setting and getting cached values'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = True
test_data = {'page': 1, 'text': 'cached content'}
extractor.set_cached('page_1', test_data)
cached = extractor.get_cached('page_1')
self.assertEqual(cached, test_data)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_advanced_features.py:339*

### test_cache_miss

**Category**: workflow  
**Description**: Workflow: Test cache miss returns None  
**Expected**: self.assertIsNone(cached)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test cache miss returns None'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = True
cached = extractor.get_cached('nonexistent_key')
self.assertIsNone(cached)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_advanced_features.py:354*

### test_cache_disabled

**Category**: workflow  
**Description**: Workflow: Test caching can be disabled  
**Expected**: self.assertIsNone(cached)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test caching can be disabled'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = False
extractor.set_cached('page_1', {'data': 'test'})
self.assertEqual(len(extractor._cache), 0)
cached = extractor.get_cached('page_1')
self.assertIsNone(cached)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_advanced_features.py:364*

### test_cache_overwrite

**Category**: workflow  
**Description**: Workflow: Test cache can be overwritten  
**Expected**: self.assertEqual(cached['version'], 2)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test cache can be overwritten'
extractor = self.PDFExtractor.__new__(self.PDFExtractor)
extractor._cache = {}
extractor.use_cache = True
extractor.set_cached('page_1', {'version': 1})
extractor.set_cached('page_1', {'version': 2})
cached = extractor.get_cached('page_1')
self.assertEqual(cached['version'], 2)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_advanced_features.py:380*

### test_no_config_no_logging

**Category**: workflow  
**Description**: Workflow: Test that default mode doesn't log exclude_dirs messages.  
**Expected**: self.assertEqual(len(exclude_warnings), 0)  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
"Test that default mode doesn't log exclude_dirs messages."
config = {'repo': 'owner/repo'}
_scraper = GitHubScraper(config)
info_calls = [str(call) for call in mock_logger.info.call_args_list]
warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
exclude_info = [c for c in info_calls if 'directory exclusion' in c]
exclude_warnings = [c for c in warning_calls if 'directory exclusion' in c]
self.assertEqual(len(exclude_info), 0)
self.assertEqual(len(exclude_warnings), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_excluded_dirs_config.py:299*

### test_no_config_no_logging

**Category**: workflow  
**Description**: Workflow: Test that default mode doesn't log exclude_dirs messages.  
**Expected**: self.assertEqual(len(exclude_warnings), 0)  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
# Fixtures: mock_logger, _mock_github

"Test that default mode doesn't log exclude_dirs messages."
config = {'repo': 'owner/repo'}
_scraper = GitHubScraper(config)
info_calls = [str(call) for call in mock_logger.info.call_args_list]
warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
exclude_info = [c for c in info_calls if 'directory exclusion' in c]
exclude_warnings = [c for c in warning_calls if 'directory exclusion' in c]
self.assertEqual(len(exclude_info), 0)
self.assertEqual(len(exclude_warnings), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_excluded_dirs_config.py:299*

### test_full_metadata

**Category**: workflow  
**Description**: Workflow: Test metadata with all fields  
**Expected**: self.assertEqual(metadata.tags, ['react', 'javascript', 'web'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test metadata with all fields'
metadata = SkillMetadata(name='react', description='React documentation', version='2.5.0', author='Test Author', tags=['react', 'javascript', 'web'])
self.assertEqual(metadata.name, 'react')
self.assertEqual(metadata.description, 'React documentation')
self.assertEqual(metadata.version, '2.5.0')
self.assertEqual(metadata.author, 'Test Author')
self.assertEqual(metadata.tags, ['react', 'javascript', 'web'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_base.py:30*

### test_full_metadata

**Category**: workflow  
**Description**: Workflow: Test metadata with all fields  
**Expected**: self.assertEqual(metadata.tags, ['react', 'javascript', 'web'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test metadata with all fields'
metadata = SkillMetadata(name='react', description='React documentation', version='2.5.0', author='Test Author', tags=['react', 'javascript', 'web'])
self.assertEqual(metadata.name, 'react')
self.assertEqual(metadata.description, 'React documentation')
self.assertEqual(metadata.version, '2.5.0')
self.assertEqual(metadata.author, 'Test Author')
self.assertEqual(metadata.tags, ['react', 'javascript', 'web'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_base.py:30*

### test_detect_from_html_swift_class

**Category**: workflow  
**Description**: Workflow: Test HTML element with Swift CSS class  
**Expected**: assert confidence == 1.0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test HTML element with Swift CSS class'
detector = LanguageDetector()
html = '<code class="language-swift">let x = 5</code>'
soup = BeautifulSoup(html, 'html.parser')
elem = soup.find('code')
lang, confidence = detector.detect_from_html(elem, 'let x = 5')
assert lang == 'swift'
assert confidence == 1.0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_swift_detection.py:44*

### test_viewcontroller_lifecycle

**Category**: workflow  
**Description**: Workflow: Test UIViewController lifecycle methods  
**Expected**: assert confidence >= 0.9  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test UIViewController lifecycle methods'
detector = LanguageDetector()
code = '\n        import UIKit\n\n        class HomeViewController: UIViewController {\n            override func viewDidLoad() {\n                super.viewDidLoad()\n                setupUI()\n            }\n\n            override func viewWillAppear(_ animated: Bool) {\n                super.viewWillAppear(animated)\n            }\n\n            override func viewDidAppear(_ animated: Bool) {\n                super.viewDidAppear(animated)\n            }\n        }\n        '
lang, confidence = detector.detect_from_code(code)
assert lang == 'swift'
assert confidence >= 0.9
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_swift_detection.py:342*

### test_nsviewcontroller_lifecycle

**Category**: workflow  
**Description**: Workflow: Test NSViewController lifecycle methods  
**Expected**: assert confidence >= 0.9  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test NSViewController lifecycle methods'
detector = LanguageDetector()
code = '\n        import AppKit\n\n        class MainViewController: NSViewController {\n            override func viewDidLoad() {\n                super.viewDidLoad()\n                setupUI()\n            }\n\n            override func viewWillAppear() {\n                super.viewWillAppear()\n            }\n\n            override func viewDidAppear() {\n                super.viewDidAppear()\n            }\n        }\n        '
lang, confidence = detector.detect_from_code(code)
assert lang == 'swift'
assert confidence >= 0.9
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_swift_detection.py:468*

### test_high_confidence_full_app

**Category**: workflow  
**Description**: Workflow: Test complete SwiftUI app (high confidence expected)  
**Expected**: assert confidence >= 0.95  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test complete SwiftUI app (high confidence expected)'
detector = LanguageDetector()
code = '\n        import SwiftUI\n\n        @main\n        struct MyApp: App {\n            @StateObject private var viewModel = AppViewModel()\n\n            var body: some Scene {\n                WindowGroup {\n                    ContentView()\n                        .environmentObject(viewModel)\n                }\n            }\n        }\n\n        struct ContentView: View {\n            @EnvironmentObject var viewModel: AppViewModel\n            @State private var searchText = ""\n\n            var body: some View {\n                NavigationStack {\n                    List {\n                        ForEach(viewModel.filteredItems) { item in\n                            NavigationLink(destination: DetailView(item: item)) {\n                                ItemRow(item: item)\n                            }\n                        }\n                    }\n                    .navigationTitle("Items")\n                    .searchable(text: $searchText)\n                    .refreshable {\n                        await viewModel.refresh()\n                    }\n                }\n            }\n        }\n        '
lang, confidence = detector.detect_from_code(code)
assert lang == 'swift'
assert confidence >= 0.95
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_swift_detection.py:960*

### test_swift_vs_similar_languages

**Category**: workflow  
**Description**: Workflow: Test Swift doesn't false-positive for similar syntax in other languages.

Critical for avoiding misclassification of:
- Go: 'func', ':=' short declaration
- Rust: 'fn', 'let mut', struct
- TypeScript: 'let', 'const', type annotations with ':'

These languages share keywords or syntax patterns with Swift,
so detection must use unique Swift patterns (guard let, @State, etc.)  
**Expected**: assert lang == 'typescript', f"Expected 'typescript', got '{lang}'"  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
"\n        Test Swift doesn't false-positive for similar syntax in other languages.\n\n        Critical for avoiding misclassification of:\n        - Go: 'func', ':=' short declaration\n        - Rust: 'fn', 'let mut', struct\n        - TypeScript: 'let', 'const', type annotations with ':'\n\n        These languages share keywords or syntax patterns with Swift,\n        so detection must use unique Swift patterns (guard let, @State, etc.)\n        "
detector = LanguageDetector()
go_code = '\n        package main\n\n        func main() {\n            message := "Hello"\n            fmt.Println(message)\n        }\n        '
lang, _ = detector.detect_from_code(go_code)
assert lang == 'go', f"Expected 'go', got '{lang}'"
rust_code = '\n        fn main() {\n            let mut x = 5;\n            println!("Value: {}", x);\n        }\n        '
lang, _ = detector.detect_from_code(rust_code)
assert lang == 'rust', f"Expected 'rust', got '{lang}'"
ts_code = "\n        interface User {\n            name: string;\n            age: number;\n        }\n\n        const greet = (user: User): string => {\n            return `Hello, ${user.name}`;\n        }\n\n        export type Status = 'active' | 'inactive';\n        "
lang, _ = detector.detect_from_code(ts_code)
assert lang == 'typescript', f"Expected 'typescript', got '{lang}'"
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_swift_detection.py:1004*

### test_malformed_regex_patterns_are_skipped

**Category**: workflow  
**Description**: Workflow: Test that invalid regex patterns are logged and skipped without crashing  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
'Test that invalid regex patterns are logged and skipped without crashing'
from unittest.mock import patch
from skill_seekers.cli.language_detector import LanguageDetector
with patch('skill_seekers.cli.language_detector.logger') as mock_logger:
    import skill_seekers.cli.language_detector as ld_module
    original_patterns = ld_module.LANGUAGE_PATTERNS.copy()
    try:
        ld_module.LANGUAGE_PATTERNS['test_malformed'] = [('(?P<invalid)', 5), ('valid_pattern', 3)]
        _detector = LanguageDetector()
        assert any(('Invalid regex pattern' in str(call) for call in mock_logger.error.call_args_list)), 'Expected error log for malformed pattern'
    finally:
        ld_module.LANGUAGE_PATTERNS = original_patterns
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_swift_detection.py:1289*

### test_empty_swift_patterns_handled_gracefully

**Category**: workflow  
**Description**: Workflow: Test that empty SWIFT_PATTERNS dict doesn't crash detection  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
"Test that empty SWIFT_PATTERNS dict doesn't crash detection"
import sys
from unittest.mock import patch
for mod in list(sys.modules.keys()):
    if 'skill_seekers.cli' in mod:
        del sys.modules[mod]
with patch.dict('sys.modules', {'skill_seekers.cli.swift_patterns': type('MockModule', (), {'SWIFT_PATTERNS': {}})}):
    from skill_seekers.cli.language_detector import LanguageDetector
    detector = LanguageDetector()
    code = 'import SwiftUI\nstruct MyView: View { }'
    lang, confidence = detector.detect_from_code(code)
    assert isinstance(lang, str)
    assert isinstance(confidence, (int, float))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_swift_detection.py:1323*

### test_non_string_pattern_handled_during_compilation

**Category**: workflow  
**Description**: Workflow: Test that non-string patterns are caught during compilation  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
'Test that non-string patterns are caught during compilation'
from unittest.mock import patch
from skill_seekers.cli.language_detector import LanguageDetector
with patch('skill_seekers.cli.language_detector.logger') as mock_logger:
    import skill_seekers.cli.language_detector as ld_module
    original = ld_module.LANGUAGE_PATTERNS.copy()
    try:
        ld_module.LANGUAGE_PATTERNS['test_nonstring'] = [(None, 5)]
        _detector = LanguageDetector()
        assert any(('not a string' in str(call) for call in mock_logger.error.call_args_list)), 'Expected error log for non-string pattern'
    finally:
        ld_module.LANGUAGE_PATTERNS = original
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_swift_detection.py:1351*

### test_format_skill_md

**Category**: workflow  
**Description**: Workflow: Test formatting SKILL.md as Weaviate objects.  
**Expected**: assert 'getting started' in categories or 'api' in categories  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test formatting SKILL.md as Weaviate objects.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
skill_md = skill_dir / 'SKILL.md'
skill_md.write_text('# Test Skill\n\nThis is a test skill for Weaviate format.')
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start.')
(refs_dir / 'api.md').write_text('# API Reference\n\nAPI docs.')
adaptor = get_adaptor('weaviate')
metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
objects_json = adaptor.format_skill_md(skill_dir, metadata)
result = json.loads(objects_json)
assert 'schema' in result
assert 'objects' in result
assert 'class_name' in result
assert len(result['objects']) == 3
for obj in result['objects']:
    assert 'id' in obj
    assert 'properties' in obj
    props = obj['properties']
    assert 'content' in props
    assert 'source' in props
    assert props['source'] == 'test_skill'
    assert props['version'] == '1.0.0'
    assert 'category' in props
    assert 'file' in props
    assert 'type' in props
categories = {obj['properties']['category'] for obj in result['objects']}
assert 'overview' in categories
assert 'getting started' in categories or 'api' in categories
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_weaviate_adaptor.py:23*

### test_package_creates_json

**Category**: workflow  
**Description**: Workflow: Test packaging skill into JSON file.  
**Expected**: assert 'properties' in result['objects'][0]  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test packaging skill into JSON file.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('weaviate')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.exists()
assert output_path.suffix == '.json'
assert 'weaviate' in output_path.name
with open(output_path) as f:
    result = json.load(f)
assert isinstance(result, dict)
assert 'objects' in result
assert len(result['objects']) > 0
assert 'id' in result['objects'][0]
assert 'properties' in result['objects'][0]
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_weaviate_adaptor.py:71*

### test_package_output_filename

**Category**: workflow  
**Description**: Workflow: Test package output filename generation.  
**Expected**: assert 'weaviate' in output_path.name  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test package output filename generation.'
skill_dir = tmp_path / 'react'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# React\n\nReact docs.')
adaptor = get_adaptor('weaviate')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.name == 'react-weaviate.json'
output_path = adaptor.package(skill_dir, tmp_path / 'test.zip')
assert output_path.suffix == '.json'
assert 'weaviate' in output_path.name
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_weaviate_adaptor.py:97*

### test_empty_skill_directory

**Category**: workflow  
**Description**: Workflow: Test handling of empty skill directory.  
**Expected**: assert result['objects'] == []  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test handling of empty skill directory.'
skill_dir = tmp_path / 'empty_skill'
skill_dir.mkdir()
adaptor = get_adaptor('weaviate')
metadata = SkillMetadata(name='empty_skill', description='Empty', version='1.0.0')
objects_json = adaptor.format_skill_md(skill_dir, metadata)
result = json.loads(objects_json)
assert 'objects' in result
assert result['objects'] == []
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_weaviate_adaptor.py:157*

### test_references_only

**Category**: workflow  
**Description**: Workflow: Test skill with references but no SKILL.md.  
**Expected**: assert result['objects'][0]['properties']['type'] == 'reference'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test skill with references but no SKILL.md.'
skill_dir = tmp_path / 'refs_only'
skill_dir.mkdir()
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'test.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('weaviate')
metadata = SkillMetadata(name='refs_only', description='Refs only', version='1.0.0')
objects_json = adaptor.format_skill_md(skill_dir, metadata)
result = json.loads(objects_json)
assert len(result['objects']) == 1
assert result['objects'][0]['properties']['category'] == 'test'
assert result['objects'][0]['properties']['type'] == 'reference'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_weaviate_adaptor.py:172*

### test_async_dry_run_completes

**Category**: workflow  
**Description**: Workflow: Test async dry run completes without errors  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
'Set up test fixtures'
self.original_cwd = os.getcwd()

'Test async dry run completes without errors'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article'}, 'async_mode': True, 'max_pages': 5}
with tempfile.TemporaryDirectory() as tmpdir:
    try:
        os.chdir(tmpdir)
        converter = DocToSkillConverter(config, dry_run=True)
        with patch.object(converter, '_try_llms_txt', return_value=False):
            converter.scrape_all()
            self.assertTrue(converter.dry_run)
    finally:
        os.chdir(self.original_cwd)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_async_scraping.py:205*

### test_async_dry_run_completes

**Category**: workflow  
**Description**: Workflow: Test async dry run completes without errors  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
'Test async dry run completes without errors'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article'}, 'async_mode': True, 'max_pages': 5}
with tempfile.TemporaryDirectory() as tmpdir:
    try:
        os.chdir(tmpdir)
        converter = DocToSkillConverter(config, dry_run=True)
        with patch.object(converter, '_try_llms_txt', return_value=False):
            converter.scrape_all()
            self.assertTrue(converter.dry_run)
    finally:
        os.chdir(self.original_cwd)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_async_scraping.py:205*

### test_enhance_guide_error_fallback

**Category**: workflow  
**Description**: Workflow: Test graceful fallback on enhancement error  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
'Test graceful fallback on enhancement error'
enhancer = GuideEnhancer(mode='none')
with patch.object(enhancer, 'enhance_guide', side_effect=Exception('API error')):
    guide_data = {'title': 'Test', 'steps': [], 'language': 'python', 'prerequisites': [], 'description': 'Test'}
    try:
        enhancer = GuideEnhancer(mode='none')
        result = enhancer.enhance_guide(guide_data)
        assert result['title'] == guide_data['title']
    except Exception:
        pytest.fail('Should handle errors gracefully')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_guide_enhancer.py:444*

### test_call_claude_local_success

**Category**: workflow  
**Description**: Workflow: Test successful LOCAL mode call  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: mock_run

'Test successful LOCAL mode call'
mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps({'step_descriptions': [], 'troubleshooting': [], 'prerequisites_detailed': [], 'next_steps': [], 'use_cases': []}))
enhancer = GuideEnhancer(mode='local')
if enhancer.mode == 'local':
    prompt = 'Test prompt'
    result = enhancer._call_claude_local(prompt)
    assert result is not None
    assert mock_run.called
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_guide_enhancer.py:471*

### test_call_claude_local_timeout

**Category**: workflow  
**Description**: Workflow: Test LOCAL mode timeout handling  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: mock_run

'Test LOCAL mode timeout handling'
from subprocess import TimeoutExpired
mock_run.side_effect = TimeoutExpired('claude', 300)
enhancer = GuideEnhancer(mode='local')
if enhancer.mode == 'local':
    prompt = 'Test prompt'
    result = enhancer._call_claude_local(prompt)
    assert result is None
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_guide_enhancer.py:495*

### test_parse_enhancement_response_valid_json

**Category**: workflow  
**Description**: Workflow: Test parsing valid JSON response  
**Expected**: assert len(result['step_enhancements']) == 1  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test parsing valid JSON response'
enhancer = GuideEnhancer(mode='none')
response = json.dumps({'step_descriptions': [{'step_index': 0, 'explanation': 'Test', 'variations': []}], 'troubleshooting': [], 'prerequisites_detailed': [], 'next_steps': [], 'use_cases': []})
guide_data = {'title': 'Test', 'steps': [{'description': 'Test', 'code': 'test'}], 'language': 'python'}
result = enhancer._parse_enhancement_response(response, guide_data)
assert 'step_enhancements' in result
assert len(result['step_enhancements']) == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_guide_enhancer.py:560*

### test_parse_enhancement_response_with_extra_text

**Category**: workflow  
**Description**: Workflow: Test parsing JSON embedded in text  
**Expected**: assert 'title' in result  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test parsing JSON embedded in text'
enhancer = GuideEnhancer(mode='none')
json_data = {'step_descriptions': [], 'troubleshooting': [], 'prerequisites_detailed': [], 'next_steps': [], 'use_cases': []}
response = f"Here's the result:\n{json.dumps(json_data)}\nDone!"
guide_data = {'title': 'Test', 'steps': [], 'language': 'python'}
result = enhancer._parse_enhancement_response(response, guide_data)
assert 'title' in result
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_guide_enhancer.py:585*

### test_compare_benchmarks

**Category**: workflow  
**Description**: Workflow: Test comparing benchmarks.  
**Expected**: assert len(comparison.improvements) > 0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test comparing benchmarks.'
runner = BenchmarkRunner(output_dir=tmp_path)

def baseline_bench(bench):
    with bench.timer('operation'):
        time.sleep(0.1)
runner.run('baseline', baseline_bench, save=True)
baseline_path = list(tmp_path.glob('baseline_*.json'))[0]

def improved_bench(bench):
    with bench.timer('operation'):
        time.sleep(0.05)
runner.run('improved', improved_bench, save=True)
improved_path = list(tmp_path.glob('improved_*.json'))[0]
from skill_seekers.benchmark.models import ComparisonReport
comparison = runner.compare(baseline_path, improved_path)
assert isinstance(comparison, ComparisonReport)
assert comparison.speedup_factor > 1.0
assert len(comparison.improvements) > 0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_benchmark.py:368*

### test_cleanup_old

**Category**: workflow  
**Description**: Workflow: Test cleaning up old benchmarks.  
**Expected**: assert 'test_00000007' in remaining_names or 'test_00000008' in remaining_names  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test cleaning up old benchmarks.'
import os
runner = BenchmarkRunner(output_dir=tmp_path)
base_time = time.time()
for i in range(10):
    filename = f'test_{i:08d}.json'
    file_path = tmp_path / filename
    report_data = {'name': 'test', 'started_at': datetime.utcnow().isoformat(), 'finished_at': datetime.utcnow().isoformat(), 'total_duration': 1.0, 'timings': [], 'memory': [], 'metrics': [], 'system_info': {}, 'recommendations': []}
    with open(file_path, 'w') as f:
        json.dump(report_data, f)
    mtime = base_time - (10 - i) * 60
    os.utime(file_path, (mtime, mtime))
assert len(list(tmp_path.glob('test_*.json'))) == 10
runner.cleanup_old(keep_latest=3)
remaining = list(tmp_path.glob('test_*.json'))
assert len(remaining) == 3
remaining_names = {f.stem for f in remaining}
assert 'test_00000007' in remaining_names or 'test_00000008' in remaining_names
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_benchmark.py:441*

### test_comparison_report_overall_improvement

**Category**: workflow  
**Description**: Workflow: Test ComparisonReport overall_improvement property.  
**Expected**: assert '✅' in improvement  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test ComparisonReport overall_improvement property.'
from skill_seekers.benchmark.models import ComparisonReport
baseline = BenchmarkReport(name='baseline', started_at=datetime.utcnow(), finished_at=datetime.utcnow(), total_duration=10.0, timings=[], memory=[], metrics=[], system_info={}, recommendations=[])
current = BenchmarkReport(name='current', started_at=datetime.utcnow(), finished_at=datetime.utcnow(), total_duration=5.0, timings=[], memory=[], metrics=[], system_info={}, recommendations=[])
comparison = ComparisonReport(name='test', baseline=baseline, current=current, improvements=[], regressions=[], speedup_factor=2.0, memory_change_mb=0.0)
improvement = comparison.overall_improvement
assert '100.0% faster' in improvement
assert '✅' in improvement
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_benchmark.py:586*

### test_init_preserves_existing_registry

**Category**: workflow  
**Description**: Workflow: Test that initialization doesn't overwrite existing registry.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_config_dir

"Test that initialization doesn't overwrite existing registry."
registry_file = temp_config_dir / 'sources.json'
existing_data = {'version': '1.0', 'sources': [{'name': 'test', 'git_url': 'https://example.com/repo.git'}]}
with open(registry_file, 'w') as f:
    json.dump(existing_data, f)
_manager = SourceManager(config_dir=str(temp_config_dir))
with open(registry_file) as f:
    data = json.load(f)
    assert len(data['sources']) == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_source_manager.py:51*

### test_add_source_full_parameters

**Category**: workflow  
**Description**: Workflow: Test adding source with all parameters.  
**Expected**: assert source['enabled'] is False  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: source_manager

'Test adding source with all parameters.'
source = source_manager.add_source(name='company', git_url='https://gitlab.company.com/platform/configs.git', source_type='gitlab', token_env='CUSTOM_TOKEN', branch='develop', priority=1, enabled=False)
assert source['name'] == 'company'
assert source['type'] == 'gitlab'
assert source['token_env'] == 'CUSTOM_TOKEN'
assert source['branch'] == 'develop'
assert source['priority'] == 1
assert source['enabled'] is False
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_source_manager.py:98*

### sample_skill_dir

**Category**: workflow  
**Description**: Workflow: Create a sample skill for integration testing.  
**Confidence**: 0.90  
**Tags**: pytest, workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Create a sample skill for integration testing.'
skill_dir = tmp_path / 'test_integration_skill'
skill_dir.mkdir()
skill_md = '# Integration Test Skill\n\nThis is a test skill for integration testing with vector databases.\n\n## Core Concepts\n\n- Concept 1: Understanding vector embeddings\n- Concept 2: Similarity search algorithms\n- Concept 3: Metadata filtering\n\n## Quick Start\n\nGet started with vector databases in 3 steps:\n1. Initialize your database\n2. Upload your documents\n3. Query with semantic search\n'
(skill_dir / 'SKILL.md').write_text(skill_md)
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
references = {'api_reference.md': '# API Reference\n\n## Core Functions\n\n### add_documents(documents, metadata)\nAdd documents to the vector database.\n\n### query(text, limit=10)\nQuery the database with semantic search.\n\n### delete_collection(name)\nDelete a collection from the database.\n', 'getting_started.md': '# Getting Started\n\n## Installation\n\n```bash\npip install vector-db-client\n```\n\n## Basic Usage\n\n```python\nfrom vector_db import Client\n\nclient = Client("http://localhost:8080")\nclient.add_documents(["doc1", "doc2"])\nresults = client.query("search query")\n```\n', 'advanced_features.md': '# Advanced Features\n\n## Hybrid Search\n\nCombine keyword and vector search for better results.\n\n## Metadata Filtering\n\nFilter results based on metadata attributes.\n\n## Multi-modal Search\n\nSearch across text, images, and audio.\n'}
for filename, content in references.items():
    (refs_dir / filename).write_text(content)
return skill_dir
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration_adaptors.py:29*

### test_chroma_query_filtering

**Category**: workflow  
**Description**: Workflow: Test metadata filtering in ChromaDB queries.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: sample_skill_dir, tmp_path

'Test metadata filtering in ChromaDB queries.'
try:
    import chromadb
except ImportError:
    pytest.skip('chromadb not installed')
if not check_service_available('http://localhost:8000/api/v1/heartbeat'):
    pytest.skip('ChromaDB not running')
try:
    client = chromadb.HttpClient(host='localhost', port=8000)
    client.heartbeat()
except Exception as e:
    pytest.skip(f'Cannot connect to ChromaDB: {e}')
adaptor = get_adaptor('chroma')
metadata = SkillMetadata(name='chroma_filter_test', description='Test filtering capabilities')
package_path = adaptor.package(sample_skill_dir, tmp_path)
with open(package_path) as f:
    data = json.load(f)
collection_name = data['collection_name']
try:
    collection = client.get_or_create_collection(name=collection_name)
    collection.add(documents=data['documents'], metadatas=data['metadatas'], ids=data['ids'])
    time.sleep(1)
    results = collection.get(where={'category': 'getting started'})
    assert len(results['documents']) > 0, 'No documents matched filter'
    for metadata in results['metadatas']:
        assert metadata['category'] == 'getting started', 'Filter returned wrong category'
finally:
    with contextlib.suppress(Exception):
        client.delete_collection(name=collection_name)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration_adaptors.py:357*

### test_factory_method_detection

**Category**: workflow  
**Description**: Workflow: Test detection of create/make methods  
**Expected**: self.assertIn('create', ' '.join(pattern.evidence).lower())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.detector = FactoryDetector(depth='deep')
self.recognizer = PatternRecognizer(depth='deep')

'Test detection of create/make methods'
code = "\nclass VehicleFactory:\n    def create(self, vehicle_type):\n        if vehicle_type == 'car':\n            return Car()\n        elif vehicle_type == 'truck':\n            return Truck()\n\n    def make_vehicle(self, specs):\n        return Vehicle(specs)\n"
report = self.recognizer.analyze_file('test.py', code, 'Python')
patterns = [p for p in report.patterns if p.pattern_type == 'Factory']
self.assertGreater(len(patterns), 0)
pattern = patterns[0]
self.assertIn('create', ' '.join(pattern.evidence).lower())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pattern_recognizer.py:135*

### test_observer_triplet_detection

**Category**: workflow  
**Description**: Workflow: Test classic attach/detach/notify triplet  
**Expected**: self.assertTrue('attach' in evidence_str and 'detach' in evidence_str and ('notify' in evidence_str))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.detector = ObserverDetector(depth='deep')
self.recognizer = PatternRecognizer(depth='deep')

'Test classic attach/detach/notify triplet'
code = '\nclass Subject:\n    def __init__(self):\n        self.observers = []\n\n    def attach(self, observer):\n        self.observers.append(observer)\n\n    def detach(self, observer):\n        self.observers.remove(observer)\n\n    def notify(self):\n        for observer in self.observers:\n            observer.update()\n'
report = self.recognizer.analyze_file('test.py', code, 'Python')
patterns = [p for p in report.patterns if p.pattern_type == 'Observer']
self.assertGreater(len(patterns), 0)
pattern = patterns[0]
self.assertGreaterEqual(pattern.confidence, 0.8)
evidence_str = ' '.join(pattern.evidence).lower()
self.assertTrue('attach' in evidence_str and 'detach' in evidence_str and ('notify' in evidence_str))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pattern_recognizer.py:199*

### test_pattern_report_summary

**Category**: workflow  
**Description**: Workflow: Test PatternReport.get_summary() method  
**Expected**: self.assertIsInstance(summary, dict)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.recognizer = PatternRecognizer(depth='deep')

'Test PatternReport.get_summary() method'
code = '\nclass LoggerSingleton:\n    _instance = None\n\n    def getInstance(self):\n        return self._instance\n\nclass LoggerFactory:\n    def create_logger(self, type):\n        return Logger(type)\n'
report = self.recognizer.analyze_file('logging.py', code, 'Python')
summary = report.get_summary()
self.assertIsInstance(summary, dict)
if summary:
    total_count = sum(summary.values())
    self.assertGreater(total_count, 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pattern_recognizer.py:329*

### test_factory_method_detection

**Category**: workflow  
**Description**: Workflow: Test detection of create/make methods  
**Expected**: self.assertIn('create', ' '.join(pattern.evidence).lower())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test detection of create/make methods'
code = "\nclass VehicleFactory:\n    def create(self, vehicle_type):\n        if vehicle_type == 'car':\n            return Car()\n        elif vehicle_type == 'truck':\n            return Truck()\n\n    def make_vehicle(self, specs):\n        return Vehicle(specs)\n"
report = self.recognizer.analyze_file('test.py', code, 'Python')
patterns = [p for p in report.patterns if p.pattern_type == 'Factory']
self.assertGreater(len(patterns), 0)
pattern = patterns[0]
self.assertIn('create', ' '.join(pattern.evidence).lower())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pattern_recognizer.py:135*

### test_observer_triplet_detection

**Category**: workflow  
**Description**: Workflow: Test classic attach/detach/notify triplet  
**Expected**: self.assertTrue('attach' in evidence_str and 'detach' in evidence_str and ('notify' in evidence_str))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test classic attach/detach/notify triplet'
code = '\nclass Subject:\n    def __init__(self):\n        self.observers = []\n\n    def attach(self, observer):\n        self.observers.append(observer)\n\n    def detach(self, observer):\n        self.observers.remove(observer)\n\n    def notify(self):\n        for observer in self.observers:\n            observer.update()\n'
report = self.recognizer.analyze_file('test.py', code, 'Python')
patterns = [p for p in report.patterns if p.pattern_type == 'Observer']
self.assertGreater(len(patterns), 0)
pattern = patterns[0]
self.assertGreaterEqual(pattern.confidence, 0.8)
evidence_str = ' '.join(pattern.evidence).lower()
self.assertTrue('attach' in evidence_str and 'detach' in evidence_str and ('notify' in evidence_str))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pattern_recognizer.py:199*

### test_pattern_report_summary

**Category**: workflow  
**Description**: Workflow: Test PatternReport.get_summary() method  
**Expected**: self.assertIsInstance(summary, dict)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test PatternReport.get_summary() method'
code = '\nclass LoggerSingleton:\n    _instance = None\n\n    def getInstance(self):\n        return self._instance\n\nclass LoggerFactory:\n    def create_logger(self, type):\n        return Logger(type)\n'
report = self.recognizer.analyze_file('logging.py', code, 'Python')
summary = report.get_summary()
self.assertIsInstance(summary, dict)
if summary:
    total_count = sum(summary.values())
    self.assertGreater(total_count, 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pattern_recognizer.py:329*

### test_generator_compute_hash

**Category**: workflow  
**Description**: Workflow: Test hash computation.  
**Expected**: assert hash1 != hash4  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test hash computation.'
hash1 = EmbeddingGenerator.compute_hash('text1', 'model1')
hash2 = EmbeddingGenerator.compute_hash('text1', 'model1')
hash3 = EmbeddingGenerator.compute_hash('text2', 'model1')
hash4 = EmbeddingGenerator.compute_hash('text1', 'model2')
assert hash1 == hash2
assert hash1 != hash3
assert hash1 != hash4
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding.py:165*

### test_cache_persistence

**Category**: workflow  
**Description**: Workflow: Test cache persistence to file.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test cache persistence to file.'
with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
    tmp_path = tmp.name
try:
    cache1 = EmbeddingCache(tmp_path)
    cache1.set('hash1', [0.1, 0.2, 0.3], 'model1')
    cache1.close()
    cache2 = EmbeddingCache(tmp_path)
    retrieved = cache2.get('hash1')
    assert retrieved == [0.1, 0.2, 0.3]
    cache2.close()
finally:
    Path(tmp_path).unlink(missing_ok=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding.py:349*

### test_format_skill_md

**Category**: workflow  
**Description**: Workflow: Test formatting SKILL.md as Haystack Documents.  
**Expected**: assert 'getting started' in categories or 'api' in categories  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test formatting SKILL.md as Haystack Documents.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
skill_md = skill_dir / 'SKILL.md'
skill_md.write_text('# Test Skill\n\nThis is a test skill for Haystack format.')
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start.')
(refs_dir / 'api.md').write_text('# API Reference\n\nAPI docs.')
adaptor = get_adaptor('haystack')
metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
documents_json = adaptor.format_skill_md(skill_dir, metadata)
documents = json.loads(documents_json)
assert len(documents) == 3
for doc in documents:
    assert 'content' in doc
    assert 'meta' in doc
    assert doc['meta']['source'] == 'test_skill'
    assert doc['meta']['version'] == '1.0.0'
    assert 'category' in doc['meta']
    assert 'file' in doc['meta']
    assert 'type' in doc['meta']
categories = {doc['meta']['category'] for doc in documents}
assert 'overview' in categories
assert 'getting started' in categories or 'api' in categories
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_haystack_adaptor.py:23*

### test_package_creates_json

**Category**: workflow  
**Description**: Workflow: Test packaging skill into JSON file.  
**Expected**: assert 'meta' in documents[0]  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test packaging skill into JSON file.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('haystack')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.exists()
assert output_path.suffix == '.json'
assert 'haystack' in output_path.name
with open(output_path) as f:
    documents = json.load(f)
assert isinstance(documents, list)
assert len(documents) > 0
assert 'content' in documents[0]
assert 'meta' in documents[0]
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_haystack_adaptor.py:65*

### test_package_output_filename

**Category**: workflow  
**Description**: Workflow: Test package output filename generation.  
**Expected**: assert 'haystack' in output_path.name  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test package output filename generation.'
skill_dir = tmp_path / 'react'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# React\n\nReact docs.')
adaptor = get_adaptor('haystack')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.name == 'react-haystack.json'
output_path = adaptor.package(skill_dir, tmp_path / 'test.zip')
assert output_path.suffix == '.json'
assert 'haystack' in output_path.name
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_haystack_adaptor.py:90*

### test_empty_skill_directory

**Category**: workflow  
**Description**: Workflow: Test handling of empty skill directory.  
**Expected**: assert documents == []  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test handling of empty skill directory.'
skill_dir = tmp_path / 'empty_skill'
skill_dir.mkdir()
adaptor = get_adaptor('haystack')
metadata = SkillMetadata(name='empty_skill', description='Empty', version='1.0.0')
documents_json = adaptor.format_skill_md(skill_dir, metadata)
documents = json.loads(documents_json)
assert documents == []
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_haystack_adaptor.py:147*

### test_references_only

**Category**: workflow  
**Description**: Workflow: Test skill with references but no SKILL.md.  
**Expected**: assert documents[0]['meta']['type'] == 'reference'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test skill with references but no SKILL.md.'
skill_dir = tmp_path / 'refs_only'
skill_dir.mkdir()
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'test.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('haystack')
metadata = SkillMetadata(name='refs_only', description='Refs only', version='1.0.0')
documents_json = adaptor.format_skill_md(skill_dir, metadata)
documents = json.loads(documents_json)
assert len(documents) == 1
assert documents[0]['meta']['category'] == 'test'
assert documents[0]['meta']['type'] == 'reference'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_haystack_adaptor.py:161*

### test_walk_with_subdirectories

**Category**: workflow  
**Description**: Workflow: Test walking nested directory structure.  
**Expected**: self.assertIn('test_module.py', filenames)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.mkdtemp()
self.root = Path(self.temp_dir)

'Test walking nested directory structure.'
src_dir = self.root / 'src'
src_dir.mkdir()
(src_dir / 'module.py').write_text('test')
tests_dir = self.root / 'tests'
tests_dir.mkdir()
(tests_dir / 'test_module.py').write_text('test')
files = walk_directory(self.root)
self.assertEqual(len(files), 2)
filenames = [f.name for f in files]
self.assertIn('module.py', filenames)
self.assertIn('test_module.py', filenames)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_codebase_scraper.py:159*

### test_no_duplicate_directories_created

**Category**: workflow  
**Description**: Workflow: Test that source directories are cleaned up after copying to references/ (Issue #279).  
**Expected**: self.assertTrue(references_dir.exists(), 'references/ should exist')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Create temporary directory for testing.'
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir) / 'output'
self.output_dir.mkdir()

'Test that source directories are cleaned up after copying to references/ (Issue #279).'
test_dirs = ['documentation', 'api_reference', 'patterns']
for dir_name in test_dirs:
    dir_path = self.output_dir / dir_name
    dir_path.mkdir()
    (dir_path / 'test.txt').write_text(f'Test content for {dir_name}')
_generate_references(self.output_dir)
references_dir = self.output_dir / 'references'
self.assertTrue(references_dir.exists(), 'references/ should exist')
for dir_name in test_dirs:
    ref_path = references_dir / dir_name
    self.assertTrue(ref_path.exists(), f'references/{dir_name} should exist')
    self.assertTrue((ref_path / 'test.txt').exists(), f'references/{dir_name}/test.txt should exist')
for dir_name in test_dirs:
    source_path = self.output_dir / dir_name
    self.assertFalse(source_path.exists(), f'Source directory {dir_name}/ should be cleaned up to avoid duplication')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_codebase_scraper.py:411*

### test_no_disk_space_wasted

**Category**: workflow  
**Description**: Workflow: Test that disk space is not wasted by duplicate directories.  
**Expected**: self.assertEqual((ref_doc_dir / 'large_file.txt').read_text(), test_content, 'File content should be preserved')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Create temporary directory for testing.'
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir) / 'output'
self.output_dir.mkdir()

'Test that disk space is not wasted by duplicate directories.'
doc_dir = self.output_dir / 'documentation'
doc_dir.mkdir()
test_content = 'x' * 1000
(doc_dir / 'large_file.txt').write_text(test_content)
_generate_references(self.output_dir)
ref_doc_dir = self.output_dir / 'references' / 'documentation'
source_doc_dir = self.output_dir / 'documentation'
self.assertTrue(ref_doc_dir.exists(), 'references/documentation/ should exist')
self.assertFalse(source_doc_dir.exists(), 'Source documentation/ should not exist (cleaned up)')
self.assertTrue((ref_doc_dir / 'large_file.txt').exists(), 'File should exist in references/')
self.assertEqual((ref_doc_dir / 'large_file.txt').read_text(), test_content, 'File content should be preserved')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_codebase_scraper.py:445*

### test_walk_with_subdirectories

**Category**: workflow  
**Description**: Workflow: Test walking nested directory structure.  
**Expected**: self.assertIn('test_module.py', filenames)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test walking nested directory structure.'
src_dir = self.root / 'src'
src_dir.mkdir()
(src_dir / 'module.py').write_text('test')
tests_dir = self.root / 'tests'
tests_dir.mkdir()
(tests_dir / 'test_module.py').write_text('test')
files = walk_directory(self.root)
self.assertEqual(len(files), 2)
filenames = [f.name for f in files]
self.assertIn('module.py', filenames)
self.assertIn('test_module.py', filenames)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_codebase_scraper.py:159*

### test_no_duplicate_directories_created

**Category**: workflow  
**Description**: Workflow: Test that source directories are cleaned up after copying to references/ (Issue #279).  
**Expected**: self.assertTrue(references_dir.exists(), 'references/ should exist')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test that source directories are cleaned up after copying to references/ (Issue #279).'
test_dirs = ['documentation', 'api_reference', 'patterns']
for dir_name in test_dirs:
    dir_path = self.output_dir / dir_name
    dir_path.mkdir()
    (dir_path / 'test.txt').write_text(f'Test content for {dir_name}')
_generate_references(self.output_dir)
references_dir = self.output_dir / 'references'
self.assertTrue(references_dir.exists(), 'references/ should exist')
for dir_name in test_dirs:
    ref_path = references_dir / dir_name
    self.assertTrue(ref_path.exists(), f'references/{dir_name} should exist')
    self.assertTrue((ref_path / 'test.txt').exists(), f'references/{dir_name}/test.txt should exist')
for dir_name in test_dirs:
    source_path = self.output_dir / dir_name
    self.assertFalse(source_path.exists(), f'Source directory {dir_name}/ should be cleaned up to avoid duplication')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_codebase_scraper.py:411*

### test_no_disk_space_wasted

**Category**: workflow  
**Description**: Workflow: Test that disk space is not wasted by duplicate directories.  
**Expected**: self.assertEqual((ref_doc_dir / 'large_file.txt').read_text(), test_content, 'File content should be preserved')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test that disk space is not wasted by duplicate directories.'
doc_dir = self.output_dir / 'documentation'
doc_dir.mkdir()
test_content = 'x' * 1000
(doc_dir / 'large_file.txt').write_text(test_content)
_generate_references(self.output_dir)
ref_doc_dir = self.output_dir / 'references' / 'documentation'
source_doc_dir = self.output_dir / 'documentation'
self.assertTrue(ref_doc_dir.exists(), 'references/documentation/ should exist')
self.assertFalse(source_doc_dir.exists(), 'Source documentation/ should not exist (cleaned up)')
self.assertTrue((ref_doc_dir / 'large_file.txt').exists(), 'File should exist in references/')
self.assertEqual((ref_doc_dir / 'large_file.txt').read_text(), test_content, 'File content should be preserved')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_codebase_scraper.py:445*

### test_build_agent_command_claude

**Category**: workflow  
**Description**: Workflow: Test Claude Code command building.  
**Expected**: assert uses_file is True  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test Claude Code command building.'
skill_dir = _make_skill_dir(tmp_path)
enhancer = LocalSkillEnhancer(skill_dir, agent='claude')
prompt_file = str(tmp_path / 'prompt.txt')
cmd_parts, uses_file = enhancer._build_agent_command(prompt_file, True)
assert cmd_parts[0] == 'claude'
assert '--dangerously-skip-permissions' in cmd_parts
assert prompt_file in cmd_parts
assert uses_file is True
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_enhance_skill_local.py:32*

### test_build_agent_command_codex

**Category**: workflow  
**Description**: Workflow: Test Codex CLI command building.  
**Expected**: assert uses_file is False  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test Codex CLI command building.'
skill_dir = _make_skill_dir(tmp_path)
enhancer = LocalSkillEnhancer(skill_dir, agent='codex')
prompt_file = str(tmp_path / 'prompt.txt')
cmd_parts, uses_file = enhancer._build_agent_command(prompt_file, False)
assert cmd_parts[0] == 'codex'
assert 'exec' in cmd_parts
assert '--full-auto' in cmd_parts
assert '--skip-git-repo-check' in cmd_parts
assert uses_file is False
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_enhance_skill_local.py:45*

### test_build_agent_command_custom_with_placeholder

**Category**: workflow  
**Description**: Workflow: Test custom command with {prompt_file} placeholder.  
**Expected**: assert uses_file is True  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

'Test custom command with {prompt_file} placeholder.'
_allow_executable(monkeypatch, name='my-agent')
skill_dir = _make_skill_dir(tmp_path)
enhancer = LocalSkillEnhancer(skill_dir, agent='custom', agent_cmd='my-agent --input {prompt_file}')
prompt_file = str(tmp_path / 'prompt.txt')
cmd_parts, uses_file = enhancer._build_agent_command(prompt_file, False)
assert cmd_parts[0] == 'my-agent'
assert '--input' in cmd_parts
assert prompt_file in cmd_parts
assert uses_file is True
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_enhance_skill_local.py:59*

### test_langchain_no_chunking_default

**Category**: workflow  
**Description**: Workflow: Test that LangChain doesn't chunk by default.  
**Expected**: assert len(data) == 2, f'Expected 2 docs, got {len(data)}'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

"Test that LangChain doesn't chunk by default."
skill_dir = create_test_skill(tmp_path, large_doc=True)
adaptor = get_adaptor('langchain')
package_path = adaptor.package(skill_dir, tmp_path)
with open(package_path) as f:
    data = json.load(f)
assert len(data) == 2, f'Expected 2 docs, got {len(data)}'
for doc in data:
    assert 'is_chunked' not in doc['metadata']
    assert 'chunk_index' not in doc['metadata']
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_chunking_integration.py:59*

### test_langchain_chunking_enabled

**Category**: workflow  
**Description**: Workflow: Test that LangChain chunks large documents when enabled.  
**Expected**: assert len(chunked_docs) > 0, 'Should have chunked documents'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test that LangChain chunks large documents when enabled.'
skill_dir = create_test_skill(tmp_path, large_doc=True)
adaptor = get_adaptor('langchain')
package_path = adaptor.package(skill_dir, tmp_path, enable_chunking=True, chunk_max_tokens=512)
with open(package_path) as f:
    data = json.load(f)
assert len(data) > 2, f'Large doc should be chunked, got {len(data)} docs'
chunked_docs = [doc for doc in data if doc['metadata'].get('is_chunked')]
assert len(chunked_docs) > 0, 'Should have chunked documents'
for doc in chunked_docs:
    assert 'chunk_index' in doc['metadata']
    assert 'total_chunks' in doc['metadata']
    assert 'chunk_id' in doc['metadata']
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_chunking_integration.py:81*

### test_chunking_preserves_small_docs

**Category**: workflow  
**Description**: Workflow: Test that small documents are not chunked.  
**Expected**: assert len(data) == 2, 'Small docs should not be chunked'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test that small documents are not chunked.'
skill_dir = create_test_skill(tmp_path, large_doc=False)
adaptor = get_adaptor('langchain')
package_path = adaptor.package(skill_dir, tmp_path, enable_chunking=True, chunk_max_tokens=512)
with open(package_path) as f:
    data = json.load(f)
assert len(data) == 2, 'Small docs should not be chunked'
for doc in data:
    assert 'is_chunked' not in doc['metadata']
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_chunking_integration.py:106*

### test_preserve_code_blocks

**Category**: workflow  
**Description**: Workflow: Test that code blocks are not split during chunking.  
**Expected**: assert len(code_chunks) >= 1, 'Code block should be preserved'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test that code blocks are not split during chunking.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
content = '# Test\n\nSome intro text that needs to be here for context.\n\n```python\ndef example_function():\n    # This code block should not be split\n    x = 1\n    y = 2\n    z = 3\n    return x + y + z\n```\n\nMore content after code block.\n' + 'Lorem ipsum dolor sit amet. ' * 1000
(skill_dir / 'SKILL.md').write_text(content)
(skill_dir / 'references').mkdir()
adaptor = get_adaptor('langchain')
package_path = adaptor.package(skill_dir, tmp_path, enable_chunking=True, chunk_max_tokens=200, preserve_code_blocks=True)
with open(package_path) as f:
    data = json.load(f)
code_chunks = [doc for doc in data if '```python' in doc['page_content']]
assert len(code_chunks) >= 1, 'Code block should be preserved'
for chunk in code_chunks:
    content = chunk['page_content']
    if '```python' in content:
        assert content.count('```') >= 2, 'Code block should be complete'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_chunking_integration.py:128*

### test_maybe_chunk_content_disabled

**Category**: workflow  
**Description**: Workflow: Test that _maybe_chunk_content returns single chunk when disabled.  
**Expected**: assert chunks[0][1] == metadata  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that _maybe_chunk_content returns single chunk when disabled.'
from skill_seekers.cli.adaptors.langchain import LangChainAdaptor
adaptor = LangChainAdaptor()
content = 'Test content ' * 1000
metadata = {'source': 'test'}
chunks = adaptor._maybe_chunk_content(content, metadata, enable_chunking=False)
assert len(chunks) == 1
assert chunks[0][0] == content
assert chunks[0][1] == metadata
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_chunking_integration.py:225*

### test_maybe_chunk_content_small_doc

**Category**: workflow  
**Description**: Workflow: Test that small docs are not chunked even when enabled.  
**Expected**: assert len(chunks) == 1  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that small docs are not chunked even when enabled.'
from skill_seekers.cli.adaptors.langchain import LangChainAdaptor
adaptor = LangChainAdaptor()
content = 'Small test content'
metadata = {'source': 'test'}
chunks = adaptor._maybe_chunk_content(content, metadata, enable_chunking=True, chunk_max_tokens=512)
assert len(chunks) == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_chunking_integration.py:241*

### test_maybe_chunk_content_large_doc

**Category**: workflow  
**Description**: Workflow: Test that large docs are chunked when enabled.  
**Expected**: assert len(chunks) > 1, f'Large doc should be chunked, got {len(chunks)} chunks'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that large docs are chunked when enabled.'
from skill_seekers.cli.adaptors.langchain import LangChainAdaptor
adaptor = LangChainAdaptor()
content = 'Lorem ipsum dolor sit amet. ' * 2000
metadata = {'source': 'test', 'file': 'test.md'}
chunks = adaptor._maybe_chunk_content(content, metadata, enable_chunking=True, chunk_max_tokens=512, preserve_code_blocks=True, source_file='test.md')
assert len(chunks) > 1, f'Large doc should be chunked, got {len(chunks)} chunks'
for chunk_text, chunk_meta in chunks:
    assert isinstance(chunk_text, str)
    assert isinstance(chunk_meta, dict)
    assert chunk_meta['is_chunked']
    assert 'chunk_index' in chunk_meta
    assert 'chunk_id' in chunk_meta
    assert chunk_meta['source'] == 'test'
    assert chunk_meta['file'] == 'test.md'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_chunking_integration.py:257*

### test_chunk_tokens_parameter

**Category**: workflow  
**Description**: Workflow: Test --chunk-tokens parameter controls chunk size.  
**Expected**: assert len(data_small) > len(data_large), f'Small chunks ({len(data_small)}) should be more than large chunks ({len(data_large)})'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test --chunk-tokens parameter controls chunk size.'
from skill_seekers.cli.package_skill import package_skill
skill_dir = create_test_skill(tmp_path, large_doc=True)
success, package_path = package_skill(skill_dir=skill_dir, open_folder_after=False, skip_quality_check=True, target='langchain', enable_chunking=True, chunk_max_tokens=256, preserve_code_blocks=True)
assert success
with open(package_path) as f:
    data_small = json.load(f)
success, package_path2 = package_skill(skill_dir=skill_dir, open_folder_after=False, skip_quality_check=True, target='langchain', enable_chunking=True, chunk_max_tokens=1024, preserve_code_blocks=True)
assert success
with open(package_path2) as f:
    data_large = json.load(f)
assert len(data_small) > len(data_large), f'Small chunks ({len(data_small)}) should be more than large chunks ({len(data_large)})'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_chunking_integration.py:318*

### test_terminal_launch_error_handling

**Category**: workflow  
**Description**: Workflow: Test error handling when terminal launch fails.  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
'Save original environment variables.'
self.original_skill_seeker = os.environ.get('SKILL_SEEKER_TERMINAL')
self.original_term_program = os.environ.get('TERM_PROGRAM')

'Test error handling when terminal launch fails.'
if sys.platform != 'darwin':
    self.skipTest('This test only runs on macOS')
mock_popen.side_effect = Exception('Terminal not found')
import tempfile
with tempfile.TemporaryDirectory() as tmpdir:
    skill_dir = Path(tmpdir) / 'test_skill'
    skill_dir.mkdir()
    (skill_dir / 'references').mkdir()
    (skill_dir / 'references' / 'test.md').write_text('# Test')
    (skill_dir / 'SKILL.md').write_text('---\nname: test\n---\n# Test')
    enhancer = LocalSkillEnhancer(skill_dir)
    from io import StringIO
    captured_output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured_output
    result = enhancer.run(headless=False)
    sys.stdout = old_stdout
    self.assertFalse(result)
    output = captured_output.getvalue()
    self.assertIn('Error launching', output)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_terminal_detection.py:218*

### test_terminal_launch_error_handling

**Category**: workflow  
**Description**: Workflow: Test error handling when terminal launch fails.  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
# Fixtures: mock_popen

'Test error handling when terminal launch fails.'
if sys.platform != 'darwin':
    self.skipTest('This test only runs on macOS')
mock_popen.side_effect = Exception('Terminal not found')
import tempfile
with tempfile.TemporaryDirectory() as tmpdir:
    skill_dir = Path(tmpdir) / 'test_skill'
    skill_dir.mkdir()
    (skill_dir / 'references').mkdir()
    (skill_dir / 'references' / 'test.md').write_text('# Test')
    (skill_dir / 'SKILL.md').write_text('---\nname: test\n---\n# Test')
    enhancer = LocalSkillEnhancer(skill_dir)
    from io import StringIO
    captured_output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured_output
    result = enhancer.run(headless=False)
    sys.stdout = old_stdout
    self.assertFalse(result)
    output = captured_output.getvalue()
    self.assertIn('Error launching', output)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_terminal_detection.py:218*

### test_detect_from_html_with_css_class

**Category**: workflow  
**Description**: Workflow: Test HTML element with CSS class  
**Expected**: assert confidence == 1.0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test HTML element with CSS class'
detector = LanguageDetector()
html = '<code class="language-python">print("hello")</code>'
soup = BeautifulSoup(html, 'html.parser')
elem = soup.find('code')
lang, confidence = detector.detect_from_html(elem, 'print("hello")')
assert lang == 'python'
assert confidence == 1.0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_language_detector.py:77*

### test_detect_from_html_with_parent_class

**Category**: workflow  
**Description**: Workflow: Test parent <pre> element with CSS class  
**Expected**: assert confidence == 1.0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test parent <pre> element with CSS class'
detector = LanguageDetector()
html = '<pre class="language-java"><code>System.out.println("hello");</code></pre>'
soup = BeautifulSoup(html, 'html.parser')
elem = soup.find('code')
lang, confidence = detector.detect_from_html(elem, 'System.out.println("hello");')
assert lang == 'java'
assert confidence == 1.0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_language_detector.py:90*

### test_unity_lifecycle_methods

**Category**: workflow  
**Description**: Workflow: Test Unity lifecycle method detection  
**Expected**: assert confidence >= 0.5  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test Unity lifecycle method detection'
detector = LanguageDetector()
code = '\n        void Awake() { }\n        void Start() { }\n        void Update() { }\n        void FixedUpdate() { }\n        void LateUpdate() { }\n        '
lang, confidence = detector.detect_from_code(code)
assert lang == 'csharp'
assert confidence >= 0.5
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_language_detector.py:128*

### test_unity_namespace

**Category**: workflow  
**Description**: Workflow: Test Unity namespace detection  
**Expected**: assert confidence >= 0.5  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test Unity namespace detection'
detector = LanguageDetector()
code = 'using UnityEngine;'
lang, confidence = detector.detect_from_code(code)
assert lang == 'csharp'
assert confidence >= 0.5
code = '\n        using UnityEngine;\n        using System.Collections;\n        '
lang, confidence = detector.detect_from_code(code)
assert lang == 'csharp'
assert confidence >= 0.5
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_language_detector.py:190*

### test_unity_full_script

**Category**: workflow  
**Description**: Workflow: Test complete Unity script (high confidence expected)  
**Expected**: assert confidence >= 0.9  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test complete Unity script (high confidence expected)'
detector = LanguageDetector()
code = '\n        using UnityEngine;\n        using System.Collections;\n\n        public class PlayerController : MonoBehaviour\n        {\n            [SerializeField]\n            private float speed = 5.0f;\n\n            [SerializeField]\n            private Rigidbody rb;\n\n            void Awake()\n            {\n                rb = GetComponent<Rigidbody>();\n            }\n\n            void Update()\n            {\n                float moveH = Input.GetAxis("Horizontal");\n                float moveV = Input.GetAxis("Vertical");\n\n                Vector3 movement = new Vector3(moveH, 0, moveV);\n                rb.AddForce(movement * speed);\n            }\n\n            IEnumerator DashCoroutine()\n            {\n                speed *= 2;\n                yield return new WaitForSeconds(0.5f);\n                speed /= 2;\n            }\n        }\n        '
lang, confidence = detector.detect_from_code(code)
assert lang == 'csharp'
assert confidence >= 0.9
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_language_detector.py:256*

### test_backward_compatibility_with_doc_scraper

**Category**: workflow  
**Description**: Workflow: Test that detector can be used as drop-in replacement  
**Expected**: assert 0.0 <= confidence <= 1.0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that detector can be used as drop-in replacement'
detector = LanguageDetector()
html = '<code class="language-python">import os\nprint("hello")</code>'
soup = BeautifulSoup(html, 'html.parser')
elem = soup.find('code')
code = elem.get_text()
lang, confidence = detector.detect_from_html(elem, code)
assert isinstance(lang, str)
assert isinstance(confidence, float)
assert lang == 'python'
assert 0.0 <= confidence <= 1.0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_language_detector.py:688*

### test_format_skill_md

**Category**: workflow  
**Description**: Workflow: Test formatting SKILL.md as FAISS index data.  
**Expected**: assert 'getting started' in categories or 'api' in categories  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test formatting SKILL.md as FAISS index data.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
skill_md = skill_dir / 'SKILL.md'
skill_md.write_text('# Test Skill\n\nThis is a test skill for FAISS format.')
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start.')
(refs_dir / 'api.md').write_text('# API Reference\n\nAPI docs.')
adaptor = get_adaptor('faiss')
metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
index_json = adaptor.format_skill_md(skill_dir, metadata)
index_data = json.loads(index_json)
assert 'documents' in index_data
assert 'metadatas' in index_data
assert 'ids' in index_data
assert 'config' in index_data
assert len(index_data['documents']) == 3
assert len(index_data['metadatas']) == 3
assert len(index_data['ids']) == 3
for meta in index_data['metadatas']:
    assert meta['source'] == 'test_skill'
    assert meta['version'] == '1.0.0'
    assert 'category' in meta
    assert 'file' in meta
    assert 'type' in meta
categories = {meta['category'] for meta in index_data['metadatas']}
assert 'overview' in categories
assert 'getting started' in categories or 'api' in categories
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_faiss_adaptor.py:23*

### test_package_creates_json

**Category**: workflow  
**Description**: Workflow: Test packaging skill into JSON file.  
**Expected**: assert len(index_data['documents']) > 0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test packaging skill into JSON file.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('faiss')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.exists()
assert output_path.suffix == '.json'
assert 'faiss' in output_path.name
with open(output_path) as f:
    index_data = json.load(f)
assert 'documents' in index_data
assert 'metadatas' in index_data
assert 'ids' in index_data
assert len(index_data['documents']) > 0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_faiss_adaptor.py:70*

### test_package_output_filename

**Category**: workflow  
**Description**: Workflow: Test package output filename generation.  
**Expected**: assert 'faiss' in output_path.name  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test package output filename generation.'
skill_dir = tmp_path / 'react'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# React\n\nReact docs.')
adaptor = get_adaptor('faiss')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.name == 'react-faiss.json'
output_path = adaptor.package(skill_dir, tmp_path / 'test.zip')
assert output_path.suffix == '.json'
assert 'faiss' in output_path.name
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_faiss_adaptor.py:95*

### test_empty_skill_directory

**Category**: workflow  
**Description**: Workflow: Test handling of empty skill directory.  
**Expected**: assert index_data['ids'] == []  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test handling of empty skill directory.'
skill_dir = tmp_path / 'empty_skill'
skill_dir.mkdir()
adaptor = get_adaptor('faiss')
metadata = SkillMetadata(name='empty_skill', description='Empty', version='1.0.0')
index_json = adaptor.format_skill_md(skill_dir, metadata)
index_data = json.loads(index_json)
assert index_data['documents'] == []
assert index_data['metadatas'] == []
assert index_data['ids'] == []
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_faiss_adaptor.py:151*

### test_references_only

**Category**: workflow  
**Description**: Workflow: Test skill with references but no SKILL.md.  
**Expected**: assert index_data['metadatas'][0]['type'] == 'reference'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test skill with references but no SKILL.md.'
skill_dir = tmp_path / 'refs_only'
skill_dir.mkdir()
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'test.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('faiss')
metadata = SkillMetadata(name='refs_only', description='Refs only', version='1.0.0')
index_json = adaptor.format_skill_md(skill_dir, metadata)
index_data = json.loads(index_json)
assert len(index_data['documents']) == 1
assert index_data['metadatas'][0]['category'] == 'test'
assert index_data['metadatas'][0]['type'] == 'reference'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_faiss_adaptor.py:167*

### test_local_provider_deterministic

**Category**: workflow  
**Description**: Workflow: Test local provider generates deterministic embeddings.  
**Expected**: assert emb1 == emb2  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test local provider generates deterministic embeddings.'
provider = LocalEmbeddingProvider(dimension=64)
text = 'same text'
emb1 = provider.generate_embeddings([text])[0]
emb2 = provider.generate_embeddings([text])[0]
assert emb1 == emb2
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding_pipeline.py:45*

### test_cache_memory

**Category**: workflow  
**Description**: Workflow: Test memory cache functionality.  
**Expected**: assert retrieved == embedding  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test memory cache functionality.'
cache = EmbeddingCache()
text = 'test text'
model = 'test-model'
embedding = [0.1, 0.2, 0.3]
cache.set(text, model, embedding)
retrieved = cache.get(text, model)
assert retrieved == embedding
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding_pipeline.py:65*

### test_pipeline_initialization

**Category**: workflow  
**Description**: Workflow: Test pipeline initialization.  
**Expected**: assert pipeline.cache is not None  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test pipeline initialization.'
config = EmbeddingConfig(provider='local', model='test-model', dimension=128, batch_size=10)
pipeline = EmbeddingPipeline(config)
assert pipeline.config == config
assert pipeline.provider is not None
assert pipeline.cache is not None
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding_pipeline.py:125*

### test_pipeline_generate_batch

**Category**: workflow  
**Description**: Workflow: Test batch embedding generation.  
**Expected**: assert result.cached_count == 0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test batch embedding generation.'
config = EmbeddingConfig(provider='local', model='test-model', dimension=64, batch_size=2)
pipeline = EmbeddingPipeline(config)
texts = ['doc 1', 'doc 2', 'doc 3']
result = pipeline.generate_batch(texts, show_progress=False)
assert len(result.embeddings) == 3
assert len(result.embeddings[0]) == 64
assert result.generated_count == 3
assert result.cached_count == 0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding_pipeline.py:136*

### test_pipeline_batch_processing

**Category**: workflow  
**Description**: Workflow: Test large batch is processed in chunks.  
**Expected**: assert len(result.embeddings) == 10  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test large batch is processed in chunks.'
config = EmbeddingConfig(provider='local', model='test-model', dimension=16, batch_size=3)
pipeline = EmbeddingPipeline(config)
texts = [f'doc {i}' for i in range(10)]
result = pipeline.generate_batch(texts, show_progress=False)
assert len(result.embeddings) == 10
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding_pipeline.py:177*

### test_validate_dimensions_valid

**Category**: workflow  
**Description**: Workflow: Test dimension validation with valid embeddings.  
**Expected**: assert is_valid  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test dimension validation with valid embeddings.'
config = EmbeddingConfig(provider='local', model='test-model', dimension=128)
pipeline = EmbeddingPipeline(config)
embeddings = [[0.1] * 128, [0.2] * 128]
is_valid = pipeline.validate_dimensions(embeddings)
assert is_valid
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding_pipeline.py:195*

### test_validate_dimensions_invalid

**Category**: workflow  
**Description**: Workflow: Test dimension validation with invalid embeddings.  
**Expected**: assert not is_valid  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test dimension validation with invalid embeddings.'
config = EmbeddingConfig(provider='local', model='test-model', dimension=128)
pipeline = EmbeddingPipeline(config)
embeddings = [[0.1] * 64, [0.2] * 128]
is_valid = pipeline.validate_dimensions(embeddings)
assert not is_valid
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding_pipeline.py:207*

### test_embedding_result_metadata

**Category**: workflow  
**Description**: Workflow: Test embedding result includes metadata.  
**Expected**: assert result.metadata['dimension'] == 256  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test embedding result includes metadata.'
config = EmbeddingConfig(provider='local', model='test-model', dimension=256)
pipeline = EmbeddingPipeline(config)
texts = ['test']
result = pipeline.generate_batch(texts, show_progress=False)
assert 'provider' in result.metadata
assert 'model' in result.metadata
assert 'dimension' in result.metadata
assert result.metadata['dimension'] == 256
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding_pipeline.py:220*

### test_cost_stats

**Category**: workflow  
**Description**: Workflow: Test cost statistics tracking.  
**Expected**: assert 'estimated_cost' in stats  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test cost statistics tracking.'
config = EmbeddingConfig(provider='local', model='test-model', dimension=64)
pipeline = EmbeddingPipeline(config)
texts = ['doc 1', 'doc 2']
pipeline.generate_batch(texts, show_progress=False)
stats = pipeline.get_cost_stats()
assert 'total_requests' in stats
assert 'cache_hits' in stats
assert 'estimated_cost' in stats
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding_pipeline.py:235*

### test_categorize_issues_basic

**Category**: workflow  
**Description**: Workflow: Test basic issue categorization.  
**Expected**: assert len(categorized['testing']) == 1  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test basic issue categorization.'
problems = [{'title': 'OAuth setup fails', 'labels': ['bug', 'oauth'], 'number': 1, 'state': 'open', 'comments': 10}, {'title': 'Testing framework issue', 'labels': ['testing'], 'number': 2, 'state': 'open', 'comments': 5}]
solutions = [{'title': 'Fixed OAuth redirect', 'labels': ['oauth'], 'number': 3, 'state': 'closed', 'comments': 3}]
topics = ['oauth', 'testing', 'async']
categorized = categorize_issues_by_topic(problems, solutions, topics)
assert 'oauth' in categorized
assert len(categorized['oauth']) == 2
assert 'testing' in categorized
assert len(categorized['testing']) == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_merge_sources_github.py:24*

### test_generate_hybrid_content_basic

**Category**: workflow  
**Description**: Workflow: Test basic hybrid content generation.  
**Expected**: assert len(hybrid['github_context']['top_labels']) == 2  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test basic hybrid content generation.'
api_data = {'apis': {'oauth_login': {'name': 'oauth_login', 'status': 'matched'}}, 'summary': {'total_apis': 1}}
github_docs = {'readme': '# Project README', 'contributing': None, 'docs_files': [{'path': 'docs/oauth.md', 'content': 'OAuth guide'}]}
github_insights = {'metadata': {'stars': 1234, 'forks': 56, 'language': 'Python', 'description': 'Test project'}, 'common_problems': [{'title': 'OAuth fails', 'number': 42, 'state': 'open', 'comments': 10, 'labels': ['bug']}], 'known_solutions': [{'title': 'Fixed OAuth', 'number': 35, 'state': 'closed', 'comments': 5, 'labels': ['bug']}], 'top_labels': [{'label': 'bug', 'count': 10}, {'label': 'enhancement', 'count': 5}]}
conflicts = []
hybrid = generate_hybrid_content(api_data, github_docs, github_insights, conflicts)
assert 'api_reference' in hybrid
assert 'github_context' in hybrid
assert 'conflict_summary' in hybrid
assert 'issue_links' in hybrid
assert hybrid['github_context']['docs']['readme'] == '# Project README'
assert hybrid['github_context']['docs']['docs_files_count'] == 1
assert hybrid['github_context']['metadata']['stars'] == 1234
assert hybrid['github_context']['metadata']['language'] == 'Python'
assert hybrid['github_context']['issues']['common_problems_count'] == 1
assert hybrid['github_context']['issues']['known_solutions_count'] == 1
assert len(hybrid['github_context']['issues']['top_problems']) == 1
assert len(hybrid['github_context']['top_labels']) == 2
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_merge_sources_github.py:133*

### test_generate_hybrid_content_with_conflicts

**Category**: workflow  
**Description**: Workflow: Test hybrid content with conflicts.  
**Expected**: assert hybrid['conflict_summary']['by_severity']['low'] == 1  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test hybrid content with conflicts.'
api_data = {'apis': {}, 'summary': {}}
github_docs = None
github_insights = None
conflicts = [Conflict(api_name='test_api', type='signature_mismatch', severity='medium', difference='Parameter count differs', docs_info={'parameters': ['a', 'b']}, code_info={'parameters': ['a', 'b', 'c']}), Conflict(api_name='test_api_2', type='missing_in_docs', severity='low', difference='API not documented', docs_info=None, code_info={'name': 'test_api_2'})]
hybrid = generate_hybrid_content(api_data, github_docs, github_insights, conflicts)
assert hybrid['conflict_summary']['total_conflicts'] == 2
assert hybrid['conflict_summary']['by_type']['signature_mismatch'] == 1
assert hybrid['conflict_summary']['by_type']['missing_in_docs'] == 1
assert hybrid['conflict_summary']['by_severity']['medium'] == 1
assert hybrid['conflict_summary']['by_severity']['low'] == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_merge_sources_github.py:196*

### test_match_issues_to_apis_basic

**Category**: workflow  
**Description**: Workflow: Test basic issue to API matching.  
**Expected**: assert issue_links['async_fetch'][0]['number'] == 35  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test basic issue to API matching.'
apis = {'oauth_login': {'name': 'oauth_login'}, 'async_fetch': {'name': 'async_fetch'}}
problems = [{'title': 'OAuth login fails', 'number': 42, 'state': 'open', 'comments': 10, 'labels': ['bug', 'oauth']}]
solutions = [{'title': 'Fixed async fetch timeout', 'number': 35, 'state': 'closed', 'comments': 5, 'labels': ['async']}]
issue_links = _match_issues_to_apis(apis, problems, solutions)
assert 'oauth_login' in issue_links
assert len(issue_links['oauth_login']) == 1
assert issue_links['oauth_login'][0]['number'] == 42
assert 'async_fetch' in issue_links
assert len(issue_links['async_fetch']) == 1
assert issue_links['async_fetch'][0]['number'] == 35
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_merge_sources_github.py:246*

### test_merger_with_github_streams

**Category**: workflow  
**Description**: Workflow: Test merger with three-stream GitHub data.  
**Expected**: assert merger.github_insights['metadata']['stars'] == 1234  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test merger with three-stream GitHub data.'
docs_data = {'pages': []}
github_data = {'apis': {}}
conflicts = []
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# README', contributing='# Contributing', docs_files=[{'path': 'docs/guide.md', 'content': 'Guide content'}])
insights_stream = InsightsStream(metadata={'stars': 1234, 'forks': 56, 'language': 'Python'}, common_problems=[{'title': 'Bug 1', 'number': 1, 'state': 'open', 'comments': 10, 'labels': ['bug']}], known_solutions=[{'title': 'Fix 1', 'number': 2, 'state': 'closed', 'comments': 5, 'labels': ['bug']}], top_labels=[{'label': 'bug', 'count': 10}])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
merger = RuleBasedMerger(docs_data, github_data, conflicts, github_streams)
assert merger.github_streams is not None
assert merger.github_docs is not None
assert merger.github_insights is not None
assert merger.github_docs['readme'] == '# README'
assert merger.github_insights['metadata']['stars'] == 1234
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_merge_sources_github.py:325*

### test_merger_merge_all_with_streams

**Category**: workflow  
**Description**: Workflow: Test merge_all() with GitHub streams.  
**Expected**: assert result['github_context']['metadata']['stars'] == 500  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test merge_all() with GitHub streams.'
docs_data = {'pages': []}
github_data = {'apis': {}}
conflicts = []
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# README', contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={'stars': 500}, common_problems=[], known_solutions=[], top_labels=[])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
merger = RuleBasedMerger(docs_data, github_data, conflicts, github_streams)
result = merger.merge_all()
assert 'github_context' in result
assert 'conflict_summary' in result
assert 'issue_links' in result
assert result['github_context']['metadata']['stars'] == 500
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_merge_sources_github.py:359*

### test_full_pipeline_with_streams

**Category**: workflow  
**Description**: Workflow: Test complete pipeline with three-stream data.  
**Expected**: assert result['conflict_summary']['total_conflicts'] == 0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test complete pipeline with three-stream data.'
docs_data = {'pages': []}
github_data = {'apis': {}}
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# Test Project\n\nA test project.', contributing='# Contributing\n\nPull requests welcome.', docs_files=[{'path': 'docs/quickstart.md', 'content': '# Quick Start'}, {'path': 'docs/api.md', 'content': '# API Reference'}])
insights_stream = InsightsStream(metadata={'stars': 2500, 'forks': 123, 'language': 'Python', 'description': 'Test framework'}, common_problems=[{'title': 'Installation fails on Windows', 'number': 150, 'state': 'open', 'comments': 25, 'labels': ['bug', 'windows']}, {'title': 'Memory leak in async mode', 'number': 142, 'state': 'open', 'comments': 18, 'labels': ['bug', 'async']}], known_solutions=[{'title': 'Fixed config loading', 'number': 130, 'state': 'closed', 'comments': 8, 'labels': ['bug']}, {'title': 'Resolved OAuth timeout', 'number': 125, 'state': 'closed', 'comments': 12, 'labels': ['oauth']}], top_labels=[{'label': 'bug', 'count': 45}, {'label': 'enhancement', 'count': 20}, {'label': 'question', 'count': 15}])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
merger = RuleBasedMerger(docs_data, github_data, [], github_streams)
result = merger.merge_all()
assert 'apis' in result
assert 'github_context' in result
gh_context = result['github_context']
assert gh_context['docs']['readme'] == '# Test Project\n\nA test project.'
assert gh_context['docs']['contributing'] == '# Contributing\n\nPull requests welcome.'
assert gh_context['docs']['docs_files_count'] == 2
assert gh_context['metadata']['stars'] == 2500
assert gh_context['metadata']['language'] == 'Python'
assert gh_context['issues']['common_problems_count'] == 2
assert gh_context['issues']['known_solutions_count'] == 2
assert len(gh_context['issues']['top_problems']) == 2
assert len(gh_context['issues']['top_solutions']) == 2
assert len(gh_context['top_labels']) == 3
assert 'conflict_summary' in result
assert result['conflict_summary']['total_conflicts'] == 0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_merge_sources_github.py:407*

### test_benchmark_format_skill_md_all_adaptors

**Category**: workflow  
**Description**: Workflow: Benchmark format_skill_md across all adaptors  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.TemporaryDirectory()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Benchmark format_skill_md across all adaptors'
print('\n' + '=' * 80)
print('BENCHMARK: format_skill_md() - All Adaptors')
print('=' * 80)
skill_dir = self._create_skill_with_n_references(10)
metadata = SkillMetadata(name='benchmark', description='Benchmark test')
platforms = ['claude', 'gemini', 'openai', 'markdown', 'langchain', 'llama-index', 'haystack', 'weaviate', 'chroma', 'faiss', 'qdrant']
results = {}
for platform in platforms:
    adaptor = get_adaptor(platform)
    adaptor.format_skill_md(skill_dir, metadata)
    times = []
    for _ in range(5):
        start = time.perf_counter()
        formatted = adaptor.format_skill_md(skill_dir, metadata)
        end = time.perf_counter()
        times.append(end - start)
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    results[platform] = {'avg': avg_time, 'min': min_time, 'max': max_time}
    print(f'{platform:15} - Avg: {avg_time * 1000:6.2f}ms | Min: {min_time * 1000:6.2f}ms | Max: {max_time * 1000:6.2f}ms')
for platform, metrics in results.items():
    self.assertLess(metrics['avg'], 0.5, f"{platform} format_skill_md too slow: {metrics['avg'] * 1000:.2f}ms")
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptor_benchmarks.py:76*

### test_benchmark_package_operations

**Category**: workflow  
**Description**: Workflow: Benchmark complete package operation  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.TemporaryDirectory()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Benchmark complete package operation'
print('\n' + '=' * 80)
print('BENCHMARK: package() - Complete Operation')
print('=' * 80)
skill_dir = self._create_skill_with_n_references(10)
platforms = ['claude', 'langchain', 'chroma', 'weaviate', 'faiss']
results = {}
for platform in platforms:
    adaptor = get_adaptor(platform)
    start = time.perf_counter()
    package_path = adaptor.package(skill_dir, self.output_dir)
    end = time.perf_counter()
    elapsed = end - start
    file_size_kb = package_path.stat().st_size / 1024
    results[platform] = {'time': elapsed, 'size_kb': file_size_kb}
    print(f'{platform:15} - Time: {elapsed * 1000:7.2f}ms | Size: {file_size_kb:7.1f} KB')
    self.assertTrue(package_path.exists())
for platform, metrics in results.items():
    self.assertLess(metrics['time'], 1.0, f"{platform} packaging too slow: {metrics['time'] * 1000:.2f}ms")
    self.assertLess(metrics['size_kb'], 1000, f"{platform} package too large: {metrics['size_kb']:.1f}KB")
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptor_benchmarks.py:141*

### test_benchmark_scaling_with_reference_count

**Category**: workflow  
**Description**: Workflow: Test how performance scales with reference count  
**Expected**: self.assertLess(scaling_factor, 3.0, f'Non-linear scaling detected: {scaling_factor:.2f}x')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.TemporaryDirectory()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Test how performance scales with reference count'
print('\n' + '=' * 80)
print('BENCHMARK: Scaling with Reference Count')
print('=' * 80)
adaptor = get_adaptor('langchain')
metadata = SkillMetadata(name='scaling_test', description='Scaling benchmark test')
reference_counts = [1, 5, 10, 25, 50]
results = []
print(f"\n{'Refs':>4} | {'Time (ms)':>10} | {'Time/Ref':>10} | {'Size (KB)':>10}")
print('-' * 50)
for ref_count in reference_counts:
    skill_dir = self._create_skill_with_n_references(ref_count)
    start = time.perf_counter()
    formatted = adaptor.format_skill_md(skill_dir, metadata)
    end = time.perf_counter()
    elapsed = end - start
    time_per_ref = elapsed / ref_count
    json.loads(formatted)
    size_kb = len(formatted) / 1024
    results.append({'count': ref_count, 'time': elapsed, 'time_per_ref': time_per_ref, 'size_kb': size_kb})
    print(f'{ref_count:4} | {elapsed * 1000:10.2f} | {time_per_ref * 1000:10.3f} | {size_kb:10.1f}')
first_per_ref = results[0]['time_per_ref']
last_per_ref = results[-1]['time_per_ref']
scaling_factor = last_per_ref / first_per_ref
print(f'\nScaling Factor: {scaling_factor:.2f}x')
print(f'(Time per ref at 50 refs / Time per ref at 1 ref)')
self.assertLess(scaling_factor, 3.0, f'Non-linear scaling detected: {scaling_factor:.2f}x')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptor_benchmarks.py:188*

### test_benchmark_json_vs_zip_size_comparison

**Category**: workflow  
**Description**: Workflow: Compare output sizes: JSON vs ZIP/tar.gz  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.TemporaryDirectory()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Compare output sizes: JSON vs ZIP/tar.gz'
print('\n' + '=' * 80)
print('BENCHMARK: Output Size Comparison')
print('=' * 80)
skill_dir = self._create_skill_with_n_references(10)
formats = {'claude': ('ZIP', '.zip'), 'gemini': ('tar.gz', '.tar.gz'), 'langchain': ('JSON', '.json'), 'weaviate': ('JSON', '.json')}
results = {}
print(f"\n{'Platform':15} | {'Format':8} | {'Size (KB)':>10}")
print('-' * 50)
for platform, (format_name, ext) in formats.items():
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(skill_dir, self.output_dir)
    size_kb = package_path.stat().st_size / 1024
    results[platform] = {'format': format_name, 'size_kb': size_kb}
    print(f'{platform:15} | {format_name:8} | {size_kb:10.1f}')
json_sizes = [v['size_kb'] for k, v in results.items() if v['format'] == 'JSON']
compressed_sizes = [v['size_kb'] for k, v in results.items() if v['format'] in ['ZIP', 'tar.gz']]
if json_sizes and compressed_sizes:
    avg_json = sum(json_sizes) / len(json_sizes)
    avg_compressed = sum(compressed_sizes) / len(compressed_sizes)
    print(f'\nAverage JSON size: {avg_json:.1f} KB')
    print(f'Average compressed size: {avg_compressed:.1f} KB')
    print(f'Compression ratio: {avg_json / avg_compressed:.2f}x')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptor_benchmarks.py:245*

### test_benchmark_metadata_overhead

**Category**: workflow  
**Description**: Workflow: Measure metadata processing overhead  
**Expected**: self.assertLess(overhead_pct, 10.0, f'Metadata overhead too high: {overhead_pct:.1f}%')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.TemporaryDirectory()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Measure metadata processing overhead'
print('\n' + '=' * 80)
print('BENCHMARK: Metadata Processing Overhead')
print('=' * 80)
skill_dir = self._create_skill_with_n_references(10)
minimal_meta = SkillMetadata(name='test', description='Test')
rich_meta = SkillMetadata(name='test', description='A comprehensive test skill for benchmarking purposes', version='2.5.0', author='Benchmark Suite', tags=['test', 'benchmark', 'performance', 'validation', 'quality'])
adaptor = get_adaptor('langchain')
times_minimal = []
for _ in range(5):
    start = time.perf_counter()
    adaptor.format_skill_md(skill_dir, minimal_meta)
    end = time.perf_counter()
    times_minimal.append(end - start)
times_rich = []
for _ in range(5):
    start = time.perf_counter()
    adaptor.format_skill_md(skill_dir, rich_meta)
    end = time.perf_counter()
    times_rich.append(end - start)
avg_minimal = sum(times_minimal) / len(times_minimal)
avg_rich = sum(times_rich) / len(times_rich)
overhead = avg_rich - avg_minimal
overhead_pct = overhead / avg_minimal * 100
print(f'\nMinimal metadata: {avg_minimal * 1000:.2f}ms')
print(f'Rich metadata:    {avg_rich * 1000:.2f}ms')
print(f'Overhead:         {overhead * 1000:.2f}ms ({overhead_pct:.1f}%)')
self.assertLess(overhead_pct, 10.0, f'Metadata overhead too high: {overhead_pct:.1f}%')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptor_benchmarks.py:291*

### test_benchmark_empty_vs_full_skill

**Category**: workflow  
**Description**: Workflow: Compare performance: empty skill vs full skill  
**Expected**: self.assertLess(full_time, 0.5, 'Full skill processing too slow')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.TemporaryDirectory()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Compare performance: empty skill vs full skill'
print('\n' + '=' * 80)
print('BENCHMARK: Empty vs Full Skill')
print('=' * 80)
adaptor = get_adaptor('chroma')
metadata = SkillMetadata(name='test', description='Test benchmark')
empty_dir = Path(self.temp_dir.name) / 'empty'
empty_dir.mkdir()
start = time.perf_counter()
adaptor.format_skill_md(empty_dir, metadata)
empty_time = time.perf_counter() - start
full_dir = self._create_skill_with_n_references(50)
start = time.perf_counter()
adaptor.format_skill_md(full_dir, metadata)
full_time = time.perf_counter() - start
print(f'\nEmpty skill: {empty_time * 1000:.2f}ms')
print(f'Full skill (50 refs): {full_time * 1000:.2f}ms')
print(f'Ratio: {full_time / empty_time:.1f}x')
self.assertLess(empty_time, 0.01, 'Empty skill processing too slow')
self.assertLess(full_time, 0.5, 'Full skill processing too slow')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptor_benchmarks.py:342*

### test_benchmark_format_skill_md_all_adaptors

**Category**: workflow  
**Description**: Workflow: Benchmark format_skill_md across all adaptors  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Benchmark format_skill_md across all adaptors'
print('\n' + '=' * 80)
print('BENCHMARK: format_skill_md() - All Adaptors')
print('=' * 80)
skill_dir = self._create_skill_with_n_references(10)
metadata = SkillMetadata(name='benchmark', description='Benchmark test')
platforms = ['claude', 'gemini', 'openai', 'markdown', 'langchain', 'llama-index', 'haystack', 'weaviate', 'chroma', 'faiss', 'qdrant']
results = {}
for platform in platforms:
    adaptor = get_adaptor(platform)
    adaptor.format_skill_md(skill_dir, metadata)
    times = []
    for _ in range(5):
        start = time.perf_counter()
        formatted = adaptor.format_skill_md(skill_dir, metadata)
        end = time.perf_counter()
        times.append(end - start)
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    results[platform] = {'avg': avg_time, 'min': min_time, 'max': max_time}
    print(f'{platform:15} - Avg: {avg_time * 1000:6.2f}ms | Min: {min_time * 1000:6.2f}ms | Max: {max_time * 1000:6.2f}ms')
for platform, metrics in results.items():
    self.assertLess(metrics['avg'], 0.5, f"{platform} format_skill_md too slow: {metrics['avg'] * 1000:.2f}ms")
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptor_benchmarks.py:76*

### test_benchmark_package_operations

**Category**: workflow  
**Description**: Workflow: Benchmark complete package operation  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Benchmark complete package operation'
print('\n' + '=' * 80)
print('BENCHMARK: package() - Complete Operation')
print('=' * 80)
skill_dir = self._create_skill_with_n_references(10)
platforms = ['claude', 'langchain', 'chroma', 'weaviate', 'faiss']
results = {}
for platform in platforms:
    adaptor = get_adaptor(platform)
    start = time.perf_counter()
    package_path = adaptor.package(skill_dir, self.output_dir)
    end = time.perf_counter()
    elapsed = end - start
    file_size_kb = package_path.stat().st_size / 1024
    results[platform] = {'time': elapsed, 'size_kb': file_size_kb}
    print(f'{platform:15} - Time: {elapsed * 1000:7.2f}ms | Size: {file_size_kb:7.1f} KB')
    self.assertTrue(package_path.exists())
for platform, metrics in results.items():
    self.assertLess(metrics['time'], 1.0, f"{platform} packaging too slow: {metrics['time'] * 1000:.2f}ms")
    self.assertLess(metrics['size_kb'], 1000, f"{platform} package too large: {metrics['size_kb']:.1f}KB")
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptor_benchmarks.py:141*

### test_benchmark_scaling_with_reference_count

**Category**: workflow  
**Description**: Workflow: Test how performance scales with reference count  
**Expected**: self.assertLess(scaling_factor, 3.0, f'Non-linear scaling detected: {scaling_factor:.2f}x')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test how performance scales with reference count'
print('\n' + '=' * 80)
print('BENCHMARK: Scaling with Reference Count')
print('=' * 80)
adaptor = get_adaptor('langchain')
metadata = SkillMetadata(name='scaling_test', description='Scaling benchmark test')
reference_counts = [1, 5, 10, 25, 50]
results = []
print(f"\n{'Refs':>4} | {'Time (ms)':>10} | {'Time/Ref':>10} | {'Size (KB)':>10}")
print('-' * 50)
for ref_count in reference_counts:
    skill_dir = self._create_skill_with_n_references(ref_count)
    start = time.perf_counter()
    formatted = adaptor.format_skill_md(skill_dir, metadata)
    end = time.perf_counter()
    elapsed = end - start
    time_per_ref = elapsed / ref_count
    json.loads(formatted)
    size_kb = len(formatted) / 1024
    results.append({'count': ref_count, 'time': elapsed, 'time_per_ref': time_per_ref, 'size_kb': size_kb})
    print(f'{ref_count:4} | {elapsed * 1000:10.2f} | {time_per_ref * 1000:10.3f} | {size_kb:10.1f}')
first_per_ref = results[0]['time_per_ref']
last_per_ref = results[-1]['time_per_ref']
scaling_factor = last_per_ref / first_per_ref
print(f'\nScaling Factor: {scaling_factor:.2f}x')
print(f'(Time per ref at 50 refs / Time per ref at 1 ref)')
self.assertLess(scaling_factor, 3.0, f'Non-linear scaling detected: {scaling_factor:.2f}x')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptor_benchmarks.py:188*

### test_benchmark_json_vs_zip_size_comparison

**Category**: workflow  
**Description**: Workflow: Compare output sizes: JSON vs ZIP/tar.gz  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Compare output sizes: JSON vs ZIP/tar.gz'
print('\n' + '=' * 80)
print('BENCHMARK: Output Size Comparison')
print('=' * 80)
skill_dir = self._create_skill_with_n_references(10)
formats = {'claude': ('ZIP', '.zip'), 'gemini': ('tar.gz', '.tar.gz'), 'langchain': ('JSON', '.json'), 'weaviate': ('JSON', '.json')}
results = {}
print(f"\n{'Platform':15} | {'Format':8} | {'Size (KB)':>10}")
print('-' * 50)
for platform, (format_name, ext) in formats.items():
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(skill_dir, self.output_dir)
    size_kb = package_path.stat().st_size / 1024
    results[platform] = {'format': format_name, 'size_kb': size_kb}
    print(f'{platform:15} | {format_name:8} | {size_kb:10.1f}')
json_sizes = [v['size_kb'] for k, v in results.items() if v['format'] == 'JSON']
compressed_sizes = [v['size_kb'] for k, v in results.items() if v['format'] in ['ZIP', 'tar.gz']]
if json_sizes and compressed_sizes:
    avg_json = sum(json_sizes) / len(json_sizes)
    avg_compressed = sum(compressed_sizes) / len(compressed_sizes)
    print(f'\nAverage JSON size: {avg_json:.1f} KB')
    print(f'Average compressed size: {avg_compressed:.1f} KB')
    print(f'Compression ratio: {avg_json / avg_compressed:.2f}x')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptor_benchmarks.py:245*

### test_estimate_tokens

**Category**: workflow  
**Description**: Workflow: Test token estimation.  
**Expected**: assert tokens == 250  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test token estimation.'
chunker = RAGChunker()
assert chunker.estimate_tokens('') == 0
text = 'Hello world!'
tokens = chunker.estimate_tokens(text)
assert tokens == 3
text = 'A' * 1000
tokens = chunker.estimate_tokens(text)
assert tokens == 250
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rag_chunker.py:40*

### test_chunk_document_simple

**Category**: workflow  
**Description**: Workflow: Test chunking simple document.  
**Expected**: assert all(('metadata' in chunk for chunk in chunks))  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test chunking simple document.'
chunker = RAGChunker(chunk_size=50, chunk_overlap=10)
text = 'This is a simple document.\n\nIt has two paragraphs.\n\nAnd a third one.'
metadata = {'source': 'test', 'category': 'simple'}
chunks = chunker.chunk_document(text, metadata)
assert len(chunks) > 0
assert all(('chunk_id' in chunk for chunk in chunks))
assert all(('page_content' in chunk for chunk in chunks))
assert all(('metadata' in chunk for chunk in chunks))
for i, chunk in enumerate(chunks):
    assert chunk['metadata']['source'] == 'test'
    assert chunk['metadata']['category'] == 'simple'
    assert chunk['metadata']['chunk_index'] == i
    assert chunk['metadata']['total_chunks'] == len(chunks)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rag_chunker.py:64*

### test_preserve_code_blocks

**Category**: workflow  
**Description**: Workflow: Test code block preservation.  
**Expected**: assert len(code_chunks) > 0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test code block preservation.'
chunker = RAGChunker(chunk_size=50, preserve_code_blocks=True)
text = '\n        Here is some text.\n\n        ```python\n        def hello():\n            print("Hello, world!")\n        ```\n\n        More text here.\n        '
chunks = chunker.chunk_document(text, {'source': 'test'})
has_code = any(('```' in chunk['page_content'] for chunk in chunks))
assert has_code
code_chunks = [c for c in chunks if c['metadata']['has_code_block']]
assert len(code_chunks) > 0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rag_chunker.py:85*

### test_code_block_not_split

**Category**: workflow  
**Description**: Workflow: Test that code blocks are not split across chunks.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that code blocks are not split across chunks.'
chunker = RAGChunker(chunk_size=20, preserve_code_blocks=True)
text = '\n        Short intro.\n\n        ```python\n        def very_long_function_that_exceeds_chunk_size():\n            # This function is longer than our chunk size\n            # But it should not be split\n            print("Line 1")\n            print("Line 2")\n            print("Line 3")\n            return True\n        ```\n\n        Short outro.\n        '
chunks = chunker.chunk_document(text, {'source': 'test'})
code_chunks = [c for c in chunks if '```python' in c['page_content']]
if code_chunks:
    code_chunk = code_chunks[0]
    assert code_chunk['page_content'].count('```') >= 2
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rag_chunker.py:110*

### test_semantic_boundaries

**Category**: workflow  
**Description**: Workflow: Test that chunks respect paragraph boundaries.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that chunks respect paragraph boundaries.'
chunker = RAGChunker(chunk_size=50, preserve_paragraphs=True)
text = '\n        First paragraph here.\n        It has multiple sentences.\n\n        Second paragraph here.\n        Also with multiple sentences.\n\n        Third paragraph.\n        '
chunks = chunker.chunk_document(text, {'source': 'test'})
for chunk in chunks:
    content = chunk['page_content']
    if content.strip():
        assert not content.strip().endswith(',')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rag_chunker.py:140*

### test_chunk_skill_directory

**Category**: workflow  
**Description**: Workflow: Test chunking entire skill directory.  
**Expected**: assert 'getting_started' in categories or 'api' in categories  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test chunking entire skill directory.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
skill_md = skill_dir / 'SKILL.md'
skill_md.write_text('# Main Skill\n\nThis is the main skill content.\n\nWith multiple paragraphs.')
references_dir = skill_dir / 'references'
references_dir.mkdir()
(references_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start guide.')
(references_dir / 'api.md').write_text('# API Reference\n\nAPI documentation.')
chunker = RAGChunker(chunk_size=50)
chunks = chunker.chunk_skill(skill_dir)
assert len(chunks) > 0
categories = {chunk['metadata']['category'] for chunk in chunks}
assert 'overview' in categories
assert 'getting_started' in categories or 'api' in categories
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rag_chunker.py:175*

### test_save_chunks

**Category**: workflow  
**Description**: Workflow: Test saving chunks to JSON file.  
**Expected**: assert loaded[0]['chunk_id'] == 'test_0'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test saving chunks to JSON file.'
chunker = RAGChunker()
chunks = [{'chunk_id': 'test_0', 'page_content': 'Test content', 'metadata': {'source': 'test', 'chunk_index': 0}}]
output_path = tmp_path / 'chunks.json'
chunker.save_chunks(chunks, output_path)
assert output_path.exists()
with open(output_path) as f:
    loaded = json.load(f)
assert len(loaded) == 1
assert loaded[0]['chunk_id'] == 'test_0'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rag_chunker.py:208*

### test_real_world_documentation

**Category**: workflow  
**Description**: Workflow: Test with realistic documentation content.  
**Expected**: assert len(code_chunks) >= 1  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test with realistic documentation content.'
chunker = RAGChunker(chunk_size=512, chunk_overlap=50)
text = '\n        # React Hooks\n\n        React Hooks are functions that let you "hook into" React state and lifecycle features from function components.\n\n        ## useState\n\n        The `useState` Hook lets you add React state to function components.\n\n        ```javascript\n        import { useState } from \'react\';\n\n        function Example() {\n          const [count, setCount] = useState(0);\n\n          return (\n            <div>\n              <p>You clicked {count} times</p>\n              <button onClick={() => setCount(count + 1)}>\n                Click me\n              </button>\n            </div>\n          );\n        }\n        ```\n\n        ## useEffect\n\n        The `useEffect` Hook lets you perform side effects in function components.\n\n        ```javascript\n        import { useEffect } from \'react\';\n\n        function Example() {\n          useEffect(() => {\n            document.title = `You clicked ${count} times`;\n          });\n        }\n        ```\n\n        ## Best Practices\n\n        - Only call Hooks at the top level\n        - Only call Hooks from React functions\n        - Use multiple Hooks to separate concerns\n        '
metadata = {'source': 'react-docs', 'category': 'hooks', 'url': 'https://react.dev/reference/react'}
chunks = chunker.chunk_document(text, metadata)
assert len(chunks) > 0
code_chunks = [c for c in chunks if c['metadata']['has_code_block']]
assert len(code_chunks) >= 1
for chunk in chunks:
    assert chunk['metadata']['source'] == 'react-docs'
    assert chunk['metadata']['category'] == 'hooks'
    assert chunk['metadata']['estimated_tokens'] > 0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rag_chunker.py:293*

### test_chunk_then_load_with_langchain

**Category**: workflow  
**Description**: Workflow: Test that chunks can be loaded by LangChain.  
**Expected**: assert all((isinstance(doc, Document) for doc in docs))  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test that chunks can be loaded by LangChain.'
pytest.importorskip('langchain')
from langchain.schema import Document
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content for LangChain.')
chunker = RAGChunker()
chunks = chunker.chunk_skill(skill_dir)
docs = [Document(page_content=chunk['page_content'], metadata=chunk['metadata']) for chunk in chunks]
assert len(docs) > 0
assert all((isinstance(doc, Document) for doc in docs))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rag_chunker.py:369*

### test_chunk_then_load_with_llamaindex

**Category**: workflow  
**Description**: Workflow: Test that chunks can be loaded by LlamaIndex.  
**Expected**: assert all((isinstance(node, TextNode) for node in nodes))  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test that chunks can be loaded by LlamaIndex.'
pytest.importorskip('llama_index')
from llama_index.core.schema import TextNode
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content for LlamaIndex.')
chunker = RAGChunker()
chunks = chunker.chunk_skill(skill_dir)
nodes = [TextNode(text=chunk['page_content'], metadata=chunk['metadata'], id_=chunk['chunk_id']) for chunk in chunks]
assert len(nodes) > 0
assert all((isinstance(node, TextNode) for node in nodes))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rag_chunker.py:394*

### test_detect_python_from_heuristics

**Category**: workflow  
**Description**: Workflow: Test Python detection from code content  
**Expected**: self.assertEqual(lang, 'python')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

'Test Python detection from code content'
html = '<code>import os\nfrom pathlib import Path</code>'
elem = BeautifulSoup(html, 'html.parser').find('code')
code = elem.get_text()
lang = self.converter.detect_language(elem, code)
self.assertEqual(lang, 'python')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_scraper_features.py:111*

### test_detect_javascript_from_const

**Category**: workflow  
**Description**: Workflow: Test JavaScript detection from const keyword  
**Expected**: self.assertEqual(lang, 'javascript')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

'Test JavaScript detection from const keyword'
html = '<code>const myVar = 10;</code>'
elem = BeautifulSoup(html, 'html.parser').find('code')
code = elem.get_text()
lang = self.converter.detect_language(elem, code)
self.assertEqual(lang, 'javascript')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_scraper_features.py:127*

### test_detect_javascript_from_arrow

**Category**: workflow  
**Description**: Workflow: Test JavaScript detection from arrow function  
**Expected**: self.assertEqual(lang, 'javascript')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

'Test JavaScript detection from arrow function'
html = '<code>const add = (a, b) => a + b;</code>'
elem = BeautifulSoup(html, 'html.parser').find('code')
code = elem.get_text()
lang = self.converter.detect_language(elem, code)
self.assertEqual(lang, 'javascript')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_scraper_features.py:135*

### test_detect_gdscript

**Category**: workflow  
**Description**: Workflow: Test GDScript detection  
**Expected**: self.assertEqual(lang, 'gdscript')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

'Test GDScript detection'
html = '<code>func _ready():\n    var x = 5</code>'
elem = BeautifulSoup(html, 'html.parser').find('code')
code = elem.get_text()
lang = self.converter.detect_language(elem, code)
self.assertEqual(lang, 'gdscript')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_scraper_features.py:143*

### test_detect_cpp

**Category**: workflow  
**Description**: Workflow: Test C++ detection  
**Expected**: self.assertEqual(lang, 'cpp')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

'Test C++ detection'
html = '<code>#include <iostream>\nint main() { return 0; }</code>'
elem = BeautifulSoup(html, 'html.parser').find('code')
code = elem.get_text()
lang = self.converter.detect_language(elem, code)
self.assertEqual(lang, 'cpp')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_scraper_features.py:151*

### test_detect_unknown

**Category**: workflow  
**Description**: Workflow: Test unknown language detection  
**Expected**: self.assertEqual(lang, 'unknown')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

'Test unknown language detection'
html = '<code>some random text without clear indicators</code>'
elem = BeautifulSoup(html, 'html.parser').find('code')
code = elem.get_text()
lang = self.converter.detect_language(elem, code)
self.assertEqual(lang, 'unknown')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_scraper_features.py:159*

### test_detect_csharp_from_using_system

**Category**: workflow  
**Description**: Workflow: Test C# detection from 'using System' keyword  
**Expected**: self.assertEqual(lang, 'csharp', 'Should detect C# from using System')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

"Test C# detection from 'using System' keyword"
html = '<code>using System;\nnamespace MyApp { }</code>'
elem = BeautifulSoup(html, 'html.parser').find('code')
code = elem.get_text()
lang = self.converter.detect_language(elem, code)
self.assertEqual(lang, 'csharp', 'Should detect C# from using System')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_scraper_features.py:188*

### test_detect_csharp_from_namespace

**Category**: workflow  
**Description**: Workflow: Test C# detection from 'namespace' keyword  
**Expected**: self.assertEqual(lang, 'csharp', 'Should detect C# from namespace')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

"Test C# detection from 'namespace' keyword"
html = '<code>namespace MyNamespace\n{\n    public class Test { }\n}</code>'
elem = BeautifulSoup(html, 'html.parser').find('code')
code = elem.get_text()
lang = self.converter.detect_language(elem, code)
self.assertEqual(lang, 'csharp', 'Should detect C# from namespace')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_scraper_features.py:196*

### test_detect_csharp_from_property_syntax

**Category**: workflow  
**Description**: Workflow: Test C# detection from property syntax  
**Expected**: self.assertEqual(lang, 'csharp', 'Should detect C# from { get; set; } syntax')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

'Test C# detection from property syntax'
html = '<code>public string Name { get; set; }</code>'
elem = BeautifulSoup(html, 'html.parser').find('code')
code = elem.get_text()
lang = self.converter.detect_language(elem, code)
self.assertEqual(lang, 'csharp', 'Should detect C# from { get; set; } syntax')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_scraper_features.py:204*

### test_detect_csharp_from_public_class

**Category**: workflow  
**Description**: Workflow: Test C# detection from 'public class' keyword  
**Expected**: self.assertEqual(lang, 'csharp', 'Should detect C# from public class')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

"Test C# detection from 'public class' keyword"
html = '<code>public class MyClass\n{\n    private int value;\n}</code>'
elem = BeautifulSoup(html, 'html.parser').find('code')
code = elem.get_text()
lang = self.converter.detect_language(elem, code)
self.assertEqual(lang, 'csharp', 'Should detect C# from public class')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_scraper_features.py:212*

### test_add_and_retrieve_github_profile

**Category**: workflow  
**Description**: Workflow: Test adding and retrieving GitHub profiles.  
**Expected**: assert profiles[0]['name'] == 'test-profile'  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

'Test adding and retrieving GitHub profiles.'
config_dir = tmp_path / '.config' / 'skill-seekers'
monkeypatch.setattr(ConfigManager, 'CONFIG_DIR', config_dir)
monkeypatch.setattr(ConfigManager, 'CONFIG_FILE', config_dir / 'config.json')
monkeypatch.setattr(ConfigManager, 'PROGRESS_DIR', tmp_path / '.local' / 'share' / 'skill-seekers' / 'progress')
config = ConfigManager()
config.add_github_profile(name='test-profile', token='ghp_test123', description='Test profile', rate_limit_strategy='wait', timeout_minutes=45, set_as_default=True)
token = config.get_github_token(profile_name='test-profile')
assert token == 'ghp_test123'
profiles = config.list_github_profiles()
assert len(profiles) == 1
assert profiles[0]['is_default'] is True
assert profiles[0]['name'] == 'test-profile'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rate_limit_handler.py:224*

### test_get_next_profile

**Category**: workflow  
**Description**: Workflow: Test profile switching.  
**Expected**: assert token == 'ghp_token1'  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: tmp_path, monkeypatch

'Test profile switching.'
test_dir = tmp_path / 'test_switching'
config_dir = test_dir / '.config' / 'skill-seekers'
monkeypatch.setattr(ConfigManager, 'CONFIG_DIR', config_dir)
monkeypatch.setattr(ConfigManager, 'CONFIG_FILE', config_dir / 'config.json')
monkeypatch.setattr(ConfigManager, 'PROGRESS_DIR', test_dir / '.local' / 'share' / 'skill-seekers' / 'progress')
monkeypatch.setattr(ConfigManager, 'WELCOME_FLAG', config_dir / '.welcomed')
config = ConfigManager()
config.config['github']['profiles'] = {}
config.add_github_profile('profile1', 'ghp_token1', set_as_default=True)
config.add_github_profile('profile2', 'ghp_token2', set_as_default=False)
profiles = config.list_github_profiles()
assert len(profiles) == 2
next_data = config.get_next_profile('ghp_token1')
assert next_data is not None
name, token = next_data
assert name == 'profile2'
assert token == 'ghp_token2'
next_data = config.get_next_profile('ghp_token2')
assert next_data is not None
name, token = next_data
assert name == 'profile1'
assert token == 'ghp_token1'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rate_limit_handler.py:257*

### test_parse_json_config

**Category**: workflow  
**Description**: Workflow: Test parsing JSON configuration  
**Expected**: self.assertGreater(len(db_settings), 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.parser = ConfigParser()
self.temp_dir = tempfile.mkdtemp()

'Test parsing JSON configuration'
json_content = {'database': {'host': 'localhost', 'port': 5432}, 'api_key': 'secret'}
config_file = ConfigFile(file_path=str(Path(self.temp_dir) / 'config.json'), relative_path='config.json', config_type='json', purpose='unknown')
file_path = Path(self.temp_dir) / 'config.json'
file_path.write_text(json.dumps(json_content))
self.parser.parse_config_file(config_file)
self.assertGreater(len(config_file.settings), 0)
db_settings = [s for s in config_file.settings if 'database' in s.key]
self.assertGreater(len(db_settings), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_extractor.py:116*

### test_parse_env_file

**Category**: workflow  
**Description**: Workflow: Test parsing .env file  
**Expected**: self.assertEqual(db_url[0].value, 'postgresql://localhost:5432/db')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.parser = ConfigParser()
self.temp_dir = tempfile.mkdtemp()

'Test parsing .env file'
env_content = '\n# Database configuration\nDATABASE_URL=postgresql://localhost:5432/db\nAPI_KEY=secret123\n\n# Server configuration\nPORT=8000\n'
config_file = ConfigFile(file_path=str(Path(self.temp_dir) / '.env'), relative_path='.env', config_type='env', purpose='unknown')
file_path = Path(self.temp_dir) / '.env'
file_path.write_text(env_content)
self.parser.parse_config_file(config_file)
self.assertGreater(len(config_file.settings), 0)
db_url = [s for s in config_file.settings if s.key == 'DATABASE_URL']
self.assertEqual(len(db_url), 1)
self.assertEqual(db_url[0].value, 'postgresql://localhost:5432/db')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_extractor.py:165*

### test_parse_python_config

**Category**: workflow  
**Description**: Workflow: Test parsing Python config module  
**Expected**: self.assertGreaterEqual(len(db_host), 1)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.parser = ConfigParser()
self.temp_dir = tempfile.mkdtemp()

'Test parsing Python config module'
python_content = "\nDATABASE_HOST = 'localhost'\nDATABASE_PORT = 5432\nDEBUG = True\nAPI_KEYS = ['key1', 'key2']\n"
config_file = ConfigFile(file_path=str(Path(self.temp_dir) / 'settings.py'), relative_path='settings.py', config_type='python', purpose='unknown')
file_path = Path(self.temp_dir) / 'settings.py'
file_path.write_text(python_content)
self.parser.parse_config_file(config_file)
self.assertGreater(len(config_file.settings), 0)
db_host = [s for s in config_file.settings if s.key == 'DATABASE_HOST']
self.assertGreaterEqual(len(db_host), 1)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_extractor.py:217*

### test_parse_dockerfile

**Category**: workflow  
**Description**: Workflow: Test parsing Dockerfile for ENV vars  
**Expected**: self.assertGreater(len(env_settings), 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.parser = ConfigParser()
self.temp_dir = tempfile.mkdtemp()

'Test parsing Dockerfile for ENV vars'
dockerfile_content = '\nFROM python:3.10\nENV DATABASE_URL=postgresql://localhost:5432/db\nENV API_KEY=secret\nWORKDIR /app\n'
config_file = ConfigFile(file_path=str(Path(self.temp_dir) / 'Dockerfile'), relative_path='Dockerfile', config_type='dockerfile', purpose='unknown')
file_path = Path(self.temp_dir) / 'Dockerfile'
file_path.write_text(dockerfile_content)
self.parser.parse_config_file(config_file)
env_settings = [s for s in config_file.settings if s.env_var]
self.assertGreater(len(env_settings), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_extractor.py:242*

### test_parse_json_config

**Category**: workflow  
**Description**: Workflow: Test parsing JSON configuration  
**Expected**: self.assertGreater(len(db_settings), 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test parsing JSON configuration'
json_content = {'database': {'host': 'localhost', 'port': 5432}, 'api_key': 'secret'}
config_file = ConfigFile(file_path=str(Path(self.temp_dir) / 'config.json'), relative_path='config.json', config_type='json', purpose='unknown')
file_path = Path(self.temp_dir) / 'config.json'
file_path.write_text(json.dumps(json_content))
self.parser.parse_config_file(config_file)
self.assertGreater(len(config_file.settings), 0)
db_settings = [s for s in config_file.settings if 'database' in s.key]
self.assertGreater(len(db_settings), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_extractor.py:116*

### test_parse_env_file

**Category**: workflow  
**Description**: Workflow: Test parsing .env file  
**Expected**: self.assertEqual(db_url[0].value, 'postgresql://localhost:5432/db')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test parsing .env file'
env_content = '\n# Database configuration\nDATABASE_URL=postgresql://localhost:5432/db\nAPI_KEY=secret123\n\n# Server configuration\nPORT=8000\n'
config_file = ConfigFile(file_path=str(Path(self.temp_dir) / '.env'), relative_path='.env', config_type='env', purpose='unknown')
file_path = Path(self.temp_dir) / '.env'
file_path.write_text(env_content)
self.parser.parse_config_file(config_file)
self.assertGreater(len(config_file.settings), 0)
db_url = [s for s in config_file.settings if s.key == 'DATABASE_URL']
self.assertEqual(len(db_url), 1)
self.assertEqual(db_url[0].value, 'postgresql://localhost:5432/db')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_extractor.py:165*

### test_parse_python_config

**Category**: workflow  
**Description**: Workflow: Test parsing Python config module  
**Expected**: self.assertGreaterEqual(len(db_host), 1)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test parsing Python config module'
python_content = "\nDATABASE_HOST = 'localhost'\nDATABASE_PORT = 5432\nDEBUG = True\nAPI_KEYS = ['key1', 'key2']\n"
config_file = ConfigFile(file_path=str(Path(self.temp_dir) / 'settings.py'), relative_path='settings.py', config_type='python', purpose='unknown')
file_path = Path(self.temp_dir) / 'settings.py'
file_path.write_text(python_content)
self.parser.parse_config_file(config_file)
self.assertGreater(len(config_file.settings), 0)
db_host = [s for s in config_file.settings if s.key == 'DATABASE_HOST']
self.assertGreaterEqual(len(db_host), 1)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_extractor.py:217*

### test_parse_dockerfile

**Category**: workflow  
**Description**: Workflow: Test parsing Dockerfile for ENV vars  
**Expected**: self.assertGreater(len(env_settings), 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test parsing Dockerfile for ENV vars'
dockerfile_content = '\nFROM python:3.10\nENV DATABASE_URL=postgresql://localhost:5432/db\nENV API_KEY=secret\nWORKDIR /app\n'
config_file = ConfigFile(file_path=str(Path(self.temp_dir) / 'Dockerfile'), relative_path='Dockerfile', config_type='dockerfile', purpose='unknown')
file_path = Path(self.temp_dir) / 'Dockerfile'
file_path.write_text(dockerfile_content)
self.parser.parse_config_file(config_file)
env_settings = [s for s in config_file.settings if s.env_var]
self.assertGreater(len(env_settings), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_extractor.py:242*

### test_analyze_python_workflow

**Category**: workflow  
**Description**: Workflow: Test analysis of Python workflow with multiple steps  
**Expected**: self.assertIn(metadata['complexity_level'], ['beginner', 'intermediate', 'advanced'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.analyzer = WorkflowAnalyzer()

'Test analysis of Python workflow with multiple steps'
workflow = {'code': "\ndef test_user_creation_workflow():\n    # Step 1: Create database\n    db = Database('test.db')\n\n    # Step 2: Create user\n    user = User(name='Alice', email='alice@example.com')\n    db.save(user)\n\n    # Step 3: Verify creation\n    assert db.get_user('Alice').email == 'alice@example.com'\n", 'language': 'python', 'category': 'workflow', 'test_name': 'test_user_creation_workflow', 'file_path': 'tests/test_user.py'}
steps, metadata = self.analyzer.analyze_workflow(workflow)
self.assertGreaterEqual(len(steps), 2)
self.assertIsInstance(steps[0], WorkflowStep)
self.assertEqual(steps[0].step_number, 1)
self.assertIsNotNone(steps[0].description)
self.assertIn('complexity_level', metadata)
self.assertIn(metadata['complexity_level'], ['beginner', 'intermediate', 'advanced'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_how_to_guide_builder.py:42*

### test_calculate_complexity

**Category**: workflow  
**Description**: Workflow: Test complexity level calculation  
**Expected**: self.assertIn(complexity_complex, ['intermediate', 'advanced'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.analyzer = WorkflowAnalyzer()

'Test complexity level calculation'
simple_steps = [WorkflowStep(1, 'x = 1', 'Assign variable'), WorkflowStep(2, 'print(x)', 'Print variable')]
simple_workflow = {'code': 'x = 1\nprint(x)', 'category': 'workflow'}
complexity_simple = self.analyzer._calculate_complexity(simple_steps, simple_workflow)
self.assertEqual(complexity_simple, 'beginner')
complex_steps = [WorkflowStep(i, f'step{i}', f'Step {i}') for i in range(1, 8)]
complex_workflow = {'code': '\n'.join([f'async def step{i}(): await complex_operation()' for i in range(7)]), 'category': 'workflow'}
complexity_complex = self.analyzer._calculate_complexity(complex_steps, complex_workflow)
self.assertIn(complexity_complex, ['intermediate', 'advanced'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_how_to_guide_builder.py:121*

### test_create_complete_example

**Category**: workflow  
**Description**: Workflow: Test complete example generation  
**Expected**: self.assertIn('```python', example_md)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.generator = GuideGenerator()

'Test complete example generation'
guide = HowToGuide(guide_id='test-1', title='Test', overview='Test', complexity_level='beginner', steps=[WorkflowStep(1, 'x = 1', 'Assign'), WorkflowStep(2, 'print(x)', 'Print')], workflows=[{'code': 'x = 1\nprint(x)', 'language': 'python'}])
example_md = self.generator._create_complete_example(guide)
self.assertIn('## Complete Example', example_md)
self.assertIn('```python', example_md)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_how_to_guide_builder.py:373*

### test_extract_workflow_examples

**Category**: workflow  
**Description**: Workflow: Test extraction of workflow examples from mixed examples  
**Expected**: self.assertEqual(workflows[0]['category'], 'workflow')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.builder = HowToGuideBuilder(enhance_with_ai=False)
self.temp_dir = tempfile.mkdtemp()

'Test extraction of workflow examples from mixed examples'
examples = [{'category': 'workflow', 'code': 'db = Database()\nuser = User()\ndb.save(user)', 'test_name': 'test_user_workflow', 'file_path': 'tests/test_user.py', 'language': 'python'}, {'category': 'instantiation', 'code': 'db = Database()', 'test_name': 'test_db', 'file_path': 'tests/test_db.py', 'language': 'python'}]
workflows = self.builder._extract_workflow_examples(examples)
self.assertEqual(len(workflows), 1)
self.assertEqual(workflows[0]['category'], 'workflow')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_how_to_guide_builder.py:427*

### test_create_guide_from_workflows

**Category**: workflow  
**Description**: Workflow: Test guide creation from grouped workflows  
**Expected**: self.assertIn(guide.complexity_level, ['beginner', 'intermediate', 'advanced'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.builder = HowToGuideBuilder(enhance_with_ai=False)
self.temp_dir = tempfile.mkdtemp()

'Test guide creation from grouped workflows'
workflows = [{'code': 'user = User(name="Alice")\ndb.save(user)', 'test_name': 'test_create_user', 'file_path': 'tests/test_user.py', 'language': 'python', 'category': 'workflow'}]
guide = self.builder._create_guide('User Management', workflows)
self.assertIsInstance(guide, HowToGuide)
self.assertEqual(guide.title, 'User Management')
self.assertGreater(len(guide.steps), 0)
self.assertIn(guide.complexity_level, ['beginner', 'intermediate', 'advanced'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_how_to_guide_builder.py:452*

### test_save_guides_to_files

**Category**: workflow  
**Description**: Workflow: Test saving guides to markdown files  
**Expected**: self.assertGreaterEqual(len(md_files), 1)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.builder = HowToGuideBuilder(enhance_with_ai=False)
self.temp_dir = tempfile.mkdtemp()

'Test saving guides to markdown files'
guides = [HowToGuide(guide_id='test-guide', title='Test Guide', overview='Test overview', complexity_level='beginner', steps=[WorkflowStep(1, 'x = 1', 'Test step')])]
collection = GuideCollection(total_guides=1, guides=guides, guides_by_complexity={'beginner': 1}, guides_by_use_case={})
output_dir = Path(self.temp_dir)
self.builder._save_guides_to_files(collection, output_dir)
self.assertTrue((output_dir / 'index.md').exists())
index_content = (output_dir / 'index.md').read_text()
self.assertIn('Test Guide', index_content)
md_files = list(output_dir.glob('*.md'))
self.assertGreaterEqual(len(md_files), 1)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_how_to_guide_builder.py:490*

### test_build_with_ai_enhancement_disabled

**Category**: workflow  
**Description**: Workflow: Test building guides WITHOUT AI enhancement (backward compatibility)  
**Expected**: self.assertTrue((output_dir / 'index.md').exists())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.temp_dir = tempfile.mkdtemp()

'Test building guides WITHOUT AI enhancement (backward compatibility)'
examples = [{'example_id': 'test_001', 'test_name': 'test_user_registration', 'category': 'workflow', 'code': '\ndef test_user_registration():\n    user = User.create(username="test", email="test@example.com")\n    assert user.id is not None\n    assert user.is_active is True\n                ', 'language': 'python', 'file_path': 'tests/test_user.py', 'line_start': 10, 'tags': ['authentication', 'user'], 'ai_analysis': {'tutorial_group': 'User Management', 'best_practices': ['Validate email format'], 'common_mistakes': ['Not checking uniqueness']}}]
builder = HowToGuideBuilder()
output_dir = Path(self.temp_dir) / 'guides'
collection = builder.build_guides_from_examples(examples=examples, grouping_strategy='ai-tutorial-group', output_dir=output_dir, enhance_with_ai=False, ai_mode='none')
self.assertIsInstance(collection, GuideCollection)
self.assertGreater(collection.total_guides, 0)
self.assertTrue(output_dir.exists())
self.assertTrue((output_dir / 'index.md').exists())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_how_to_guide_builder.py:653*

### test_build_with_ai_enhancement_api_mode_mocked

**Category**: workflow  
**Description**: Workflow: Test building guides WITH AI enhancement in API mode (mocked)  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
self.temp_dir = tempfile.mkdtemp()

'Test building guides WITH AI enhancement in API mode (mocked)'
from unittest.mock import patch
examples = [{'example_id': 'test_002', 'test_name': 'test_data_scraping', 'category': 'workflow', 'code': '\ndef test_data_scraping():\n    scraper = DocumentationScraper()\n    result = scraper.scrape("https://example.com/docs")\n    assert result.pages > 0\n                ', 'language': 'python', 'file_path': 'tests/test_scraper.py', 'line_start': 20, 'tags': ['scraping', 'documentation'], 'ai_analysis': {'tutorial_group': 'Data Collection', 'best_practices': ['Handle rate limiting'], 'common_mistakes': ['Not handling SSL errors']}}]
builder = HowToGuideBuilder()
output_dir = Path(self.temp_dir) / 'guides_enhanced'
with patch('skill_seekers.cli.guide_enhancer.GuideEnhancer') as MockEnhancer:
    mock_enhancer = MockEnhancer.return_value
    mock_enhancer.mode = 'api'

    def mock_enhance_guide(guide_data):
        enhanced = guide_data.copy()
        enhanced['step_enhancements'] = [StepEnhancement(step_index=0, explanation='Test explanation', variations=[])]
        enhanced['troubleshooting_detailed'] = []
        enhanced['prerequisites_detailed'] = []
        enhanced['next_steps_detailed'] = []
        enhanced['use_cases'] = []
        return enhanced
    mock_enhancer.enhance_guide = mock_enhance_guide
    collection = builder.build_guides_from_examples(examples=examples, grouping_strategy='ai-tutorial-group', output_dir=output_dir, enhance_with_ai=True, ai_mode='api')
    self.assertIsInstance(collection, GuideCollection)
    self.assertGreater(collection.total_guides, 0)
    MockEnhancer.assert_called_once_with(mode='api')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_how_to_guide_builder.py:698*

### test_build_with_ai_enhancement_local_mode_mocked

**Category**: workflow  
**Description**: Workflow: Test building guides WITH AI enhancement in LOCAL mode (mocked)  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
self.temp_dir = tempfile.mkdtemp()

'Test building guides WITH AI enhancement in LOCAL mode (mocked)'
from unittest.mock import patch
examples = [{'example_id': 'test_003', 'test_name': 'test_api_integration', 'category': 'workflow', 'code': '\ndef test_api_integration():\n    client = APIClient(base_url="https://api.example.com")\n    response = client.get("/users")\n    assert response.status_code == 200\n                ', 'language': 'python', 'file_path': 'tests/test_api.py', 'line_start': 30, 'tags': ['api', 'integration'], 'ai_analysis': {'tutorial_group': 'API Testing', 'best_practices': ['Use environment variables'], 'common_mistakes': ['Hardcoded credentials']}}]
builder = HowToGuideBuilder()
output_dir = Path(self.temp_dir) / 'guides_local'
with patch('skill_seekers.cli.guide_enhancer.GuideEnhancer') as MockEnhancer:
    mock_enhancer = MockEnhancer.return_value
    mock_enhancer.mode = 'local'

    def mock_enhance_guide(guide_data):
        enhanced = guide_data.copy()
        enhanced['step_enhancements'] = []
        enhanced['troubleshooting_detailed'] = []
        enhanced['prerequisites_detailed'] = []
        enhanced['next_steps_detailed'] = []
        enhanced['use_cases'] = []
        return enhanced
    mock_enhancer.enhance_guide = mock_enhance_guide
    collection = builder.build_guides_from_examples(examples=examples, grouping_strategy='ai-tutorial-group', output_dir=output_dir, enhance_with_ai=True, ai_mode='local')
    self.assertIsInstance(collection, GuideCollection)
    self.assertGreater(collection.total_guides, 0)
    MockEnhancer.assert_called_once_with(mode='local')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_how_to_guide_builder.py:764*

### test_build_with_ai_enhancement_auto_mode

**Category**: workflow  
**Description**: Workflow: Test building guides WITH AI enhancement in AUTO mode  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
self.temp_dir = tempfile.mkdtemp()

'Test building guides WITH AI enhancement in AUTO mode'
from unittest.mock import patch
examples = [{'example_id': 'test_004', 'test_name': 'test_database_migration', 'category': 'workflow', 'code': '\ndef test_database_migration():\n    migrator = DatabaseMigrator()\n    migrator.run_migrations()\n    assert migrator.current_version == "2.0"\n                ', 'language': 'python', 'file_path': 'tests/test_db.py', 'line_start': 40, 'tags': ['database', 'migration'], 'ai_analysis': {'tutorial_group': 'Database Operations', 'best_practices': ['Backup before migration'], 'common_mistakes': ['Not testing rollback']}}]
builder = HowToGuideBuilder()
output_dir = Path(self.temp_dir) / 'guides_auto'
with patch('skill_seekers.cli.guide_enhancer.GuideEnhancer') as MockEnhancer:
    mock_enhancer = MockEnhancer.return_value
    mock_enhancer.mode = 'local'

    def mock_enhance_guide(guide_data):
        enhanced = guide_data.copy()
        enhanced['step_enhancements'] = []
        enhanced['troubleshooting_detailed'] = []
        enhanced['prerequisites_detailed'] = []
        enhanced['next_steps_detailed'] = []
        enhanced['use_cases'] = []
        return enhanced
    mock_enhancer.enhance_guide = mock_enhance_guide
    collection = builder.build_guides_from_examples(examples=examples, grouping_strategy='ai-tutorial-group', output_dir=output_dir, enhance_with_ai=True, ai_mode='auto')
    self.assertIsInstance(collection, GuideCollection)
    self.assertGreater(collection.total_guides, 0)
    MockEnhancer.assert_called_once_with(mode='auto')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_how_to_guide_builder.py:827*

### test_detect_modified_file

**Category**: workflow  
**Description**: Workflow: Test detection of modified files.  
**Expected**: assert change_set.modified[0].version == 2  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_skill_dir

'Test detection of modified files.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
time.sleep(0.01)
skill_md = temp_skill_dir / 'SKILL.md'
skill_md.write_text('# Test Skill\n\nModified content')
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
assert len(change_set.modified) == 1
assert len(change_set.added) == 0
assert len(change_set.deleted) == 0
assert change_set.modified[0].file_path == 'SKILL.md'
assert change_set.modified[0].version == 2
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_incremental_updates.py:80*

### test_detect_added_file

**Category**: workflow  
**Description**: Workflow: Test detection of new files.  
**Expected**: assert change_set.added[0].file_path == 'references/api_reference.md'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_skill_dir

'Test detection of new files.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
refs_dir = temp_skill_dir / 'references'
new_ref = refs_dir / 'api_reference.md'
new_ref.write_text('# API Reference\n\nNew documentation')
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
assert len(change_set.added) == 1
assert len(change_set.modified) == 0
assert len(change_set.deleted) == 0
assert change_set.added[0].file_path == 'references/api_reference.md'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_incremental_updates.py:104*

### test_detect_deleted_file

**Category**: workflow  
**Description**: Workflow: Test detection of deleted files.  
**Expected**: assert 'references/getting_started.md' in change_set.deleted  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_skill_dir

'Test detection of deleted files.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
ref_file = temp_skill_dir / 'references' / 'getting_started.md'
ref_file.unlink()
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
assert len(change_set.deleted) == 1
assert len(change_set.added) == 0
assert len(change_set.modified) == 0
assert 'references/getting_started.md' in change_set.deleted
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_incremental_updates.py:127*

### test_mixed_changes

**Category**: workflow  
**Description**: Workflow: Test detection of multiple types of changes.  
**Expected**: assert change_set.total_changes == 3  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_skill_dir

'Test detection of multiple types of changes.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
time.sleep(0.01)
(temp_skill_dir / 'SKILL.md').write_text('# Test Skill\n\nModified')
refs_dir = temp_skill_dir / 'references'
(refs_dir / 'new_file.md').write_text('# New File')
(refs_dir / 'getting_started.md').unlink()
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
assert len(change_set.modified) == 1
assert len(change_set.added) == 1
assert len(change_set.deleted) == 1
assert change_set.total_changes == 3
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_incremental_updates.py:149*

### test_generate_update_package

**Category**: workflow  
**Description**: Workflow: Test update package generation.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_skill_dir

'Test update package generation.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
time.sleep(0.01)
(temp_skill_dir / 'SKILL.md').write_text('# Modified')
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
with tempfile.TemporaryDirectory() as tmpdir:
    package_path = Path(tmpdir) / 'update.json'
    result_path = updater2.generate_update_package(change_set, package_path)
    assert result_path.exists()
    package_data = json.loads(result_path.read_text())
    assert 'metadata' in package_data
    assert 'changes' in package_data
    assert package_data['metadata']['total_changes'] == 1
    assert 'SKILL.md' in package_data['changes']
    assert package_data['changes']['SKILL.md']['action'] == 'modify'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_incremental_updates.py:180*

### test_diff_report_generation

**Category**: workflow  
**Description**: Workflow: Test diff report generation.  
**Expected**: assert 'SKILL.md' in report  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_skill_dir

'Test diff report generation.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
time.sleep(0.01)
(temp_skill_dir / 'SKILL.md').write_text('# Modified content')
updater2 = IncrementalUpdater(temp_skill_dir)
change_set = updater2.detect_changes()
report = updater2.generate_diff_report(change_set)
assert 'INCREMENTAL UPDATE REPORT' in report
assert 'Modified: 1 files' in report
assert 'SKILL.md' in report
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_incremental_updates.py:212*

### test_version_increment

**Category**: workflow  
**Description**: Workflow: Test version numbers increment correctly.  
**Expected**: assert change_set3.modified[0].version == 3  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_skill_dir

'Test version numbers increment correctly.'
updater = IncrementalUpdater(temp_skill_dir)
change_set1 = updater.detect_changes()
updater.save_current_versions()
for doc in change_set1.added:
    assert doc.version == 1
time.sleep(0.01)
(temp_skill_dir / 'SKILL.md').write_text('Modified once')
updater2 = IncrementalUpdater(temp_skill_dir)
change_set2 = updater2.detect_changes()
updater2.save_current_versions()
assert change_set2.modified[0].version == 2
time.sleep(0.01)
(temp_skill_dir / 'SKILL.md').write_text('Modified twice')
updater3 = IncrementalUpdater(temp_skill_dir)
change_set3 = updater3.detect_changes()
assert change_set3.modified[0].version == 3
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_incremental_updates.py:234*

### test_apply_update_package

**Category**: workflow  
**Description**: Workflow: Test applying an update package.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_skill_dir

'Test applying an update package.'
updater = IncrementalUpdater(temp_skill_dir)
updater.detect_changes()
updater.save_current_versions()
with tempfile.TemporaryDirectory() as tmpdir:
    package_path = Path(tmpdir) / 'update.json'
    update_data = {'metadata': {'timestamp': '2026-02-05T12:00:00', 'skill_name': 'test_skill', 'change_summary': {'modified': 1}, 'total_changes': 1}, 'changes': {'SKILL.md': {'action': 'modify', 'version': 2, 'content': '# Updated Content\n\nApplied from package'}}}
    package_path.write_text(json.dumps(update_data))
    success = updater.apply_update_package(package_path)
    assert success
    assert (temp_skill_dir / 'SKILL.md').read_text() == '# Updated Content\n\nApplied from package'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_incremental_updates.py:266*

### test_content_hash_consistency

**Category**: workflow  
**Description**: Workflow: Test content hash is consistent for same content.  
**Expected**: assert hash1 == hash2  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_skill_dir

'Test content hash is consistent for same content.'
updater = IncrementalUpdater(temp_skill_dir)
skill_md = temp_skill_dir / 'SKILL.md'
hash1 = updater._compute_file_hash(skill_md)
content = skill_md.read_text()
skill_md.write_text(content)
hash2 = updater._compute_file_hash(skill_md)
assert hash1 == hash2
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_incremental_updates.py:304*

### test_scraping_proceeds_when_llms_txt_skipped

**Category**: workflow  
**Description**: Workflow: Test that HTML scraping proceeds normally when llms.txt is skipped.  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
'Test that HTML scraping proceeds normally when llms.txt is skipped.'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article'}, 'skip_llms_txt': True}
original_cwd = os.getcwd()
with tempfile.TemporaryDirectory() as tmpdir:
    try:
        os.chdir(tmpdir)
        converter = DocToSkillConverter(config, dry_run=False)
        scrape_called = []

        def mock_scrape(url):
            scrape_called.append(url)
            return None
        with patch.object(converter, 'scrape_page', side_effect=mock_scrape), patch.object(converter, 'save_summary'):
            converter.scrape_all()
            self.assertTrue(len(scrape_called) > 0)
    finally:
        os.chdir(original_cwd)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_skip_llms_txt.py:295*

### test_scraping_proceeds_when_llms_txt_skipped

**Category**: workflow  
**Description**: Workflow: Test that HTML scraping proceeds normally when llms.txt is skipped.  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
'Test that HTML scraping proceeds normally when llms.txt is skipped.'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article'}, 'skip_llms_txt': True}
original_cwd = os.getcwd()
with tempfile.TemporaryDirectory() as tmpdir:
    try:
        os.chdir(tmpdir)
        converter = DocToSkillConverter(config, dry_run=False)
        scrape_called = []

        def mock_scrape(url):
            scrape_called.append(url)
            return None
        with patch.object(converter, 'scrape_page', side_effect=mock_scrape), patch.object(converter, 'save_summary'):
            converter.scrape_all()
            self.assertTrue(len(scrape_called) > 0)
    finally:
        os.chdir(original_cwd)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_skip_llms_txt.py:295*

### test_issue_categorization_by_topic

**Category**: workflow  
**Description**: Workflow: Test that issues are correctly categorized by topic keywords.  
**Expected**: assert any(('OAuth' in title for title in oauth_titles))  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that issues are correctly categorized by topic keywords.'
problems = [{'title': 'OAuth fails on redirect', 'number': 50, 'state': 'open', 'comments': 20, 'labels': ['oauth', 'bug']}, {'title': 'Token refresh issue', 'number': 45, 'state': 'open', 'comments': 15, 'labels': ['oauth', 'token']}, {'title': 'Async deadlock', 'number': 40, 'state': 'open', 'comments': 12, 'labels': ['async', 'bug']}, {'title': 'Database connection lost', 'number': 35, 'state': 'open', 'comments': 10, 'labels': ['database']}]
solutions = [{'title': 'Fixed OAuth flow', 'number': 30, 'state': 'closed', 'comments': 8, 'labels': ['oauth']}, {'title': 'Resolved async race', 'number': 25, 'state': 'closed', 'comments': 6, 'labels': ['async']}]
topics = ['oauth', 'auth', 'authentication']
categorized = categorize_issues_by_topic(problems, solutions, topics)
assert 'oauth' in categorized or 'auth' in categorized or 'authentication' in categorized
oauth_issues = categorized.get('oauth', []) + categorized.get('auth', []) + categorized.get('authentication', [])
assert len(oauth_issues) >= 2
oauth_titles = [issue['title'] for issue in oauth_issues]
assert any(('OAuth' in title for title in oauth_titles))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_e2e_three_stream_pipeline.py:154*

### test_github_overhead_within_limits

**Category**: workflow  
**Description**: Workflow: Test that GitHub integration adds ~30-50 lines per skill (not more).

Quality metric: GitHub overhead should be minimal.  
**Expected**: assert 20 <= github_overhead <= 60, f'GitHub overhead is {github_overhead} lines, expected 20-60'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'\n        Test that GitHub integration adds ~30-50 lines per skill (not more).\n\n        Quality metric: GitHub overhead should be minimal.\n        '
config = {'name': 'test-skill', 'description': 'Test skill', 'base_url': 'https://github.com/test/repo', 'categories': {'api': ['api']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
code_stream = CodeStream(directory=tmp_path, files=[])
docs_stream = DocsStream(readme='# Test\n\nA short README.', contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={'stars': 100, 'forks': 10, 'language': 'Python', 'description': 'Test'}, common_problems=[{'title': 'Issue 1', 'number': 1, 'state': 'open', 'comments': 5, 'labels': ['bug']}, {'title': 'Issue 2', 'number': 2, 'state': 'open', 'comments': 3, 'labels': ['bug']}], known_solutions=[], top_labels=[{'label': 'bug', 'count': 10}])
github_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
generator_no_github = RouterGenerator([str(config_path)])
skill_md_no_github = generator_no_github.generate_skill_md()
lines_no_github = len(skill_md_no_github.split('\n'))
generator_with_github = RouterGenerator([str(config_path)], github_streams=github_streams)
skill_md_with_github = generator_with_github.generate_skill_md()
lines_with_github = len(skill_md_with_github.split('\n'))
github_overhead = lines_with_github - lines_no_github
assert 20 <= github_overhead <= 60, f'GitHub overhead is {github_overhead} lines, expected 20-60'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_e2e_three_stream_pipeline.py:407*

### test_router_size_within_limits

**Category**: workflow  
**Description**: Workflow: Test that router SKILL.md is ~150 lines (±20).

Quality metric: Router should be concise overview, not exhaustive.  
**Expected**: assert 60 <= lines <= 250, f'Router is {lines} lines, expected 60-250 for 4 sub-skills'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'\n        Test that router SKILL.md is ~150 lines (±20).\n\n        Quality metric: Router should be concise overview, not exhaustive.\n        '
configs = []
for i in range(4):
    config = {'name': f'test-skill-{i}', 'description': f'Test skill {i}', 'base_url': 'https://github.com/test/repo', 'categories': {f'topic{i}': [f'topic{i}']}}
    config_path = tmp_path / f'config{i}.json'
    with open(config_path, 'w') as f:
        json.dump(config, f)
    configs.append(str(config_path))
generator = RouterGenerator(configs)
skill_md = generator.generate_skill_md()
lines = len(skill_md.split('\n'))
assert 60 <= lines <= 250, f'Router is {lines} lines, expected 60-250 for 4 sub-skills'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_e2e_three_stream_pipeline.py:471*

### test_router_without_github_streams

**Category**: workflow  
**Description**: Workflow: Test that router generation works without GitHub streams (backward compat).  
**Expected**: assert 'Common Issues (from GitHub)' not in skill_md  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test that router generation works without GitHub streams (backward compat).'
config = {'name': 'test-skill', 'description': 'Test skill', 'base_url': 'https://example.com', 'categories': {'api': ['api']}}
config_path = tmp_path / 'config.json'
with open(config_path, 'w') as f:
    json.dump(config, f)
generator = RouterGenerator([str(config_path)])
assert generator.github_metadata is None
assert generator.github_docs is None
assert generator.github_issues is None
skill_md = generator.generate_skill_md()
assert 'When to Use This Skill' in skill_md
assert 'How It Works' in skill_md
assert '⭐' not in skill_md
assert 'Repository Info' not in skill_md
assert 'Quick Start (from README)' not in skill_md
assert 'Common Issues (from GitHub)' not in skill_md
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_e2e_three_stream_pipeline.py:504*

### test_three_stream_produces_compact_output

**Category**: workflow  
**Description**: Workflow: Test that three-stream architecture produces compact, efficient output.

This is a qualitative test - we verify that output is structured and
not duplicated across streams.  
**Expected**: assert str(tmp_path) not in docs_stream.readme  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'\n        Test that three-stream architecture produces compact, efficient output.\n\n        This is a qualitative test - we verify that output is structured and\n        not duplicated across streams.\n        '
(tmp_path / 'main.py').write_text("import os\nprint('test')")
code_stream = CodeStream(directory=tmp_path, files=[tmp_path / 'main.py'])
docs_stream = DocsStream(readme='# Test\n\nQuick start guide.', contributing=None, docs_files=[])
insights_stream = InsightsStream(metadata={'stars': 100}, common_problems=[], known_solutions=[], top_labels=[])
_three_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
assert code_stream.directory == tmp_path
assert docs_stream.readme is not None
assert insights_stream.metadata is not None
assert 'Quick start guide' not in str(code_stream.files)
assert str(tmp_path) not in docs_stream.readme
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_e2e_three_stream_pipeline.py:567*

### test_preset_flag_preferred

**Category**: workflow  
**Description**: Workflow: Test that --preset flag is the recommended way.  
**Expected**: assert updated['depth'] == 'full'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that --preset flag is the recommended way.'
args = {'preset': 'quick'}
updated = PresetManager.apply_preset('quick', args)
assert updated['depth'] == 'surface'
args = {'preset': 'standard'}
updated = PresetManager.apply_preset('standard', args)
assert updated['depth'] == 'deep'
args = {'preset': 'comprehensive'}
updated = PresetManager.apply_preset('comprehensive', args)
assert updated['depth'] == 'full'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_preset_system.py:319*

### test_completeness_full

**Category**: workflow  
**Description**: Workflow: Test completeness analysis with complete skill.  
**Expected**: assert score >= 70  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: complete_skill_dir

'Test completeness analysis with complete skill.'
analyzer = QualityAnalyzer(complete_skill_dir)
score = analyzer.analyze_completeness()
assert score >= 70
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_metrics.py:60*

### test_completeness_minimal

**Category**: workflow  
**Description**: Workflow: Test completeness analysis with minimal skill.  
**Expected**: assert score < 80  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: minimal_skill_dir

'Test completeness analysis with minimal skill.'
analyzer = QualityAnalyzer(minimal_skill_dir)
score = analyzer.analyze_completeness()
assert score < 80
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_metrics.py:68*

### mock_github_repo

**Category**: workflow  
**Description**: Workflow: Create mock GitHub repository structure.  
**Expected**: (tests_dir / 'test_auth.py').write_text("\ndef test_google_provider():\n    provider = google_provider('id', 'secret')\n    assert provider.name == 'google'\n\ndef test_azure_provider():\n    provider = azure_provider('tenant', 'id')\n    assert provider.name == 'azure'\n")  
**Confidence**: 0.90  
**Tags**: mock, pytest, workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Create mock GitHub repository structure.'
repo_dir = tmp_path / 'fastmcp'
repo_dir.mkdir()
src_dir = repo_dir / 'src'
src_dir.mkdir()
(src_dir / 'auth.py').write_text("\n# OAuth authentication\ndef google_provider(client_id, client_secret):\n    '''Google OAuth provider'''\n    return Provider('google', client_id, client_secret)\n\ndef azure_provider(tenant_id, client_id):\n    '''Azure OAuth provider'''\n    return Provider('azure', tenant_id, client_id)\n")
(src_dir / 'async_tools.py').write_text('\nimport asyncio\n\nasync def async_tool():\n    \'\'\'Async tool decorator\'\'\'\n    await asyncio.sleep(1)\n    return "result"\n')
tests_dir = repo_dir / 'tests'
tests_dir.mkdir()
(tests_dir / 'test_auth.py').write_text("\ndef test_google_provider():\n    provider = google_provider('id', 'secret')\n    assert provider.name == 'google'\n\ndef test_azure_provider():\n    provider = azure_provider('tenant', 'id')\n    assert provider.name == 'azure'\n")
(repo_dir / 'README.md').write_text('\n# FastMCP\n\nFastMCP is a Python framework for building MCP servers.\n\n## Quick Start\n\nInstall with pip:\n```bash\npip install fastmcp\n```\n\n## Features\n- OAuth authentication (Google, Azure, GitHub)\n- Async/await support\n- Easy testing with pytest\n')
(repo_dir / 'CONTRIBUTING.md').write_text('\n# Contributing\n\nPlease follow these guidelines when contributing.\n')
docs_dir = repo_dir / 'docs'
docs_dir.mkdir()
(docs_dir / 'oauth.md').write_text('\n# OAuth Guide\n\nHow to set up OAuth providers.\n')
(docs_dir / 'async.md').write_text('\n# Async Guide\n\nHow to use async tools.\n')
return repo_dir
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_architecture_scenarios.py:65*

### test_scenario_1_quality_metrics

**Category**: workflow  
**Description**: Workflow: Test quality metrics meet architecture targets.  
**Expected**: assert 'Quick Start' in router_md or 'README' in router_md, 'Missing README content'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test quality metrics meet architecture targets.'
router_md = '---\nname: fastmcp\ndescription: FastMCP framework overview\n---\n\n# FastMCP - Overview\n\n**Repository:** https://github.com/jlowin/fastmcp\n**Stars:** ⭐ 1,234 | **Language:** Python\n\n## Quick Start (from README)\n\nInstall with pip:\n```bash\npip install fastmcp\n```\n\n## Common Issues (from GitHub)\n\n1. **OAuth setup fails** (Issue #42, 15 comments)\n   - See `fastmcp-oauth` skill\n\n2. **Async tools not working** (Issue #38, 8 comments)\n   - See `fastmcp-async` skill\n\n## Choose Your Path\n\n**OAuth?** → Use `fastmcp-oauth` skill\n**Async?** → Use `fastmcp-async` skill\n'
lines = router_md.strip().split('\n')
assert len(lines) <= 200, f'Router too large: {len(lines)} lines (max 200)'
github_lines = 0
if 'Repository:' in router_md:
    github_lines += 1
if 'Stars:' in router_md or '⭐' in router_md:
    github_lines += 1
if 'Common Issues' in router_md:
    github_lines += router_md.count('Issue #')
assert github_lines >= 3, f'GitHub overhead too small: {github_lines} lines'
assert github_lines <= 60, f'GitHub overhead too large: {github_lines} lines'
assert 'Issue #42' in router_md, 'Missing issue references'
assert '⭐' in router_md or 'Stars:' in router_md, 'Missing GitHub metadata'
assert 'Quick Start' in router_md or 'README' in router_md, 'Missing README content'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_architecture_scenarios.py:427*

### test_scenario_2_issue_categorization

**Category**: workflow  
**Description**: Workflow: Test categorizing GitHub issues by topic.  
**Expected**: assert len(testing_issues) >= 1  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test categorizing GitHub issues by topic.'
problems = [{'number': 42, 'title': 'OAuth setup fails', 'labels': ['oauth', 'bug']}, {'number': 38, 'title': 'Async tools not working', 'labels': ['async', 'question']}, {'number': 35, 'title': 'Testing with pytest', 'labels': ['testing', 'question']}, {'number': 30, 'title': 'Google OAuth redirect', 'labels': ['oauth', 'question']}]
solutions = [{'number': 25, 'title': 'Fixed OAuth redirect', 'labels': ['oauth', 'bug']}, {'number': 20, 'title': 'Async timeout solution', 'labels': ['async', 'bug']}]
topics = ['oauth', 'async', 'testing']
categorized = categorize_issues_by_topic(problems, solutions, topics)
assert 'oauth' in categorized
assert 'async' in categorized
assert 'testing' in categorized
oauth_issues = categorized['oauth']
assert len(oauth_issues) >= 2
oauth_numbers = [i['number'] for i in oauth_issues]
assert 42 in oauth_numbers
async_issues = categorized['async']
assert len(async_issues) >= 2
async_numbers = [i['number'] for i in async_issues]
assert 38 in async_numbers
testing_issues = categorized['testing']
assert len(testing_issues) >= 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_architecture_scenarios.py:519*

### test_scenario_2_conflict_detection

**Category**: workflow  
**Description**: Workflow: Test conflict detection between docs and code.  
**Expected**: assert github_docs is not None  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test conflict detection between docs and code.'
api_data = {'GoogleProvider': {'params': ['app_id', 'app_secret'], 'source': 'html_docs'}}
github_docs = {'readme': 'Use client_id and client_secret for Google OAuth'}
assert 'GoogleProvider' in api_data
assert 'params' in api_data['GoogleProvider']
assert github_docs is not None
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_architecture_scenarios.py:574*

### test_scenario_2_multi_layer_merge

**Category**: workflow  
**Description**: Workflow: Test multi-layer source merging priority.  
**Expected**: assert isinstance(merged, dict)  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test multi-layer source merging priority.'
source1_data = {'api': [{'name': 'GoogleProvider', 'params': ['app_id', 'app_secret']}]}
source2_data = {'api': [{'name': 'GoogleProvider', 'params': ['client_id', 'client_secret']}]}
_github_streams = ThreeStreamData(code_stream=CodeStream(directory=Path('/tmp'), files=[]), docs_stream=DocsStream(readme='Use client_id and client_secret', contributing=None, docs_files=[]), insights_stream=InsightsStream(metadata={'stars': 1000}, common_problems=[{'number': 42, 'title': 'OAuth parameter confusion', 'labels': ['oauth']}], known_solutions=[], top_labels=[]))
merger = RuleBasedMerger(docs_data=source1_data, github_data=source2_data, conflicts=[])
merged = merger.merge_all()
assert merged is not None
assert isinstance(merged, dict)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_architecture_scenarios.py:597*

### test_scenario_3_local_analysis_basic

**Category**: workflow  
**Description**: Workflow: Test basic analysis of local codebase.  
**Expected**: assert result.github_insights is None  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: local_codebase

'Test basic analysis of local codebase.'
analyzer = UnifiedCodebaseAnalyzer()
result = analyzer.analyze(source=str(local_codebase), depth='basic', fetch_github_metadata=False)
assert isinstance(result, AnalysisResult)
assert result.source_type == 'local'
assert result.analysis_depth == 'basic'
assert result.code_analysis is not None
assert 'files' in result.code_analysis
assert len(result.code_analysis['files']) >= 2
assert result.github_docs is None
assert result.github_insights is None
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_architecture_scenarios.py:720*

### test_scenario_3_local_analysis_c3x

**Category**: workflow  
**Description**: Workflow: Test C3.x analysis of local codebase.  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: local_codebase

'Test C3.x analysis of local codebase.'
analyzer = UnifiedCodebaseAnalyzer()
with patch('skill_seekers.cli.unified_codebase_analyzer.UnifiedCodebaseAnalyzer.c3x_analysis') as mock_c3x:
    mock_c3x.return_value = {'files': ['database.py', 'api.py'], 'analysis_type': 'c3x', 'c3_1_patterns': [{'name': 'Singleton', 'count': 1, 'file': 'database.py'}], 'c3_2_examples': [{'name': 'test_connection', 'file': 'test_database.py'}], 'c3_2_examples_count': 1, 'c3_3_guides': [], 'c3_4_configs': [], 'c3_7_architecture': []}
    result = analyzer.analyze(source=str(local_codebase), depth='c3x', fetch_github_metadata=False)
    assert result.source_type == 'local'
    assert result.analysis_depth == 'c3x'
    assert result.code_analysis['analysis_type'] == 'c3x'
    assert 'c3_1_patterns' in result.code_analysis
    assert 'c3_2_examples' in result.code_analysis
    assert result.github_docs is None
    assert result.github_insights is None
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_architecture_scenarios.py:742*

### test_scenario_3_router_without_github

**Category**: workflow  
**Description**: Workflow: Test router generation without GitHub data.  
**Expected**: assert 'internal-api' in skill_md  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test router generation without GitHub data.'
config1 = tmp_path / 'internal-database.json'
config1.write_text(json.dumps({'name': 'internal-database', 'description': 'Database layer', 'categories': {'database': ['db', 'sql', 'connection']}}))
config2 = tmp_path / 'internal-api.json'
config2.write_text(json.dumps({'name': 'internal-api', 'description': 'API endpoints', 'categories': {'api': ['api', 'endpoint', 'route']}}))
generator = RouterGenerator(config_paths=[str(config1), str(config2)], router_name='internal-tool', github_streams=None)
skill_md = generator.generate_skill_md()
assert 'internal-tool' in skill_md.lower()
assert 'Repository:' not in skill_md
assert 'Stars:' not in skill_md
assert '⭐' not in skill_md
assert 'Common Issues' not in skill_md
assert 'Issue #' not in skill_md
assert 'internal-database' in skill_md
assert 'internal-api' in skill_md
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_architecture_scenarios.py:778*

### test_token_efficiency_calculation

**Category**: workflow  
**Description**: Workflow: Calculate token efficiency with GitHub overhead.  
**Expected**: assert reduction_percent >= 29, f'Token reduction {reduction_percent:.1f}% below 29% (conservative target)'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Calculate token efficiency with GitHub overhead.'
monolithic_size = 666 + 50
router_size = 150 + 50
avg_subskill_size = (250 + 200 + 250 + 400) / 4
avg_subskill_with_github = avg_subskill_size + 30
avg_router_query = router_size + avg_subskill_with_github
reduction = (monolithic_size - avg_router_query) / monolithic_size
reduction_percent = reduction * 100
print('\n=== Token Efficiency Calculation ===')
print(f'Monolithic: {monolithic_size} lines')
print(f'Router: {router_size} lines')
print(f'Avg Sub-skill: {avg_subskill_with_github} lines')
print(f'Avg Query: {avg_router_query} lines')
print(f'Reduction: {reduction_percent:.1f}%')
print('Target: 35-40%')
assert reduction_percent >= 29, f'Token reduction {reduction_percent:.1f}% below 29% (conservative target)'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_architecture_scenarios.py:1025*

### test_bootstrap_validates_yaml_frontmatter

**Category**: workflow  
**Description**: Workflow: Verify generated SKILL.md has valid YAML frontmatter  
**Expected**: assert 'description:' in content[:500], 'Missing description field'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: run_bootstrap, output_skill_dir

'Verify generated SKILL.md has valid YAML frontmatter'
result = run_bootstrap()
assert result.returncode == 0
content = (output_skill_dir / 'SKILL.md').read_text()
assert content.startswith('---'), 'Missing frontmatter start'
lines = content.split('\n')
closing_found = False
for _i, line in enumerate(lines[1:], 1):
    if line.strip() == '---':
        closing_found = True
        break
assert closing_found, 'Missing frontmatter closing delimiter'
assert 'name:' in content[:500], 'Missing name field'
assert 'description:' in content[:500], 'Missing description field'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_bootstrap_skill_e2e.py:85*

### test_skill_installable_in_venv

**Category**: workflow  
**Description**: Workflow: Test skill is installable in clean virtual environment  
**Expected**: assert result.returncode == 0, f'Install failed: {result.stderr}'  
**Confidence**: 0.90  
**Tags**: pytest, workflow, integration  

```python
# Setup
# Fixtures: run_bootstrap, output_skill_dir, tmp_path

'Test skill is installable in clean virtual environment'
result = run_bootstrap()
assert result.returncode == 0
venv_path = tmp_path / 'test_venv'
subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True, timeout=60)
pip_path = venv_path / 'bin' / 'pip'
result = subprocess.run([str(pip_path), 'install', '-e', '.'], cwd=output_skill_dir.parent.parent, capture_output=True, text=True, timeout=120)
assert result.returncode == 0, f'Install failed: {result.stderr}'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_bootstrap_skill_e2e.py:122*

### test_analyze_quick_preset

**Category**: workflow  
**Description**: Workflow: Test quick analysis preset (real execution).  
**Expected**: self.assertIn('name:', skill_content, 'Missing name in frontmatter')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test quick analysis preset (real execution).'
output_dir = self.test_dir / 'output_quick'
result = self.run_command('analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick')
self.assertEqual(result.returncode, 0, f'Quick analysis failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}')
self.assertTrue(output_dir.exists(), 'Output directory not created')
skill_file = output_dir / 'SKILL.md'
self.assertTrue(skill_file.exists(), 'SKILL.md not generated')
skill_content = skill_file.read_text()
self.assertGreater(len(skill_content), 100, 'SKILL.md is too short')
self.assertIn('Codebase', skill_content, 'Missing codebase header')
self.assertIn('Analysis', skill_content, 'Missing analysis section')
self.assertTrue(skill_content.startswith('---'), 'Missing YAML frontmatter')
self.assertIn('name:', skill_content, 'Missing name in frontmatter')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_e2e.py:106*

### test_analyze_output_structure

**Category**: workflow  
**Description**: Workflow: Test that output has expected structure.  
**Expected**: self.assertTrue((output_dir / 'SKILL.md').exists(), 'SKILL.md missing')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test that output has expected structure.'
output_dir = self.test_dir / 'output_structure'
result = self.run_command('analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick')
self.assertEqual(result.returncode, 0, f'Analysis failed: {result.stderr}')
self.assertTrue((output_dir / 'SKILL.md').exists(), 'SKILL.md missing')
analysis_file = output_dir / 'code_analysis.json'
if analysis_file.exists():
    with open(analysis_file) as f:
        data = json.load(f)
        self.assertIsInstance(data, (dict, list), 'code_analysis.json is not valid JSON')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_e2e.py:228*

### test_analyze_then_check_output

**Category**: workflow  
**Description**: Workflow: Test analyzing and verifying output can be read.  
**Expected**: self.assertTrue(content.startswith('---'), 'Missing YAML frontmatter')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test directory.'
self.test_dir = Path(tempfile.mkdtemp(prefix='analyze_int_'))
(self.test_dir / 'main.py').write_text('\ndef hello():\n    """Say hello."""\n    return "Hello, World!"\n')

'Test analyzing and verifying output can be read.'
output_dir = self.test_dir / 'output'
result = subprocess.run(['skill-seekers', 'analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick'], capture_output=True, text=True, timeout=120)
self.assertEqual(result.returncode, 0, f'Analysis failed: {result.stderr}')
skill_file = output_dir / 'SKILL.md'
self.assertTrue(skill_file.exists(), 'SKILL.md not created')
content = skill_file.read_text()
self.assertGreater(len(content), 50, 'Output too short')
self.assertIn('Codebase', content, 'Missing codebase header')
self.assertTrue(content.startswith('---'), 'Missing YAML frontmatter')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_e2e.py:283*

### test_analyze_quick_preset

**Category**: workflow  
**Description**: Workflow: Test quick analysis preset (real execution).  
**Expected**: self.assertIn('name:', skill_content, 'Missing name in frontmatter')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test quick analysis preset (real execution).'
output_dir = self.test_dir / 'output_quick'
result = self.run_command('analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick')
self.assertEqual(result.returncode, 0, f'Quick analysis failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}')
self.assertTrue(output_dir.exists(), 'Output directory not created')
skill_file = output_dir / 'SKILL.md'
self.assertTrue(skill_file.exists(), 'SKILL.md not generated')
skill_content = skill_file.read_text()
self.assertGreater(len(skill_content), 100, 'SKILL.md is too short')
self.assertIn('Codebase', skill_content, 'Missing codebase header')
self.assertIn('Analysis', skill_content, 'Missing analysis section')
self.assertTrue(skill_content.startswith('---'), 'Missing YAML frontmatter')
self.assertIn('name:', skill_content, 'Missing name in frontmatter')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_e2e.py:106*

### test_analyze_output_structure

**Category**: workflow  
**Description**: Workflow: Test that output has expected structure.  
**Expected**: self.assertTrue((output_dir / 'SKILL.md').exists(), 'SKILL.md missing')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test that output has expected structure.'
output_dir = self.test_dir / 'output_structure'
result = self.run_command('analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick')
self.assertEqual(result.returncode, 0, f'Analysis failed: {result.stderr}')
self.assertTrue((output_dir / 'SKILL.md').exists(), 'SKILL.md missing')
analysis_file = output_dir / 'code_analysis.json'
if analysis_file.exists():
    with open(analysis_file) as f:
        data = json.load(f)
        self.assertIsInstance(data, (dict, list), 'code_analysis.json is not valid JSON')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_e2e.py:228*

### test_analyze_then_check_output

**Category**: workflow  
**Description**: Workflow: Test analyzing and verifying output can be read.  
**Expected**: self.assertTrue(content.startswith('---'), 'Missing YAML frontmatter')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test analyzing and verifying output can be read.'
output_dir = self.test_dir / 'output'
result = subprocess.run(['skill-seekers', 'analyze', '--directory', str(self.test_dir), '--output', str(output_dir), '--quick'], capture_output=True, text=True, timeout=120)
self.assertEqual(result.returncode, 0, f'Analysis failed: {result.stderr}')
skill_file = output_dir / 'SKILL.md'
self.assertTrue(skill_file.exists(), 'SKILL.md not created')
content = skill_file.read_text()
self.assertGreater(len(content), 50, 'Output too short')
self.assertIn('Codebase', content, 'Missing codebase header')
self.assertTrue(content.startswith('---'), 'Missing YAML frontmatter')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_e2e.py:283*

### test_e2e_all_platforms_from_same_skill

**Category**: workflow  
**Description**: Workflow: Test that all platforms can package the same skill  
**Expected**: self.assertTrue(str(packages['markdown']).endswith('.zip'))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Test that all platforms can package the same skill'
platforms = ['claude', 'gemini', 'openai', 'markdown']
packages = {}
for platform in platforms:
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(self.skill_dir, self.output_dir)
    self.assertTrue(package_path.exists(), f'Package not created for {platform}')
    packages[platform] = package_path
self.assertEqual(len(packages), 4)
self.assertTrue(str(packages['claude']).endswith('.zip'))
self.assertTrue(str(packages['gemini']).endswith('.tar.gz'))
self.assertTrue(str(packages['openai']).endswith('.zip'))
self.assertTrue(str(packages['markdown']).endswith('.zip'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_adaptors_e2e.py:129*

### test_e2e_claude_workflow

**Category**: workflow  
**Description**: Workflow: Test complete Claude workflow: package + verify structure  
**Expected**: self.assertTrue(str(package_path).endswith('.zip'))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Test complete Claude workflow: package + verify structure'
adaptor = get_adaptor('claude')
package_path = adaptor.package(self.skill_dir, self.output_dir)
self.assertTrue(package_path.exists())
self.assertTrue(str(package_path).endswith('.zip'))
with zipfile.ZipFile(package_path, 'r') as zf:
    names = zf.namelist()
    self.assertIn('SKILL.md', names)
    self.assertTrue(any(('references/' in name for name in names)))
    skill_content = zf.read('SKILL.md').decode('utf-8')
    self.assertGreater(len(skill_content), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_adaptors_e2e.py:155*

### test_e2e_gemini_workflow

**Category**: workflow  
**Description**: Workflow: Test complete Gemini workflow: package + verify structure  
**Expected**: self.assertTrue(str(package_path).endswith('.tar.gz'))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Test complete Gemini workflow: package + verify structure'
adaptor = get_adaptor('gemini')
package_path = adaptor.package(self.skill_dir, self.output_dir)
self.assertTrue(package_path.exists())
self.assertTrue(str(package_path).endswith('.tar.gz'))
with tarfile.open(package_path, 'r:gz') as tar:
    names = tar.getnames()
    self.assertIn('system_instructions.md', names)
    self.assertTrue(any(('references/' in name for name in names)))
    self.assertIn('gemini_metadata.json', names)
    metadata_member = tar.getmember('gemini_metadata.json')
    metadata_file = tar.extractfile(metadata_member)
    metadata = json.loads(metadata_file.read().decode('utf-8'))
    self.assertEqual(metadata['platform'], 'gemini')
    self.assertEqual(metadata['name'], 'test-skill')
    self.assertIn('created_with', metadata)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_adaptors_e2e.py:182*

### test_e2e_openai_workflow

**Category**: workflow  
**Description**: Workflow: Test complete OpenAI workflow: package + verify structure  
**Expected**: self.assertTrue(str(package_path).endswith('.zip'))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Test complete OpenAI workflow: package + verify structure'
adaptor = get_adaptor('openai')
package_path = adaptor.package(self.skill_dir, self.output_dir)
self.assertTrue(package_path.exists())
self.assertTrue(str(package_path).endswith('.zip'))
with zipfile.ZipFile(package_path, 'r') as zf:
    names = zf.namelist()
    self.assertIn('assistant_instructions.txt', names)
    self.assertTrue(any(('vector_store_files/' in name for name in names)))
    self.assertIn('openai_metadata.json', names)
    metadata_content = zf.read('openai_metadata.json').decode('utf-8')
    metadata = json.loads(metadata_content)
    self.assertEqual(metadata['platform'], 'openai')
    self.assertEqual(metadata['name'], 'test-skill')
    self.assertEqual(metadata['model'], 'gpt-4o')
    self.assertIn('file_search', metadata['tools'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_adaptors_e2e.py:215*

### test_e2e_markdown_workflow

**Category**: workflow  
**Description**: Workflow: Test complete Markdown workflow: package + verify structure  
**Expected**: self.assertTrue(str(package_path).endswith('.zip'))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Test complete Markdown workflow: package + verify structure'
adaptor = get_adaptor('markdown')
package_path = adaptor.package(self.skill_dir, self.output_dir)
self.assertTrue(package_path.exists())
self.assertTrue(str(package_path).endswith('.zip'))
with zipfile.ZipFile(package_path, 'r') as zf:
    names = zf.namelist()
    self.assertIn('README.md', names)
    self.assertIn('DOCUMENTATION.md', names)
    self.assertTrue(any(('references/' in name for name in names)))
    self.assertIn('metadata.json', names)
    doc_content = zf.read('DOCUMENTATION.md').decode('utf-8')
    self.assertIn('Getting Started', doc_content)
    self.assertIn('React Hooks', doc_content)
    self.assertIn('Components', doc_content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_adaptors_e2e.py:248*

### test_e2e_package_format_validation

**Category**: workflow  
**Description**: Workflow: Test that each platform creates correct package format  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Test that each platform creates correct package format'
test_cases = [('claude', '.zip'), ('gemini', '.tar.gz'), ('openai', '.zip'), ('markdown', '.zip')]
for platform, expected_ext in test_cases:
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(self.skill_dir, self.output_dir)
    if expected_ext == '.tar.gz':
        self.assertTrue(str(package_path).endswith('.tar.gz'), f'{platform} should create .tar.gz file')
    else:
        self.assertTrue(str(package_path).endswith('.zip'), f'{platform} should create .zip file')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_adaptors_e2e.py:283*

### test_e2e_package_filename_convention

**Category**: workflow  
**Description**: Workflow: Test that package filenames follow convention  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Test that package filenames follow convention'
test_cases = [('claude', 'test-skill.zip'), ('gemini', 'test-skill-gemini.tar.gz'), ('openai', 'test-skill-openai.zip'), ('markdown', 'test-skill-markdown.zip')]
for platform, expected_name in test_cases:
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(self.skill_dir, self.output_dir)
    self.assertEqual(package_path.name, expected_name, f'{platform} package filename incorrect')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_adaptors_e2e.py:306*

### test_e2e_all_platforms_preserve_references

**Category**: workflow  
**Description**: Workflow: Test that all platforms preserve reference files  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Test that all platforms preserve reference files'
ref_files = ['getting_started.md', 'hooks.md', 'components.md']
for platform in ['claude', 'gemini', 'openai', 'markdown']:
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(self.skill_dir, self.output_dir)
    if platform == 'gemini':
        with tarfile.open(package_path, 'r:gz') as tar:
            names = tar.getnames()
            for ref_file in ref_files:
                self.assertTrue(any((ref_file in name for name in names)), f'{platform}: {ref_file} not found in package')
    else:
        with zipfile.ZipFile(package_path, 'r') as zf:
            names = zf.namelist()
            for ref_file in ref_files:
                if platform == 'openai':
                    self.assertTrue(any((f'vector_store_files/{ref_file}' in name for name in names)), f'{platform}: {ref_file} not found in vector_store_files/')
                else:
                    self.assertTrue(any((ref_file in name for name in names)), f'{platform}: {ref_file} not found in package')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_adaptors_e2e.py:324*

### test_e2e_metadata_consistency

**Category**: workflow  
**Description**: Workflow: Test that metadata is consistent across platforms  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Test that metadata is consistent across platforms'
platforms_with_metadata = ['gemini', 'openai', 'markdown']
for platform in platforms_with_metadata:
    adaptor = get_adaptor(platform)
    package_path = adaptor.package(self.skill_dir, self.output_dir)
    if platform == 'gemini':
        with tarfile.open(package_path, 'r:gz') as tar:
            metadata_member = tar.getmember('gemini_metadata.json')
            metadata_file = tar.extractfile(metadata_member)
            metadata = json.loads(metadata_file.read().decode('utf-8'))
    else:
        with zipfile.ZipFile(package_path, 'r') as zf:
            metadata_filename = f'{platform}_metadata.json' if platform == 'openai' else 'metadata.json'
            metadata_content = zf.read(metadata_filename).decode('utf-8')
            metadata = json.loads(metadata_content)
    self.assertEqual(metadata['platform'], platform)
    self.assertEqual(metadata['name'], 'test-skill')
    self.assertIn('created_with', metadata)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_adaptors_e2e.py:357*

### test_e2e_format_skill_md_differences

**Category**: workflow  
**Description**: Workflow: Test that each platform formats SKILL.md differently  
**Expected**: self.assertFalse(formats['markdown'].startswith('---'))  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment with sample skill directory'
self.temp_dir = tempfile.TemporaryDirectory()
self.skill_dir = Path(self.temp_dir.name) / 'test-skill'
self.skill_dir.mkdir()
self._create_sample_skill()
self.output_dir = Path(self.temp_dir.name) / 'output'
self.output_dir.mkdir()

'Test that each platform formats SKILL.md differently'
metadata = SkillMetadata(name='test-skill', description='Test skill for E2E testing')
formats = {}
for platform in ['claude', 'gemini', 'openai', 'markdown']:
    adaptor = get_adaptor(platform)
    formatted = adaptor.format_skill_md(self.skill_dir, metadata)
    formats[platform] = formatted
self.assertTrue(formats['claude'].startswith('---'))
self.assertFalse(formats['gemini'].startswith('---'))
self.assertFalse(formats['markdown'].startswith('---'))
for platform, formatted in formats.items():
    self.assertIn('react', formatted.lower(), f'{platform} should contain skill content')
    self.assertGreater(len(formatted), 100, f'{platform} should have substantial content')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_adaptors_e2e.py:384*

### test_comprehensive_preset_implies_full_depth

**Category**: workflow  
**Description**: Workflow: Test that --comprehensive preset should trigger full depth.  
**Expected**: self.assertTrue(args.comprehensive)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Create parser for testing.'
self.parser = create_parser()

'Test that --comprehensive preset should trigger full depth.'
args = self.parser.parse_args(['analyze', '--directory', '.', '--comprehensive'])
self.assertTrue(args.comprehensive)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_command.py:170*

### test_comprehensive_preset_implies_full_depth

**Category**: workflow  
**Description**: Workflow: Test that --comprehensive preset should trigger full depth.  
**Expected**: self.assertTrue(args.comprehensive)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test that --comprehensive preset should trigger full depth.'
args = self.parser.parse_args(['analyze', '--directory', '.', '--comprehensive'])
self.assertTrue(args.comprehensive)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_command.py:170*

### test_codebase_analysis_enabled_by_default

**Category**: workflow  
**Description**: Workflow: Test that enable_codebase_analysis defaults to True.  
**Expected**: assert github_source.get('enable_codebase_analysis', True)  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: mock_config, temp_dir

'Test that enable_codebase_analysis defaults to True.'
config_without_flag = {'name': 'test', 'description': 'Test', 'sources': [{'type': 'github', 'repo': 'test/repo', 'local_repo_path': temp_dir}]}
config_path = os.path.join(temp_dir, 'config.json')
with open(config_path, 'w') as f:
    json.dump(config_without_flag, f)
scraper = UnifiedScraper(config_path)
github_source = scraper.config['sources'][0]
assert github_source.get('enable_codebase_analysis', True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_c3_integration.py:139*

### test_skip_codebase_analysis_flag

**Category**: workflow  
**Description**: Workflow: Test --skip-codebase-analysis CLI flag disables analysis.  
**Expected**: assert not github_source['enable_codebase_analysis']  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: mock_config, temp_dir

'Test --skip-codebase-analysis CLI flag disables analysis.'
config_path = os.path.join(temp_dir, 'config.json')
with open(config_path, 'w') as f:
    json.dump(mock_config, f)
scraper = UnifiedScraper(config_path)
for source in scraper.config.get('sources', []):
    if source['type'] == 'github':
        source['enable_codebase_analysis'] = False
github_source = scraper.config['sources'][0]
assert not github_source['enable_codebase_analysis']
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_c3_integration.py:160*

### test_architecture_md_generation

**Category**: workflow  
**Description**: Workflow: Test ARCHITECTURE.md is generated with all 8 sections.  
**Expected**: assert 'Security Alert' in content  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: mock_config, mock_c3_data, temp_dir

'Test ARCHITECTURE.md is generated with all 8 sections.'
github_data = {'readme': 'Test README', 'c3_analysis': mock_c3_data}
scraped_data = {'github': [{'repo': 'test/repo', 'repo_id': 'test_repo', 'idx': 0, 'data': github_data}]}
builder = UnifiedSkillBuilder(mock_config, scraped_data)
builder.skill_dir = temp_dir
c3_dir = os.path.join(temp_dir, 'references', 'codebase_analysis')
os.makedirs(c3_dir, exist_ok=True)
builder._generate_architecture_overview(c3_dir, mock_c3_data, github_data)
arch_file = os.path.join(c3_dir, 'ARCHITECTURE.md')
assert os.path.exists(arch_file)
with open(arch_file) as f:
    content = f.read()
assert '## 1. Overview' in content
assert '## 2. Architectural Patterns' in content
assert '## 3. Technology Stack' in content
assert '## 4. Design Patterns' in content
assert '## 5. Configuration Overview' in content
assert '## 6. Common Workflows' in content
assert '## 7. Usage Examples' in content
assert '## 8. Entry Points & Directory Structure' in content
assert 'MVC' in content
assert 'Flask' in content
assert 'Factory' in content
assert '15 usage example(s)' in content or '15 total' in content
assert 'Security Alert' in content
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_c3_integration.py:179*

### test_c3_reference_directory_structure

**Category**: workflow  
**Description**: Workflow: Test correct C3.x reference directory structure is created.  
**Expected**: assert os.path.exists(os.path.join(c3_dir, 'configuration', 'config_patterns.json'))  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: mock_config, mock_c3_data, temp_dir

'Test correct C3.x reference directory structure is created.'
github_data = {'readme': 'Test README', 'c3_analysis': mock_c3_data}
scraped_data = {'github': [{'repo': 'test/repo', 'repo_id': 'test_repo', 'idx': 0, 'data': github_data}]}
builder = UnifiedSkillBuilder(mock_config, scraped_data)
builder.skill_dir = temp_dir
c3_dir = os.path.join(temp_dir, 'references', 'codebase_analysis')
os.makedirs(c3_dir, exist_ok=True)
builder._generate_architecture_overview(c3_dir, mock_c3_data, github_data)
builder._generate_pattern_references(c3_dir, mock_c3_data.get('patterns'))
builder._generate_example_references(c3_dir, mock_c3_data.get('test_examples'))
builder._generate_guide_references(c3_dir, mock_c3_data.get('how_to_guides'))
builder._generate_config_references(c3_dir, mock_c3_data.get('config_patterns'))
builder._copy_architecture_details(c3_dir, mock_c3_data.get('architecture'))
assert os.path.exists(os.path.join(c3_dir, 'ARCHITECTURE.md'))
assert os.path.exists(os.path.join(c3_dir, 'patterns'))
assert os.path.exists(os.path.join(c3_dir, 'examples'))
assert os.path.exists(os.path.join(c3_dir, 'guides'))
assert os.path.exists(os.path.join(c3_dir, 'configuration'))
assert os.path.exists(os.path.join(c3_dir, 'architecture_details'))
assert os.path.exists(os.path.join(c3_dir, 'patterns', 'index.md'))
assert os.path.exists(os.path.join(c3_dir, 'examples', 'index.md'))
assert os.path.exists(os.path.join(c3_dir, 'guides', 'index.md'))
assert os.path.exists(os.path.join(c3_dir, 'configuration', 'index.md'))
assert os.path.exists(os.path.join(c3_dir, 'architecture_details', 'index.md'))
assert os.path.exists(os.path.join(c3_dir, 'patterns', 'detected_patterns.json'))
assert os.path.exists(os.path.join(c3_dir, 'examples', 'test_examples.json'))
assert os.path.exists(os.path.join(c3_dir, 'configuration', 'config_patterns.json'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_c3_integration.py:220*

### test_skill_md_includes_c3_summary

**Category**: workflow  
**Description**: Workflow: Test SKILL.md includes C3.x architecture summary.  
**Expected**: assert 'references/codebase_analysis/ARCHITECTURE.md' in content  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: mock_config, mock_c3_data, temp_dir

'Test SKILL.md includes C3.x architecture summary.'
scraped_data = {'github': {'data': {'readme': 'Test README', 'c3_analysis': mock_c3_data}}}
builder = UnifiedSkillBuilder(mock_config, scraped_data)
builder.skill_dir = temp_dir
builder._generate_skill_md()
skill_file = os.path.join(temp_dir, 'SKILL.md')
with open(skill_file) as f:
    content = f.read()
assert '## 🏗️ Architecture & Code Analysis' in content
assert 'Primary Architecture' in content
assert 'MVC' in content
assert 'Design Patterns' in content
assert 'Factory' in content
assert 'references/codebase_analysis/ARCHITECTURE.md' in content
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_c3_integration.py:339*

### test_format_skill_md

**Category**: workflow  
**Description**: Workflow: Test formatting SKILL.md as Chroma collection data.  
**Expected**: assert 'getting started' in categories or 'api' in categories  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test formatting SKILL.md as Chroma collection data.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
skill_md = skill_dir / 'SKILL.md'
skill_md.write_text('# Test Skill\n\nThis is a test skill for Chroma format.')
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start.')
(refs_dir / 'api.md').write_text('# API Reference\n\nAPI docs.')
adaptor = get_adaptor('chroma')
metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
collection_json = adaptor.format_skill_md(skill_dir, metadata)
collection = json.loads(collection_json)
assert 'documents' in collection
assert 'metadatas' in collection
assert 'ids' in collection
assert len(collection['documents']) == 3
assert len(collection['metadatas']) == 3
assert len(collection['ids']) == 3
for meta in collection['metadatas']:
    assert meta['source'] == 'test_skill'
    assert meta['version'] == '1.0.0'
    assert 'category' in meta
    assert 'file' in meta
    assert 'type' in meta
categories = {meta['category'] for meta in collection['metadatas']}
assert 'overview' in categories
assert 'getting started' in categories or 'api' in categories
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_chroma_adaptor.py:23*

### test_package_creates_json

**Category**: workflow  
**Description**: Workflow: Test packaging skill into JSON file.  
**Expected**: assert len(collection['documents']) > 0  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test packaging skill into JSON file.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('chroma')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.exists()
assert output_path.suffix == '.json'
assert 'chroma' in output_path.name
with open(output_path) as f:
    collection = json.load(f)
assert 'documents' in collection
assert 'metadatas' in collection
assert 'ids' in collection
assert len(collection['documents']) > 0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_chroma_adaptor.py:69*

### test_package_output_filename

**Category**: workflow  
**Description**: Workflow: Test package output filename generation.  
**Expected**: assert 'chroma' in output_path.name  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test package output filename generation.'
skill_dir = tmp_path / 'react'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# React\n\nReact docs.')
adaptor = get_adaptor('chroma')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.name == 'react-chroma.json'
output_path = adaptor.package(skill_dir, tmp_path / 'test.zip')
assert output_path.suffix == '.json'
assert 'chroma' in output_path.name
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_chroma_adaptor.py:94*

### test_empty_skill_directory

**Category**: workflow  
**Description**: Workflow: Test handling of empty skill directory.  
**Expected**: assert collection['ids'] == []  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test handling of empty skill directory.'
skill_dir = tmp_path / 'empty_skill'
skill_dir.mkdir()
adaptor = get_adaptor('chroma')
metadata = SkillMetadata(name='empty_skill', description='Empty', version='1.0.0')
collection_json = adaptor.format_skill_md(skill_dir, metadata)
collection = json.loads(collection_json)
assert collection['documents'] == []
assert collection['metadatas'] == []
assert collection['ids'] == []
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_chroma_adaptor.py:153*

### test_references_only

**Category**: workflow  
**Description**: Workflow: Test skill with references but no SKILL.md.  
**Expected**: assert collection['metadatas'][0]['type'] == 'reference'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test skill with references but no SKILL.md.'
skill_dir = tmp_path / 'refs_only'
skill_dir.mkdir()
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'test.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('chroma')
metadata = SkillMetadata(name='refs_only', description='Refs only', version='1.0.0')
collection_json = adaptor.format_skill_md(skill_dir, metadata)
collection = json.loads(collection_json)
assert len(collection['documents']) == 1
assert collection['metadatas'][0]['category'] == 'test'
assert collection['metadatas'][0]['type'] == 'reference'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_chroma_adaptor.py:169*

### test_get_config_in_subdir

**Category**: workflow  
**Description**: Workflow: Test loading config from subdirectory.  
**Expected**: assert result == config_data  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: git_repo, temp_cache_dir

'Test loading config from subdirectory.'
repo_path = temp_cache_dir / 'test-repo'
configs_dir = repo_path / 'configs'
configs_dir.mkdir(parents=True)
config_data = {'name': 'nestjs'}
(configs_dir / 'nestjs.json').write_text(json.dumps(config_data))
result = git_repo.get_config(repo_path, 'nestjs')
assert result == config_data
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_repo.py:370*

### test_valid_complete_config

**Category**: workflow  
**Description**: Workflow: Test valid complete configuration  
**Expected**: self.assertEqual(len(errors), 0, f'Valid config should have no errors, got: {errors}')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test valid complete configuration'
config = {'name': 'godot', 'base_url': 'https://docs.godotengine.org/en/stable/', 'description': 'Godot Engine documentation', 'selectors': {'main_content': 'div[role="main"]', 'title': 'title', 'code_blocks': 'pre code'}, 'url_patterns': {'include': ['/guide/', '/api/'], 'exclude': ['/blog/']}, 'categories': {'getting_started': ['intro', 'tutorial'], 'api': ['api', 'reference']}, 'rate_limit': 0.5, 'max_pages': 500}
errors, _ = validate_config(config)
self.assertEqual(len(errors), 0, f'Valid config should have no errors, got: {errors}')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_validation.py:27*

### test_valid_name_formats

**Category**: workflow  
**Description**: Workflow: Test various valid name formats  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test various valid name formats'
valid_names = ['test', 'test-skill', 'test_skill', 'TestSkill123', 'my-awesome-skill_v2']
for name in valid_names:
    config = {'name': name, 'base_url': 'https://example.com/'}
    errors, _ = validate_config(config)
    name_errors = [e for e in errors if 'invalid name' in e.lower()]
    self.assertEqual(len(name_errors), 0, f"Name '{name}' should be valid")
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_validation.py:64*

### test_valid_complete_config

**Category**: workflow  
**Description**: Workflow: Test valid complete configuration  
**Expected**: self.assertEqual(len(errors), 0, f'Valid config should have no errors, got: {errors}')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test valid complete configuration'
config = {'name': 'godot', 'base_url': 'https://docs.godotengine.org/en/stable/', 'description': 'Godot Engine documentation', 'selectors': {'main_content': 'div[role="main"]', 'title': 'title', 'code_blocks': 'pre code'}, 'url_patterns': {'include': ['/guide/', '/api/'], 'exclude': ['/blog/']}, 'categories': {'getting_started': ['intro', 'tutorial'], 'api': ['api', 'reference']}, 'rate_limit': 0.5, 'max_pages': 500}
errors, _ = validate_config(config)
self.assertEqual(len(errors), 0, f'Valid config should have no errors, got: {errors}')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_validation.py:27*

### test_valid_name_formats

**Category**: workflow  
**Description**: Workflow: Test various valid name formats  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test various valid name formats'
valid_names = ['test', 'test-skill', 'test_skill', 'TestSkill123', 'my-awesome-skill_v2']
for name in valid_names:
    config = {'name': name, 'base_url': 'https://example.com/'}
    errors, _ = validate_config(config)
    name_errors = [e for e in errors if 'invalid name' in e.lower()]
    self.assertEqual(len(name_errors), 0, f"Name '{name}' should be valid")
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_validation.py:64*

### test_class_formatting

**Category**: workflow  
**Description**: Workflow: Test markdown formatting for class signatures.  
**Expected**: self.assertIn('Add two numbers', content)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir) / 'api_reference'

'Test markdown formatting for class signatures.'
code_analysis = {'files': [{'file': 'test.py', 'language': 'Python', 'classes': [{'name': 'Calculator', 'docstring': 'A simple calculator class.', 'base_classes': ['object'], 'methods': [{'name': 'add', 'parameters': [{'name': 'a', 'type_hint': 'int', 'default': None}, {'name': 'b', 'type_hint': 'int', 'default': None}], 'return_type': 'int', 'docstring': 'Add two numbers.', 'is_async': False, 'is_method': True, 'decorators': []}]}], 'functions': []}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
self.assertEqual(len(generated), 1)
output_file = list(generated.values())[0]
self.assertTrue(output_file.exists())
content = output_file.read_text()
self.assertIn('### Calculator', content)
self.assertIn('A simple calculator class', content)
self.assertIn('**Inherits from**: object', content)
self.assertIn('##### add', content)
self.assertIn('Add two numbers', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_api_reference_builder.py:38*

### test_function_formatting

**Category**: workflow  
**Description**: Workflow: Test markdown formatting for function signatures.  
**Expected**: self.assertIn('**Returns**: `int`', content)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir) / 'api_reference'

'Test markdown formatting for function signatures.'
code_analysis = {'files': [{'file': 'utils.py', 'language': 'Python', 'classes': [], 'functions': [{'name': 'calculate_sum', 'parameters': [{'name': 'numbers', 'type_hint': 'list', 'default': None}], 'return_type': 'int', 'docstring': 'Calculate sum of numbers.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
output_file = list(generated.values())[0]
content = output_file.read_text()
self.assertIn('## Functions', content)
self.assertIn('### calculate_sum', content)
self.assertIn('Calculate sum of numbers', content)
self.assertIn('**Returns**: `int`', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_api_reference_builder.py:87*

### test_parameter_table_generation

**Category**: workflow  
**Description**: Workflow: Test parameter table formatting.  
**Expected**: self.assertIn('| active | bool | True |', content)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir) / 'api_reference'

'Test parameter table formatting.'
code_analysis = {'files': [{'file': 'test.py', 'language': 'Python', 'classes': [], 'functions': [{'name': 'create_user', 'parameters': [{'name': 'name', 'type_hint': 'str', 'default': None}, {'name': 'age', 'type_hint': 'int', 'default': '18'}, {'name': 'active', 'type_hint': 'bool', 'default': 'True'}], 'return_type': 'dict', 'docstring': 'Create a user object.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
output_file = list(generated.values())[0]
content = output_file.read_text()
self.assertIn('**Parameters**:', content)
self.assertIn('| Name | Type | Default | Description |', content)
self.assertIn('| name | str | - |', content)
self.assertIn('| age | int | 18 |', content)
self.assertIn('| active | bool | True |', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_api_reference_builder.py:124*

### test_markdown_output_structure

**Category**: workflow  
**Description**: Workflow: Test overall markdown document structure.  
**Expected**: self.assertLess(classes_pos, functions_pos)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir) / 'api_reference'

'Test overall markdown document structure.'
code_analysis = {'files': [{'file': 'module.py', 'language': 'Python', 'classes': [{'name': 'TestClass', 'docstring': 'Test class.', 'base_classes': [], 'methods': []}], 'functions': [{'name': 'test_func', 'parameters': [], 'return_type': None, 'docstring': 'Test function.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
output_file = list(generated.values())[0]
content = output_file.read_text()
self.assertIn('# API Reference: module.py', content)
self.assertIn('**Language**: Python', content)
self.assertIn('**Source**: `module.py`', content)
classes_pos = content.find('## Classes')
functions_pos = content.find('## Functions')
self.assertNotEqual(classes_pos, -1)
self.assertNotEqual(functions_pos, -1)
self.assertLess(classes_pos, functions_pos)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_api_reference_builder.py:164*

### test_integration_with_code_analyzer

**Category**: workflow  
**Description**: Workflow: Test integration with actual code analyzer output format.  
**Expected**: self.assertIn('**Language**: JavaScript', js_content)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir) / 'api_reference'

'Test integration with actual code analyzer output format.'
code_analysis = {'files': [{'file': 'calculator.py', 'language': 'Python', 'classes': [{'name': 'Calculator', 'base_classes': [], 'methods': [{'name': 'add', 'parameters': [{'name': 'a', 'type_hint': 'float', 'default': None}, {'name': 'b', 'type_hint': 'float', 'default': None}], 'return_type': 'float', 'docstring': 'Add two numbers.', 'decorators': [], 'is_async': False, 'is_method': True}], 'docstring': 'Calculator class.', 'line_number': 1}], 'functions': []}, {'file': 'utils.js', 'language': 'JavaScript', 'classes': [], 'functions': [{'name': 'formatDate', 'parameters': [{'name': 'date', 'type_hint': None, 'default': None}], 'return_type': None, 'docstring': None, 'is_async': False, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
self.assertEqual(len(generated), 2)
filenames = [f.name for f in generated.values()]
self.assertIn('calculator.md', filenames)
self.assertIn('utils.md', filenames)
py_file = next((f for f in generated.values() if f.name == 'calculator.md'))
py_content = py_file.read_text()
self.assertIn('Calculator class', py_content)
self.assertIn('add(a: float, b: float) → float', py_content)
js_file = next((f for f in generated.values() if f.name == 'utils.md'))
js_content = js_file.read_text()
self.assertIn('formatDate', js_content)
self.assertIn('**Language**: JavaScript', js_content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_api_reference_builder.py:214*

### test_async_function_indicator

**Category**: workflow  
**Description**: Workflow: Test that async functions are marked in output.  
**Expected**: self.assertIn('fetch_data', content)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test environment'
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir) / 'api_reference'

'Test that async functions are marked in output.'
code_analysis = {'files': [{'file': 'async_utils.py', 'language': 'Python', 'classes': [], 'functions': [{'name': 'fetch_data', 'parameters': [{'name': 'url', 'type_hint': 'str', 'default': None}], 'return_type': 'dict', 'docstring': 'Fetch data from URL.', 'is_async': True, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
output_file = list(generated.values())[0]
content = output_file.read_text()
self.assertIn('**Async function**', content)
self.assertIn('fetch_data', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_api_reference_builder.py:288*

### test_class_formatting

**Category**: workflow  
**Description**: Workflow: Test markdown formatting for class signatures.  
**Expected**: self.assertIn('Add two numbers', content)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test markdown formatting for class signatures.'
code_analysis = {'files': [{'file': 'test.py', 'language': 'Python', 'classes': [{'name': 'Calculator', 'docstring': 'A simple calculator class.', 'base_classes': ['object'], 'methods': [{'name': 'add', 'parameters': [{'name': 'a', 'type_hint': 'int', 'default': None}, {'name': 'b', 'type_hint': 'int', 'default': None}], 'return_type': 'int', 'docstring': 'Add two numbers.', 'is_async': False, 'is_method': True, 'decorators': []}]}], 'functions': []}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
self.assertEqual(len(generated), 1)
output_file = list(generated.values())[0]
self.assertTrue(output_file.exists())
content = output_file.read_text()
self.assertIn('### Calculator', content)
self.assertIn('A simple calculator class', content)
self.assertIn('**Inherits from**: object', content)
self.assertIn('##### add', content)
self.assertIn('Add two numbers', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_api_reference_builder.py:38*

### test_function_formatting

**Category**: workflow  
**Description**: Workflow: Test markdown formatting for function signatures.  
**Expected**: self.assertIn('**Returns**: `int`', content)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test markdown formatting for function signatures.'
code_analysis = {'files': [{'file': 'utils.py', 'language': 'Python', 'classes': [], 'functions': [{'name': 'calculate_sum', 'parameters': [{'name': 'numbers', 'type_hint': 'list', 'default': None}], 'return_type': 'int', 'docstring': 'Calculate sum of numbers.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
output_file = list(generated.values())[0]
content = output_file.read_text()
self.assertIn('## Functions', content)
self.assertIn('### calculate_sum', content)
self.assertIn('Calculate sum of numbers', content)
self.assertIn('**Returns**: `int`', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_api_reference_builder.py:87*

### test_parameter_table_generation

**Category**: workflow  
**Description**: Workflow: Test parameter table formatting.  
**Expected**: self.assertIn('| active | bool | True |', content)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test parameter table formatting.'
code_analysis = {'files': [{'file': 'test.py', 'language': 'Python', 'classes': [], 'functions': [{'name': 'create_user', 'parameters': [{'name': 'name', 'type_hint': 'str', 'default': None}, {'name': 'age', 'type_hint': 'int', 'default': '18'}, {'name': 'active', 'type_hint': 'bool', 'default': 'True'}], 'return_type': 'dict', 'docstring': 'Create a user object.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
output_file = list(generated.values())[0]
content = output_file.read_text()
self.assertIn('**Parameters**:', content)
self.assertIn('| Name | Type | Default | Description |', content)
self.assertIn('| name | str | - |', content)
self.assertIn('| age | int | 18 |', content)
self.assertIn('| active | bool | True |', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_api_reference_builder.py:124*

### test_markdown_output_structure

**Category**: workflow  
**Description**: Workflow: Test overall markdown document structure.  
**Expected**: self.assertLess(classes_pos, functions_pos)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test overall markdown document structure.'
code_analysis = {'files': [{'file': 'module.py', 'language': 'Python', 'classes': [{'name': 'TestClass', 'docstring': 'Test class.', 'base_classes': [], 'methods': []}], 'functions': [{'name': 'test_func', 'parameters': [], 'return_type': None, 'docstring': 'Test function.', 'is_async': False, 'is_method': False, 'decorators': []}]}]}
builder = APIReferenceBuilder(code_analysis)
generated = builder.build_reference(self.output_dir)
output_file = list(generated.values())[0]
content = output_file.read_text()
self.assertIn('# API Reference: module.py', content)
self.assertIn('**Language**: Python', content)
self.assertIn('**Source**: `module.py`', content)
classes_pos = content.find('## Classes')
functions_pos = content.find('## Functions')
self.assertNotEqual(classes_pos, -1)
self.assertNotEqual(functions_pos, -1)
self.assertLess(classes_pos, functions_pos)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_api_reference_builder.py:164*

### test_export_to_weaviate

**Category**: workflow  
**Description**: Workflow: Test Weaviate export tool.  
**Expected**: assert 'weaviate.Client' in text  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: test_skill_dir

'Test Weaviate export tool.'
output_dir = test_skill_dir.parent
args = {'skill_dir': str(test_skill_dir), 'output_dir': str(output_dir)}
result = run_async(export_to_weaviate_impl(args))
assert isinstance(result, list)
assert len(result) == 1
assert hasattr(result[0], 'text')
text = result[0].text
assert '✅ Weaviate Export Complete!' in text
assert 'test_skill-weaviate.json' in text
assert 'weaviate.Client' in text
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_vector_dbs.py:60*

### test_export_to_chroma

**Category**: workflow  
**Description**: Workflow: Test Chroma export tool.  
**Expected**: assert 'chromadb' in text  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: test_skill_dir

'Test Chroma export tool.'
output_dir = test_skill_dir.parent
args = {'skill_dir': str(test_skill_dir), 'output_dir': str(output_dir)}
result = run_async(export_to_chroma_impl(args))
assert isinstance(result, list)
assert len(result) == 1
assert hasattr(result[0], 'text')
text = result[0].text
assert '✅ Chroma Export Complete!' in text
assert 'test_skill-chroma.json' in text
assert 'chromadb' in text
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_vector_dbs.py:83*

### test_export_to_faiss

**Category**: workflow  
**Description**: Workflow: Test FAISS export tool.  
**Expected**: assert 'import faiss' in text  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: test_skill_dir

'Test FAISS export tool.'
output_dir = test_skill_dir.parent
args = {'skill_dir': str(test_skill_dir), 'output_dir': str(output_dir)}
result = run_async(export_to_faiss_impl(args))
assert isinstance(result, list)
assert len(result) == 1
assert hasattr(result[0], 'text')
text = result[0].text
assert '✅ FAISS Export Complete!' in text
assert 'test_skill-faiss.json' in text
assert 'import faiss' in text
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_vector_dbs.py:106*

### test_export_to_qdrant

**Category**: workflow  
**Description**: Workflow: Test Qdrant export tool.  
**Expected**: assert 'QdrantClient' in text  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: test_skill_dir

'Test Qdrant export tool.'
output_dir = test_skill_dir.parent
args = {'skill_dir': str(test_skill_dir), 'output_dir': str(output_dir)}
result = run_async(export_to_qdrant_impl(args))
assert isinstance(result, list)
assert len(result) == 1
assert hasattr(result[0], 'text')
text = result[0].text
assert '✅ Qdrant Export Complete!' in text
assert 'test_skill-qdrant.json' in text
assert 'QdrantClient' in text
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_vector_dbs.py:129*

### test_all_exports_create_files

**Category**: workflow  
**Description**: Workflow: Test that all export tools create output files.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: test_skill_dir

'Test that all export tools create output files.'
output_dir = test_skill_dir.parent
exports = [('weaviate', export_to_weaviate_impl), ('chroma', export_to_chroma_impl), ('faiss', export_to_faiss_impl), ('qdrant', export_to_qdrant_impl)]
for target, export_func in exports:
    args = {'skill_dir': str(test_skill_dir), 'output_dir': str(output_dir)}
    result = run_async(export_func(args))
    assert isinstance(result, list)
    text = result[0].text
    assert '✅' in text
    expected_file = output_dir / f'test_skill-{target}.json'
    assert expected_file.exists(), f'{target} export file not created'
    with open(expected_file) as f:
        data = json.load(f)
        assert isinstance(data, dict)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_vector_dbs.py:179*

### test_format_skill_md

**Category**: workflow  
**Description**: Workflow: Test formatting SKILL.md as LlamaIndex Documents.  
**Expected**: assert 'getting started' in categories or 'api' in categories  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test formatting SKILL.md as LlamaIndex Documents.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
skill_md = skill_dir / 'SKILL.md'
skill_md.write_text('# Test Skill\n\nThis is a test skill for LlamaIndex format.')
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start.')
(refs_dir / 'api.md').write_text('# API Reference\n\nAPI docs.')
adaptor = get_adaptor('llama-index')
metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
documents_json = adaptor.format_skill_md(skill_dir, metadata)
documents = json.loads(documents_json)
assert len(documents) == 3
for doc in documents:
    assert 'text' in doc
    assert 'metadata' in doc
    assert doc['metadata']['source'] == 'test_skill'
    assert doc['metadata']['version'] == '1.0.0'
    assert 'category' in doc['metadata']
    assert 'file' in doc['metadata']
    assert 'type' in doc['metadata']
categories = {doc['metadata']['category'] for doc in documents}
assert 'overview' in categories
assert 'getting started' in categories or 'api' in categories
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_llama_index_adaptor.py:23*

### test_package_creates_json

**Category**: workflow  
**Description**: Workflow: Test packaging skill into JSON file.  
**Expected**: assert 'metadata' in documents[0]  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test packaging skill into JSON file.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('llama-index')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.exists()
assert output_path.suffix == '.json'
assert 'llama' in output_path.name
with open(output_path) as f:
    documents = json.load(f)
assert isinstance(documents, list)
assert len(documents) > 0
assert 'text' in documents[0]
assert 'metadata' in documents[0]
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_llama_index_adaptor.py:65*

### test_package_output_filename

**Category**: workflow  
**Description**: Workflow: Test package output filename generation.  
**Expected**: assert 'llama' in output_path.name  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test package output filename generation.'
skill_dir = tmp_path / 'react'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# React\n\nReact docs.')
adaptor = get_adaptor('llama-index')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.name == 'react-llama-index.json'
output_path = adaptor.package(skill_dir, tmp_path / 'test.zip')
assert output_path.suffix == '.json'
assert 'llama' in output_path.name
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_llama_index_adaptor.py:90*

### test_empty_skill_directory

**Category**: workflow  
**Description**: Workflow: Test handling of empty skill directory.  
**Expected**: assert documents == []  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test handling of empty skill directory.'
skill_dir = tmp_path / 'empty_skill'
skill_dir.mkdir()
adaptor = get_adaptor('llama-index')
metadata = SkillMetadata(name='empty_skill', description='Empty', version='1.0.0')
documents_json = adaptor.format_skill_md(skill_dir, metadata)
documents = json.loads(documents_json)
assert documents == []
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_llama_index_adaptor.py:146*

### test_references_only

**Category**: workflow  
**Description**: Workflow: Test skill with references but no SKILL.md.  
**Expected**: assert documents[0]['metadata']['type'] == 'reference'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test skill with references but no SKILL.md.'
skill_dir = tmp_path / 'refs_only'
skill_dir.mkdir()
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'test.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('llama-index')
metadata = SkillMetadata(name='refs_only', description='Refs only', version='1.0.0')
documents_json = adaptor.format_skill_md(skill_dir, metadata)
documents = json.loads(documents_json)
assert len(documents) == 1
assert documents[0]['metadata']['category'] == 'test'
assert documents[0]['metadata']['type'] == 'reference'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_llama_index_adaptor.py:160*

### test_chroma_upload_without_chromadb_installed

**Category**: workflow  
**Description**: Workflow: Test upload fails gracefully without chromadb installed.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: sample_chroma_package

'Test upload fails gracefully without chromadb installed.'
adaptor = get_adaptor('chroma')
import sys
chromadb_backup = sys.modules.get('chromadb')
if 'chromadb' in sys.modules:
    del sys.modules['chromadb']
try:
    result = adaptor.upload(sample_chroma_package)
    assert result['success'] is False
    assert 'chromadb not installed' in result['message']
    assert 'pip install chromadb' in result['message']
finally:
    if chromadb_backup:
        sys.modules['chromadb'] = chromadb_backup
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_integration.py:79*

### test_weaviate_upload_without_weaviate_installed

**Category**: workflow  
**Description**: Workflow: Test upload fails gracefully without weaviate-client installed.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: sample_weaviate_package

'Test upload fails gracefully without weaviate-client installed.'
adaptor = get_adaptor('weaviate')
import sys
weaviate_backup = sys.modules.get('weaviate')
if 'weaviate' in sys.modules:
    del sys.modules['weaviate']
try:
    result = adaptor.upload(sample_weaviate_package)
    assert result['success'] is False
    assert 'weaviate-client not installed' in result['message']
    assert 'pip install weaviate-client' in result['message']
finally:
    if weaviate_backup:
        sys.modules['weaviate'] = weaviate_backup
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_integration.py:121*

### test_chunk_document_single_chunk

**Category**: workflow  
**Description**: Workflow: Test chunking when document fits in single chunk.  
**Expected**: assert chunk_meta.source == 'test'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test chunking when document fits in single chunk.'
ingester = StreamingIngester(chunk_size=1000, chunk_overlap=100)
content = 'Small document'
metadata = {'source': 'test', 'file': 'test.md', 'category': 'overview'}
chunks = list(ingester.chunk_document(content, metadata))
assert len(chunks) == 1
chunk_text, chunk_meta = chunks[0]
assert chunk_text == content
assert chunk_meta.chunk_index == 0
assert chunk_meta.total_chunks == 1
assert chunk_meta.source == 'test'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_streaming_ingestion.py:48*

### test_chunk_document_multiple_chunks

**Category**: workflow  
**Description**: Workflow: Test chunking with multiple chunks.  
**Expected**: assert len(chunks) > 1  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test chunking with multiple chunks.'
ingester = StreamingIngester(chunk_size=100, chunk_overlap=20)
content = 'A' * 250
metadata = {'source': 'test', 'file': 'test.md', 'category': 'overview'}
chunks = list(ingester.chunk_document(content, metadata))
assert len(chunks) > 1
for i in range(len(chunks) - 1):
    chunk1_text, chunk1_meta = chunks[i]
    chunk2_text, chunk2_meta = chunks[i + 1]
    assert chunk2_meta.char_start < chunk1_meta.char_end
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_streaming_ingestion.py:66*

### test_chunk_document_metadata

**Category**: workflow  
**Description**: Workflow: Test chunk metadata is correct.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test chunk metadata is correct.'
ingester = StreamingIngester(chunk_size=100, chunk_overlap=20)
content = 'B' * 250
metadata = {'source': 'test_source', 'file': 'test_file.md', 'category': 'test_cat'}
chunks = list(ingester.chunk_document(content, metadata))
for i, (chunk_text, chunk_meta) in enumerate(chunks):
    assert chunk_meta.chunk_index == i
    assert chunk_meta.total_chunks == len(chunks)
    assert chunk_meta.source == 'test_source'
    assert chunk_meta.file == 'test_file.md'
    assert chunk_meta.category == 'test_cat'
    assert len(chunk_meta.chunk_id) == 32
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_streaming_ingestion.py:87*

### test_stream_skill_directory

**Category**: workflow  
**Description**: Workflow: Test streaming entire skill directory.  
**Expected**: assert 'overview' in categories  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: temp_skill_dir

'Test streaming entire skill directory.'
ingester = StreamingIngester(chunk_size=500, chunk_overlap=50)
chunks = list(ingester.stream_skill_directory(temp_skill_dir))
assert len(chunks) > 0
assert ingester.progress is not None
assert ingester.progress.total_documents == 3
assert ingester.progress.processed_documents == 3
assert ingester.progress.total_chunks > 0
assert ingester.progress.processed_chunks == len(chunks)
sources = set()
categories = set()
for chunk_text, chunk_meta in chunks:
    assert chunk_text
    assert chunk_meta['chunk_id']
    sources.add(chunk_meta['source'])
    categories.add(chunk_meta['category'])
assert 'test_skill' in sources
assert 'overview' in categories
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_streaming_ingestion.py:105*

### test_checkpoint_save_load

**Category**: workflow  
**Description**: Workflow: Test checkpoint save and load.  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test checkpoint save and load.'
ingester = StreamingIngester()
with tempfile.TemporaryDirectory() as tmpdir:
    checkpoint_path = Path(tmpdir) / 'checkpoint.json'
    ingester.progress = IngestionProgress(total_documents=10, processed_documents=5, total_chunks=100, processed_chunks=50, failed_chunks=2, bytes_processed=10000, start_time=1234567890.0)
    state = {'last_processed_file': 'test.md', 'batch_number': 3}
    ingester.save_checkpoint(checkpoint_path, state)
    assert checkpoint_path.exists()
    loaded_state = ingester.load_checkpoint(checkpoint_path)
    assert loaded_state == state
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_streaming_ingestion.py:178*

### test_chunk_size_validation

**Category**: workflow  
**Description**: Workflow: Test different chunk sizes.  
**Expected**: assert len(chunks_small) > len(chunks_large)  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test different chunk sizes.'
content = 'X' * 1000
ingester_small = StreamingIngester(chunk_size=100, chunk_overlap=10)
chunks_small = list(ingester_small.chunk_document(content, {'source': 'test', 'file': 'test.md', 'category': 'test'}))
ingester_large = StreamingIngester(chunk_size=500, chunk_overlap=50)
chunks_large = list(ingester_large.chunk_document(content, {'source': 'test', 'file': 'test.md', 'category': 'test'}))
assert len(chunks_small) > len(chunks_large)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_streaming_ingestion.py:243*

### test_format_skill_md

**Category**: workflow  
**Description**: Workflow: Test formatting SKILL.md as Qdrant points.  
**Expected**: assert 'getting started' in categories or 'api' in categories  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test formatting SKILL.md as Qdrant points.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
skill_md = skill_dir / 'SKILL.md'
skill_md.write_text('# Test Skill\n\nThis is a test skill for Qdrant format.')
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'getting_started.md').write_text('# Getting Started\n\nQuick start.')
(refs_dir / 'api.md').write_text('# API Reference\n\nAPI docs.')
adaptor = get_adaptor('qdrant')
metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
points_json = adaptor.format_skill_md(skill_dir, metadata)
result = json.loads(points_json)
assert 'collection_name' in result
assert 'points' in result
assert 'config' in result
assert len(result['points']) == 3
for point in result['points']:
    assert 'id' in point
    assert 'vector' in point
    assert 'payload' in point
    payload = point['payload']
    assert 'content' in payload
    assert payload['source'] == 'test_skill'
    assert payload['version'] == '1.0.0'
    assert 'category' in payload
    assert 'file' in payload
    assert 'type' in payload
categories = {point['payload']['category'] for point in result['points']}
assert 'overview' in categories
assert 'getting started' in categories or 'api' in categories
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_qdrant_adaptor.py:23*

### test_package_creates_json

**Category**: workflow  
**Description**: Workflow: Test packaging skill into JSON file.  
**Expected**: assert 'payload' in result['points'][0]  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test packaging skill into JSON file.'
skill_dir = tmp_path / 'test_skill'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('qdrant')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.exists()
assert output_path.suffix == '.json'
assert 'qdrant' in output_path.name
with open(output_path) as f:
    result = json.load(f)
assert isinstance(result, dict)
assert 'points' in result
assert len(result['points']) > 0
assert 'id' in result['points'][0]
assert 'payload' in result['points'][0]
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_qdrant_adaptor.py:71*

### test_package_output_filename

**Category**: workflow  
**Description**: Workflow: Test package output filename generation.  
**Expected**: assert 'qdrant' in output_path.name  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test package output filename generation.'
skill_dir = tmp_path / 'react'
skill_dir.mkdir()
(skill_dir / 'SKILL.md').write_text('# React\n\nReact docs.')
adaptor = get_adaptor('qdrant')
output_path = adaptor.package(skill_dir, tmp_path)
assert output_path.name == 'react-qdrant.json'
output_path = adaptor.package(skill_dir, tmp_path / 'test.zip')
assert output_path.suffix == '.json'
assert 'qdrant' in output_path.name
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_qdrant_adaptor.py:97*

### test_empty_skill_directory

**Category**: workflow  
**Description**: Workflow: Test handling of empty skill directory.  
**Expected**: assert result['points'] == []  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test handling of empty skill directory.'
skill_dir = tmp_path / 'empty_skill'
skill_dir.mkdir()
adaptor = get_adaptor('qdrant')
metadata = SkillMetadata(name='empty_skill', description='Empty', version='1.0.0')
points_json = adaptor.format_skill_md(skill_dir, metadata)
result = json.loads(points_json)
assert 'points' in result
assert result['points'] == []
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_qdrant_adaptor.py:153*

### test_references_only

**Category**: workflow  
**Description**: Workflow: Test skill with references but no SKILL.md.  
**Expected**: assert result['points'][0]['payload']['type'] == 'reference'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test skill with references but no SKILL.md.'
skill_dir = tmp_path / 'refs_only'
skill_dir.mkdir()
refs_dir = skill_dir / 'references'
refs_dir.mkdir()
(refs_dir / 'test.md').write_text('# Test\n\nTest content.')
adaptor = get_adaptor('qdrant')
metadata = SkillMetadata(name='refs_only', description='Refs only', version='1.0.0')
points_json = adaptor.format_skill_md(skill_dir, metadata)
result = json.loads(points_json)
assert len(result['points']) == 1
assert result['points'][0]['payload']['category'] == 'test'
assert result['points'][0]['payload']['type'] == 'reference'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_qdrant_adaptor.py:168*

### test_categorize_by_keywords

**Category**: workflow  
**Description**: Workflow: Test categorization using keyword matching  
**Expected**: self.assertEqual(len(categories['test']['pages']), 2)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()

'Test categorization using keyword matching'
config = {'name': 'test', 'pdf_path': 'test.pdf', 'categories': {'getting_started': ['introduction', 'getting started'], 'api': ['api', 'reference', 'function']}}
converter = self.PDFToSkillConverter(config)
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Introduction to the API', 'chapter': 'Chapter 1: Getting Started'}, {'page_number': 2, 'text': 'API reference for functions', 'chapter': None}]}
categories = converter.categorize_content()
self.assertIn('test', categories)
self.assertEqual(len(categories), 1)
self.assertEqual(len(categories['test']['pages']), 2)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_scraper.py:90*

### test_categorize_by_chapters

**Category**: workflow  
**Description**: Workflow: Test categorization using chapter information  
**Expected**: self.assertGreater(len(categories), 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()

'Test categorization using chapter information'
config = {'name': 'test', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Content here', 'chapter': 'Chapter 1: Introduction'}, {'page_number': 2, 'text': 'More content', 'chapter': 'Chapter 1: Introduction'}, {'page_number': 3, 'text': 'New chapter', 'chapter': 'Chapter 2: Advanced Topics'}]}
categories = converter.categorize_content()
self.assertIsInstance(categories, dict)
self.assertGreater(len(categories), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_scraper.py:123*

### test_categorize_handles_no_chapters

**Category**: workflow  
**Description**: Workflow: Test categorization when no chapters are detected  
**Expected**: self.assertIsInstance(categories, dict)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()

'Test categorization when no chapters are detected'
config = {'name': 'test', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Some content', 'chapter': None}]}
categories = converter.categorize_content()
self.assertIsInstance(categories, dict)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_scraper.py:143*

### test_build_skill_creates_structure

**Category**: workflow  
**Description**: Workflow: Test that build_skill creates required directory structure  
**Expected**: self.assertTrue((skill_dir / 'assets').exists())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()

'Test that build_skill creates required directory structure'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Test content', 'code_blocks': [], 'images': []}], 'total_pages': 1}
converter.categories = {'getting_started': [converter.extracted_data['pages'][0]]}
converter.build_skill()
skill_dir = Path(self.temp_dir) / 'test_skill'
self.assertTrue(skill_dir.exists())
self.assertTrue((skill_dir / 'references').exists())
self.assertTrue((skill_dir / 'scripts').exists())
self.assertTrue((skill_dir / 'assets').exists())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_scraper.py:173*

### test_build_skill_creates_skill_md

**Category**: workflow  
**Description**: Workflow: Test that SKILL.md is created  
**Expected**: self.assertIn('Test description', content)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()

'Test that SKILL.md is created'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf', 'description': 'Test description'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Test', 'code_blocks': [], 'images': []}], 'total_pages': 1}
converter.categories = {'test': [converter.extracted_data['pages'][0]]}
converter.build_skill()
skill_md = Path(self.temp_dir) / 'test_skill' / 'SKILL.md'
self.assertTrue(skill_md.exists())
content = skill_md.read_text()
self.assertIn('test_skill', content)
self.assertIn('Test description', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_scraper.py:199*

### test_build_skill_creates_reference_files

**Category**: workflow  
**Description**: Workflow: Test that reference files are created for categories  
**Expected**: self.assertTrue((refs_dir / 'index.md').exists())  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()

'Test that reference files are created for categories'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Getting started', 'code_blocks': [], 'images': []}, {'page_number': 2, 'text': 'API reference', 'code_blocks': [], 'images': []}], 'total_pages': 2}
converter.build_skill()
refs_dir = Path(self.temp_dir) / 'test_skill' / 'references'
self.assertTrue((refs_dir / 'test.md').exists())
self.assertTrue((refs_dir / 'index.md').exists())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_scraper.py:223*

### test_code_blocks_included_in_references

**Category**: workflow  
**Description**: Workflow: Test that code blocks are included in reference files  
**Expected**: self.assertIn("print('world')", content)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()

'Test that code blocks are included in reference files'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Example code', 'code_blocks': [{'code': "def hello():\n    print('world')", 'language': 'python', 'quality': 8.0}], 'images': []}], 'total_pages': 1}
converter.build_skill()
ref_file = Path(self.temp_dir) / 'test_skill' / 'references' / 'test.md'
content = ref_file.read_text()
self.assertIn('```python', content)
self.assertIn('def hello()', content)
self.assertIn("print('world')", content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_scraper.py:262*

### test_high_quality_code_preferred

**Category**: workflow  
**Description**: Workflow: Test that high-quality code blocks are prioritized  
**Expected**: self.assertIn('def process()', content)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()

'Test that high-quality code blocks are prioritized'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Code examples', 'code_blocks': [{'code': 'x = 1', 'language': 'python', 'quality': 2.0}, {'code': 'def process():\n    return result', 'language': 'python', 'quality': 9.0}], 'images': []}], 'total_pages': 1}
converter.build_skill()
ref_file = Path(self.temp_dir) / 'test_skill' / 'references' / 'test.md'
content = ref_file.read_text()
self.assertIn('def process()', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_scraper.py:300*

### test_images_saved_to_assets

**Category**: workflow  
**Description**: Workflow: Test that images are saved to assets directory  
**Expected**: self.assertGreater(len(image_files), 0)  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()

'Test that images are saved to assets directory'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
mock_image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'See diagram', 'code_blocks': [], 'images': [{'page': 1, 'index': 0, 'width': 100, 'height': 100, 'data': mock_image_bytes}]}], 'total_pages': 1}
converter.categories = {'diagrams': [converter.extracted_data['pages'][0]]}
converter.build_skill()
assets_dir = Path(self.temp_dir) / 'test_skill' / 'assets'
image_files = list(assets_dir.glob('*.png'))
self.assertGreater(len(image_files), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_scraper.py:352*

### test_image_references_in_markdown

**Category**: workflow  
**Description**: Workflow: Test that images are referenced in markdown files  
**Expected**: self.assertIn('../assets/', content)  
**Confidence**: 0.90  
**Tags**: mock, unittest, workflow, integration  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from skill_seekers.cli.pdf_scraper import PDFToSkillConverter
self.PDFToSkillConverter = PDFToSkillConverter
self.temp_dir = tempfile.mkdtemp()

'Test that images are referenced in markdown files'
config = {'name': 'test_skill', 'pdf_path': 'test.pdf'}
converter = self.PDFToSkillConverter(config)
converter.skill_dir = str(Path(self.temp_dir) / 'test_skill')
mock_image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
converter.extracted_data = {'pages': [{'page_number': 1, 'text': 'Architecture diagram', 'code_blocks': [], 'images': [{'page': 1, 'index': 0, 'width': 200, 'height': 150, 'data': mock_image_bytes}]}], 'total_pages': 1}
converter.build_skill()
ref_file = Path(self.temp_dir) / 'test_skill' / 'references' / 'test.md'
content = ref_file.read_text()
self.assertIn('![', content)
self.assertIn('../assets/', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_scraper.py:391*

### test_summarize_reference_basic

**Category**: workflow  
**Description**: Workflow: Test basic summarization preserves structure  
**Expected**: assert len(summarized) < len(content)  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test basic summarization preserves structure'
enhancer = LocalSkillEnhancer(tmp_path)
sections = []
for i in range(20):
    sections.append(f'\n## Section {i}\n\nThis is section {i} with detailed explanation that would benefit from summarization.\nWe add multiple paragraphs to make the content more realistic and substantial.\nThis content explains various aspects of the framework in detail.\n\nAnother paragraph with more information about this specific topic.\nTechnical details and explanations continue here with examples and use cases.\n\n```python\n# Example code for section {i}\ndef function_{i}():\n    print("Section {i}")\n    return {i}\n```\n\nFinal paragraph wrapping up this section with concluding remarks.\n')
content = '# Introduction\n\nThis is the framework introduction.\n' + '\n'.join(sections)
summarized = enhancer.summarize_reference(content, target_ratio=0.3)
assert '# Introduction' in summarized
assert '```python' in summarized
assert '[Content intelligently summarized' in summarized
assert len(summarized) < len(content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_smart_summarization.py:16*

### test_summarize_large_content

**Category**: workflow  
**Description**: Workflow: Test summarization with very large content  
**Expected**: assert 0.2 <= ratio <= 0.5, f'Ratio {ratio:.2f} not in expected range'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

'Test summarization with very large content'
enhancer = LocalSkillEnhancer(tmp_path)
sections = []
for i in range(50):
    sections.append(f'\n## Section {i}\n\nThis is section {i} with lots of content that needs to be summarized.\nWe add multiple paragraphs to make it realistic.\n\n```python\n# Code example {i}\ndef function_{i}():\n    return {i}\n```\n\nMore explanatory text follows here.\nAnother paragraph of content.\n')
content = '\n'.join(sections)
original_size = len(content)
summarized = enhancer.summarize_reference(content, target_ratio=0.3)
summarized_size = len(summarized)
assert summarized_size < original_size
ratio = summarized_size / original_size
assert 0.2 <= ratio <= 0.5, f'Ratio {ratio:.2f} not in expected range'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_smart_summarization.py:94*

### test_python_docstring_extraction

**Category**: workflow  
**Description**: Workflow: Test docstring extraction for functions and classes.  
**Expected**: self.assertIn('Returns:', add_method['docstring'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

'Test docstring extraction for functions and classes.'
code = '\nclass Calculator:\n    """A simple calculator class.\n\n    Supports basic arithmetic operations.\n    """\n\n    def add(self, a, b):\n        """Add two numbers.\n\n        Args:\n            a: First number\n            b: Second number\n\n        Returns:\n            Sum of a and b\n        """\n        return a + b\n'
result = self.analyzer.analyze_file('test.py', code, 'Python')
calc_class = result['classes'][0]
self.assertIn('A simple calculator class', calc_class['docstring'])
self.assertIn('Supports basic arithmetic operations', calc_class['docstring'])
add_method = calc_class['methods'][0]
self.assertIn('Add two numbers', add_method['docstring'])
self.assertIn('Args:', add_method['docstring'])
self.assertIn('Returns:', add_method['docstring'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_code_analyzer.py:134*

### test_javascript_class_methods

**Category**: workflow  
**Description**: Workflow: Test ES6 class method extraction.

Note: Regex-based parser has limitations in extracting all methods.
This test verifies basic method extraction works.  
**Expected**: self.assertGreater(len(method_names), 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

'Test ES6 class method extraction.\n\n        Note: Regex-based parser has limitations in extracting all methods.\n        This test verifies basic method extraction works.\n        '
code = "\nclass User {\n    constructor(name, email) {\n        this.name = name;\n        this.email = email;\n    }\n\n    getProfile() {\n        return { name: this.name, email: this.email };\n    }\n\n    async fetchData() {\n        return await fetch('/api/user');\n    }\n}\n"
result = self.analyzer.analyze_file('test.js', code, 'JavaScript')
self.assertIn('classes', result)
user_class = result['classes'][0]
self.assertEqual(user_class['name'], 'User')
self.assertGreaterEqual(len(user_class['methods']), 1)
method_names = [m['name'] for m in user_class['methods']]
self.assertGreater(len(method_names), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_code_analyzer.py:253*

### test_typescript_type_annotations

**Category**: workflow  
**Description**: Workflow: Test TypeScript type annotation extraction.

Note: Current regex-based parser extracts parameter type hints
but NOT return types. Return type extraction requires a proper
TypeScript parser (ts-morph or typescript library).  
**Expected**: self.assertIsNone(create_func['return_type'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

'Test TypeScript type annotation extraction.\n\n        Note: Current regex-based parser extracts parameter type hints\n        but NOT return types. Return type extraction requires a proper\n        TypeScript parser (ts-morph or typescript library).\n        '
code = '\nfunction calculate(a: number, b: number): number {\n    return a + b;\n}\n\ninterface User {\n    name: string;\n    age: number;\n}\n\nfunction createUser(name: string, age: number = 18): User {\n    return { name, age };\n}\n'
result = self.analyzer.analyze_file('test.ts', code, 'TypeScript')
self.assertIn('functions', result)
calc_func = result['functions'][0]
self.assertEqual(calc_func['name'], 'calculate')
self.assertEqual(calc_func['parameters'][0]['type_hint'], 'number')
self.assertIsNone(calc_func['return_type'])
create_func = result['functions'][1]
self.assertEqual(create_func['name'], 'createUser')
self.assertEqual(create_func['parameters'][1]['default'], '18')
self.assertIsNone(create_func['return_type'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_code_analyzer.py:288*

### test_cpp_class_extraction

**Category**: workflow  
**Description**: Workflow: Test C++ class extraction with inheritance.  
**Expected**: self.assertIn('Animal', dog_class['base_classes'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

'Test C++ class extraction with inheritance.'
code = '\nclass Animal {\npublic:\n    virtual void makeSound() = 0;\n};\n\nclass Dog : public Animal {\npublic:\n    void makeSound() override;\n    void bark();\nprivate:\n    std::string breed;\n};\n'
result = self.analyzer.analyze_file('test.h', code, 'C++')
self.assertIn('classes', result)
self.assertEqual(len(result['classes']), 2)
animal_class = result['classes'][0]
self.assertEqual(animal_class['name'], 'Animal')
dog_class = result['classes'][1]
self.assertEqual(dog_class['name'], 'Dog')
self.assertIn('Animal', dog_class['base_classes'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_code_analyzer.py:376*

### test_deep_depth_extracts_signatures

**Category**: workflow  
**Description**: Workflow: Test that deep depth extracts full signatures.  
**Expected**: self.assertEqual(func['return_type'], 'int')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test that deep depth extracts full signatures.'
analyzer = CodeAnalyzer(depth='deep')
code = '\ndef calculate(x: int, y: int) -> int:\n    """Calculate sum."""\n    return x + y\n'
result = analyzer.analyze_file('test.py', code, 'Python')
self.assertIn('functions', result)
self.assertEqual(len(result['functions']), 1)
func = result['functions'][0]
self.assertEqual(func['name'], 'calculate')
self.assertEqual(func['return_type'], 'int')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_code_analyzer.py:459*

### test_javascript_inline_comments

**Category**: workflow  
**Description**: Workflow: Test JavaScript // comment extraction.  
**Expected**: self.assertGreaterEqual(len(inline_comments), 3)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

'Test JavaScript // comment extraction.'
code = '\n// Top-level comment\nfunction test() {\n    // Inside function\n    const x = 5; // Inline (not extracted)\n    return x;\n}\n\n// Another comment\nconst y = 10;\n'
result = self.analyzer.analyze_file('test.js', code, 'JavaScript')
self.assertIn('comments', result)
comments = result['comments']
self.assertGreaterEqual(len(comments), 3)
inline_comments = [c for c in comments if c['type'] == 'inline']
self.assertGreaterEqual(len(inline_comments), 3)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_code_analyzer.py:627*

### test_javascript_block_comments

**Category**: workflow  
**Description**: Workflow: Test JavaScript /* */ block comment extraction.  
**Expected**: self.assertIn('multi-line', first_block['text'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

'Test JavaScript /* */ block comment extraction.'
code = '\n/* This is a\n   multi-line\n   block comment */\nfunction test() {\n    /* Another block comment */\n    return 42;\n}\n'
result = self.analyzer.analyze_file('test.js', code, 'JavaScript')
comments = result['comments']
block_comments = [c for c in comments if c['type'] == 'block']
self.assertGreaterEqual(len(block_comments), 2)
first_block = next((c for c in comments if 'multi-line' in c['text']))
self.assertIn('multi-line', first_block['text'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_code_analyzer.py:652*

### test_javascript_mixed_comments

**Category**: workflow  
**Description**: Workflow: Test JavaScript mixed inline and block comments.  
**Expected**: self.assertGreaterEqual(len(block_comments), 2)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

'Test JavaScript mixed inline and block comments.'
code = '\n// Inline comment\n/* Block comment */\nfunction test() {\n    // Another inline\n    /* Another block */\n    return true;\n}\n'
result = self.analyzer.analyze_file('test.js', code, 'JavaScript')
comments = result['comments']
inline_comments = [c for c in comments if c['type'] == 'inline']
block_comments = [c for c in comments if c['type'] == 'block']
self.assertGreaterEqual(len(inline_comments), 2)
self.assertGreaterEqual(len(block_comments), 2)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_code_analyzer.py:675*

### test_cpp_comment_extraction

**Category**: workflow  
**Description**: Workflow: Test C++ comment extraction (uses same logic as JavaScript).  
**Expected**: self.assertGreaterEqual(len(block_comments), 1)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test analyzer with deep analysis'
self.analyzer = CodeAnalyzer(depth='deep')

'Test C++ comment extraction (uses same logic as JavaScript).'
code = '\n// Header comment\nclass Node {\npublic:\n    // Method comment\n    void update();\n\n    /* Block comment for data member */\n    int value;\n};\n'
result = self.analyzer.analyze_file('test.h', code, 'C++')
self.assertIn('comments', result)
comments = result['comments']
self.assertGreaterEqual(len(comments), 3)
inline_comments = [c for c in comments if c['type'] == 'inline']
block_comments = [c for c in comments if c['type'] == 'block']
self.assertGreaterEqual(len(inline_comments), 2)
self.assertGreaterEqual(len(block_comments), 1)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_code_analyzer.py:697*

### test_python_docstring_extraction

**Category**: workflow  
**Description**: Workflow: Test docstring extraction for functions and classes.  
**Expected**: self.assertIn('Returns:', add_method['docstring'])  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test docstring extraction for functions and classes.'
code = '\nclass Calculator:\n    """A simple calculator class.\n\n    Supports basic arithmetic operations.\n    """\n\n    def add(self, a, b):\n        """Add two numbers.\n\n        Args:\n            a: First number\n            b: Second number\n\n        Returns:\n            Sum of a and b\n        """\n        return a + b\n'
result = self.analyzer.analyze_file('test.py', code, 'Python')
calc_class = result['classes'][0]
self.assertIn('A simple calculator class', calc_class['docstring'])
self.assertIn('Supports basic arithmetic operations', calc_class['docstring'])
add_method = calc_class['methods'][0]
self.assertIn('Add two numbers', add_method['docstring'])
self.assertIn('Args:', add_method['docstring'])
self.assertIn('Returns:', add_method['docstring'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_code_analyzer.py:134*

### test_extract_instantiation

**Category**: workflow  
**Description**: Workflow: Test extraction of object instantiation patterns  
**Expected**: self.assertGreaterEqual(inst.confidence, 0.7)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.analyzer = PythonTestAnalyzer()

'Test extraction of object instantiation patterns'
code = '\nimport unittest\n\nclass TestDatabase(unittest.TestCase):\n    def test_connection(self):\n        """Test database connection"""\n        db = Database(host="localhost", port=5432, user="admin")\n        self.assertTrue(db.connect())\n'
examples = self.analyzer.extract('test_db.py', code)
instantiations = [ex for ex in examples if ex.category == 'instantiation']
self.assertGreater(len(instantiations), 0)
inst = instantiations[0]
self.assertIn('Database', inst.code)
self.assertIn('host', inst.code)
self.assertGreaterEqual(inst.confidence, 0.7)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_test_example_extractor.py:40*

### test_extract_method_call_with_assertion

**Category**: workflow  
**Description**: Workflow: Test extraction of method calls followed by assertions  
**Expected**: self.assertGreater(len(examples), 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.analyzer = PythonTestAnalyzer()

'Test extraction of method calls followed by assertions'
code = '\nimport unittest\n\nclass TestAPI(unittest.TestCase):\n    def test_api_response(self):\n        """Test API returns correct status"""\n        response = self.client.get("/users/1")\n        self.assertEqual(response.status_code, 200)\n'
examples = self.analyzer.extract('test_api.py', code)
self.assertGreater(len(examples), 0)
method_calls = [ex for ex in examples if ex.category == 'method_call']
if method_calls:
    call = method_calls[0]
    self.assertIn('get', call.code)
    self.assertGreaterEqual(call.confidence, 0.7)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_test_example_extractor.py:62*

### test_extract_config_dict

**Category**: workflow  
**Description**: Workflow: Test extraction of configuration dictionaries  
**Expected**: self.assertGreaterEqual(config.confidence, 0.7)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.analyzer = PythonTestAnalyzer()

'Test extraction of configuration dictionaries'
code = '\ndef test_app_config():\n    """Test application configuration"""\n    config = {\n        "debug": True,\n        "database_url": "postgresql://localhost/test",\n        "cache_enabled": False,\n        "max_connections": 100\n    }\n    app = Application(config)\n    assert app.is_configured()\n'
examples = self.analyzer.extract('test_config.py', code)
configs = [ex for ex in examples if ex.category == 'config']
self.assertGreater(len(configs), 0)
config = configs[0]
self.assertIn('debug', config.code)
self.assertIn('database_url', config.code)
self.assertGreaterEqual(config.confidence, 0.7)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_test_example_extractor.py:85*

### test_confidence_scoring

**Category**: workflow  
**Description**: Workflow: Test confidence scores are calculated correctly  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.analyzer = PythonTestAnalyzer()

'Test confidence scores are calculated correctly'
simple_code = '\ndef test_simple():\n    obj = MyClass()\n    assert obj is not None\n'
simple_examples = self.analyzer.extract('test_simple.py', simple_code)
complex_code = '\ndef test_complex():\n    """Test complex initialization"""\n    obj = MyClass(\n        param1="value1",\n        param2="value2",\n        param3={"nested": "dict"},\n        param4=[1, 2, 3]\n    )\n    result = obj.process()\n    assert result.status == "success"\n'
complex_examples = self.analyzer.extract('test_complex.py', complex_code)
if simple_examples and complex_examples:
    simple_complexity = max((ex.complexity_score for ex in simple_examples))
    complex_complexity = max((ex.complexity_score for ex in complex_examples))
    self.assertGreater(complex_complexity, simple_complexity)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_test_example_extractor.py:209*

### test_extract_gdscript_gut_tests

**Category**: workflow  
**Description**: Workflow: Test GDScript GUT/gdUnit4 test extraction  
**Expected**: self.assertTrue(has_preload or len(instantiations) > 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.analyzer = GenericTestAnalyzer()

'Test GDScript GUT/gdUnit4 test extraction'
code = '\nextends GutTest\n\n# GUT test framework example\nfunc test_player_instantiation():\n    """Test player node creation"""\n    var player = preload("res://Player.gd").new()\n    player.name = "TestPlayer"\n    player.health = 100\n\n    assert_eq(player.name, "TestPlayer")\n    assert_eq(player.health, 100)\n    assert_true(player.is_alive())\n\nfunc test_signal_connections():\n    """Test signal connections"""\n    var enemy = Enemy.new()\n    enemy.connect("died", self, "_on_enemy_died")\n\n    enemy.take_damage(100)\n\n    assert_signal_emitted(enemy, "died")\n\n@test\nfunc test_gdunit4_annotation():\n    """Test with gdUnit4 @test annotation"""\n    var inventory = load("res://Inventory.gd").new()\n    inventory.add_item("sword", 1)\n\n    assert_contains(inventory.items, "sword")\n    assert_eq(inventory.get_item_count("sword"), 1)\n\nfunc test_game_state():\n    """Test game state management"""\n    const MAX_HEALTH = 100\n    var player = Player.new()\n    var game_state = GameState.new()\n\n    game_state.initialize(player)\n\n    assert_not_null(game_state.player)\n    assert_eq(game_state.player.health, MAX_HEALTH)\n'
examples = self.analyzer.extract('test_game.gd', code, 'GDScript')
self.assertGreater(len(examples), 0)
self.assertEqual(examples[0].language, 'GDScript')
instantiations = [e for e in examples if e.category == 'instantiation']
self.assertGreater(len(instantiations), 0)
has_preload = any(('preload' in e.code or 'load' in e.code for e in instantiations))
self.assertTrue(has_preload or len(instantiations) > 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_test_example_extractor.py:386*

### test_language_filtering

**Category**: workflow  
**Description**: Workflow: Test filtering by programming language  
**Expected**: js_file.write_text('\ntest("javascript test", () => {\n    const obj = new MyClass();\n    expect(obj).toBeDefined();\n});\n')  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.temp_dir = Path(tempfile.mkdtemp())
self.extractor = TestExampleExtractor(min_confidence=0.5, max_per_file=10)

'Test filtering by programming language'
py_file = self.temp_dir / 'test_py.py'
py_file.write_text('\ndef test_python():\n    obj = MyClass(param="value")\n    assert obj is not None\n')
js_file = self.temp_dir / 'test_js.js'
js_file.write_text('\ntest("javascript test", () => {\n    const obj = new MyClass();\n    expect(obj).toBeDefined();\n});\n')
python_extractor = TestExampleExtractor(languages=['python'])
report = python_extractor.extract_from_directory(self.temp_dir)
for example in report.examples:
    self.assertEqual(example.language, 'Python')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_test_example_extractor.py:622*

### test_max_examples_limit

**Category**: workflow  
**Description**: Workflow: Test max examples per file limit  
**Expected**: self.assertLessEqual(len(examples), 5)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.temp_dir = Path(tempfile.mkdtemp())
self.extractor = TestExampleExtractor(min_confidence=0.5, max_per_file=10)

'Test max examples per file limit'
test_file = self.temp_dir / 'test_many.py'
test_code = 'import unittest\n\nclass TestSuite(unittest.TestCase):\n'
for i in range(20):
    test_code += f'\n    def test_example_{i}(self):\n        """Test {i}"""\n        obj = MyClass(id={i}, name="test_{i}")\n        self.assertIsNotNone(obj)\n'
test_file.write_text(test_code)
limited_extractor = TestExampleExtractor(max_per_file=5)
examples = limited_extractor.extract_from_file(test_file)
self.assertLessEqual(len(examples), 5)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_test_example_extractor.py:649*

### test_end_to_end_workflow

**Category**: workflow  
**Description**: Workflow: Test complete extraction workflow  
**Expected**: self.assertGreater(len(report.examples_by_category), 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
self.temp_dir = Path(tempfile.mkdtemp())
self.extractor = TestExampleExtractor(min_confidence=0.5, max_per_file=10)

'Test complete extraction workflow'
(self.temp_dir / 'tests').mkdir()
(self.temp_dir / 'tests' / 'test_unit.py').write_text('\nimport unittest\n\nclass TestAPI(unittest.TestCase):\n    def test_connection(self):\n        """Test API connection"""\n        api = APIClient(url="https://api.example.com", timeout=30)\n        self.assertTrue(api.connect())\n')
(self.temp_dir / 'tests' / 'test_integration.py').write_text('\ndef test_workflow():\n    """Test complete workflow"""\n    user = User(name="John", email="john@example.com")\n    user.save()\n    user.verify()\n    assert user.is_active\n')
report = self.extractor.extract_from_directory(self.temp_dir / 'tests')
self.assertGreater(report.total_examples, 0)
self.assertIsInstance(report.examples_by_category, dict)
self.assertIsInstance(report.examples_by_language, dict)
self.assertGreaterEqual(report.avg_complexity, 0.0)
self.assertLessEqual(report.avg_complexity, 1.0)
self.assertGreater(len(report.examples_by_category), 0)
for example in report.examples:
    self.assertIsNotNone(example.example_id)
    self.assertIsNotNone(example.test_name)
    self.assertIsNotNone(example.category)
    self.assertIsNotNone(example.code)
    self.assertIsNotNone(example.language)
    self.assertGreaterEqual(example.confidence, 0.0)
    self.assertLessEqual(example.confidence, 1.0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_test_example_extractor.py:670*

### test_extract_instantiation

**Category**: workflow  
**Description**: Workflow: Test extraction of object instantiation patterns  
**Expected**: self.assertGreaterEqual(inst.confidence, 0.7)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test extraction of object instantiation patterns'
code = '\nimport unittest\n\nclass TestDatabase(unittest.TestCase):\n    def test_connection(self):\n        """Test database connection"""\n        db = Database(host="localhost", port=5432, user="admin")\n        self.assertTrue(db.connect())\n'
examples = self.analyzer.extract('test_db.py', code)
instantiations = [ex for ex in examples if ex.category == 'instantiation']
self.assertGreater(len(instantiations), 0)
inst = instantiations[0]
self.assertIn('Database', inst.code)
self.assertIn('host', inst.code)
self.assertGreaterEqual(inst.confidence, 0.7)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_test_example_extractor.py:40*

### test_extract_method_call_with_assertion

**Category**: workflow  
**Description**: Workflow: Test extraction of method calls followed by assertions  
**Expected**: self.assertGreater(len(examples), 0)  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test extraction of method calls followed by assertions'
code = '\nimport unittest\n\nclass TestAPI(unittest.TestCase):\n    def test_api_response(self):\n        """Test API returns correct status"""\n        response = self.client.get("/users/1")\n        self.assertEqual(response.status_code, 200)\n'
examples = self.analyzer.extract('test_api.py', code)
self.assertGreater(len(examples), 0)
method_calls = [ex for ex in examples if ex.category == 'method_call']
if method_calls:
    call = method_calls[0]
    self.assertIn('get', call.code)
    self.assertGreaterEqual(call.confidence, 0.7)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_test_example_extractor.py:62*

### test_issue_277_error_message_urls

**Category**: workflow  
**Description**: Workflow: Test the exact URLs that appeared in error messages from the issue report.
These were the actual 404-causing URLs that need to be fixed.  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
# Setup
'Set up test converter with MikroORM-like configuration'
self.config = {'name': 'MikroORM', 'description': 'ORM', 'base_url': 'https://mikro-orm.io/docs/', 'selectors': {'main_content': 'article'}, 'url_patterns': {'include': ['/docs'], 'exclude': []}}
self.converter = DocToSkillConverter(self.config, dry_run=True)

'\n        Test the exact URLs that appeared in error messages from the issue report.\n        These were the actual 404-causing URLs that need to be fixed.\n        '
error_urls_with_anchors = ['https://mikro-orm.io/docs/quick-start#synchronous-initialization/index.html.md', 'https://mikro-orm.io/docs/defining-entities#formulas/index.html.md', 'https://mikro-orm.io/docs/defining-entities#postgresql-native-enums/index.html.md']
input_urls = ['https://mikro-orm.io/docs/quick-start#synchronous-initialization', 'https://mikro-orm.io/docs/propagation', 'https://mikro-orm.io/docs/defining-entities#formulas', 'https://mikro-orm.io/docs/defining-entities#postgresql-native-enums']
result = self.converter._convert_to_md_urls(input_urls)
for error_url in error_urls_with_anchors:
    self.assertNotIn(error_url, result, f'Should not generate the 404-causing URL: {error_url}')
correct_urls = ['https://mikro-orm.io/docs/quick-start/index.html.md', 'https://mikro-orm.io/docs/propagation/index.html.md', 'https://mikro-orm.io/docs/defining-entities/index.html.md']
for correct_url in correct_urls:
    self.assertIn(correct_url, result, f'Should generate the correct URL: {correct_url}')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_277_real_world.py:213*

### test_issue_277_error_message_urls

**Category**: workflow  
**Description**: Workflow: Test the exact URLs that appeared in error messages from the issue report.
These were the actual 404-causing URLs that need to be fixed.  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'\n        Test the exact URLs that appeared in error messages from the issue report.\n        These were the actual 404-causing URLs that need to be fixed.\n        '
error_urls_with_anchors = ['https://mikro-orm.io/docs/quick-start#synchronous-initialization/index.html.md', 'https://mikro-orm.io/docs/defining-entities#formulas/index.html.md', 'https://mikro-orm.io/docs/defining-entities#postgresql-native-enums/index.html.md']
input_urls = ['https://mikro-orm.io/docs/quick-start#synchronous-initialization', 'https://mikro-orm.io/docs/propagation', 'https://mikro-orm.io/docs/defining-entities#formulas', 'https://mikro-orm.io/docs/defining-entities#postgresql-native-enums']
result = self.converter._convert_to_md_urls(input_urls)
for error_url in error_urls_with_anchors:
    self.assertNotIn(error_url, result, f'Should not generate the 404-causing URL: {error_url}')
correct_urls = ['https://mikro-orm.io/docs/quick-start/index.html.md', 'https://mikro-orm.io/docs/propagation/index.html.md', 'https://mikro-orm.io/docs/defining-entities/index.html.md']
for correct_url in correct_urls:
    self.assertIn(correct_url, result, f'Should generate the correct URL: {correct_url}')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_277_real_world.py:213*

### test_simple_import

**Category**: method_call  
**Description**: Test simple import statement.  
**Expected**: self.assertEqual(deps[0].imported_module, 'os')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
if not ANALYZER_AVAILABLE:
    self.skipTest('dependency_analyzer not available')
self.analyzer = DependencyAnalyzer()

self.assertEqual(len(deps), 2)
self.assertEqual(deps[0].imported_module, 'os')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_dependency_analyzer.py:39*

### test_simple_import

**Category**: method_call  
**Description**: Test simple import statement.  
**Expected**: self.assertEqual(deps[0].import_type, 'import')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
if not ANALYZER_AVAILABLE:
    self.skipTest('dependency_analyzer not available')
self.analyzer = DependencyAnalyzer()

self.assertEqual(deps[0].imported_module, 'os')
self.assertEqual(deps[0].import_type, 'import')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_dependency_analyzer.py:40*

### test_simple_import

**Category**: method_call  
**Description**: Test simple import statement.  
**Expected**: self.assertFalse(deps[0].is_relative)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
if not ANALYZER_AVAILABLE:
    self.skipTest('dependency_analyzer not available')
self.analyzer = DependencyAnalyzer()

self.assertEqual(deps[0].import_type, 'import')
self.assertFalse(deps[0].is_relative)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_dependency_analyzer.py:41*

### test_from_import

**Category**: method_call  
**Description**: Test from...import statement.  
**Expected**: self.assertEqual(deps[0].imported_module, 'pathlib')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
if not ANALYZER_AVAILABLE:
    self.skipTest('dependency_analyzer not available')
self.analyzer = DependencyAnalyzer()

self.assertEqual(len(deps), 2)
self.assertEqual(deps[0].imported_module, 'pathlib')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_dependency_analyzer.py:49*

### test_from_import

**Category**: method_call  
**Description**: Test from...import statement.  
**Expected**: self.assertEqual(deps[0].import_type, 'from')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
if not ANALYZER_AVAILABLE:
    self.skipTest('dependency_analyzer not available')
self.analyzer = DependencyAnalyzer()

self.assertEqual(deps[0].imported_module, 'pathlib')
self.assertEqual(deps[0].import_type, 'from')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_dependency_analyzer.py:50*

### test_relative_import

**Category**: method_call  
**Description**: Test relative import.  
**Expected**: self.assertTrue(deps[0].is_relative)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
if not ANALYZER_AVAILABLE:
    self.skipTest('dependency_analyzer not available')
self.analyzer = DependencyAnalyzer()

self.assertEqual(len(deps), 2)
self.assertTrue(deps[0].is_relative)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_dependency_analyzer.py:58*

### test_relative_import

**Category**: method_call  
**Description**: Test relative import.  
**Expected**: self.assertEqual(deps[0].imported_module, '.')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
if not ANALYZER_AVAILABLE:
    self.skipTest('dependency_analyzer not available')
self.analyzer = DependencyAnalyzer()

self.assertTrue(deps[0].is_relative)
self.assertEqual(deps[0].imported_module, '.')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_dependency_analyzer.py:59*

### test_relative_import

**Category**: method_call  
**Description**: Test relative import.  
**Expected**: self.assertTrue(deps[1].is_relative)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
if not ANALYZER_AVAILABLE:
    self.skipTest('dependency_analyzer not available')
self.analyzer = DependencyAnalyzer()

self.assertEqual(deps[0].imported_module, '.')
self.assertTrue(deps[1].is_relative)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_dependency_analyzer.py:60*

### test_init_with_repo_name

**Category**: method_call  
**Description**: Test initialization with repository name  
**Expected**: self.assertEqual(scraper.name, 'react')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
if not PYGITHUB_AVAILABLE:
    self.skipTest('PyGithub not installed')
from skill_seekers.cli.github_scraper import GitHubScraper
self.GitHubScraper = GitHubScraper
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir)

self.assertEqual(scraper.repo_name, 'facebook/react')
self.assertEqual(scraper.name, 'react')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_scraper.py:59*

### test_init_with_repo_name

**Category**: method_call  
**Description**: Test initialization with repository name  
**Expected**: self.assertIsNotNone(scraper.github)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
if not PYGITHUB_AVAILABLE:
    self.skipTest('PyGithub not installed')
from skill_seekers.cli.github_scraper import GitHubScraper
self.GitHubScraper = GitHubScraper
self.temp_dir = tempfile.mkdtemp()
self.output_dir = Path(self.temp_dir)

self.assertEqual(scraper.name, 'react')
self.assertIsNotNone(scraper.github)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_scraper.py:60*

### test_init_with_repo_name

**Category**: method_call  
**Description**: Test initialization with repository name  
**Expected**: self.assertEqual(scraper.name, 'react')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(scraper.repo_name, 'facebook/react')
self.assertEqual(scraper.name, 'react')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_scraper.py:59*

### test_init_with_repo_name

**Category**: method_call  
**Description**: Test initialization with repository name  
**Expected**: self.assertIsNotNone(scraper.github)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(scraper.name, 'react')
self.assertIsNotNone(scraper.github)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_scraper.py:60*

### test_flask_framework_detection_from_imports

**Category**: method_call  
**Description**: Test that Flask is detected from import statements (Issue #239).  
**Expected**: self.assertIn('Flask', arch_data['frameworks_detected'], 'Flask should be detected from imports')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create temporary directory for testing.'
self.temp_dir = tempfile.mkdtemp()
self.test_project = Path(self.temp_dir) / 'test_project'
self.test_project.mkdir()
self.output_dir = Path(self.temp_dir) / 'output'

self.assertIn('frameworks_detected', arch_data)
self.assertIn('Flask', arch_data['frameworks_detected'], 'Flask should be detected from imports')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_framework_detection.py:82*

### test_files_with_imports_are_included

**Category**: method_call  
**Description**: Test that files with only imports are included in analysis (Issue #239).  
**Expected**: self.assertIn('imports', import_file, 'Imports should be extracted')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create temporary directory for testing.'
self.temp_dir = tempfile.mkdtemp()
self.test_project = Path(self.temp_dir) / 'test_project'
self.test_project.mkdir()
self.output_dir = Path(self.temp_dir) / 'output'

self.assertIsNotNone(import_file, 'Import-only file should be in analysis')
self.assertIn('imports', import_file, 'Imports should be extracted')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_framework_detection.py:129*

### test_files_with_imports_are_included

**Category**: method_call  
**Description**: Test that files with only imports are included in analysis (Issue #239).  
**Expected**: self.assertGreater(len(import_file['imports']), 0, 'Should have captured imports')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create temporary directory for testing.'
self.temp_dir = tempfile.mkdtemp()
self.test_project = Path(self.temp_dir) / 'test_project'
self.test_project.mkdir()
self.output_dir = Path(self.temp_dir) / 'output'

self.assertIn('imports', import_file, 'Imports should be extracted')
self.assertGreater(len(import_file['imports']), 0, 'Should have captured imports')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_framework_detection.py:132*

### test_files_with_imports_are_included

**Category**: method_call  
**Description**: Test that files with only imports are included in analysis (Issue #239).  
**Expected**: self.assertIn('django', import_file['imports'], 'Django import should be captured')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create temporary directory for testing.'
self.temp_dir = tempfile.mkdtemp()
self.test_project = Path(self.temp_dir) / 'test_project'
self.test_project.mkdir()
self.output_dir = Path(self.temp_dir) / 'output'

self.assertGreater(len(import_file['imports']), 0, 'Should have captured imports')
self.assertIn('django', import_file['imports'], 'Django import should be captured')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_framework_detection.py:133*

### test_auto_fetch_enabled

**Category**: method_call  
**Description**: Test that auto-fetch runs when enabled.  
**Expected**: assert result is not None  
**Confidence**: 0.85  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_fetch, tmp_path

mock_fetch.assert_called_once_with('react', destination='configs')
assert result is not None
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_fetcher.py:277*

### test_classify_files

**Category**: method_call  
**Description**: Test classify_files separates code and docs correctly.  
**Expected**: (tmp_path / 'node_modules' / 'lib.js').write_text('// should be excluded')  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: tmp_path

(tmp_path / 'node_modules').mkdir()
(tmp_path / 'node_modules' / 'lib.js').write_text('// should be excluded')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_fetcher.py:117*

### test_upload_with_nonexistent_file

**Category**: method_call  
**Description**: Test upload with nonexistent file  
**Expected**: self.assertIn('not found', message.lower())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Store original API key state'
self.original_api_key = os.environ.get('ANTHROPIC_API_KEY')

self.assertFalse(success)
self.assertIn('not found', message.lower())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_skill.py:60*

### test_upload_with_nonexistent_file

**Category**: method_call  
**Description**: Test upload with nonexistent file  
**Expected**: self.assertIn('not found', message.lower())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(success)
self.assertIn('not found', message.lower())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_skill.py:60*

### test_extract_headings_h2_to_h6

**Category**: method_call  
**Description**: Test extracting h2-h6 headings (not h1).  
**Expected**: self.assertEqual(result['headings'][0]['level'], 'h2')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test fixtures.'
from skill_seekers.cli.doc_scraper import DocToSkillConverter
self.config = {'name': 'test_md_parsing', 'base_url': 'https://example.com', 'selectors': {}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}}
self.converter = DocToSkillConverter(self.config)

self.assertEqual(len(result['headings']), 5)
self.assertEqual(result['headings'][0]['level'], 'h2')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_markdown_parsing.py:58*

### test_extract_headings_h2_to_h6

**Category**: method_call  
**Description**: Test extracting h2-h6 headings (not h1).  
**Expected**: self.assertEqual(result['headings'][0]['text'], 'Section One')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test fixtures.'
from skill_seekers.cli.doc_scraper import DocToSkillConverter
self.config = {'name': 'test_md_parsing', 'base_url': 'https://example.com', 'selectors': {}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}}
self.converter = DocToSkillConverter(self.config)

self.assertEqual(result['headings'][0]['level'], 'h2')
self.assertEqual(result['headings'][0]['text'], 'Section One')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_markdown_parsing.py:59*

### test_extract_code_blocks_with_language

**Category**: method_call  
**Description**: Test extracting code blocks with language tags.  
**Expected**: self.assertEqual(result['code_samples'][0]['language'], 'python')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test fixtures.'
from skill_seekers.cli.doc_scraper import DocToSkillConverter
self.config = {'name': 'test_md_parsing', 'base_url': 'https://example.com', 'selectors': {}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}}
self.converter = DocToSkillConverter(self.config)

self.assertEqual(len(result['code_samples']), 3)
self.assertEqual(result['code_samples'][0]['language'], 'python')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_markdown_parsing.py:82*

### test_extract_code_blocks_with_language

**Category**: method_call  
**Description**: Test extracting code blocks with language tags.  
**Expected**: self.assertEqual(result['code_samples'][1]['language'], 'javascript')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test fixtures.'
from skill_seekers.cli.doc_scraper import DocToSkillConverter
self.config = {'name': 'test_md_parsing', 'base_url': 'https://example.com', 'selectors': {}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}}
self.converter = DocToSkillConverter(self.config)

self.assertEqual(result['code_samples'][0]['language'], 'python')
self.assertEqual(result['code_samples'][1]['language'], 'javascript')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_markdown_parsing.py:83*

### test_extract_code_blocks_with_language

**Category**: method_call  
**Description**: Test extracting code blocks with language tags.  
**Expected**: self.assertEqual(result['code_samples'][2]['language'], 'unknown')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test fixtures.'
from skill_seekers.cli.doc_scraper import DocToSkillConverter
self.config = {'name': 'test_md_parsing', 'base_url': 'https://example.com', 'selectors': {}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}}
self.converter = DocToSkillConverter(self.config)

self.assertEqual(result['code_samples'][1]['language'], 'javascript')
self.assertEqual(result['code_samples'][2]['language'], 'unknown')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_markdown_parsing.py:84*

### test_extract_content_paragraphs

**Category**: method_call  
**Description**: Test extracting paragraph content.  
**Expected**: self.assertNotIn('Short.', result['content'])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test fixtures.'
from skill_seekers.cli.doc_scraper import DocToSkillConverter
self.config = {'name': 'test_md_parsing', 'base_url': 'https://example.com', 'selectors': {}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}}
self.converter = DocToSkillConverter(self.config)

self.assertIn('paragraph with enough content', result['content'])
self.assertNotIn('Short.', result['content'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_markdown_parsing.py:114*

### test_extract_markdown_style_links

**Category**: method_call  
**Description**: Test extracting [text](url) style links.  
**Expected**: self.assertIn('https://docs.example.com/api/index.md', urls)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('https://docs.example.com/start.md', urls)
self.assertIn('https://docs.example.com/api/index.md', urls)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_markdown_parsing.py:212*

### test_extract_markdown_style_links

**Category**: method_call  
**Description**: Test extracting [text](url) style links.  
**Expected**: self.assertIn('https://docs.example.com/advanced.md', urls)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('https://docs.example.com/api/index.md', urls)
self.assertIn('https://docs.example.com/advanced.md', urls)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_markdown_parsing.py:213*

### test_estimate_pages_with_minimal_config

**Category**: method_call  
**Description**: Test estimation with minimal configuration  
**Expected**: self.assertIn('discovered', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(result, dict)
self.assertIn('discovered', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_estimate_pages.py:25*

### test_estimate_pages_with_minimal_config

**Category**: method_call  
**Description**: Test estimation with minimal configuration  
**Expected**: self.assertIn('estimated_total', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('discovered', result)
self.assertIn('estimated_total', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_estimate_pages.py:26*

### test_estimate_pages_with_minimal_config

**Category**: method_call  
**Description**: Test estimation with minimal configuration  
**Expected**: self.assertIn('elapsed_seconds', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('estimated_total', result)
self.assertIn('elapsed_seconds', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_estimate_pages.py:27*

### test_estimate_pages_returns_discovered_count

**Category**: method_call  
**Description**: Test that result contains discovered page count  
**Expected**: self.assertIsInstance(result['discovered'], int)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertGreaterEqual(result['discovered'], 0)
self.assertIsInstance(result['discovered'], int)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_estimate_pages.py:37*

### test_estimate_pages_with_start_urls

**Category**: method_call  
**Description**: Test estimation with custom start_urls  
**Expected**: self.assertIn('discovered', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(result, dict)
self.assertIn('discovered', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_estimate_pages.py:60*

### test_estimate_with_real_config_file

**Category**: method_call  
**Description**: Test estimation using a real config file (if exists)  
**Expected**: self.assertIn('discovered', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(result, dict)
self.assertIn('discovered', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_estimate_pages.py:181*

### test_estimate_with_real_config_file

**Category**: method_call  
**Description**: Test estimation using a real config file (if exists)  
**Expected**: self.assertGreater(result['discovered'], 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('discovered', result)
self.assertGreater(result['discovered'], 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_estimate_pages.py:182*

### test_estimate_pages_with_minimal_config

**Category**: method_call  
**Description**: Test estimation with minimal configuration  
**Expected**: self.assertIn('discovered', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(result, dict)
self.assertIn('discovered', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_estimate_pages.py:25*

### test_estimate_pages_with_minimal_config

**Category**: method_call  
**Description**: Test estimation with minimal configuration  
**Expected**: self.assertIn('estimated_total', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('discovered', result)
self.assertIn('estimated_total', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_estimate_pages.py:26*

### test_estimate_pages_with_minimal_config

**Category**: method_call  
**Description**: Test estimation with minimal configuration  
**Expected**: self.assertIn('elapsed_seconds', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('estimated_total', result)
self.assertIn('elapsed_seconds', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_estimate_pages.py:27*

### test_extract_text_with_ocr_disabled

**Category**: method_call  
**Description**: Test that OCR can be disabled  
**Expected**: mock_page.get_text.assert_called_once_with('text')  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor
self.temp_dir = tempfile.mkdtemp()

self.assertEqual(text, 'This is regular text')
mock_page.get_text.assert_called_once_with('text')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_advanced_features.py:73*

### test_extract_text_with_ocr_sufficient_text

**Category**: method_call  
**Description**: Test OCR not triggered when sufficient text exists  
**Expected**: mock_page.get_pixmap.assert_not_called()  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
# Setup
if not PYMUPDF_AVAILABLE:
    self.skipTest('PyMuPDF not installed')
from pdf_extractor_poc import PDFExtractor
self.PDFExtractor = PDFExtractor
self.temp_dir = tempfile.mkdtemp()

self.assertEqual(len(text), 53)
mock_page.get_pixmap.assert_not_called()
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pdf_advanced_features.py:88*

### test_exponential_backoff

**Category**: method_call  
**Description**: Test that exponential backoff delays are correct  
**Expected**: mock_sleep.assert_any_call(2)  
**Confidence**: 0.85  
**Tags**: mock  

```python
mock_sleep.assert_any_call(1)
mock_sleep.assert_any_call(2)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_downloader.py:102*

### test_github_command_has_enhancement_flags

**Category**: method_call  
**Description**: E2E: Verify --enhance-local flag exists in github command help  
**Expected**: self.assertIn('--enhance', result.stdout, 'Missing --enhance flag')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(result.returncode, 0, 'github --help should succeed')
self.assertIn('--enhance', result.stdout, 'Missing --enhance flag')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_219_e2e.py:129*

### test_github_command_has_enhancement_flags

**Category**: method_call  
**Description**: E2E: Verify --enhance-local flag exists in github command help  
**Expected**: self.assertIn('--enhance-local', result.stdout, 'Missing --enhance-local flag')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('--enhance', result.stdout, 'Missing --enhance flag')
self.assertIn('--enhance-local', result.stdout, 'Missing --enhance-local flag')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_219_e2e.py:132*

### test_github_command_has_enhancement_flags

**Category**: method_call  
**Description**: E2E: Verify --enhance-local flag exists in github command help  
**Expected**: self.assertIn('--api-key', result.stdout, 'Missing --api-key flag')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('--enhance-local', result.stdout, 'Missing --enhance-local flag')
self.assertIn('--api-key', result.stdout, 'Missing --api-key flag')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_219_e2e.py:133*

### test_all_fixes_work_together

**Category**: method_call  
**Description**: E2E: Verify all 3 fixes work in combination  
**Expected**: self.assertIn('--enhance-local', result.stdout)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('--enhance', result.stdout)
self.assertIn('--enhance-local', result.stdout)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_219_e2e.py:351*

### test_all_fixes_work_together

**Category**: method_call  
**Description**: E2E: Verify all 3 fixes work in combination  
**Expected**: self.assertIn('--api-key', result.stdout)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('--enhance-local', result.stdout)
self.assertIn('--api-key', result.stdout)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_219_e2e.py:352*

### test_github_command_has_enhancement_flags

**Category**: method_call  
**Description**: E2E: Verify --enhance-local flag exists in github command help  
**Expected**: self.assertIn('--enhance', result.stdout, 'Missing --enhance flag')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(result.returncode, 0, 'github --help should succeed')
self.assertIn('--enhance', result.stdout, 'Missing --enhance flag')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_219_e2e.py:129*

### test_github_command_has_enhancement_flags

**Category**: method_call  
**Description**: E2E: Verify --enhance-local flag exists in github command help  
**Expected**: self.assertIn('--enhance-local', result.stdout, 'Missing --enhance-local flag')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('--enhance', result.stdout, 'Missing --enhance flag')
self.assertIn('--enhance-local', result.stdout, 'Missing --enhance-local flag')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_219_e2e.py:132*

### test_github_command_has_enhancement_flags

**Category**: method_call  
**Description**: E2E: Verify --enhance-local flag exists in github command help  
**Expected**: self.assertIn('--api-key', result.stdout, 'Missing --api-key flag')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('--enhance-local', result.stdout, 'Missing --enhance-local flag')
self.assertIn('--api-key', result.stdout, 'Missing --api-key flag')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_219_e2e.py:133*

### test_all_fixes_work_together

**Category**: method_call  
**Description**: E2E: Verify all 3 fixes work in combination  
**Expected**: self.assertIn('--enhance-local', result.stdout)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('--enhance', result.stdout)
self.assertIn('--enhance-local', result.stdout)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_219_e2e.py:351*

### test_all_fixes_work_together

**Category**: method_call  
**Description**: E2E: Verify all 3 fixes work in combination  
**Expected**: self.assertIn('--api-key', result.stdout)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('--enhance-local', result.stdout)
self.assertIn('--api-key', result.stdout)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_219_e2e.py:352*

### test_dry_run_no_directories_created

**Category**: method_call  
**Description**: Test that dry-run mode doesn't create directories  
**Expected**: self.assertFalse(skill_dir.exists(), 'Dry-run should not create skill directory')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test configuration'
self.config = {'name': 'test-dry-run', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre code'}, 'url_patterns': {'include': [], 'exclude': []}, 'rate_limit': 0.1, 'max_pages': 10}

self.assertFalse(data_dir.exists(), 'Dry-run should not create data directory')
self.assertFalse(skill_dir.exists(), 'Dry-run should not create skill directory')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration.py:44*

### test_normal_mode_creates_directories

**Category**: method_call  
**Description**: Test that normal mode creates directories  
**Expected**: self.assertTrue(skill_dir.exists(), 'Normal mode should create skill directory')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test configuration'
self.config = {'name': 'test-dry-run', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre code'}, 'url_patterns': {'include': [], 'exclude': []}, 'rate_limit': 0.1, 'max_pages': 10}

self.assertTrue(data_dir.exists(), 'Normal mode should create data directory')
self.assertTrue(skill_dir.exists(), 'Normal mode should create skill directory')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration.py:67*

### test_load_valid_config

**Category**: method_call  
**Description**: Test loading a valid configuration file (unified format)  
**Expected**: self.assertEqual(len(loaded_config['sources']), 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up temporary directory for test configs'
self.temp_dir = tempfile.mkdtemp()

self.assertEqual(loaded_config['name'], 'test-config')
self.assertEqual(len(loaded_config['sources']), 1)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration.py:111*

### test_load_valid_config

**Category**: method_call  
**Description**: Test loading a valid configuration file (unified format)  
**Expected**: self.assertEqual(loaded_config['sources'][0]['base_url'], 'https://example.com/')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up temporary directory for test configs'
self.temp_dir = tempfile.mkdtemp()

self.assertEqual(len(loaded_config['sources']), 1)
self.assertEqual(loaded_config['sources'][0]['base_url'], 'https://example.com/')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration.py:112*

### test_start_urls_fallback

**Category**: method_call  
**Description**: Test that start_urls defaults to base_url  
**Expected**: self.assertEqual(converter.pending_urls[0], 'https://example.com/')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(converter.pending_urls), 1)
self.assertEqual(converter.pending_urls[0], 'https://example.com/')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration.py:239*

### test_scraper_has_llms_txt_attributes

**Category**: method_call  
**Description**: Test that scraper has llms.txt detection attributes  
**Expected**: self.assertIsNone(scraper.llms_txt_variant)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(scraper.llms_txt_detected)
self.assertIsNone(scraper.llms_txt_variant)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration.py:277*

### test_scraper_has_try_llms_txt_method

**Category**: method_call  
**Description**: Test that scraper has _try_llms_txt method  
**Expected**: self.assertTrue(callable(scraper._try_llms_txt))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(hasattr(scraper, '_try_llms_txt'))
self.assertTrue(callable(scraper._try_llms_txt))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration.py:292*

### test_extract_empty_content

**Category**: method_call  
**Description**: Test extracting from empty HTML  
**Expected**: self.assertEqual(page['title'], '')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre code'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(page['url'], 'https://example.com/test')
self.assertEqual(page['title'], '')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration.py:319*

### test_extract_empty_content

**Category**: method_call  
**Description**: Test extracting from empty HTML  
**Expected**: self.assertEqual(page['content'], '')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre code'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(page['title'], '')
self.assertEqual(page['content'], '')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration.py:320*

### test_extract_empty_content

**Category**: method_call  
**Description**: Test extracting from empty HTML  
**Expected**: self.assertEqual(len(page['code_samples']), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter'
config = {'name': 'test', 'base_url': 'https://example.com/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre code'}, 'rate_limit': 0.1, 'max_pages': 10}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(page['content'], '')
self.assertEqual(len(page['code_samples']), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration.py:321*

### test_defaults_exclude_common_dirs

**Category**: method_call  
**Description**: Test that default exclusions work correctly.  
**Expected**: self.assertTrue(scraper.should_exclude_dir('node_modules'))  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
self.assertTrue(scraper.should_exclude_dir('venv'))
self.assertTrue(scraper.should_exclude_dir('node_modules'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_excluded_dirs_config.py:33*

### test_defaults_exclude_common_dirs

**Category**: method_call  
**Description**: Test that default exclusions work correctly.  
**Expected**: self.assertTrue(scraper.should_exclude_dir('__pycache__'))  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
self.assertTrue(scraper.should_exclude_dir('node_modules'))
self.assertTrue(scraper.should_exclude_dir('__pycache__'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_excluded_dirs_config.py:34*

### test_defaults_exclude_common_dirs

**Category**: method_call  
**Description**: Test that default exclusions work correctly.  
**Expected**: self.assertTrue(scraper.should_exclude_dir('.git'))  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
self.assertTrue(scraper.should_exclude_dir('__pycache__'))
self.assertTrue(scraper.should_exclude_dir('.git'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_excluded_dirs_config.py:35*

### test_defaults_exclude_common_dirs

**Category**: method_call  
**Description**: Test that default exclusions work correctly.  
**Expected**: self.assertTrue(scraper.should_exclude_dir('build'))  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
self.assertTrue(scraper.should_exclude_dir('.git'))
self.assertTrue(scraper.should_exclude_dir('build'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_excluded_dirs_config.py:36*

### test_defaults_exclude_common_dirs

**Category**: method_call  
**Description**: Test that default exclusions work correctly.  
**Expected**: self.assertFalse(scraper.should_exclude_dir('src'))  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
self.assertTrue(scraper.should_exclude_dir('build'))
self.assertFalse(scraper.should_exclude_dir('src'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_excluded_dirs_config.py:37*

### test_defaults_exclude_common_dirs

**Category**: method_call  
**Description**: Test that default exclusions work correctly.  
**Expected**: self.assertFalse(scraper.should_exclude_dir('tests'))  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
self.assertFalse(scraper.should_exclude_dir('src'))
self.assertFalse(scraper.should_exclude_dir('tests'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_excluded_dirs_config.py:40*

### test_defaults_exclude_common_dirs

**Category**: method_call  
**Description**: Test that default exclusions work correctly.  
**Expected**: self.assertFalse(scraper.should_exclude_dir('docs'))  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
self.assertFalse(scraper.should_exclude_dir('tests'))
self.assertFalse(scraper.should_exclude_dir('docs'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_excluded_dirs_config.py:41*

### test_dot_directories_always_excluded

**Category**: method_call  
**Description**: Test that directories starting with '.' are always excluded.  
**Expected**: self.assertTrue(scraper.should_exclude_dir('.cache'))  
**Confidence**: 0.85  
**Tags**: mock, unittest  

```python
self.assertTrue(scraper.should_exclude_dir('.hidden'))
self.assertTrue(scraper.should_exclude_dir('.cache'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_excluded_dirs_config.py:52*

### test_01_three_streams_present

**Category**: method_call  
**Description**: Test that all 3 streams are present and populated.  
**Expected**: assert result.code_analysis is not None, 'Code analysis missing'  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: fastmcp_analysis

print('\n📊 STREAM 1: Code Analysis')
assert result.code_analysis is not None, 'Code analysis missing'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_real_world_fastmcp.py:126*

### test_01_three_streams_present

**Category**: method_call  
**Description**: Test that all 3 streams are present and populated.  
**Expected**: assert len(files) > 0, 'No files found in code analysis'  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: fastmcp_analysis

print(f'   ✅ Files analyzed: {len(files)}')
assert len(files) > 0, 'No files found in code analysis'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_real_world_fastmcp.py:130*

### test_01_three_streams_present

**Category**: method_call  
**Description**: Test that all 3 streams are present and populated.  
**Expected**: assert result.github_docs is not None, 'GitHub docs missing'  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: fastmcp_analysis

print('\n📄 STREAM 2: GitHub Documentation')
assert result.github_docs is not None, 'GitHub docs missing'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_real_world_fastmcp.py:134*

### test_01_three_streams_present

**Category**: method_call  
**Description**: Test that all 3 streams are present and populated.  
**Expected**: assert len(readme) > 100, 'README too short (< 100 chars)'  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: fastmcp_analysis

print(f'   ✅ README length: {len(readme)} chars')
assert len(readme) > 100, 'README too short (< 100 chars)'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_real_world_fastmcp.py:139*

### test_01_three_streams_present

**Category**: method_call  
**Description**: Test that all 3 streams are present and populated.  
**Expected**: assert result.github_insights is not None, 'GitHub insights missing'  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: fastmcp_analysis

print('\n🐛 STREAM 3: GitHub Insights')
assert result.github_insights is not None, 'GitHub insights missing'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_real_world_fastmcp.py:153*

### test_01_three_streams_present

**Category**: method_call  
**Description**: Test that all 3 streams are present and populated.  
**Expected**: assert stars >= 0, 'Stars count invalid'  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: fastmcp_analysis

print(f'   ✅ Description: {description}')
assert stars >= 0, 'Stars count invalid'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_real_world_fastmcp.py:165*

### test_02_c3x_components_populated

**Category**: method_call  
**Description**: Test that C3.x components have ACTUAL data (not placeholders).  
**Expected**: assert total_c3x_items > 0, '❌ CRITICAL: No C3.x data found! This suggests placeholders are being used instead of actual analysis.'  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: fastmcp_analysis

print(f'\n📊 Total C3.x items: {total_c3x_items}')
assert total_c3x_items > 0, '❌ CRITICAL: No C3.x data found! This suggests placeholders are being used instead of actual analysis.'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_real_world_fastmcp.py:253*

### test_03_router_generation

**Category**: method_call  
**Description**: Test router generation with GitHub integration.  
**Expected**: assert 'fastmcp' in skill_md.lower(), "Router doesn't mention FastMCP"  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: fastmcp_analysis, output_dir

print('\n📝 Router Content Analysis:')
assert 'fastmcp' in skill_md.lower(), "Router doesn't mention FastMCP"
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_real_world_fastmcp.py:332*

### test_04_quality_metrics

**Category**: method_call  
**Description**: Test that quality metrics meet architecture targets.  
**Expected**: assert code_files > 0, 'No code files found'  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: fastmcp_analysis, output_dir

print(f'   Code files: {code_files}')
assert code_files > 0, 'No code files found'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_real_world_fastmcp.py:406*

### test_04_quality_metrics

**Category**: method_call  
**Description**: Test that quality metrics meet architecture targets.  
**Expected**: assert readme_len > 100, 'README too short'  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: fastmcp_analysis, output_dir

print(f'   README length: {readme_len} chars')
assert readme_len > 100, 'README too short'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_real_world_fastmcp.py:411*

### test_basic_metadata

**Category**: method_call  
**Description**: Test basic metadata creation  
**Expected**: self.assertEqual(metadata.description, 'Test skill description')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(metadata.name, 'test-skill')
self.assertEqual(metadata.description, 'Test skill description')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_base.py:24*

### test_basic_metadata

**Category**: method_call  
**Description**: Test basic metadata creation  
**Expected**: self.assertEqual(metadata.version, '1.0.0')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(metadata.description, 'Test skill description')
self.assertEqual(metadata.version, '1.0.0')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_base.py:25*

### test_basic_metadata

**Category**: method_call  
**Description**: Test basic metadata creation  
**Expected**: self.assertIsNone(metadata.author)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(metadata.version, '1.0.0')
self.assertIsNone(metadata.author)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_base.py:26*

### test_basic_metadata

**Category**: method_call  
**Description**: Test basic metadata creation  
**Expected**: self.assertEqual(metadata.tags, [])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsNone(metadata.author)
self.assertEqual(metadata.tags, [])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_base.py:27*

### test_full_metadata

**Category**: method_call  
**Description**: Test metadata with all fields  
**Expected**: self.assertEqual(metadata.description, 'React documentation')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(metadata.name, 'react')
self.assertEqual(metadata.description, 'React documentation')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_base.py:40*

### test_full_metadata

**Category**: method_call  
**Description**: Test metadata with all fields  
**Expected**: self.assertEqual(metadata.version, '2.5.0')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(metadata.description, 'React documentation')
self.assertEqual(metadata.version, '2.5.0')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_base.py:41*

### test_full_metadata

**Category**: method_call  
**Description**: Test metadata with all fields  
**Expected**: self.assertEqual(metadata.author, 'Test Author')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(metadata.version, '2.5.0')
self.assertEqual(metadata.author, 'Test Author')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_base.py:42*

### test_full_metadata

**Category**: method_call  
**Description**: Test metadata with all fields  
**Expected**: self.assertEqual(metadata.tags, ['react', 'javascript', 'web'])  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(metadata.author, 'Test Author')
self.assertEqual(metadata.tags, ['react', 'javascript', 'web'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_base.py:43*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertIn('Claude', self.adaptor.PLATFORM_NAME)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('claude')

self.assertEqual(self.adaptor.PLATFORM, 'claude')
self.assertIn('Claude', self.adaptor.PLATFORM_NAME)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_claude_adaptor.py:25*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertIsNotNone(self.adaptor.DEFAULT_API_ENDPOINT)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('claude')

self.assertIn('Claude', self.adaptor.PLATFORM_NAME)
self.assertIsNotNone(self.adaptor.DEFAULT_API_ENDPOINT)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_claude_adaptor.py:26*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertIn('anthropic.com', self.adaptor.DEFAULT_API_ENDPOINT)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('claude')

self.assertIsNotNone(self.adaptor.DEFAULT_API_ENDPOINT)
self.assertIn('anthropic.com', self.adaptor.DEFAULT_API_ENDPOINT)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_claude_adaptor.py:27*

### test_validate_api_key_valid

**Category**: method_call  
**Description**: Test valid Claude API keys  
**Expected**: self.assertTrue(self.adaptor.validate_api_key('sk-ant-api03-test'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('claude')

self.assertTrue(self.adaptor.validate_api_key('sk-ant-abc123'))
self.assertTrue(self.adaptor.validate_api_key('sk-ant-api03-test'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_claude_adaptor.py:32*

### test_validate_api_key_valid

**Category**: method_call  
**Description**: Test valid Claude API keys  
**Expected**: self.assertTrue(self.adaptor.validate_api_key('  sk-ant-test  '))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('claude')

self.assertTrue(self.adaptor.validate_api_key('sk-ant-api03-test'))
self.assertTrue(self.adaptor.validate_api_key('  sk-ant-test  '))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_claude_adaptor.py:33*

### test_validate_api_key_invalid

**Category**: method_call  
**Description**: Test invalid API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key('sk-proj-123'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('claude')

self.assertFalse(self.adaptor.validate_api_key('AIzaSyABC123'))
self.assertFalse(self.adaptor.validate_api_key('sk-proj-123'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_claude_adaptor.py:38*

### test_validate_api_key_invalid

**Category**: method_call  
**Description**: Test invalid API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key('invalid'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('claude')

self.assertFalse(self.adaptor.validate_api_key('sk-proj-123'))
self.assertFalse(self.adaptor.validate_api_key('invalid'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_claude_adaptor.py:39*

### test_validate_api_key_invalid

**Category**: method_call  
**Description**: Test invalid API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key(''))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('claude')

self.assertFalse(self.adaptor.validate_api_key('invalid'))
self.assertFalse(self.adaptor.validate_api_key(''))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_claude_adaptor.py:40*

### test_validate_api_key_invalid

**Category**: method_call  
**Description**: Test invalid API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key('sk-test'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('claude')

self.assertFalse(self.adaptor.validate_api_key(''))
self.assertFalse(self.adaptor.validate_api_key('sk-test'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_claude_adaptor.py:41*

### test_upload_invalid_file

**Category**: method_call  
**Description**: Test upload with invalid file  
**Expected**: self.assertIn('not found', result['message'].lower())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('claude')

self.assertFalse(result['success'])
self.assertIn('not found', result['message'].lower())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_claude_adaptor.py:195*

### test_format_bytes_below_1kb

**Category**: method_call  
**Description**: Test formatting bytes below 1 KB  
**Expected**: self.assertEqual(format_file_size(1023), '1023 bytes')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(format_file_size(500), '500 bytes')
self.assertEqual(format_file_size(1023), '1023 bytes')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_utilities.py:96*

### test_format_kilobytes

**Category**: method_call  
**Description**: Test formatting KB sizes  
**Expected**: self.assertEqual(format_file_size(1536), '1.5 KB')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(format_file_size(1024), '1.0 KB')
self.assertEqual(format_file_size(1536), '1.5 KB')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_utilities.py:101*

### test_format_kilobytes

**Category**: method_call  
**Description**: Test formatting KB sizes  
**Expected**: self.assertEqual(format_file_size(10240), '10.0 KB')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(format_file_size(1536), '1.5 KB')
self.assertEqual(format_file_size(10240), '10.0 KB')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_utilities.py:102*

### test_format_megabytes

**Category**: method_call  
**Description**: Test formatting MB sizes  
**Expected**: self.assertEqual(format_file_size(1572864), '1.5 MB')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(format_file_size(1048576), '1.0 MB')
self.assertEqual(format_file_size(1572864), '1.5 MB')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_utilities.py:107*

### test_format_megabytes

**Category**: method_call  
**Description**: Test formatting MB sizes  
**Expected**: self.assertEqual(format_file_size(10485760), '10.0 MB')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(format_file_size(1572864), '1.5 MB')
self.assertEqual(format_file_size(10485760), '10.0 MB')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_utilities.py:108*

### test_format_large_files

**Category**: method_call  
**Description**: Test formatting large file sizes  
**Expected**: self.assertEqual(format_file_size(1073741824), '1024.0 MB')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(format_file_size(104857600), '100.0 MB')
self.assertEqual(format_file_size(1073741824), '1024.0 MB')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_utilities.py:118*

### test_nonexistent_directory

**Category**: method_call  
**Description**: Test validation of nonexistent directory  
**Expected**: self.assertIn('not found', error.lower())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(is_valid)
self.assertIn('not found', error.lower())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_utilities.py:140*

### test_nonexistent_file

**Category**: method_call  
**Description**: Test validation of nonexistent file  
**Expected**: self.assertIn('not found', error.lower())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(is_valid)
self.assertIn('not found', error.lower())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_utilities.py:177*

### test_successful_operation_first_try

**Category**: method_call  
**Description**: Test operation that succeeds on first try  
**Expected**: self.assertEqual(call_count, 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(result, 'success')
self.assertEqual(call_count, 1)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_utilities.py:235*

### test_successful_operation_after_retry

**Category**: method_call  
**Description**: Test operation that fails once then succeeds  
**Expected**: self.assertEqual(call_count, 2)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(result, 'success')
self.assertEqual(call_count, 2)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_utilities.py:250*

### test_add_timing

**Category**: method_call  
**Description**: Test adding timing result.  
**Expected**: assert len(result.timings) == 1  
**Confidence**: 0.85  

```python
result.add_timing(timing)
assert len(result.timings) == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_benchmark.py:45*

### test_add_memory

**Category**: method_call  
**Description**: Test adding memory usage.  
**Expected**: assert len(result.memory) == 1  
**Confidence**: 0.85  

```python
result.add_memory(usage)
assert len(result.memory) == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_benchmark.py:59*

### test_add_metric

**Category**: method_call  
**Description**: Test adding custom metric.  
**Expected**: assert len(result.metrics) == 1  
**Confidence**: 0.85  

```python
result.add_metric(metric)
assert len(result.metrics) == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_benchmark.py:71*

### test_add_recommendation

**Category**: method_call  
**Description**: Test adding recommendation.  
**Expected**: assert len(result.recommendations) == 1  
**Confidence**: 0.85  

```python
result.add_recommendation('Consider caching')
assert len(result.recommendations) == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_benchmark.py:81*

### test_set_system_info

**Category**: method_call  
**Description**: Test collecting system info.  
**Expected**: assert 'cpu_count' in result.system_info  
**Confidence**: 0.85  

```python
result.set_system_info()
assert 'cpu_count' in result.system_info
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_benchmark.py:90*

### test_measure_with_memory_tracking

**Category**: method_call  
**Description**: Test measure with memory tracking.  
**Expected**: assert len(benchmark.result.timings) == 1  
**Confidence**: 0.85  

```python
benchmark.measure(allocate_memory, operation='allocate', track_memory=True)
assert len(benchmark.result.timings) == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_benchmark.py:177*

### test_timed_decorator_with_memory

**Category**: method_call  
**Description**: Test timed decorator with memory tracking.  
**Expected**: assert len(benchmark.result.timings) == 1  
**Confidence**: 0.85  

```python
allocate()
assert len(benchmark.result.timings) == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_benchmark.py:205*

### test_surface_detection_by_name

**Category**: method_call  
**Description**: Test surface detection using class name  
**Expected**: self.assertGreaterEqual(pattern.confidence, 0.5)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.detector = SingletonDetector(depth='deep')
self.recognizer = PatternRecognizer(depth='deep')

self.assertEqual(pattern.pattern_type, 'Singleton')
self.assertGreaterEqual(pattern.confidence, 0.5)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pattern_recognizer.py:48*

### test_surface_detection_by_name

**Category**: method_call  
**Description**: Test surface detection using class name  
**Expected**: self.assertIn('Singleton', pattern.class_name)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.detector = SingletonDetector(depth='deep')
self.recognizer = PatternRecognizer(depth='deep')

self.assertGreaterEqual(pattern.confidence, 0.5)
self.assertIn('Singleton', pattern.class_name)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pattern_recognizer.py:51*

### test_deep_detection_with_instance_method

**Category**: method_call  
**Description**: Test deep detection with getInstance() method  
**Expected**: self.assertEqual(report.language, 'Python')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.detector = SingletonDetector(depth='deep')
self.recognizer = PatternRecognizer(depth='deep')

self.assertIsNotNone(report)
self.assertEqual(report.language, 'Python')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pattern_recognizer.py:68*

### test_python_singleton_with_new

**Category**: method_call  
**Description**: Test Python-specific __new__ singleton pattern  
**Expected**: self.assertGreaterEqual(report.total_classes, 1)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.detector = SingletonDetector(depth='deep')
self.recognizer = PatternRecognizer(depth='deep')

self.assertIsNotNone(report)
self.assertGreaterEqual(report.total_classes, 1)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_pattern_recognizer.py:86*

### test_cache_has

**Category**: method_call  
**Description**: Test cache has method.  
**Expected**: assert cache.has('hash123') is True  
**Confidence**: 0.85  

```python
cache.set('hash123', embedding, 'test-model')
assert cache.has('hash123') is True
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding.py:52*

### test_cache_delete

**Category**: method_call  
**Description**: Test cache deletion.  
**Expected**: assert cache.has('hash123') is True  
**Confidence**: 0.85  

```python
cache.set('hash123', embedding, 'test-model')
assert cache.has('hash123') is True
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding.py:63*

### test_cache_delete

**Category**: method_call  
**Description**: Test cache deletion.  
**Expected**: assert cache.has('hash123') is False  
**Confidence**: 0.85  

```python
cache.delete('hash123')
assert cache.has('hash123') is False
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding.py:67*

### test_cache_clear

**Category**: method_call  
**Description**: Test cache clearing.  
**Expected**: assert cache.size() == 3  
**Confidence**: 0.85  

```python
cache.set('hash3', [0.3], 'model1')
assert cache.size() == 3
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding.py:78*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertEqual(self.adaptor.PLATFORM_NAME, 'OpenAI ChatGPT')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('openai')

self.assertEqual(self.adaptor.PLATFORM, 'openai')
self.assertEqual(self.adaptor.PLATFORM_NAME, 'OpenAI ChatGPT')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_openai_adaptor.py:24*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertIsNotNone(self.adaptor.DEFAULT_API_ENDPOINT)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('openai')

self.assertEqual(self.adaptor.PLATFORM_NAME, 'OpenAI ChatGPT')
self.assertIsNotNone(self.adaptor.DEFAULT_API_ENDPOINT)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_openai_adaptor.py:25*

### test_validate_api_key_valid

**Category**: method_call  
**Description**: Test valid OpenAI API keys  
**Expected**: self.assertTrue(self.adaptor.validate_api_key('sk-abc123'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('openai')

self.assertTrue(self.adaptor.validate_api_key('sk-proj-abc123'))
self.assertTrue(self.adaptor.validate_api_key('sk-abc123'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_openai_adaptor.py:30*

### test_validate_api_key_valid

**Category**: method_call  
**Description**: Test valid OpenAI API keys  
**Expected**: self.assertTrue(self.adaptor.validate_api_key('  sk-test  '))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('openai')

self.assertTrue(self.adaptor.validate_api_key('sk-abc123'))
self.assertTrue(self.adaptor.validate_api_key('  sk-test  '))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_openai_adaptor.py:31*

### test_validate_api_key_invalid

**Category**: method_call  
**Description**: Test invalid API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key('invalid'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('openai')

self.assertFalse(self.adaptor.validate_api_key('AIzaSyABC123'))
self.assertFalse(self.adaptor.validate_api_key('invalid'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_openai_adaptor.py:36*

### test_validate_api_key_invalid

**Category**: method_call  
**Description**: Test invalid API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key(''))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('openai')

self.assertFalse(self.adaptor.validate_api_key('invalid'))
self.assertFalse(self.adaptor.validate_api_key(''))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_openai_adaptor.py:38*

### test_upload_invalid_file

**Category**: method_call  
**Description**: Test upload with invalid file  
**Expected**: self.assertIn('not found', result['message'].lower())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('openai')

self.assertFalse(result['success'])
self.assertIn('not found', result['message'].lower())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_openai_adaptor.py:113*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertEqual(self.adaptor.PLATFORM_NAME, 'OpenAI ChatGPT')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(self.adaptor.PLATFORM, 'openai')
self.assertEqual(self.adaptor.PLATFORM_NAME, 'OpenAI ChatGPT')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_openai_adaptor.py:24*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertIsNotNone(self.adaptor.DEFAULT_API_ENDPOINT)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(self.adaptor.PLATFORM_NAME, 'OpenAI ChatGPT')
self.assertIsNotNone(self.adaptor.DEFAULT_API_ENDPOINT)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_openai_adaptor.py:25*

### test_validate_api_key_valid

**Category**: method_call  
**Description**: Test valid OpenAI API keys  
**Expected**: self.assertTrue(self.adaptor.validate_api_key('sk-abc123'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(self.adaptor.validate_api_key('sk-proj-abc123'))
self.assertTrue(self.adaptor.validate_api_key('sk-abc123'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_openai_adaptor.py:30*

### test_javascript_detection

**Category**: method_call  
**Description**: Test JavaScript file detection.  
**Expected**: self.assertEqual(detect_language(Path('test.jsx')), 'JavaScript')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(detect_language(Path('test.js')), 'JavaScript')
self.assertEqual(detect_language(Path('test.jsx')), 'JavaScript')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_codebase_scraper.py:48*

### test_typescript_detection

**Category**: method_call  
**Description**: Test TypeScript file detection.  
**Expected**: self.assertEqual(detect_language(Path('test.tsx')), 'TypeScript')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(detect_language(Path('test.ts')), 'TypeScript')
self.assertEqual(detect_language(Path('test.tsx')), 'TypeScript')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_codebase_scraper.py:53*

### test_cpp_detection

**Category**: method_call  
**Description**: Test C++ file detection.  
**Expected**: self.assertEqual(detect_language(Path('test.h')), 'C++')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(detect_language(Path('test.cpp')), 'C++')
self.assertEqual(detect_language(Path('test.h')), 'C++')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_codebase_scraper.py:58*

### test_cpp_detection

**Category**: method_call  
**Description**: Test C++ file detection.  
**Expected**: self.assertEqual(detect_language(Path('test.hpp')), 'C++')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(detect_language(Path('test.h')), 'C++')
self.assertEqual(detect_language(Path('test.hpp')), 'C++')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_codebase_scraper.py:59*

### test_detect_terminal_with_skill_seeker_env

**Category**: method_call  
**Description**: Test that SKILL_SEEKER_TERMINAL env var takes highest priority.  
**Expected**: self.assertEqual(detection_method, 'SKILL_SEEKER_TERMINAL')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Save original environment variables.'
self.original_skill_seeker = os.environ.get('SKILL_SEEKER_TERMINAL')
self.original_term_program = os.environ.get('TERM_PROGRAM')

self.assertEqual(terminal_app, 'Ghostty')
self.assertEqual(detection_method, 'SKILL_SEEKER_TERMINAL')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_terminal_detection.py:53*

### test_detect_terminal_with_term_program_known

**Category**: method_call  
**Description**: Test detection from TERM_PROGRAM with known terminal (iTerm).  
**Expected**: self.assertEqual(detection_method, 'TERM_PROGRAM')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Save original environment variables.'
self.original_skill_seeker = os.environ.get('SKILL_SEEKER_TERMINAL')
self.original_term_program = os.environ.get('TERM_PROGRAM')

self.assertEqual(terminal_app, 'iTerm')
self.assertEqual(detection_method, 'TERM_PROGRAM')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_terminal_detection.py:66*

### test_detect_terminal_with_term_program_ghostty

**Category**: method_call  
**Description**: Test detection from TERM_PROGRAM with Ghostty terminal.  
**Expected**: self.assertEqual(detection_method, 'TERM_PROGRAM')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Save original environment variables.'
self.original_skill_seeker = os.environ.get('SKILL_SEEKER_TERMINAL')
self.original_term_program = os.environ.get('TERM_PROGRAM')

self.assertEqual(terminal_app, 'Ghostty')
self.assertEqual(detection_method, 'TERM_PROGRAM')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_terminal_detection.py:78*

### test_detect_terminal_with_term_program_apple_terminal

**Category**: method_call  
**Description**: Test detection from TERM_PROGRAM with Apple Terminal.  
**Expected**: self.assertEqual(detection_method, 'TERM_PROGRAM')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Save original environment variables.'
self.original_skill_seeker = os.environ.get('SKILL_SEEKER_TERMINAL')
self.original_term_program = os.environ.get('TERM_PROGRAM')

self.assertEqual(terminal_app, 'Terminal')
self.assertEqual(detection_method, 'TERM_PROGRAM')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_terminal_detection.py:90*

### test_detect_terminal_with_term_program_wezterm

**Category**: method_call  
**Description**: Test detection from TERM_PROGRAM with WezTerm.  
**Expected**: self.assertEqual(detection_method, 'TERM_PROGRAM')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Save original environment variables.'
self.original_skill_seeker = os.environ.get('SKILL_SEEKER_TERMINAL')
self.original_term_program = os.environ.get('TERM_PROGRAM')

self.assertEqual(terminal_app, 'WezTerm')
self.assertEqual(detection_method, 'TERM_PROGRAM')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_terminal_detection.py:102*

### test_detect_terminal_with_term_program_unknown

**Category**: method_call  
**Description**: Test fallback behavior when TERM_PROGRAM is unknown (e.g., IDE terminals).  
**Expected**: self.assertEqual(detection_method, 'unknown TERM_PROGRAM (zed)')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Save original environment variables.'
self.original_skill_seeker = os.environ.get('SKILL_SEEKER_TERMINAL')
self.original_term_program = os.environ.get('TERM_PROGRAM')

self.assertEqual(terminal_app, 'Terminal')
self.assertEqual(detection_method, 'unknown TERM_PROGRAM (zed)')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_terminal_detection.py:114*

### test_detect_terminal_default_fallback

**Category**: method_call  
**Description**: Test default fallback when no environment variables are set.  
**Expected**: self.assertEqual(detection_method, 'default')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Save original environment variables.'
self.original_skill_seeker = os.environ.get('SKILL_SEEKER_TERMINAL')
self.original_term_program = os.environ.get('TERM_PROGRAM')

self.assertEqual(terminal_app, 'Terminal')
self.assertEqual(detection_method, 'default')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_terminal_detection.py:127*

### test_detect_terminal_priority_order

**Category**: method_call  
**Description**: Test that SKILL_SEEKER_TERMINAL takes priority over TERM_PROGRAM.  
**Expected**: self.assertEqual(detection_method, 'SKILL_SEEKER_TERMINAL')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Save original environment variables.'
self.original_skill_seeker = os.environ.get('SKILL_SEEKER_TERMINAL')
self.original_term_program = os.environ.get('TERM_PROGRAM')

self.assertEqual(terminal_app, 'Ghostty')
self.assertEqual(detection_method, 'SKILL_SEEKER_TERMINAL')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_terminal_detection.py:138*

### test_strips_anchor_fragments

**Category**: method_call  
**Description**: Test that anchor fragments (#anchor) are properly stripped from URLs  
**Expected**: self.assertEqual(result[0], 'https://example.com/docs/quick-start/index.html.md')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter instance'
config = {'name': 'test', 'description': 'Test', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article'}}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(len(result), 3)
self.assertEqual(result[0], 'https://example.com/docs/quick-start/index.html.md')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_url_conversion.py:35*

### test_strips_anchor_fragments

**Category**: method_call  
**Description**: Test that anchor fragments (#anchor) are properly stripped from URLs  
**Expected**: self.assertEqual(result[1], 'https://example.com/docs/api/index.html.md')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter instance'
config = {'name': 'test', 'description': 'Test', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article'}}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(result[0], 'https://example.com/docs/quick-start/index.html.md')
self.assertEqual(result[1], 'https://example.com/docs/api/index.html.md')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_url_conversion.py:36*

### test_strips_anchor_fragments

**Category**: method_call  
**Description**: Test that anchor fragments (#anchor) are properly stripped from URLs  
**Expected**: self.assertEqual(result[2], 'https://example.com/docs/guide/index.html.md')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter instance'
config = {'name': 'test', 'description': 'Test', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article'}}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(result[1], 'https://example.com/docs/api/index.html.md')
self.assertEqual(result[2], 'https://example.com/docs/guide/index.html.md')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_url_conversion.py:37*

### test_deduplicates_multiple_anchors_same_url

**Category**: method_call  
**Description**: Test that multiple anchors on the same URL are deduplicated  
**Expected**: self.assertEqual(result[0], 'https://example.com/docs/api/index.html.md')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter instance'
config = {'name': 'test', 'description': 'Test', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article'}}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(len(result), 1)
self.assertEqual(result[0], 'https://example.com/docs/api/index.html.md')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_url_conversion.py:52*

### test_preserves_md_extension_urls

**Category**: method_call  
**Description**: Test that URLs already ending with .md are preserved  
**Expected**: self.assertEqual(result[0], 'https://example.com/docs/guide.md')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter instance'
config = {'name': 'test', 'description': 'Test', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article'}}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(len(result), 3)
self.assertEqual(result[0], 'https://example.com/docs/guide.md')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_url_conversion.py:66*

### test_preserves_md_extension_urls

**Category**: method_call  
**Description**: Test that URLs already ending with .md are preserved  
**Expected**: self.assertEqual(result[1], 'https://example.com/docs/readme.md')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter instance'
config = {'name': 'test', 'description': 'Test', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article'}}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(result[0], 'https://example.com/docs/guide.md')
self.assertEqual(result[1], 'https://example.com/docs/readme.md')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_url_conversion.py:67*

### test_preserves_md_extension_urls

**Category**: method_call  
**Description**: Test that URLs already ending with .md are preserved  
**Expected**: self.assertEqual(result[2], 'https://example.com/docs/api-reference.md')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter instance'
config = {'name': 'test', 'description': 'Test', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article'}}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(result[1], 'https://example.com/docs/readme.md')
self.assertEqual(result[2], 'https://example.com/docs/api-reference.md')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_url_conversion.py:68*

### test_md_extension_with_anchor_fragments

**Category**: method_call  
**Description**: Test that .md URLs with anchors are handled correctly  
**Expected**: self.assertIn('https://example.com/docs/guide.md', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter instance'
config = {'name': 'test', 'description': 'Test', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article'}}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(len(result), 2)
self.assertIn('https://example.com/docs/guide.md', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_url_conversion.py:82*

### test_md_extension_with_anchor_fragments

**Category**: method_call  
**Description**: Test that .md URLs with anchors are handled correctly  
**Expected**: self.assertIn('https://example.com/docs/api.md', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter instance'
config = {'name': 'test', 'description': 'Test', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article'}}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertIn('https://example.com/docs/guide.md', result)
self.assertIn('https://example.com/docs/api.md', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_url_conversion.py:83*

### test_does_not_match_md_in_path

**Category**: method_call  
**Description**: Test that URLs containing 'md' in path (but not ending with .md) are converted  
**Expected**: self.assertEqual(result[0], 'https://example.com/cmd-line/index.html.md')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter instance'
config = {'name': 'test', 'description': 'Test', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article'}}
self.converter = DocToSkillConverter(config, dry_run=True)

self.assertEqual(len(result), 3)
self.assertEqual(result[0], 'https://example.com/cmd-line/index.html.md')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_url_conversion.py:97*

### test_detect_json_files

**Category**: method_call  
**Description**: Test detection of JSON config files  
**Expected**: self.assertTrue(any(('package.json' in f for f in filenames)))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.detector = ConfigFileDetector()
self.temp_dir = tempfile.mkdtemp()

self.assertTrue(any(('config.json' in f for f in filenames)))
self.assertTrue(any(('package.json' in f for f in filenames)))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_extractor.py:59*

### test_parse_json_config

**Category**: method_call  
**Description**: Test parsing JSON configuration  
**Expected**: self.assertGreater(len(config_file.settings), 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
self.parser = ConfigParser()
self.temp_dir = tempfile.mkdtemp()

self.parser.parse_config_file(config_file)
self.assertGreater(len(config_file.settings), 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_extractor.py:130*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertEqual(self.adaptor.PLATFORM_NAME, 'Google Gemini')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('gemini')

self.assertEqual(self.adaptor.PLATFORM, 'gemini')
self.assertEqual(self.adaptor.PLATFORM_NAME, 'Google Gemini')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_gemini_adaptor.py:24*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertIsNotNone(self.adaptor.DEFAULT_API_ENDPOINT)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('gemini')

self.assertEqual(self.adaptor.PLATFORM_NAME, 'Google Gemini')
self.assertIsNotNone(self.adaptor.DEFAULT_API_ENDPOINT)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_gemini_adaptor.py:25*

### test_validate_api_key_valid

**Category**: method_call  
**Description**: Test valid Google API key  
**Expected**: self.assertTrue(self.adaptor.validate_api_key('  AIzaSyTest  '))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('gemini')

self.assertTrue(self.adaptor.validate_api_key('AIzaSyABC123'))
self.assertTrue(self.adaptor.validate_api_key('  AIzaSyTest  '))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_gemini_adaptor.py:30*

### test_validate_api_key_invalid

**Category**: method_call  
**Description**: Test invalid API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key('invalid'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('gemini')

self.assertFalse(self.adaptor.validate_api_key('sk-ant-123'))
self.assertFalse(self.adaptor.validate_api_key('invalid'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_gemini_adaptor.py:35*

### test_validate_api_key_invalid

**Category**: method_call  
**Description**: Test invalid API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key(''))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('gemini')

self.assertFalse(self.adaptor.validate_api_key('invalid'))
self.assertFalse(self.adaptor.validate_api_key(''))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_gemini_adaptor.py:36*

### test_upload_invalid_file

**Category**: method_call  
**Description**: Test upload with invalid file  
**Expected**: self.assertIn('not found', result['message'].lower())  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('gemini')

self.assertFalse(result['success'])
self.assertIn('not found', result['message'].lower())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_gemini_adaptor.py:115*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertEqual(self.adaptor.PLATFORM_NAME, 'Google Gemini')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(self.adaptor.PLATFORM, 'gemini')
self.assertEqual(self.adaptor.PLATFORM_NAME, 'Google Gemini')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_gemini_adaptor.py:24*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertIsNotNone(self.adaptor.DEFAULT_API_ENDPOINT)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(self.adaptor.PLATFORM_NAME, 'Google Gemini')
self.assertIsNotNone(self.adaptor.DEFAULT_API_ENDPOINT)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_gemini_adaptor.py:25*

### test_validate_api_key_valid

**Category**: method_call  
**Description**: Test valid Google API key  
**Expected**: self.assertTrue(self.adaptor.validate_api_key('  AIzaSyTest  '))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(self.adaptor.validate_api_key('AIzaSyABC123'))
self.assertTrue(self.adaptor.validate_api_key('  AIzaSyTest  '))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_gemini_adaptor.py:30*

### test_validate_api_key_invalid

**Category**: method_call  
**Description**: Test invalid API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key('invalid'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(self.adaptor.validate_api_key('sk-ant-123'))
self.assertFalse(self.adaptor.validate_api_key('invalid'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_gemini_adaptor.py:35*

### test_version_increment

**Category**: method_call  
**Description**: Test version numbers increment correctly.  
**Expected**: assert change_set2.modified[0].version == 2  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: temp_skill_dir

updater2.save_current_versions()
assert change_set2.modified[0].version == 2
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_incremental_updates.py:252*

### test_telegram_bots_config_pattern

**Category**: method_call  
**Description**: Test the telegram-bots config pattern which uses skip_llms_txt.  
**Expected**: self.assertEqual(converter.name, 'telegram-bots')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(converter.skip_llms_txt)
self.assertEqual(converter.name, 'telegram-bots')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_skip_llms_txt.py:213*

### test_skip_llms_txt_with_multiple_start_urls

**Category**: method_call  
**Description**: Test skip_llms_txt works correctly with multiple start URLs.  
**Expected**: self.assertEqual(len(converter.pending_urls), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(converter.skip_llms_txt)
self.assertEqual(len(converter.pending_urls), 3)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_skip_llms_txt.py:231*

### test_telegram_bots_config_pattern

**Category**: method_call  
**Description**: Test the telegram-bots config pattern which uses skip_llms_txt.  
**Expected**: self.assertEqual(converter.name, 'telegram-bots')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(converter.skip_llms_txt)
self.assertEqual(converter.name, 'telegram-bots')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_skip_llms_txt.py:213*

### test_skip_llms_txt_with_multiple_start_urls

**Category**: method_call  
**Description**: Test skip_llms_txt works correctly with multiple start URLs.  
**Expected**: self.assertEqual(len(converter.pending_urls), 3)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(converter.skip_llms_txt)
self.assertEqual(len(converter.pending_urls), 3)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_skip_llms_txt.py:231*

### test_scraping_constants_exist

**Category**: method_call  
**Description**: Test that scraping constants are defined.  
**Expected**: self.assertIsNotNone(DEFAULT_MAX_PAGES)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsNotNone(DEFAULT_RATE_LIMIT)
self.assertIsNotNone(DEFAULT_MAX_PAGES)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_constants.py:37*

### test_scraping_constants_exist

**Category**: method_call  
**Description**: Test that scraping constants are defined.  
**Expected**: self.assertIsNotNone(DEFAULT_CHECKPOINT_INTERVAL)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsNotNone(DEFAULT_MAX_PAGES)
self.assertIsNotNone(DEFAULT_CHECKPOINT_INTERVAL)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_constants.py:38*

### test_scraping_constants_types

**Category**: method_call  
**Description**: Test that scraping constants have correct types.  
**Expected**: self.assertIsInstance(DEFAULT_MAX_PAGES, int)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(DEFAULT_RATE_LIMIT, (int, float))
self.assertIsInstance(DEFAULT_MAX_PAGES, int)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_constants.py:43*

### test_scraping_constants_types

**Category**: method_call  
**Description**: Test that scraping constants have correct types.  
**Expected**: self.assertIsInstance(DEFAULT_CHECKPOINT_INTERVAL, int)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIsInstance(DEFAULT_MAX_PAGES, int)
self.assertIsInstance(DEFAULT_CHECKPOINT_INTERVAL, int)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_constants.py:44*

### test_scraping_constants_ranges

**Category**: method_call  
**Description**: Test that scraping constants have sensible values.  
**Expected**: self.assertGreater(DEFAULT_MAX_PAGES, 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertGreater(DEFAULT_RATE_LIMIT, 0)
self.assertGreater(DEFAULT_MAX_PAGES, 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_constants.py:49*

### test_scraping_constants_ranges

**Category**: method_call  
**Description**: Test that scraping constants have sensible values.  
**Expected**: self.assertGreater(DEFAULT_CHECKPOINT_INTERVAL, 0)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertGreater(DEFAULT_MAX_PAGES, 0)
self.assertGreater(DEFAULT_CHECKPOINT_INTERVAL, 0)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_constants.py:50*

### test_scraping_constants_ranges

**Category**: method_call  
**Description**: Test that scraping constants have sensible values.  
**Expected**: self.assertEqual(DEFAULT_RATE_LIMIT, 0.5)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertGreater(DEFAULT_CHECKPOINT_INTERVAL, 0)
self.assertEqual(DEFAULT_RATE_LIMIT, 0.5)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_constants.py:51*

### test_scraping_constants_ranges

**Category**: method_call  
**Description**: Test that scraping constants have sensible values.  
**Expected**: self.assertEqual(DEFAULT_MAX_PAGES, 500)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(DEFAULT_RATE_LIMIT, 0.5)
self.assertEqual(DEFAULT_MAX_PAGES, 500)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_constants.py:52*

### test_scraping_constants_ranges

**Category**: method_call  
**Description**: Test that scraping constants have sensible values.  
**Expected**: self.assertEqual(DEFAULT_CHECKPOINT_INTERVAL, 1000)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(DEFAULT_MAX_PAGES, 500)
self.assertEqual(DEFAULT_CHECKPOINT_INTERVAL, 1000)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_constants.py:53*

### test_content_analysis_constants

**Category**: method_call  
**Description**: Test content analysis constants.  
**Expected**: self.assertEqual(MAX_PAGES_WARNING_THRESHOLD, 10000)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(CONTENT_PREVIEW_LENGTH, 500)
self.assertEqual(MAX_PAGES_WARNING_THRESHOLD, 10000)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_constants.py:58*

### mock_github_repo

**Category**: method_call  
**Description**: Create mock GitHub repository structure.  
**Expected**: (tests_dir / 'test_auth.py').write_text("\ndef test_google_provider():\n    provider = google_provider('id', 'secret')\n    assert provider.name == 'google'\n\ndef test_azure_provider():\n    provider = azure_provider('tenant', 'id')\n    assert provider.name == 'azure'\n")  
**Confidence**: 0.85  
**Tags**: mock, pytest  

```python
# Setup
# Fixtures: tmp_path

tests_dir.mkdir()
(tests_dir / 'test_auth.py').write_text("\ndef test_google_provider():\n    provider = google_provider('id', 'secret')\n    assert provider.name == 'google'\n\ndef test_azure_provider():\n    provider = azure_provider('tenant', 'id')\n    assert provider.name == 'azure'\n")
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_architecture_scenarios.py:98*

### test_doc_scraper_uses_modern_commands

**Category**: method_call  
**Description**: Test doc_scraper.py uses skill-seekers commands  
**Expected**: self.assertNotIn('python3 cli/doc_scraper.py', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('skill-seekers scrape', content)
self.assertNotIn('python3 cli/doc_scraper.py', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_paths.py:30*

### test_enhance_skill_local_uses_modern_commands

**Category**: method_call  
**Description**: Test enhance_skill_local.py uses skill-seekers commands  
**Expected**: self.assertNotIn('python3 cli/enhance_skill_local.py', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('skill-seekers', content)
self.assertNotIn('python3 cli/enhance_skill_local.py', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_paths.py:49*

### test_estimate_pages_uses_modern_commands

**Category**: method_call  
**Description**: Test estimate_pages.py uses skill-seekers commands  
**Expected**: self.assertNotIn('python3 cli/estimate_pages.py', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('skill-seekers estimate', content)
self.assertNotIn('python3 cli/estimate_pages.py', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_paths.py:64*

### test_package_skill_uses_modern_commands

**Category**: method_call  
**Description**: Test package_skill.py uses skill-seekers commands  
**Expected**: self.assertNotIn('python3 cli/package_skill.py', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('skill-seekers package', content)
self.assertNotIn('python3 cli/package_skill.py', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_paths.py:79*

### test_github_scraper_uses_modern_commands

**Category**: method_call  
**Description**: Test github_scraper.py uses skill-seekers commands  
**Expected**: self.assertNotIn('python3 cli/github_scraper.py', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('skill-seekers', content)
self.assertNotIn('python3 cli/github_scraper.py', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_paths.py:94*

### test_doc_scraper_uses_modern_commands

**Category**: method_call  
**Description**: Test doc_scraper.py uses skill-seekers commands  
**Expected**: self.assertNotIn('python3 cli/doc_scraper.py', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('skill-seekers scrape', content)
self.assertNotIn('python3 cli/doc_scraper.py', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_paths.py:30*

### test_enhance_skill_local_uses_modern_commands

**Category**: method_call  
**Description**: Test enhance_skill_local.py uses skill-seekers commands  
**Expected**: self.assertNotIn('python3 cli/enhance_skill_local.py', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('skill-seekers', content)
self.assertNotIn('python3 cli/enhance_skill_local.py', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_paths.py:49*

### test_estimate_pages_uses_modern_commands

**Category**: method_call  
**Description**: Test estimate_pages.py uses skill-seekers commands  
**Expected**: self.assertNotIn('python3 cli/estimate_pages.py', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('skill-seekers estimate', content)
self.assertNotIn('python3 cli/estimate_pages.py', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_paths.py:64*

### test_package_skill_uses_modern_commands

**Category**: method_call  
**Description**: Test package_skill.py uses skill-seekers commands  
**Expected**: self.assertNotIn('python3 cli/package_skill.py', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('skill-seekers package', content)
self.assertNotIn('python3 cli/package_skill.py', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_paths.py:79*

### test_github_scraper_uses_modern_commands

**Category**: method_call  
**Description**: Test github_scraper.py uses skill-seekers commands  
**Expected**: self.assertNotIn('python3 cli/github_scraper.py', content)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('skill-seekers', content)
self.assertNotIn('python3 cli/github_scraper.py', content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_paths.py:94*

### test_analyze_help_shows_command

**Category**: method_call  
**Description**: Test that analyze command appears in main help.  
**Expected**: self.assertIn('analyze', result.stdout)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(result.returncode, 0, f'Help failed: {result.stderr}')
self.assertIn('analyze', result.stdout)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_e2e.py:93*

### test_analyze_help_shows_command

**Category**: method_call  
**Description**: Test that analyze command appears in main help.  
**Expected**: self.assertIn('Analyze local codebase', result.stdout)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('analyze', result.stdout)
self.assertIn('Analyze local codebase', result.stdout)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_e2e.py:94*

### test_analyze_subcommand_help

**Category**: method_call  
**Description**: Test that analyze subcommand has proper help.  
**Expected**: self.assertIn('--quick', result.stdout)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(result.returncode, 0, f'Analyze help failed: {result.stderr}')
self.assertIn('--quick', result.stdout)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_e2e.py:100*

### test_analyze_subcommand_help

**Category**: method_call  
**Description**: Test that analyze subcommand has proper help.  
**Expected**: self.assertIn('--comprehensive', result.stdout)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertIn('--quick', result.stdout)
self.assertIn('--comprehensive', result.stdout)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_e2e.py:101*

### test_analyze_subcommand_exists

**Category**: method_call  
**Description**: Test that analyze subcommand is registered.  
**Expected**: self.assertEqual(args.directory, '.')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create parser for testing.'
self.parser = create_parser()

self.assertEqual(args.command, 'analyze')
self.assertEqual(args.directory, '.')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_command.py:23*

### test_quick_preset_flag

**Category**: method_call  
**Description**: Test --quick preset flag parsing.  
**Expected**: self.assertFalse(args.comprehensive)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create parser for testing.'
self.parser = create_parser()

self.assertTrue(args.quick)
self.assertFalse(args.comprehensive)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_command.py:34*

### test_comprehensive_preset_flag

**Category**: method_call  
**Description**: Test --comprehensive preset flag parsing.  
**Expected**: self.assertFalse(args.quick)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create parser for testing.'
self.parser = create_parser()

self.assertTrue(args.comprehensive)
self.assertFalse(args.quick)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_command.py:40*

### test_quick_and_comprehensive_mutually_exclusive

**Category**: method_call  
**Description**: Test that both flags can be parsed (mutual exclusion enforced at runtime).  
**Expected**: self.assertTrue(args.comprehensive)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create parser for testing.'
self.parser = create_parser()

self.assertTrue(args.quick)
self.assertTrue(args.comprehensive)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_command.py:47*

### test_skip_flags_passed_through

**Category**: method_call  
**Description**: Test that skip flags are recognized.  
**Expected**: self.assertTrue(args.skip_test_examples)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create parser for testing.'
self.parser = create_parser()

self.assertTrue(args.skip_patterns)
self.assertTrue(args.skip_test_examples)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_command.py:61*

### test_all_skip_flags

**Category**: method_call  
**Description**: Test all skip flags are properly parsed.  
**Expected**: self.assertTrue(args.skip_dependency_graph)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create parser for testing.'
self.parser = create_parser()

self.assertTrue(args.skip_api_reference)
self.assertTrue(args.skip_dependency_graph)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_command.py:80*

### test_all_skip_flags

**Category**: method_call  
**Description**: Test all skip flags are properly parsed.  
**Expected**: self.assertTrue(args.skip_patterns)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create parser for testing.'
self.parser = create_parser()

self.assertTrue(args.skip_dependency_graph)
self.assertTrue(args.skip_patterns)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_command.py:81*

### test_all_skip_flags

**Category**: method_call  
**Description**: Test all skip flags are properly parsed.  
**Expected**: self.assertTrue(args.skip_test_examples)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Create parser for testing.'
self.parser = create_parser()

self.assertTrue(args.skip_patterns)
self.assertTrue(args.skip_test_examples)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_analyze_command.py:82*

### test_cors_middleware

**Category**: method_call  
**Description**: Test that CORS middleware can be added.  
**Expected**: assert len(app.user_middleware) > 0  
**Confidence**: 0.85  

```python
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
assert len(app.user_middleware) > 0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_server_fastmcp_http.py:101*

### test_c3_reference_directory_structure

**Category**: method_call  
**Description**: Test correct C3.x reference directory structure is created.  
**Expected**: assert os.path.exists(os.path.join(c3_dir, 'ARCHITECTURE.md'))  
**Confidence**: 0.85  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_config, mock_c3_data, temp_dir

builder._copy_architecture_details(c3_dir, mock_c3_data.get('architecture'))
assert os.path.exists(os.path.join(c3_dir, 'ARCHITECTURE.md'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_c3_integration.py:240*

### test_force_refresh_deletes_cache

**Category**: method_call  
**Description**: Test force refresh deletes existing cache.  
**Expected**: mock_clone.assert_called_once()  
**Confidence**: 0.85  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_clone, git_repo, temp_cache_dir

git_repo.clone_or_pull(source_name='test-source', git_url='https://github.com/org/repo.git', force_refresh=True)
mock_clone.assert_called_once()
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_repo.py:207*

### test_missing_recommended_selectors

**Category**: method_call  
**Description**: Test warning for missing recommended selectors  
**Expected**: self.assertTrue(any(('code_blocks' in warning.lower() for warning in warnings)))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(any(('title' in warning.lower() for warning in warnings)))
self.assertTrue(any(('code_blocks' in warning.lower() for warning in warnings)))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_validation.py:106*

### test_config_with_skip_llms_txt

**Category**: method_call  
**Description**: Test config validation accepts skip_llms_txt  
**Expected**: self.assertTrue(config.get('skip_llms_txt'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(errors, [])
self.assertTrue(config.get('skip_llms_txt'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_validation.py:257*

### test_config_with_skip_llms_txt_false

**Category**: method_call  
**Description**: Test config validation accepts skip_llms_txt as False  
**Expected**: self.assertFalse(config.get('skip_llms_txt'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(errors, [])
self.assertFalse(config.get('skip_llms_txt'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_validation.py:265*

### test_missing_recommended_selectors

**Category**: method_call  
**Description**: Test warning for missing recommended selectors  
**Expected**: self.assertTrue(any(('code_blocks' in warning.lower() for warning in warnings)))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertTrue(any(('title' in warning.lower() for warning in warnings)))
self.assertTrue(any(('code_blocks' in warning.lower() for warning in warnings)))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_validation.py:106*

### test_config_with_skip_llms_txt

**Category**: method_call  
**Description**: Test config validation accepts skip_llms_txt  
**Expected**: self.assertTrue(config.get('skip_llms_txt'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(errors, [])
self.assertTrue(config.get('skip_llms_txt'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_validation.py:257*

### test_config_with_skip_llms_txt_false

**Category**: method_call  
**Description**: Test config validation accepts skip_llms_txt as False  
**Expected**: self.assertFalse(config.get('skip_llms_txt'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(errors, [])
self.assertFalse(config.get('skip_llms_txt'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_validation.py:265*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertEqual(self.adaptor.PLATFORM_NAME, 'Generic Markdown (Universal)')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('markdown')

self.assertEqual(self.adaptor.PLATFORM, 'markdown')
self.assertEqual(self.adaptor.PLATFORM_NAME, 'Generic Markdown (Universal)')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_markdown_adaptor.py:24*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertIsNone(self.adaptor.DEFAULT_API_ENDPOINT)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('markdown')

self.assertEqual(self.adaptor.PLATFORM_NAME, 'Generic Markdown (Universal)')
self.assertIsNone(self.adaptor.DEFAULT_API_ENDPOINT)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_markdown_adaptor.py:25*

### test_validate_api_key

**Category**: method_call  
**Description**: Test that markdown export doesn't use API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key('AIzaSyABC123'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('markdown')

self.assertFalse(self.adaptor.validate_api_key('sk-ant-123'))
self.assertFalse(self.adaptor.validate_api_key('AIzaSyABC123'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_markdown_adaptor.py:31*

### test_validate_api_key

**Category**: method_call  
**Description**: Test that markdown export doesn't use API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key('any-key'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('markdown')

self.assertFalse(self.adaptor.validate_api_key('AIzaSyABC123'))
self.assertFalse(self.adaptor.validate_api_key('any-key'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_markdown_adaptor.py:32*

### test_validate_api_key

**Category**: method_call  
**Description**: Test that markdown export doesn't use API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key(''))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test adaptor'
self.adaptor = get_adaptor('markdown')

self.assertFalse(self.adaptor.validate_api_key('any-key'))
self.assertFalse(self.adaptor.validate_api_key(''))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_markdown_adaptor.py:33*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertEqual(self.adaptor.PLATFORM_NAME, 'Generic Markdown (Universal)')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(self.adaptor.PLATFORM, 'markdown')
self.assertEqual(self.adaptor.PLATFORM_NAME, 'Generic Markdown (Universal)')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_markdown_adaptor.py:24*

### test_platform_info

**Category**: method_call  
**Description**: Test platform identifiers  
**Expected**: self.assertIsNone(self.adaptor.DEFAULT_API_ENDPOINT)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(self.adaptor.PLATFORM_NAME, 'Generic Markdown (Universal)')
self.assertIsNone(self.adaptor.DEFAULT_API_ENDPOINT)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_markdown_adaptor.py:25*

### test_validate_api_key

**Category**: method_call  
**Description**: Test that markdown export doesn't use API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key('AIzaSyABC123'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(self.adaptor.validate_api_key('sk-ant-123'))
self.assertFalse(self.adaptor.validate_api_key('AIzaSyABC123'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_markdown_adaptor.py:31*

### test_validate_api_key

**Category**: method_call  
**Description**: Test that markdown export doesn't use API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key('any-key'))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(self.adaptor.validate_api_key('AIzaSyABC123'))
self.assertFalse(self.adaptor.validate_api_key('any-key'))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_markdown_adaptor.py:32*

### test_validate_api_key

**Category**: method_call  
**Description**: Test that markdown export doesn't use API keys  
**Expected**: self.assertFalse(self.adaptor.validate_api_key(''))  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(self.adaptor.validate_api_key('any-key'))
self.assertFalse(self.adaptor.validate_api_key(''))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_markdown_adaptor.py:33*

### test_progress_tracking

**Category**: method_call  
**Description**: Test progress tracking during streaming.  
**Expected**: assert len(progress_updates) > 0  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: temp_skill_dir

list(ingester.stream_skill_directory(temp_skill_dir, callback=callback))
assert len(progress_updates) > 0
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_streaming_ingestion.py:166*

### test_package_nonexistent_directory

**Category**: method_call  
**Description**: Test packaging a nonexistent directory  
**Expected**: self.assertIsNone(zip_path)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(success)
self.assertIsNone(zip_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_package_skill.py:101*

### test_package_nonexistent_directory

**Category**: method_call  
**Description**: Test packaging a nonexistent directory  
**Expected**: self.assertIsNone(zip_path)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertFalse(success)
self.assertIsNone(zip_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_package_skill.py:101*

### test_mikro_orm_urls_from_issue_277

**Category**: method_call  
**Description**: Test the exact URLs that caused 404 errors in issue #277  
**Expected**: self.assertIn('https://mikro-orm.io/docs/quick-start/index.html.md', result, 'quick-start URL should be correctly transformed')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter with MikroORM-like configuration'
self.config = {'name': 'MikroORM', 'description': 'ORM', 'base_url': 'https://mikro-orm.io/docs/', 'selectors': {'main_content': 'article'}, 'url_patterns': {'include': ['/docs'], 'exclude': []}}
self.converter = DocToSkillConverter(self.config, dry_run=True)

self.assertEqual(len(result), 7, f'Should have 7 unique base URLs after deduplication, got {len(result)}')
self.assertIn('https://mikro-orm.io/docs/quick-start/index.html.md', result, 'quick-start URL should be correctly transformed')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_277_real_world.py:67*

### test_mikro_orm_urls_from_issue_277

**Category**: method_call  
**Description**: Test the exact URLs that caused 404 errors in issue #277  
**Expected**: self.assertIn('https://mikro-orm.io/docs/propagation/index.html.md', result, 'propagation URL should be correctly transformed')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter with MikroORM-like configuration'
self.config = {'name': 'MikroORM', 'description': 'ORM', 'base_url': 'https://mikro-orm.io/docs/', 'selectors': {'main_content': 'article'}, 'url_patterns': {'include': ['/docs'], 'exclude': []}}
self.converter = DocToSkillConverter(self.config, dry_run=True)

self.assertIn('https://mikro-orm.io/docs/quick-start/index.html.md', result, 'quick-start URL should be correctly transformed')
self.assertIn('https://mikro-orm.io/docs/propagation/index.html.md', result, 'propagation URL should be correctly transformed')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_277_real_world.py:74*

### test_mikro_orm_urls_from_issue_277

**Category**: method_call  
**Description**: Test the exact URLs that caused 404 errors in issue #277  
**Expected**: self.assertIn('https://mikro-orm.io/docs/defining-entities.md', result, 'defining-entities.md should preserve .md extension')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter with MikroORM-like configuration'
self.config = {'name': 'MikroORM', 'description': 'ORM', 'base_url': 'https://mikro-orm.io/docs/', 'selectors': {'main_content': 'article'}, 'url_patterns': {'include': ['/docs'], 'exclude': []}}
self.converter = DocToSkillConverter(self.config, dry_run=True)

self.assertIn('https://mikro-orm.io/docs/propagation/index.html.md', result, 'propagation URL should be correctly transformed')
self.assertIn('https://mikro-orm.io/docs/defining-entities.md', result, 'defining-entities.md should preserve .md extension')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_277_real_world.py:79*

### test_deduplication_prevents_multiple_requests

**Category**: method_call  
**Description**: Verify that multiple anchors on same page don't create duplicate requests  
**Expected**: self.assertEqual(result[0], 'https://mikro-orm.io/docs/defining-entities/index.html.md')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter with MikroORM-like configuration'
self.config = {'name': 'MikroORM', 'description': 'ORM', 'base_url': 'https://mikro-orm.io/docs/', 'selectors': {'main_content': 'article'}, 'url_patterns': {'include': ['/docs'], 'exclude': []}}
self.converter = DocToSkillConverter(self.config, dry_run=True)

self.assertEqual(len(result), 1, 'Multiple anchors on same page should deduplicate to single request')
self.assertEqual(result[0], 'https://mikro-orm.io/docs/defining-entities/index.html.md')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_277_real_world.py:134*

### test_md_files_with_anchors_preserved

**Category**: method_call  
**Description**: Test that .md files with anchors are handled correctly  
**Expected**: self.assertIn('https://mikro-orm.io/docs/repositories.md', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter with MikroORM-like configuration'
self.config = {'name': 'MikroORM', 'description': 'ORM', 'base_url': 'https://mikro-orm.io/docs/', 'selectors': {'main_content': 'article'}, 'url_patterns': {'include': ['/docs'], 'exclude': []}}
self.converter = DocToSkillConverter(self.config, dry_run=True)

self.assertEqual(len(result), 3)
self.assertIn('https://mikro-orm.io/docs/repositories.md', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_277_real_world.py:155*

### test_md_files_with_anchors_preserved

**Category**: method_call  
**Description**: Test that .md files with anchors are handled correctly  
**Expected**: self.assertIn('https://mikro-orm.io/docs/defining-entities.md', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter with MikroORM-like configuration'
self.config = {'name': 'MikroORM', 'description': 'ORM', 'base_url': 'https://mikro-orm.io/docs/', 'selectors': {'main_content': 'article'}, 'url_patterns': {'include': ['/docs'], 'exclude': []}}
self.converter = DocToSkillConverter(self.config, dry_run=True)

self.assertIn('https://mikro-orm.io/docs/repositories.md', result)
self.assertIn('https://mikro-orm.io/docs/defining-entities.md', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_277_real_world.py:156*

### test_md_files_with_anchors_preserved

**Category**: method_call  
**Description**: Test that .md files with anchors are handled correctly  
**Expected**: self.assertIn('https://mikro-orm.io/docs/inheritance-mapping.md', result)  
**Confidence**: 0.85  
**Tags**: unittest  

```python
# Setup
'Set up test converter with MikroORM-like configuration'
self.config = {'name': 'MikroORM', 'description': 'ORM', 'base_url': 'https://mikro-orm.io/docs/', 'selectors': {'main_content': 'article'}, 'url_patterns': {'include': ['/docs'], 'exclude': []}}
self.converter = DocToSkillConverter(self.config, dry_run=True)

self.assertIn('https://mikro-orm.io/docs/defining-entities.md', result)
self.assertIn('https://mikro-orm.io/docs/inheritance-mapping.md', result)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_277_real_world.py:157*

### test_mikro_orm_urls_from_issue_277

**Category**: method_call  
**Description**: Test the exact URLs that caused 404 errors in issue #277  
**Expected**: self.assertIn('https://mikro-orm.io/docs/quick-start/index.html.md', result, 'quick-start URL should be correctly transformed')  
**Confidence**: 0.85  
**Tags**: unittest  

```python
self.assertEqual(len(result), 7, f'Should have 7 unique base URLs after deduplication, got {len(result)}')
self.assertIn('https://mikro-orm.io/docs/quick-start/index.html.md', result, 'quick-start URL should be correctly transformed')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_issue_277_real_world.py:67*

### test_add_document_single_language

**Category**: method_call  
**Description**: Test adding documents in single language.  
**Expected**: assert len(manager.get_languages()) == 1  
**Confidence**: 0.85  

```python
manager.add_document('README.md', 'This is an English document.', {'category': 'overview'})
assert len(manager.get_languages()) == 1
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multilang_support.py:118*

### test_add_document_multiple_languages

**Category**: method_call  
**Description**: Test adding documents in multiple languages.  
**Expected**: assert len(manager.get_languages()) == 3  
**Confidence**: 0.85  

```python
manager.add_document('README.fr.md', 'Ceci est français.', {})
assert len(manager.get_languages()) == 3
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multilang_support.py:131*

### test_force_language

**Category**: method_call  
**Description**: Test forcing language override.  
**Expected**: assert 'es' in manager.get_languages()  
**Confidence**: 0.85  

```python
manager.add_document('file.md', 'This is actually English content.', {}, force_language='es')
assert 'es' in manager.get_languages()
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multilang_support.py:144*

### test_filename_language_priority

**Category**: method_call  
**Description**: Test filename pattern takes priority over content detection.  
**Expected**: assert 'es' in manager.get_languages()  
**Confidence**: 0.85  

```python
manager.add_document('guide.es.md', 'This is English content.', {})
assert 'es' in manager.get_languages()
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multilang_support.py:155*

### test_document_count_all

**Category**: method_call  
**Description**: Test total document count.  
**Expected**: assert manager.get_document_count() == 3  
**Confidence**: 0.85  

```python
manager.add_document('file3.es.md', 'Spanish doc', {})
assert manager.get_document_count() == 3
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multilang_support.py:167*

### test_primary_language

**Category**: method_call  
**Description**: Test primary language is set correctly.  
**Expected**: assert manager.primary_language == 'en'  
**Confidence**: 0.85  

```python
manager.add_document('file2.es.md', 'Spanish doc', {})
assert manager.primary_language == 'en'
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multilang_support.py:179*

### test_get_agent_path_home_expansion

**Category**: instantiation  
**Description**: Instantiate get_agent_path: Test that ~ expands to home directory for global agents.  
**Expected**: assert path.is_absolute()  
**Confidence**: 0.80  

```python
path = get_agent_path('claude')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_agent.py:41*

### test_get_agent_path_project_relative

**Category**: instantiation  
**Description**: Instantiate get_agent_path: Test that project-relative paths use current directory.  
**Expected**: assert path.is_absolute()  
**Confidence**: 0.80  

```python
path = get_agent_path('cursor')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_agent.py:49*

### test_get_agent_path_project_relative_with_custom_root

**Category**: instantiation  
**Description**: Instantiate Path: Test project-relative paths with custom project root.  
**Expected**: assert path.is_absolute()  
**Confidence**: 0.80  

```python
custom_root = Path('/tmp/test-project')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_agent.py:57*

### test_get_agent_path_project_relative_with_custom_root

**Category**: instantiation  
**Description**: Instantiate get_agent_path: Test project-relative paths with custom project root.  
**Expected**: assert path.is_absolute()  
**Confidence**: 0.80  

```python
path = get_agent_path('cursor', project_root=custom_root)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_agent.py:58*

### test_agent_path_case_insensitive

**Category**: instantiation  
**Description**: Instantiate get_agent_path: Test that agent names are case-insensitive.  
**Expected**: assert path_lower == path_upper == path_mixed  
**Confidence**: 0.80  

```python
path_lower = get_agent_path('claude')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_agent.py:82*

### test_agent_path_case_insensitive

**Category**: instantiation  
**Description**: Instantiate get_agent_path: Test that agent names are case-insensitive.  
**Expected**: assert path_lower == path_upper == path_mixed  
**Confidence**: 0.80  

```python
path_upper = get_agent_path('CLAUDE')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_agent.py:83*

### test_agent_path_case_insensitive

**Category**: instantiation  
**Description**: Instantiate get_agent_path: Test that agent names are case-insensitive.  
**Expected**: assert path_lower == path_upper == path_mixed  
**Confidence**: 0.80  

```python
path_mixed = get_agent_path('Claude')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_agent.py:84*

### test_validate_valid_agent

**Category**: instantiation  
**Description**: Instantiate validate_agent_name: Test that valid agent names pass validation.  
**Expected**: assert is_valid is True  
**Confidence**: 0.80  

```python
is_valid, error = validate_agent_name('claude')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_agent.py:93*

### test_validate_invalid_agent_suggests_similar

**Category**: instantiation  
**Description**: Instantiate validate_agent_name: Test that similar agent names are suggested for typos.  
**Expected**: assert is_valid is False  
**Confidence**: 0.80  

```python
is_valid, error = validate_agent_name('courser')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_agent.py:99*

### test_validate_special_all

**Category**: instantiation  
**Description**: Instantiate validate_agent_name: Test that 'all' is a valid special agent name.  
**Expected**: assert is_valid is True  
**Confidence**: 0.80  

```python
is_valid, error = validate_agent_name('all')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_agent.py:105*

### test_checker_detects_missing_skill_md

**Category**: instantiation  
**Description**: Instantiate SkillQualityChecker: Test that checker detects missing SKILL.md  
**Confidence**: 0.80  
**Tags**: unittest  

```python
checker = SkillQualityChecker(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_checker.py:42*

### test_checker_detects_missing_references

**Category**: instantiation  
**Description**: Instantiate create_test_skill: Test that checker warns about missing references  
**Confidence**: 0.80  
**Tags**: unittest  

```python
skill_dir = self.create_test_skill(tmpdir, skill_md, create_references=False)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_checker.py:60*

### test_checker_detects_missing_references

**Category**: instantiation  
**Description**: Instantiate SkillQualityChecker: Test that checker warns about missing references  
**Confidence**: 0.80  
**Tags**: unittest  

```python
checker = SkillQualityChecker(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_checker.py:62*

### test_checker_detects_invalid_frontmatter

**Category**: instantiation  
**Description**: Instantiate create_test_skill: Test that checker detects invalid YAML frontmatter  
**Confidence**: 0.80  
**Tags**: unittest  

```python
skill_dir = self.create_test_skill(tmpdir, skill_md)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_checker.py:76*

### test_checker_detects_invalid_frontmatter

**Category**: instantiation  
**Description**: Instantiate SkillQualityChecker: Test that checker detects invalid YAML frontmatter  
**Confidence**: 0.80  
**Tags**: unittest  

```python
checker = SkillQualityChecker(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_checker.py:78*

### test_checker_detects_missing_name_field

**Category**: instantiation  
**Description**: Instantiate create_test_skill: Test that checker detects missing name field in frontmatter  
**Confidence**: 0.80  
**Tags**: unittest  

```python
skill_dir = self.create_test_skill(tmpdir, skill_md)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_checker.py:94*

### test_checker_detects_missing_name_field

**Category**: instantiation  
**Description**: Instantiate SkillQualityChecker: Test that checker detects missing name field in frontmatter  
**Confidence**: 0.80  
**Tags**: unittest  

```python
checker = SkillQualityChecker(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_checker.py:96*

### test_checker_detects_code_without_language

**Category**: instantiation  
**Description**: Instantiate create_test_skill: Test that checker warns about code blocks without language tags  
**Confidence**: 0.80  
**Tags**: unittest  

```python
skill_dir = self.create_test_skill(tmpdir, skill_md)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_checker.py:118*

### test_checker_detects_code_without_language

**Category**: instantiation  
**Description**: Instantiate SkillQualityChecker: Test that checker warns about code blocks without language tags  
**Confidence**: 0.80  
**Tags**: unittest  

```python
checker = SkillQualityChecker(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_checker.py:120*

### test_checker_approves_good_skill

**Category**: instantiation  
**Description**: Instantiate create_test_skill: Test that checker gives high score to well-formed skill  
**Confidence**: 0.80  
**Tags**: unittest  

```python
skill_dir = self.create_test_skill(tmpdir, skill_md)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_checker.py:164*

### test_scrape_parser_creates_subparser

**Category**: instantiation  
**Description**: Instantiate create_parser: Test that ScrapeParser creates valid subparser.  
**Expected**: assert subparser is not None  
**Confidence**: 0.80  

```python
subparser = scrape_parser.create_parser(subparsers)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_parsers.py:78*

### test_github_parser_creates_subparser

**Category**: instantiation  
**Description**: Instantiate create_parser: Test that GitHubParser creates valid subparser.  
**Expected**: assert subparser is not None  
**Confidence**: 0.80  

```python
subparser = github_parser.create_parser(subparsers)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cli_parsers.py:90*

### test_cli_validation_error_no_config

**Category**: instantiation  
**Description**: Instantiate run: E2E test: CLI validation error (no config provided)  
**Expected**: assert result.returncode != 0  
**Confidence**: 0.80  

```python
result = subprocess.run([sys.executable, '-m', 'skill_seekers.cli.install_skill'], capture_output=True, text=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_skill_e2e.py:355*

### test_cli_help

**Category**: instantiation  
**Description**: Instantiate run: E2E test: CLI help command  
**Expected**: assert result.returncode == 0  
**Confidence**: 0.80  

```python
result = subprocess.run([sys.executable, '-m', 'skill_seekers.cli.install_skill', '--help'], capture_output=True, text=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_skill_e2e.py:370*

### test_cli_via_unified_command

**Category**: instantiation  
**Description**: Instantiate run: E2E test: Using 'skill-seekers install' unified CLI

Note: Skipped because subprocess execution has asyncio.run() issues.
The functionality is already tested in test_cli_full_workflow_mocked
via direct function calls.  
**Expected**: assert result.returncode == 0 or 'DRY RUN' in result.stdout, f'Unified CLI failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}'  
**Confidence**: 0.80  
**Tags**: mock, async, pytest  

```python
# Setup
# Fixtures: test_config_file

result = subprocess.run(['skill-seekers', 'install', '--config', test_config_file, '--dry-run'], capture_output=True, text=True, timeout=30)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_skill_e2e.py:438*

### real_test_config

**Category**: instantiation  
**Description**: Instantiate Path: Create a real minimal config that can be scraped  
**Confidence**: 0.80  
**Tags**: pytest  

```python
# Setup
# Fixtures: tmp_path

test_config_path = Path('configs/test-manual.json')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_skill_e2e.py:459*

### test_mcp_directory_structure

**Category**: instantiation  
**Description**: Instantiate Path: Test that MCP directory structure is correct (new src/ layout)  
**Expected**: assert mcp_dir.exists(), 'src/skill_seekers/mcp/ directory should exist'  
**Confidence**: 0.80  

```python
mcp_dir = Path('src/skill_seekers/mcp')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_setup_scripts.py:242*

### test_mcp_directory_structure

**Category**: instantiation  
**Description**: Instantiate Path: Test that MCP directory structure is correct (new src/ layout)  
**Confidence**: 0.80  

```python
old_mcp = Path('mcp')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_setup_scripts.py:249*

### test_mcp_directory_structure

**Category**: instantiation  
**Description**: Instantiate Path: Test that MCP directory structure is correct (new src/ layout)  
**Confidence**: 0.80  

```python
old_skill_seeker_mcp = Path('skill_seeker_mcp')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_setup_scripts.py:250*

### test_bash_syntax_valid

**Category**: instantiation  
**Description**: Instantiate run: Test that setup_mcp.sh has valid bash syntax  
**Expected**: assert result.returncode == 0, f'Bash syntax error: {result.stderr}'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: script_path

result = subprocess.run(['bash', '-n', str(script_path)], capture_output=True, text=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_setup_scripts.py:36*

### test_references_correct_mcp_directory

**Category**: instantiation  
**Description**: Instantiate findall: Test that script references src/skill_seekers/mcp/ (v2.4.0 MCP 2025 upgrade)  
**Expected**: assert len(old_mcp_refs) == 0, f"Found {len(old_mcp_refs)} references to old 'mcp/' directory: {old_mcp_refs}"  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: script_content

old_mcp_refs = re.findall('(?:^|[^a-z_])(?<!/)mcp/(?!\\.json)', script_content, re.MULTILINE)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_setup_scripts.py:42*

### test_references_correct_mcp_directory

**Category**: instantiation  
**Description**: Instantiate findall: Test that script references src/skill_seekers/mcp/ (v2.4.0 MCP 2025 upgrade)  
**Expected**: assert len(old_mcp_refs) == 0, f"Found {len(old_mcp_refs)} references to old 'mcp/' directory: {old_mcp_refs}"  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: script_content

old_skill_seeker_refs = re.findall('skill_seeker_mcp/', script_content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_setup_scripts.py:45*

### test_references_correct_mcp_directory

**Category**: instantiation  
**Description**: Instantiate findall: Test that script references src/skill_seekers/mcp/ (v2.4.0 MCP 2025 upgrade)  
**Expected**: assert len(new_refs) >= 2, f"Expected at least 2 references to 'skill_seekers.mcp' module, found {len(new_refs)}"  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: script_content

new_refs = re.findall('skill_seekers\\.mcp', script_content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_setup_scripts.py:57*

### test_requirements_txt_path

**Category**: instantiation  
**Description**: Instantiate findall: Test that script uses pip install -e . (v2.0.0 modern packaging)  
**Expected**: assert len(old_skill_seeker_refs) == 0, f"Should NOT reference 'skill_seeker_mcp/requirements.txt' (found {len(old_skill_seeker_refs)})"  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: script_content

old_skill_seeker_refs = re.findall('skill_seeker_mcp/requirements\\.txt', script_content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_setup_scripts.py:77*

### test_requirements_txt_path

**Category**: instantiation  
**Description**: Instantiate findall: Test that script uses pip install -e . (v2.0.0 modern packaging)  
**Expected**: assert len(old_skill_seeker_refs) == 0, f"Should NOT reference 'skill_seeker_mcp/requirements.txt' (found {len(old_skill_seeker_refs)})"  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: script_content

old_mcp_refs = re.findall('(?<!skill_seeker_)mcp/requirements\\.txt', script_content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_setup_scripts.py:78*

### test_adaptor_registration

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test that LangChain adaptor is registered.  
**Expected**: assert adaptor.PLATFORM == 'langchain'  
**Confidence**: 0.80  

```python
adaptor = get_adaptor('langchain')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_langchain_adaptor.py:19*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test formatting SKILL.md as LangChain Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

adaptor = get_adaptor('langchain')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_langchain_adaptor.py:40*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate SkillMetadata: Test formatting SKILL.md as LangChain Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_langchain_adaptor.py:41*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate format_skill_md: Test formatting SKILL.md as LangChain Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

documents_json = adaptor.format_skill_md(skill_dir, metadata)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_langchain_adaptor.py:43*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate loads: Test formatting SKILL.md as LangChain Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

documents = json.loads(documents_json)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_langchain_adaptor.py:46*

### test_successful_fetch

**Category**: instantiation  
**Description**: Instantiate str: Test successful config download from API.  
**Expected**: assert result is not None  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client_class, tmp_path

destination = str(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_fetcher.py:55*

### test_successful_fetch

**Category**: instantiation  
**Description**: Instantiate fetch_config_from_api: Test successful config download from API.  
**Expected**: assert result is not None  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client_class, tmp_path

result = fetch_config_from_api('react', destination=destination)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_fetcher.py:56*

### test_successful_fetch

**Category**: instantiation  
**Description**: Instantiate load: Test successful config download from API.  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client_class, tmp_path

config = json.load(f)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_fetcher.py:65*

### test_config_not_found

**Category**: instantiation  
**Description**: Instantiate fetch_config_from_api: Test handling of 404 response.  
**Expected**: assert result is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client_class

result = fetch_config_from_api('nonexistent')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_fetcher.py:80*

### test_no_download_url

**Category**: instantiation  
**Description**: Instantiate fetch_config_from_api: Test handling of missing download_url.  
**Expected**: assert result is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client_class

result = fetch_config_from_api('test')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_fetcher.py:96*

### test_http_error

**Category**: instantiation  
**Description**: Instantiate HTTPError: Test handling of HTTP errors.  
**Expected**: assert result is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client_class

mock_client.get.side_effect = httpx.HTTPError('Connection failed')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_fetcher.py:106*

### test_http_error

**Category**: instantiation  
**Description**: Instantiate fetch_config_from_api: Test handling of HTTP errors.  
**Expected**: assert result is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client_class

result = fetch_config_from_api('react')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_config_fetcher.py:108*

### test_code_stream

**Category**: instantiation  
**Description**: Instantiate CodeStream: Test CodeStream data class.  
**Expected**: assert code_stream.directory == Path('/tmp/repo')  
**Confidence**: 0.80  

```python
code_stream = CodeStream(directory=Path('/tmp/repo'), files=[Path('/tmp/repo/src/main.py')])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_fetcher.py:29*

### test_docs_stream

**Category**: instantiation  
**Description**: Instantiate DocsStream: Test DocsStream data class.  
**Expected**: assert docs_stream.readme == '# README'  
**Confidence**: 0.80  

```python
docs_stream = DocsStream(readme='# README', contributing='# Contributing', docs_files=[{'path': 'docs/guide.md', 'content': '# Guide'}])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_fetcher.py:35*

### test_insights_stream

**Category**: instantiation  
**Description**: Instantiate InsightsStream: Test InsightsStream data class.  
**Expected**: assert insights_stream.metadata['stars'] == 1234  
**Confidence**: 0.80  

```python
insights_stream = InsightsStream(metadata={'stars': 1234, 'forks': 56}, common_problems=[{'title': 'Bug', 'number': 42}], known_solutions=[{'title': 'Fix', 'number': 35}], top_labels=[{'label': 'bug', 'count': 10}])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_fetcher.py:46*

### test_three_stream_data

**Category**: instantiation  
**Description**: Instantiate ThreeStreamData: Test ThreeStreamData combination.  
**Expected**: assert isinstance(three_streams.code_stream, CodeStream)  
**Confidence**: 0.80  

```python
three_streams = ThreeStreamData(code_stream=CodeStream(Path('/tmp'), []), docs_stream=DocsStream(None, None, []), insights_stream=InsightsStream({}, [], [], []))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_fetcher.py:59*

### test_parse_https_url

**Category**: instantiation  
**Description**: Instantiate GitHubThreeStreamFetcher: Test parsing HTTPS GitHub URLs.  
**Expected**: assert fetcher.owner == 'facebook'  
**Confidence**: 0.80  

```python
fetcher = GitHubThreeStreamFetcher('https://github.com/facebook/react')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_fetcher.py:74*

### test_parse_https_url_with_git

**Category**: instantiation  
**Description**: Instantiate GitHubThreeStreamFetcher: Test parsing HTTPS URLs with .git suffix.  
**Expected**: assert fetcher.owner == 'facebook'  
**Confidence**: 0.80  

```python
fetcher = GitHubThreeStreamFetcher('https://github.com/facebook/react.git')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_fetcher.py:80*

### test_parse_git_url

**Category**: instantiation  
**Description**: Instantiate GitHubThreeStreamFetcher: Test parsing git@ URLs.  
**Expected**: assert fetcher.owner == 'facebook'  
**Confidence**: 0.80  

```python
fetcher = GitHubThreeStreamFetcher('git@github.com:facebook/react.git')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_fetcher.py:86*

### test_github_token_from_env

**Category**: instantiation  
**Description**: Instantiate GitHubThreeStreamFetcher: Test GitHub token loaded from environment.  
**Expected**: assert fetcher.github_token == 'test_token'  
**Confidence**: 0.80  
**Tags**: mock  

```python
fetcher = GitHubThreeStreamFetcher('https://github.com/facebook/react')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_github_fetcher.py:98*

### test_single_worker_default

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test default is single-worker mode  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_parallel_scraping.py:35*

### test_multiple_workers_creates_lock

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test multiple workers creates thread lock  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_parallel_scraping.py:51*

### test_workers_from_config

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test workers parameter is read from config  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_parallel_scraping.py:66*

### test_unlimited_with_none

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test max_pages: None enables unlimited mode  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_parallel_scraping.py:92*

### test_unlimited_with_minus_one

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test max_pages: -1 enables unlimited mode  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_parallel_scraping.py:106*

### test_limited_mode_default

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test default max_pages is limited  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_parallel_scraping.py:119*

### test_limited_mode_default

**Category**: instantiation  
**Description**: Instantiate get: Test default max_pages is limited  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

max_pages = converter.config.get('max_pages', 500)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_parallel_scraping.py:120*

### test_rate_limit_from_config

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test rate_limit is read from config  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_parallel_scraping.py:147*

### test_rate_limit_default

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test default rate_limit is 0.5  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_parallel_scraping.py:160*

### test_zero_rate_limit_disables

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test rate_limit: 0 disables rate limiting  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_parallel_scraping.py:174*

### test_router_generator_init

**Category**: instantiation  
**Description**: Instantiate RouterGenerator: Test router generator initialization.  
**Expected**: assert generator.router_name == 'test'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

generator = RouterGenerator([str(config_path1), str(config_path2)])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_generate_router_github.py:45*

### test_upload_without_api_key

**Category**: instantiation  
**Description**: Instantiate create_test_zip: Test that upload fails gracefully without API key  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Store original API key state'
self.original_api_key = os.environ.get('ANTHROPIC_API_KEY')

zip_path = self.create_test_zip(tmpdir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_skill.py:46*

### test_upload_without_api_key

**Category**: instantiation  
**Description**: Instantiate upload_skill_api: Test that upload fails gracefully without API key  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Store original API key state'
self.original_api_key = os.environ.get('ANTHROPIC_API_KEY')

success, message = upload_skill_api(zip_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_skill.py:48*

### test_upload_with_nonexistent_file

**Category**: instantiation  
**Description**: Instantiate upload_skill_api: Test upload with nonexistent file  
**Expected**: self.assertFalse(success)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Store original API key state'
self.original_api_key = os.environ.get('ANTHROPIC_API_KEY')

success, message = upload_skill_api('/nonexistent/file.zip')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_skill.py:58*

### test_upload_with_invalid_zip

**Category**: instantiation  
**Description**: Instantiate upload_skill_api: Test upload with invalid zip file (not a zip)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Store original API key state'
self.original_api_key = os.environ.get('ANTHROPIC_API_KEY')

success, message = upload_skill_api(tmpfile.name)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_skill.py:72*

### test_upload_accepts_path_object

**Category**: instantiation  
**Description**: Instantiate create_test_zip: Test that upload_skill_api accepts Path objects  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Store original API key state'
self.original_api_key = os.environ.get('ANTHROPIC_API_KEY')

zip_path = self.create_test_zip(tmpdir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_skill.py:84*

### test_upload_accepts_path_object

**Category**: instantiation  
**Description**: Instantiate upload_skill_api: Test that upload_skill_api accepts Path objects  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Store original API key state'
self.original_api_key = os.environ.get('ANTHROPIC_API_KEY')

success, message = upload_skill_api(Path(zip_path))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_skill.py:88*

### test_cli_help_output

**Category**: instantiation  
**Description**: Instantiate run: Test that skill-seekers upload --help works  
**Confidence**: 0.80  
**Tags**: unittest  

```python
result = subprocess.run(['skill-seekers', 'upload', '--help'], capture_output=True, text=True, timeout=5)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_skill.py:101*

### test_cli_executes_without_errors

**Category**: instantiation  
**Description**: Instantiate run: Test that skill-seekers-upload entry point works  
**Confidence**: 0.80  
**Tags**: unittest  

```python
result = subprocess.run(['skill-seekers-upload', '--help'], capture_output=True, text=True, timeout=5)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_skill.py:117*

### test_bootstrap_script_runs

**Category**: instantiation  
**Description**: Instantiate run: Test that bootstrap script runs successfully.

Note: This test is slow as it runs full codebase analysis.
Run with: pytest -m slow  
**Expected**: assert result.returncode == 0, f'Script failed: {result.stderr}'  
**Confidence**: 0.80  
**Tags**: pytest  

```python
# Setup
# Fixtures: project_root

result = subprocess.run(['bash', str(script)], cwd=project_root, capture_output=True, text=True, timeout=600)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_bootstrap_skill.py:63*

### test_successful_download

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDownloader: Test successful download with valid markdown content  
**Expected**: assert content is not None  
**Confidence**: 0.80  
**Tags**: mock  

```python
downloader = LlmsTxtDownloader('https://example.com/llms.txt')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_downloader.py:10*

### test_timeout_with_retry

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDownloader: Test timeout scenario with retry logic  
**Expected**: assert content is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
downloader = LlmsTxtDownloader('https://example.com/llms.txt', max_retries=2)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_downloader.py:31*

### test_empty_content_rejection

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDownloader: Test rejection of content shorter than 100 chars  
**Expected**: assert content is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
downloader = LlmsTxtDownloader('https://example.com/llms.txt')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_downloader.py:46*

### test_non_markdown_rejection

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDownloader: Test rejection of content that doesn't look like markdown  
**Expected**: assert content is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
downloader = LlmsTxtDownloader('https://example.com/llms.txt')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_downloader.py:60*

### test_http_error_handling

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDownloader: Test handling of HTTP errors (404, 500, etc.)  
**Expected**: assert content is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
downloader = LlmsTxtDownloader('https://example.com/llms.txt', max_retries=2)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_downloader.py:74*

### test_http_error_handling

**Category**: instantiation  
**Description**: Instantiate HTTPError: Test handling of HTTP errors (404, 500, etc.)  
**Expected**: assert content is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
mock_response.raise_for_status.side_effect = requests.HTTPError('404 Not Found')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_downloader.py:77*

### test_exponential_backoff

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDownloader: Test that exponential backoff delays are correct  
**Expected**: assert content is None  
**Confidence**: 0.80  
**Tags**: mock  

```python
downloader = LlmsTxtDownloader('https://example.com/llms.txt', max_retries=3)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_downloader.py:91*

### test_markdown_validation

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDownloader: Test markdown pattern detection  
**Expected**: assert downloader._is_markdown('# Header')  
**Confidence**: 0.80  

```python
downloader = LlmsTxtDownloader('https://example.com/llms.txt')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_downloader.py:108*

### test_custom_timeout

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDownloader: Test custom timeout parameter  
**Expected**: assert content is not None  
**Confidence**: 0.80  
**Tags**: mock  

```python
downloader = LlmsTxtDownloader('https://example.com/llms.txt', timeout=10)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_downloader.py:124*

### test_cli_accepts_target_flag

**Category**: instantiation  
**Description**: Instantiate parse_args: Test that CLI accepts --target flag  
**Confidence**: 0.80  
**Tags**: unittest  

```python
args = parser.parse_args(['--config', 'test'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_multiplatform.py:36*

### test_cli_accepts_target_flag

**Category**: instantiation  
**Description**: Instantiate parse_args: Test that CLI accepts --target flag  
**Confidence**: 0.80  
**Tags**: unittest  

```python
args = parser.parse_args(['--config', 'test', '--target', platform])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_multiplatform.py:32*

### test_cli_accepts_target_flag

**Category**: instantiation  
**Description**: Instantiate parse_args: Test that CLI accepts --target flag  
**Confidence**: 0.80  
**Tags**: unittest  

```python
args = parser.parse_args(['--config', 'test'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_multiplatform.py:36*

### test_cli_accepts_target_flag

**Category**: instantiation  
**Description**: Instantiate parse_args: Test that CLI accepts --target flag  
**Confidence**: 0.80  
**Tags**: unittest  

```python
args = parser.parse_args(['--config', 'test', '--target', platform])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_multiplatform.py:32*

### test_detect_llms_txt_variants

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDetector: Test detection of llms.txt file variants  
**Confidence**: 0.80  
**Tags**: mock  

```python
detector = LlmsTxtDetector('https://hono.dev/docs')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_detector.py:8*

### test_detect_no_llms_txt

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDetector: Test detection when no llms.txt file exists  
**Confidence**: 0.80  
**Tags**: mock  

```python
detector = LlmsTxtDetector('https://example.com/docs')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_detector.py:25*

### test_url_parsing_with_complex_paths

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDetector: Test URL parsing handles non-standard paths correctly  
**Confidence**: 0.80  
**Tags**: mock  

```python
detector = LlmsTxtDetector('https://example.com/docs/v2/guide')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_detector.py:40*

### test_detect_all_variants

**Category**: instantiation  
**Description**: Instantiate LlmsTxtDetector: Test detecting all llms.txt variants  
**Confidence**: 0.80  
**Tags**: mock  

```python
detector = LlmsTxtDetector('https://hono.dev/docs')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_detector.py:58*

### test_detect_from_html_swift_class

**Category**: instantiation  
**Description**: Instantiate BeautifulSoup: Test HTML element with Swift CSS class  
**Expected**: assert lang == 'swift'  
**Confidence**: 0.80  

```python
soup = BeautifulSoup(html, 'html.parser')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_swift_detection.py:48*

### test_detect_from_html_swift_class

**Category**: instantiation  
**Description**: Instantiate find: Test HTML element with Swift CSS class  
**Expected**: assert lang == 'swift'  
**Confidence**: 0.80  

```python
elem = soup.find('code')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_swift_detection.py:49*

### test_adaptor_registration

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test that Weaviate adaptor is registered.  
**Expected**: assert adaptor.PLATFORM == 'weaviate'  
**Confidence**: 0.80  

```python
adaptor = get_adaptor('weaviate')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_weaviate_adaptor.py:19*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test formatting SKILL.md as Weaviate objects.  
**Expected**: assert 'schema' in result  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

adaptor = get_adaptor('weaviate')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_weaviate_adaptor.py:40*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate SkillMetadata: Test formatting SKILL.md as Weaviate objects.  
**Expected**: assert 'schema' in result  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_weaviate_adaptor.py:41*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate format_skill_md: Test formatting SKILL.md as Weaviate objects.  
**Expected**: assert 'schema' in result  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

objects_json = adaptor.format_skill_md(skill_dir, metadata)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_weaviate_adaptor.py:43*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate loads: Test formatting SKILL.md as Weaviate objects.  
**Expected**: assert 'schema' in result  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

result = json.loads(objects_json)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_weaviate_adaptor.py:46*

### test_async_mode_default_false

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test async mode is disabled by default  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_async_scraping.py:40*

### test_async_mode_enabled_from_config

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test async mode can be enabled via config  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_async_scraping.py:58*

### test_async_mode_with_workers

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test async mode works with multiple workers  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Save original working directory'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_async_scraping.py:76*

### test_scrape_page_async_exists

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test scrape_page_async method exists  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Set up test fixtures'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_async_scraping.py:105*

### test_scrape_all_async_exists

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test scrape_all_async method exists  
**Confidence**: 0.80  
**Tags**: unittest  

```python
# Setup
'Set up test fixtures'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_async_scraping.py:122*

### test_scrape_all_routes_to_async_when_enabled

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test scrape_all calls async version when async_mode=True  
**Confidence**: 0.80  
**Tags**: mock, unittest  

```python
# Setup
'Set up test fixtures'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_async_scraping.py:153*

### test_scrape_all_uses_sync_when_async_disabled

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test scrape_all uses sync version when async_mode=False  
**Confidence**: 0.80  
**Tags**: mock, unittest  

```python
# Setup
'Set up test fixtures'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_async_scraping.py:178*

### test_async_dry_run_completes

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test async dry run completes without errors  
**Confidence**: 0.80  
**Tags**: mock, unittest  

```python
# Setup
'Set up test fixtures'
self.original_cwd = os.getcwd()

converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_async_scraping.py:218*

### test_auto_mode_with_api_key

**Category**: instantiation  
**Description**: Instantiate GuideEnhancer: Test auto mode detects API when key present and library available  
**Confidence**: 0.80  
**Tags**: mock  

```python
enhancer = GuideEnhancer(mode='auto')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_guide_enhancer.py:37*

### test_auto_mode_without_api_key

**Category**: instantiation  
**Description**: Instantiate GuideEnhancer: Test auto mode falls back to LOCAL when no API key  
**Confidence**: 0.80  
**Tags**: mock  

```python
enhancer = GuideEnhancer(mode='auto')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_guide_enhancer.py:47*

### test_explicit_api_mode

**Category**: instantiation  
**Description**: Instantiate GuideEnhancer: Test explicit API mode  
**Expected**: assert enhancer.mode in ['api', 'none']  
**Confidence**: 0.80  

```python
enhancer = GuideEnhancer(mode='api')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_guide_enhancer.py:52*

### test_explicit_local_mode

**Category**: instantiation  
**Description**: Instantiate GuideEnhancer: Test explicit LOCAL mode  
**Expected**: assert enhancer.mode in ['local', 'none']  
**Confidence**: 0.80  

```python
enhancer = GuideEnhancer(mode='local')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_guide_enhancer.py:57*

### test_explicit_none_mode

**Category**: instantiation  
**Description**: Instantiate GuideEnhancer: Test explicit none mode  
**Expected**: assert enhancer.mode == 'none'  
**Confidence**: 0.80  

```python
enhancer = GuideEnhancer(mode='none')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_guide_enhancer.py:62*

### test_init_creates_config_dir

**Category**: instantiation  
**Description**: Instantiate SourceManager: Test that initialization creates config directory.  
**Expected**: assert config_dir.exists()  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

manager = SourceManager(config_dir=str(config_dir))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_source_manager.py:34*

### test_init_creates_registry_file

**Category**: instantiation  
**Description**: Instantiate SourceManager: Test that initialization creates registry file.  
**Expected**: assert registry_file.exists()  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: temp_config_dir

_manager = SourceManager(config_dir=str(temp_config_dir))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_source_manager.py:41*

### test_init_preserves_existing_registry

**Category**: instantiation  
**Description**: Instantiate SourceManager: Test that initialization doesn't overwrite existing registry.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: temp_config_dir

_manager = SourceManager(config_dir=str(temp_config_dir))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_source_manager.py:64*

### test_add_source_minimal

**Category**: instantiation  
**Description**: Instantiate add_source: Test adding source with minimal parameters.  
**Expected**: assert source['name'] == 'team'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: source_manager

source = source_manager.add_source(name='team', git_url='https://github.com/myorg/configs.git')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_source_manager.py:84*

### test_add_source_full_parameters

**Category**: instantiation  
**Description**: Instantiate add_source: Test adding source with all parameters.  
**Expected**: assert source['name'] == 'company'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: source_manager

source = source_manager.add_source(name='company', git_url='https://gitlab.company.com/platform/configs.git', source_type='gitlab', token_env='CUSTOM_TOKEN', branch='develop', priority=1, enabled=False)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_source_manager.py:100*

### test_add_source_normalizes_name

**Category**: instantiation  
**Description**: Instantiate add_source: Test that source names are normalized to lowercase.  
**Expected**: assert source['name'] == 'myteam'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: source_manager

source = source_manager.add_source(name='MyTeam', git_url='https://github.com/org/repo.git')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_source_manager.py:119*

### test_add_source_valid_name_with_hyphens

**Category**: instantiation  
**Description**: Instantiate add_source: Test that source names with hyphens are allowed.  
**Expected**: assert source['name'] == 'team-alpha'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: source_manager

source = source_manager.add_source(name='team-alpha', git_url='https://github.com/org/repo.git')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_source_manager.py:137*

### test_add_source_valid_name_with_underscores

**Category**: instantiation  
**Description**: Instantiate add_source: Test that source names with underscores are allowed.  
**Expected**: assert source['name'] == 'team_alpha'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: source_manager

source = source_manager.add_source(name='team_alpha', git_url='https://github.com/org/repo.git')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_source_manager.py:145*

### test_complete_workflow_with_weaviate

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test: package → upload to Weaviate → query → verify.  
**Expected**: assert package_path.exists(), 'Package not created'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_skill_dir, tmp_path

adaptor = get_adaptor('weaviate')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration_adaptors.py:149*

### test_complete_workflow_with_weaviate

**Category**: instantiation  
**Description**: Instantiate package: Test: package → upload to Weaviate → query → verify.  
**Expected**: assert package_path.exists(), 'Package not created'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_skill_dir, tmp_path

package_path = adaptor.package(sample_skill_dir, tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration_adaptors.py:151*

### test_complete_workflow_with_weaviate

**Category**: instantiation  
**Description**: Instantiate Client: Test: package → upload to Weaviate → query → verify.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_skill_dir, tmp_path

client = weaviate.Client('http://localhost:8080')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration_adaptors.py:143*

### test_weaviate_metadata_preservation

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test that metadata is correctly stored and retrieved.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_skill_dir, tmp_path

adaptor = get_adaptor('weaviate')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration_adaptors.py:229*

### test_weaviate_metadata_preservation

**Category**: instantiation  
**Description**: Instantiate package: Test that metadata is correctly stored and retrieved.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_skill_dir, tmp_path

package_path = adaptor.package(sample_skill_dir, tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration_adaptors.py:237*

### test_weaviate_metadata_preservation

**Category**: instantiation  
**Description**: Instantiate Client: Test that metadata is correctly stored and retrieved.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_skill_dir, tmp_path

client = weaviate.Client('http://localhost:8080')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration_adaptors.py:223*

### test_complete_workflow_with_chroma

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test: package → upload to Chroma → query → verify.  
**Expected**: assert package_path.exists(), 'Package not created'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_skill_dir, tmp_path

adaptor = get_adaptor('chroma')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration_adaptors.py:299*

### test_complete_workflow_with_chroma

**Category**: instantiation  
**Description**: Instantiate package: Test: package → upload to Chroma → query → verify.  
**Expected**: assert package_path.exists(), 'Package not created'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_skill_dir, tmp_path

package_path = adaptor.package(sample_skill_dir, tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_integration_adaptors.py:303*

### test_cache_init

**Category**: instantiation  
**Description**: Instantiate EmbeddingCache: Test cache initialization.  
**Expected**: assert cache.size() == 0  
**Confidence**: 0.80  

```python
cache = EmbeddingCache(':memory:')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding.py:32*

### test_cache_set_get

**Category**: instantiation  
**Description**: Instantiate EmbeddingCache: Test cache set and get.  
**Expected**: assert retrieved == embedding  
**Confidence**: 0.80  

```python
cache = EmbeddingCache(':memory:')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding.py:38*

### test_cache_set_get

**Category**: instantiation  
**Description**: Instantiate get: Test cache set and get.  
**Expected**: assert retrieved == embedding  
**Confidence**: 0.80  

```python
retrieved = cache.get('hash123')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding.py:43*

### test_cache_has

**Category**: instantiation  
**Description**: Instantiate EmbeddingCache: Test cache has method.  
**Expected**: assert cache.has('hash123') is True  
**Confidence**: 0.80  

```python
cache = EmbeddingCache(':memory:')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding.py:49*

### test_validate_existing_unified_configs

**Category**: instantiation  
**Description**: Instantiate validate_config: Test that all existing unified configs are valid  
**Confidence**: 0.80  

```python
validator = validate_config(str(config_path))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\src\skill_seekers\cli\test_unified_simple.py:35*

### test_backward_compatibility

**Category**: instantiation  
**Description**: Instantiate validate_config: Test that legacy configs still work  
**Confidence**: 0.80  

```python
validator = validate_config(str(config_path))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\src\skill_seekers\cli\test_unified_simple.py:52*

### test_create_temp_unified_config

**Category**: instantiation  
**Description**: Instantiate validate_config: Test creating a unified config from scratch  
**Confidence**: 0.80  

```python
validator = validate_config(config_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\src\skill_seekers\cli\test_unified_simple.py:85*

### test_mixed_source_types

**Category**: instantiation  
**Description**: Instantiate validate_config: Test config with documentation, GitHub, and PDF sources  
**Confidence**: 0.80  

```python
validator = validate_config(config_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\src\skill_seekers\cli\test_unified_simple.py:114*

### test_config_validation_errors

**Category**: instantiation  
**Description**: Instantiate validate_config: Test that invalid configs are rejected  
**Confidence**: 0.80  

```python
_validator = validate_config(config_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\src\skill_seekers\cli\test_unified_simple.py:145*

### test_vector_databases

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test all 4 vector database adaptors.  
**Confidence**: 0.80  

```python
adaptor = get_adaptor(target)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\test_week2_features.py:31*

### test_vector_databases

**Category**: instantiation  
**Description**: Instantiate package: Test all 4 vector database adaptors.  
**Confidence**: 0.80  

```python
package_path = adaptor.package(skill_dir, Path(tmpdir))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\test_week2_features.py:32*

### test_streaming

**Category**: instantiation  
**Description**: Instantiate StreamingIngester: Test streaming ingestion.  
**Confidence**: 0.80  

```python
ingester = StreamingIngester(chunk_size=1000, chunk_overlap=100)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\test_week2_features.py:50*

### test_streaming

**Category**: instantiation  
**Description**: Instantiate list: Test streaming ingestion.  
**Confidence**: 0.80  

```python
chunks = list(ingester.chunk_document(large_content, {'source': 'test'}))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\test_week2_features.py:52*

### test_incremental

**Category**: instantiation  
**Description**: Instantiate IncrementalUpdater: Test incremental updates.  
**Confidence**: 0.80  

```python
updater = IncrementalUpdater(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\test_week2_features.py:87*

### test_incremental

**Category**: instantiation  
**Description**: Instantiate IncrementalUpdater: Test incremental updates.  
**Confidence**: 0.80  

```python
updater2 = IncrementalUpdater(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\test_week2_features.py:99*

### test_multilang

**Category**: instantiation  
**Description**: Instantiate detect: Test multi-language support.  
**Confidence**: 0.80  

```python
en_detected = detector.detect(en_text)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\test_week2_features.py:130*

### test_multilang

**Category**: instantiation  
**Description**: Instantiate detect: Test multi-language support.  
**Confidence**: 0.80  

```python
es_detected = detector.detect(es_text)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\test_week2_features.py:131*

### test_embeddings

**Category**: instantiation  
**Description**: Instantiate EmbeddingConfig: Test embedding pipeline.  
**Confidence**: 0.80  

```python
config = EmbeddingConfig(provider='local', model='test-model', dimension=64, batch_size=10, cache_dir=Path(tmpdir))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\test_week2_features.py:166*

### test_embeddings

**Category**: instantiation  
**Description**: Instantiate EmbeddingPipeline: Test embedding pipeline.  
**Confidence**: 0.80  

```python
pipeline = EmbeddingPipeline(config)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\test_week2_features.py:174*

### test_adaptor_registration

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test that Haystack adaptor is registered.  
**Expected**: assert adaptor.PLATFORM == 'haystack'  
**Confidence**: 0.80  

```python
adaptor = get_adaptor('haystack')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_haystack_adaptor.py:19*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test formatting SKILL.md as Haystack Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

adaptor = get_adaptor('haystack')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_haystack_adaptor.py:40*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate SkillMetadata: Test formatting SKILL.md as Haystack Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_haystack_adaptor.py:41*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate format_skill_md: Test formatting SKILL.md as Haystack Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

documents_json = adaptor.format_skill_md(skill_dir, metadata)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_haystack_adaptor.py:43*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate loads: Test formatting SKILL.md as Haystack Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

documents = json.loads(documents_json)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_haystack_adaptor.py:46*

### test_parse_markdown_sections

**Category**: instantiation  
**Description**: Instantiate LlmsTxtParser: Test parsing markdown into page sections  
**Expected**: assert len(pages) >= 2  
**Confidence**: 0.80  

```python
parser = LlmsTxtParser(sample_content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_llms_txt_parser.py:27*

### test_server_initialization

**Category**: instantiation  
**Description**: Instantiate Server: Test server initializes correctly  
**Expected**: self.assertEqual(app.name, 'test-skill-seeker')  
**Confidence**: 0.80  
**Tags**: unittest  

```python
app = mcp.server.Server('test-skill-seeker')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_server.py:61*

### test_server_initialization

**Category**: instantiation  
**Description**: Instantiate Server: Test server initializes correctly  
**Expected**: self.assertEqual(app.name, 'test-skill-seeker')  
**Confidence**: 0.80  
**Tags**: unittest  

```python
app = mcp.server.Server('test-skill-seeker')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_server.py:61*

### test_build_agent_command_claude

**Category**: instantiation  
**Description**: Instantiate _make_skill_dir: Test Claude Code command building.  
**Expected**: assert cmd_parts[0] == 'claude'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

skill_dir = _make_skill_dir(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_enhance_skill_local.py:34*

### test_build_agent_command_claude

**Category**: instantiation  
**Description**: Instantiate LocalSkillEnhancer: Test Claude Code command building.  
**Expected**: assert cmd_parts[0] == 'claude'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

enhancer = LocalSkillEnhancer(skill_dir, agent='claude')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_enhance_skill_local.py:35*

### test_build_agent_command_claude

**Category**: instantiation  
**Description**: Instantiate str: Test Claude Code command building.  
**Expected**: assert cmd_parts[0] == 'claude'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

prompt_file = str(tmp_path / 'prompt.txt')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_enhance_skill_local.py:36*

### test_build_agent_command_claude

**Category**: instantiation  
**Description**: Instantiate _build_agent_command: Test Claude Code command building.  
**Expected**: assert cmd_parts[0] == 'claude'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

cmd_parts, uses_file = enhancer._build_agent_command(prompt_file, True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_enhance_skill_local.py:38*

### test_build_agent_command_codex

**Category**: instantiation  
**Description**: Instantiate _make_skill_dir: Test Codex CLI command building.  
**Expected**: assert cmd_parts[0] == 'codex'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

skill_dir = _make_skill_dir(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_enhance_skill_local.py:47*

### test_build_agent_command_codex

**Category**: instantiation  
**Description**: Instantiate LocalSkillEnhancer: Test Codex CLI command building.  
**Expected**: assert cmd_parts[0] == 'codex'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

enhancer = LocalSkillEnhancer(skill_dir, agent='codex')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_enhance_skill_local.py:48*

### test_build_agent_command_codex

**Category**: instantiation  
**Description**: Instantiate str: Test Codex CLI command building.  
**Expected**: assert cmd_parts[0] == 'codex'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

prompt_file = str(tmp_path / 'prompt.txt')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_enhance_skill_local.py:49*

### test_langchain_no_chunking_default

**Category**: instantiation  
**Description**: Instantiate create_test_skill: Test that LangChain doesn't chunk by default.  
**Expected**: assert len(data) == 2, f'Expected 2 docs, got {len(data)}'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

skill_dir = create_test_skill(tmp_path, large_doc=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_chunking_integration.py:61*

### test_langchain_no_chunking_default

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test that LangChain doesn't chunk by default.  
**Expected**: assert len(data) == 2, f'Expected 2 docs, got {len(data)}'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

adaptor = get_adaptor('langchain')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_chunking_integration.py:63*

### test_analysis_result_basic

**Category**: instantiation  
**Description**: Instantiate AnalysisResult: Test basic AnalysisResult creation.  
**Expected**: assert result.code_analysis == {'files': []}  
**Confidence**: 0.80  

```python
result = AnalysisResult(code_analysis={'files': []}, source_type='local', analysis_depth='basic')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified_analyzer.py:33*

### test_analysis_result_with_github

**Category**: instantiation  
**Description**: Instantiate AnalysisResult: Test AnalysisResult with GitHub data.  
**Expected**: assert result.github_docs is not None  
**Confidence**: 0.80  

```python
result = AnalysisResult(code_analysis={'files': []}, github_docs={'readme': '# README'}, github_insights={'metadata': {'stars': 1234}}, source_type='github', analysis_depth='c3x')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified_analyzer.py:44*

### test_basic_analysis_local

**Category**: instantiation  
**Description**: Instantiate analyze: Test basic analysis on local directory.  
**Expected**: assert result.source_type == 'local'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

result = analyzer.analyze(source=str(tmp_path), depth='basic')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified_analyzer.py:92*

### test_list_files

**Category**: instantiation  
**Description**: Instantiate list_files: Test file listing.  
**Expected**: assert len(files) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

files = analyzer.list_files(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified_analyzer.py:107*

### test_get_directory_structure

**Category**: instantiation  
**Description**: Instantiate get_directory_structure: Test directory structure extraction.  
**Expected**: assert structure['type'] == 'directory'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

structure = analyzer.get_directory_structure(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified_analyzer.py:123*

### test_extract_imports_python

**Category**: instantiation  
**Description**: Instantiate extract_imports: Test Python import extraction.  
**Expected**: assert '.py' in imports  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

imports = analyzer.extract_imports(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified_analyzer.py:146*

### test_extract_imports_javascript

**Category**: instantiation  
**Description**: Instantiate extract_imports: Test JavaScript import extraction.  
**Expected**: assert '.js' in imports  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

imports = analyzer.extract_imports(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified_analyzer.py:164*

### test_find_entry_points

**Category**: instantiation  
**Description**: Instantiate find_entry_points: Test entry point detection.  
**Expected**: assert 'main.py' in entry_points  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

entry_points = analyzer.find_entry_points(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified_analyzer.py:177*

### test_compute_statistics

**Category**: instantiation  
**Description**: Instantiate compute_statistics: Test statistics computation.  
**Expected**: assert stats['total_files'] == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

stats = analyzer.compute_statistics(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified_analyzer.py:190*

### test_c3x_analysis_local

**Category**: instantiation  
**Description**: Instantiate analyze: Test C3.x analysis on local directory with actual components.  
**Expected**: assert result.source_type == 'local'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

result = analyzer.analyze(source=str(tmp_path), depth='c3x')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_unified_analyzer.py:209*

### test_detect_from_html_with_css_class

**Category**: instantiation  
**Description**: Instantiate BeautifulSoup: Test HTML element with CSS class  
**Expected**: assert lang == 'python'  
**Confidence**: 0.80  

```python
soup = BeautifulSoup(html, 'html.parser')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_language_detector.py:83*

### test_detect_from_html_with_css_class

**Category**: instantiation  
**Description**: Instantiate find: Test HTML element with CSS class  
**Expected**: assert lang == 'python'  
**Confidence**: 0.80  

```python
elem = soup.find('code')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_language_detector.py:84*

### test_detect_from_html_with_css_class

**Category**: instantiation  
**Description**: Instantiate detect_from_html: Test HTML element with CSS class  
**Expected**: assert lang == 'python'  
**Confidence**: 0.80  

```python
lang, confidence = detector.detect_from_html(elem, 'print("hello")')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_language_detector.py:86*

### test_detect_from_html_with_parent_class

**Category**: instantiation  
**Description**: Instantiate BeautifulSoup: Test parent <pre> element with CSS class  
**Expected**: assert lang == 'java'  
**Confidence**: 0.80  

```python
soup = BeautifulSoup(html, 'html.parser')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_language_detector.py:96*

### test_adaptor_registration

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test that FAISS adaptor is registered.  
**Expected**: assert adaptor.PLATFORM == 'faiss'  
**Confidence**: 0.80  

```python
adaptor = get_adaptor('faiss')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_faiss_adaptor.py:19*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test formatting SKILL.md as FAISS index data.  
**Expected**: assert 'documents' in index_data  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

adaptor = get_adaptor('faiss')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_faiss_adaptor.py:40*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate SkillMetadata: Test formatting SKILL.md as FAISS index data.  
**Expected**: assert 'documents' in index_data  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_faiss_adaptor.py:41*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate format_skill_md: Test formatting SKILL.md as FAISS index data.  
**Expected**: assert 'documents' in index_data  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

index_json = adaptor.format_skill_md(skill_dir, metadata)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_faiss_adaptor.py:43*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate loads: Test formatting SKILL.md as FAISS index data.  
**Expected**: assert 'documents' in index_data  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

index_data = json.loads(index_json)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_faiss_adaptor.py:46*

### test_local_provider_generation

**Category**: instantiation  
**Description**: Instantiate LocalEmbeddingProvider: Test local embedding provider.  
**Expected**: assert len(embeddings) == 2  
**Confidence**: 0.80  

```python
provider = LocalEmbeddingProvider(dimension=128)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_embedding_pipeline.py:35*

### test_categorize_issues_basic

**Category**: instantiation  
**Description**: Instantiate categorize_issues_by_topic: Test basic issue categorization.  
**Expected**: assert 'oauth' in categorized  
**Confidence**: 0.80  

```python
categorized = categorize_issues_by_topic(problems, solutions, topics)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_merge_sources_github.py:54*

### test_categorize_issues_keyword_matching

**Category**: instantiation  
**Description**: Instantiate categorize_issues_by_topic: Test keyword matching in titles and labels.  
**Expected**: assert 'database' in categorized or 'other' in categorized  
**Confidence**: 0.80  

```python
categorized = categorize_issues_by_topic(problems, solutions, topics)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_merge_sources_github.py:76*

### test_categorize_issues_multi_keyword_topic

**Category**: instantiation  
**Description**: Instantiate categorize_issues_by_topic: Test topics with multiple keywords.  
**Expected**: assert 'async api' in categorized  
**Confidence**: 0.80  

```python
categorized = categorize_issues_by_topic(problems, solutions, topics)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_merge_sources_github.py:96*

### test_create_headers_no_token

**Category**: instantiation  
**Description**: Instantiate create_github_headers: Test header creation without token.  
**Expected**: assert headers == {}  
**Confidence**: 0.80  

```python
headers = create_github_headers(None)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rate_limit_handler.py:25*

### test_create_headers_with_token

**Category**: instantiation  
**Description**: Instantiate create_github_headers: Test header creation with token.  
**Expected**: assert headers == {'Authorization': 'token ghp_test123'}  
**Confidence**: 0.80  

```python
headers = create_github_headers(token)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rate_limit_handler.py:31*

### test_init_without_token

**Category**: instantiation  
**Description**: Instantiate RateLimitHandler: Test initialization without token.  
**Expected**: assert handler.token is None  
**Confidence**: 0.80  

```python
handler = RateLimitHandler(token=None, interactive=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rate_limit_handler.py:36*

### test_init_with_token

**Category**: instantiation  
**Description**: Instantiate RateLimitHandler: Test initialization with token.  
**Expected**: assert handler.token == 'ghp_test'  
**Confidence**: 0.80  

```python
handler = RateLimitHandler(token='ghp_test', interactive=False)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rate_limit_handler.py:43*

### test_init_with_config_strategy

**Category**: instantiation  
**Description**: Instantiate RateLimitHandler: Test initialization pulls strategy from config.  
**Expected**: assert handler.strategy == 'wait'  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_get_config

handler = RateLimitHandler(token='ghp_test', interactive=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rate_limit_handler.py:62*

### test_extract_rate_limit_info

**Category**: instantiation  
**Description**: Instantiate int: Test extracting rate limit info from response headers.  
**Expected**: assert info['limit'] == 5000  
**Confidence**: 0.80  
**Tags**: mock  

```python
reset_time = int((datetime.now() + timedelta(minutes=30)).timestamp())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rate_limit_handler.py:73*

### test_extract_rate_limit_info

**Category**: instantiation  
**Description**: Instantiate extract_rate_limit_info: Test extracting rate limit info from response headers.  
**Expected**: assert info['limit'] == 5000  
**Confidence**: 0.80  
**Tags**: mock  

```python
info = handler.extract_rate_limit_info(mock_response)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rate_limit_handler.py:80*

### test_check_upfront_no_token_declined

**Category**: instantiation  
**Description**: Instantiate RateLimitHandler: Test upfront check with no token, user declines.  
**Expected**: assert result is False  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_input

handler = RateLimitHandler(token=None, interactive=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_rate_limit_handler.py:90*

### test_default_skip_llms_txt_is_false

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test that skip_llms_txt defaults to False when not specified.  
**Expected**: self.assertFalse(converter.skip_llms_txt)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_skip_llms_txt.py:29*

### test_skip_llms_txt_can_be_set_true

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test that skip_llms_txt can be explicitly set to True.  
**Expected**: self.assertTrue(converter.skip_llms_txt)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_skip_llms_txt.py:41*

### test_skip_llms_txt_can_be_set_false

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test that skip_llms_txt can be explicitly set to False.  
**Expected**: self.assertFalse(converter.skip_llms_txt)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
converter = DocToSkillConverter(config, dry_run=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_skip_llms_txt.py:53*

### test_llms_txt_tried_when_not_skipped

**Category**: instantiation  
**Description**: Instantiate DocToSkillConverter: Test that _try_llms_txt is called when skip_llms_txt is False.  
**Confidence**: 0.80  
**Tags**: mock, unittest  

```python
converter = DocToSkillConverter(config, dry_run=False)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_skip_llms_txt.py:73*

### test_github_url_to_basic_analysis

**Category**: instantiation  
**Description**: Instantiate CodeStream: Test complete pipeline: GitHub URL → Basic analysis → Merged output

This tests the fast path (1-2 minutes) without C3.x analysis.  
**Expected**: assert result.source_type == 'github'  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_fetcher_class, tmp_path

code_stream = CodeStream(directory=tmp_path, files=[tmp_path / 'main.py', tmp_path / 'utils.js'])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_e2e_three_stream_pipeline.py:57*

### test_github_url_to_basic_analysis

**Category**: instantiation  
**Description**: Instantiate DocsStream: Test complete pipeline: GitHub URL → Basic analysis → Merged output

This tests the fast path (1-2 minutes) without C3.x analysis.  
**Expected**: assert result.source_type == 'github'  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_fetcher_class, tmp_path

docs_stream = DocsStream(readme='# Test Project\n\nA simple test project for demonstrating the three-stream architecture.\n\n## Installation\n\n```bash\npip install test-project\n```\n\n## Quick Start\n\n```python\nfrom test_project import hello\nhello()\n```\n', contributing='# Contributing\n\nPull requests welcome!', docs_files=[{'path': 'docs/guide.md', 'content': '# User Guide\n\nHow to use this project.'}])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_e2e_three_stream_pipeline.py:60*

### test_github_url_to_basic_analysis

**Category**: instantiation  
**Description**: Instantiate InsightsStream: Test complete pipeline: GitHub URL → Basic analysis → Merged output

This tests the fast path (1-2 minutes) without C3.x analysis.  
**Expected**: assert result.source_type == 'github'  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_fetcher_class, tmp_path

insights_stream = InsightsStream(metadata={'stars': 1234, 'forks': 56, 'language': 'Python', 'description': 'A test project'}, common_problems=[{'title': 'Installation fails on Windows', 'number': 42, 'state': 'open', 'comments': 15, 'labels': ['bug', 'windows']}, {'title': 'Import error with Python 3.6', 'number': 38, 'state': 'open', 'comments': 10, 'labels': ['bug', 'python']}], known_solutions=[{'title': 'Fixed: Module not found', 'number': 35, 'state': 'closed', 'comments': 8, 'labels': ['bug']}], top_labels=[{'label': 'bug', 'count': 25}, {'label': 'enhancement', 'count': 15}, {'label': 'documentation', 'count': 10}])
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_e2e_three_stream_pipeline.py:83*

### test_github_url_to_basic_analysis

**Category**: instantiation  
**Description**: Instantiate ThreeStreamData: Test complete pipeline: GitHub URL → Basic analysis → Merged output

This tests the fast path (1-2 minutes) without C3.x analysis.  
**Expected**: assert result.source_type == 'github'  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_fetcher_class, tmp_path

three_streams = ThreeStreamData(code_stream, docs_stream, insights_stream)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_e2e_three_stream_pipeline.py:121*

### test_github_url_to_basic_analysis

**Category**: instantiation  
**Description**: Instantiate analyze: Test complete pipeline: GitHub URL → Basic analysis → Merged output

This tests the fast path (1-2 minutes) without C3.x analysis.  
**Expected**: assert result.source_type == 'github'  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_fetcher_class, tmp_path

result = analyzer.analyze(source='https://github.com/test/project', depth='basic', fetch_github_metadata=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_e2e_three_stream_pipeline.py:126*

### test_get_preset

**Category**: instantiation  
**Description**: Instantiate get_preset: Test PresetManager.get_preset().  
**Expected**: assert quick is not None  
**Confidence**: 0.80  

```python
quick = PresetManager.get_preset('quick')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_preset_system.py:84*

### test_get_preset

**Category**: instantiation  
**Description**: Instantiate get_preset: Test PresetManager.get_preset().  
**Expected**: assert standard is not None  
**Confidence**: 0.80  

```python
standard = PresetManager.get_preset('STANDARD')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_preset_system.py:90*

### test_get_preset_invalid

**Category**: instantiation  
**Description**: Instantiate get_preset: Test PresetManager.get_preset() with invalid name.  
**Expected**: assert invalid is None  
**Confidence**: 0.80  

```python
invalid = PresetManager.get_preset('nonexistent')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_preset_system.py:96*

### test_apply_preset_quick

**Category**: instantiation  
**Description**: Instantiate apply_preset: Test applying quick preset.  
**Expected**: assert updated['depth'] == 'surface'  
**Confidence**: 0.80  

```python
updated = PresetManager.apply_preset('quick', args)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_preset_system.py:130*

### test_apply_preset_standard

**Category**: instantiation  
**Description**: Instantiate apply_preset: Test applying standard preset.  
**Expected**: assert updated['depth'] == 'deep'  
**Confidence**: 0.80  

```python
updated = PresetManager.apply_preset('standard', args)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_preset_system.py:144*

### test_apply_preset_comprehensive

**Category**: instantiation  
**Description**: Instantiate apply_preset: Test applying comprehensive preset.  
**Expected**: assert updated['depth'] == 'full'  
**Confidence**: 0.80  

```python
updated = PresetManager.apply_preset('comprehensive', args)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_preset_system.py:158*

### test_cli_overrides_preset

**Category**: instantiation  
**Description**: Instantiate apply_preset: Test that CLI args override preset defaults.  
**Expected**: assert updated['enhance_level'] == 2  
**Confidence**: 0.80  

```python
updated = PresetManager.apply_preset('quick', args)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_preset_system.py:179*

### test_apply_preset_preserves_args

**Category**: instantiation  
**Description**: Instantiate apply_preset: Test that apply_preset preserves existing args.  
**Expected**: assert updated['directory'] == '/tmp/test'  
**Confidence**: 0.80  

```python
updated = PresetManager.apply_preset('standard', args)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_preset_system.py:195*

### test_check_deprecated_flags_quick

**Category**: instantiation  
**Description**: Instantiate Namespace: Test deprecation warning for --quick flag.  
**Expected**: assert 'DEPRECATED' in captured.out  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: capsys

args = argparse.Namespace(quick=True, comprehensive=False, depth=None, ai_mode='auto')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_preset_system.py:218*

### test_completeness_full

**Category**: instantiation  
**Description**: Instantiate QualityAnalyzer: Test completeness analysis with complete skill.  
**Expected**: assert score >= 70  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: complete_skill_dir

analyzer = QualityAnalyzer(complete_skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_metrics.py:62*

### test_completeness_minimal

**Category**: instantiation  
**Description**: Instantiate QualityAnalyzer: Test completeness analysis with minimal skill.  
**Expected**: assert score < 80  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: minimal_skill_dir

analyzer = QualityAnalyzer(minimal_skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_metrics.py:70*

### test_accuracy_clean

**Category**: instantiation  
**Description**: Instantiate QualityAnalyzer: Test accuracy analysis with clean content.  
**Confidence**: 0.80  

```python
analyzer = QualityAnalyzer(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_metrics.py:84*

### test_accuracy_with_todos

**Category**: instantiation  
**Description**: Instantiate QualityAnalyzer: Test accuracy detects TODO markers.  
**Confidence**: 0.80  

```python
analyzer = QualityAnalyzer(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_metrics.py:98*

### test_accuracy_with_placeholder

**Category**: instantiation  
**Description**: Instantiate QualityAnalyzer: Test accuracy detects placeholder text.  
**Confidence**: 0.80  

```python
analyzer = QualityAnalyzer(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_metrics.py:112*

### test_coverage_high

**Category**: instantiation  
**Description**: Instantiate QualityAnalyzer: Test coverage analysis with good coverage.  
**Expected**: assert score >= 60  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: complete_skill_dir

analyzer = QualityAnalyzer(complete_skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_metrics.py:120*

### test_coverage_low

**Category**: instantiation  
**Description**: Instantiate QualityAnalyzer: Test coverage analysis with low coverage.  
**Confidence**: 0.80  

```python
analyzer = QualityAnalyzer(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_metrics.py:134*

### test_health_good

**Category**: instantiation  
**Description**: Instantiate QualityAnalyzer: Test health analysis with healthy skill.  
**Confidence**: 0.80  

```python
analyzer = QualityAnalyzer(skill_dir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_quality_metrics.py:151*

### run_bootstrap

**Category**: instantiation  
**Description**: Instantiate run: Execute bootstrap script and return result  
**Confidence**: 0.80  
**Tags**: pytest  

```python
# Setup
# Fixtures: project_root

result = subprocess.run(['bash', str(script)], cwd=project_root, capture_output=True, text=True, timeout=timeout)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_bootstrap_skill_e2e.py:45*

### test_bootstrap_validates_yaml_frontmatter

**Category**: instantiation  
**Description**: Instantiate split: Verify generated SKILL.md has valid YAML frontmatter  
**Expected**: assert closing_found, 'Missing frontmatter closing delimiter'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: run_bootstrap, output_skill_dir

lines = content.split('\n')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_bootstrap_skill_e2e.py:96*

### test_bootstrap_output_line_count

**Category**: instantiation  
**Description**: Instantiate len: Verify output SKILL.md has reasonable line count  
**Expected**: assert line_count > 100, f'SKILL.md too short: {line_count} lines'  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: run_bootstrap, output_skill_dir

line_count = len((output_skill_dir / 'SKILL.md').read_text().splitlines())
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_bootstrap_skill_e2e.py:114*

### test_skill_installable_in_venv

**Category**: instantiation  
**Description**: Instantiate run: Test skill is installable in clean virtual environment  
**Expected**: assert result.returncode == 0, f'Install failed: {result.stderr}'  
**Confidence**: 0.80  
**Tags**: pytest  

```python
# Setup
# Fixtures: run_bootstrap, output_skill_dir, tmp_path

result = subprocess.run([str(pip_path), 'install', '-e', '.'], cwd=output_skill_dir.parent.parent, capture_output=True, text=True, timeout=120)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_bootstrap_skill_e2e.py:134*

### test_skill_packageable_with_adaptors

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Verify bootstrap output works with all platform adaptors  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: run_bootstrap, output_skill_dir, tmp_path

adaptor = get_adaptor('claude')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_bootstrap_skill_e2e.py:153*

### test_skill_packageable_with_adaptors

**Category**: instantiation  
**Description**: Instantiate package: Verify bootstrap output works with all platform adaptors  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: run_bootstrap, output_skill_dir, tmp_path

package_path = adaptor.package(skill_dir=output_skill_dir, output_path=tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_bootstrap_skill_e2e.py:157*

### test_health_check_endpoint

**Category**: instantiation  
**Description**: Instantiate get: Test that health check endpoint returns correct response.  
**Confidence**: 0.80  

```python
response = client.get('/health')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_server_fastmcp_http.py:64*

### test_codebase_analysis_enabled_by_default

**Category**: instantiation  
**Description**: Instantiate join: Test that enable_codebase_analysis defaults to True.  
**Expected**: assert github_source.get('enable_codebase_analysis', True)  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_config, temp_dir

config_path = os.path.join(temp_dir, 'config.json')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_c3_integration.py:149*

### test_codebase_analysis_enabled_by_default

**Category**: instantiation  
**Description**: Instantiate UnifiedScraper: Test that enable_codebase_analysis defaults to True.  
**Expected**: assert github_source.get('enable_codebase_analysis', True)  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_config, temp_dir

scraper = UnifiedScraper(config_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_c3_integration.py:154*

### test_skip_codebase_analysis_flag

**Category**: instantiation  
**Description**: Instantiate join: Test --skip-codebase-analysis CLI flag disables analysis.  
**Expected**: assert not github_source['enable_codebase_analysis']  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_config, temp_dir

config_path = os.path.join(temp_dir, 'config.json')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_c3_integration.py:163*

### test_skip_codebase_analysis_flag

**Category**: instantiation  
**Description**: Instantiate UnifiedScraper: Test --skip-codebase-analysis CLI flag disables analysis.  
**Expected**: assert not github_source['enable_codebase_analysis']  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_config, temp_dir

scraper = UnifiedScraper(config_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_c3_integration.py:168*

### test_adaptor_registration

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test that Chroma adaptor is registered.  
**Expected**: assert adaptor.PLATFORM == 'chroma'  
**Confidence**: 0.80  

```python
adaptor = get_adaptor('chroma')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_chroma_adaptor.py:19*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test formatting SKILL.md as Chroma collection data.  
**Expected**: assert 'documents' in collection  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

adaptor = get_adaptor('chroma')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_chroma_adaptor.py:40*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate SkillMetadata: Test formatting SKILL.md as Chroma collection data.  
**Expected**: assert 'documents' in collection  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_chroma_adaptor.py:41*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate format_skill_md: Test formatting SKILL.md as Chroma collection data.  
**Expected**: assert 'documents' in collection  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

collection_json = adaptor.format_skill_md(skill_dir, metadata)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_chroma_adaptor.py:43*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate loads: Test formatting SKILL.md as Chroma collection data.  
**Expected**: assert 'documents' in collection  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

collection = json.loads(collection_json)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_chroma_adaptor.py:46*

### test_init_with_custom_cache_dir

**Category**: instantiation  
**Description**: Instantiate GitConfigRepo: Test initialization with custom cache directory.  
**Expected**: assert repo.cache_dir == temp_cache_dir  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: temp_cache_dir

repo = GitConfigRepo(cache_dir=str(temp_cache_dir))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_repo.py:35*

### test_inject_token_https

**Category**: instantiation  
**Description**: Instantiate inject_token: Test token injection into HTTPS URL.  
**Expected**: assert result == 'https://ghp_testtoken123@github.com/org/repo.git'  
**Confidence**: 0.80  

```python
result = GitConfigRepo.inject_token(url, token)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_repo.py:101*

### test_inject_token_ssh_to_https

**Category**: instantiation  
**Description**: Instantiate inject_token: Test SSH URL conversion to HTTPS with token.  
**Expected**: assert result == 'https://ghp_testtoken123@github.com/org/repo.git'  
**Confidence**: 0.80  

```python
result = GitConfigRepo.inject_token(url, token)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_repo.py:109*

### test_inject_token_with_port

**Category**: instantiation  
**Description**: Instantiate inject_token: Test token injection with custom port.  
**Expected**: assert result == 'https://token123@gitlab.example.com:8443/org/repo.git'  
**Confidence**: 0.80  

```python
result = GitConfigRepo.inject_token(url, token)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_repo.py:117*

### test_inject_token_gitlab_ssh

**Category**: instantiation  
**Description**: Instantiate inject_token: Test GitLab SSH URL conversion.  
**Expected**: assert result == 'https://glpat-token123@gitlab.com/group/project.git'  
**Confidence**: 0.80  

```python
result = GitConfigRepo.inject_token(url, token)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_repo.py:125*

### test_clone_new_repo

**Category**: instantiation  
**Description**: Instantiate clone_or_pull: Test cloning a new repository.  
**Expected**: assert result == git_repo.cache_dir / 'test-source'  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_clone, git_repo

result = git_repo.clone_or_pull(source_name='test-source', git_url='https://github.com/org/repo.git')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_repo.py:137*

### test_pull_existing_repo

**Category**: instantiation  
**Description**: Instantiate clone_or_pull: Test pulling updates to existing repository.  
**Expected**: assert result == repo_path  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_repo_class, git_repo, temp_cache_dir

result = git_repo.clone_or_pull(source_name='test-source', git_url='https://github.com/org/repo.git')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_repo.py:164*

### test_pull_with_token_update

**Category**: instantiation  
**Description**: Instantiate clone_or_pull: Test pulling with token updates remote URL.  
**Expected**: mock_origin.set_url.assert_called_once()  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_repo_class, git_repo, temp_cache_dir

_result = git_repo.clone_or_pull(source_name='test-source', git_url='https://github.com/org/repo.git', token='ghp_token123')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_git_repo.py:185*

### test_export_to_weaviate

**Category**: instantiation  
**Description**: Instantiate run_async: Test Weaviate export tool.  
**Expected**: assert isinstance(result, list)  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: test_skill_dir

result = run_async(export_to_weaviate_impl(args))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_vector_dbs.py:69*

### test_export_to_chroma

**Category**: instantiation  
**Description**: Instantiate run_async: Test Chroma export tool.  
**Expected**: assert isinstance(result, list)  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: test_skill_dir

result = run_async(export_to_chroma_impl(args))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_vector_dbs.py:92*

### test_export_to_faiss

**Category**: instantiation  
**Description**: Instantiate run_async: Test FAISS export tool.  
**Expected**: assert isinstance(result, list)  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: test_skill_dir

result = run_async(export_to_faiss_impl(args))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_vector_dbs.py:115*

### test_export_to_qdrant

**Category**: instantiation  
**Description**: Instantiate run_async: Test Qdrant export tool.  
**Expected**: assert isinstance(result, list)  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: test_skill_dir

result = run_async(export_to_qdrant_impl(args))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_vector_dbs.py:138*

### test_export_with_default_output_dir

**Category**: instantiation  
**Description**: Instantiate run_async: Test export with default output directory.  
**Expected**: assert isinstance(result, list)  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: test_skill_dir

result = run_async(export_to_weaviate_impl(args))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_vector_dbs.py:157*

### test_adaptor_registration

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test that LlamaIndex adaptor is registered.  
**Expected**: assert adaptor.PLATFORM == 'llama-index'  
**Confidence**: 0.80  

```python
adaptor = get_adaptor('llama-index')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_llama_index_adaptor.py:19*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test formatting SKILL.md as LlamaIndex Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

adaptor = get_adaptor('llama-index')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_llama_index_adaptor.py:40*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate SkillMetadata: Test formatting SKILL.md as LlamaIndex Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_llama_index_adaptor.py:41*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate format_skill_md: Test formatting SKILL.md as LlamaIndex Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

documents_json = adaptor.format_skill_md(skill_dir, metadata)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_llama_index_adaptor.py:43*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate loads: Test formatting SKILL.md as LlamaIndex Documents.  
**Expected**: assert len(documents) == 3  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

documents = json.loads(documents_json)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_llama_index_adaptor.py:46*

### test_chroma_adaptor_exists

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test that ChromaDB adaptor can be loaded.  
**Expected**: assert adaptor is not None  
**Confidence**: 0.80  

```python
adaptor = get_adaptor('chroma')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_integration.py:75*

### test_chroma_upload_without_chromadb_installed

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test upload fails gracefully without chromadb installed.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_chroma_package

adaptor = get_adaptor('chroma')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_integration.py:81*

### test_chroma_upload_without_chromadb_installed

**Category**: instantiation  
**Description**: Instantiate get: Test upload fails gracefully without chromadb installed.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_chroma_package

chromadb_backup = sys.modules.get('chromadb')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_integration.py:86*

### test_chroma_upload_without_chromadb_installed

**Category**: instantiation  
**Description**: Instantiate upload: Test upload fails gracefully without chromadb installed.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_chroma_package

result = adaptor.upload(sample_chroma_package)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_integration.py:91*

### test_chroma_upload_api_signature

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test ChromaDB upload has correct API signature.  
**Expected**: assert hasattr(adaptor, 'upload')  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_chroma_package

adaptor = get_adaptor('chroma')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_integration.py:102*

### test_weaviate_adaptor_exists

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test that Weaviate adaptor can be loaded.  
**Expected**: assert adaptor is not None  
**Confidence**: 0.80  

```python
adaptor = get_adaptor('weaviate')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_integration.py:117*

### test_weaviate_upload_without_weaviate_installed

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test upload fails gracefully without weaviate-client installed.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_weaviate_package

adaptor = get_adaptor('weaviate')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_integration.py:123*

### test_weaviate_upload_without_weaviate_installed

**Category**: instantiation  
**Description**: Instantiate get: Test upload fails gracefully without weaviate-client installed.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: sample_weaviate_package

weaviate_backup = sys.modules.get('weaviate')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_upload_integration.py:128*

### test_chunk_document_single_chunk

**Category**: instantiation  
**Description**: Instantiate StreamingIngester: Test chunking when document fits in single chunk.  
**Expected**: assert len(chunks) == 1  
**Confidence**: 0.80  

```python
ingester = StreamingIngester(chunk_size=1000, chunk_overlap=100)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_streaming_ingestion.py:50*

### test_chunk_document_single_chunk

**Category**: instantiation  
**Description**: Instantiate list: Test chunking when document fits in single chunk.  
**Expected**: assert len(chunks) == 1  
**Confidence**: 0.80  

```python
chunks = list(ingester.chunk_document(content, metadata))
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_streaming_ingestion.py:55*

### test_chunk_document_multiple_chunks

**Category**: instantiation  
**Description**: Instantiate StreamingIngester: Test chunking with multiple chunks.  
**Expected**: assert len(chunks) > 1  
**Confidence**: 0.80  

```python
ingester = StreamingIngester(chunk_size=100, chunk_overlap=20)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_streaming_ingestion.py:68*

### test_get_storage_adaptor_s3

**Category**: instantiation  
**Description**: Instantiate get_storage_adaptor: Test S3 adaptor factory.  
**Confidence**: 0.80  
**Tags**: mock  

```python
adaptor = get_storage_adaptor('s3', bucket='test-bucket')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cloud_storage.py:53*

### test_get_storage_adaptor_gcs

**Category**: instantiation  
**Description**: Instantiate get_storage_adaptor: Test GCS adaptor factory.  
**Confidence**: 0.80  
**Tags**: mock  

```python
adaptor = get_storage_adaptor('gcs', bucket='test-bucket')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cloud_storage.py:62*

### test_get_storage_adaptor_azure

**Category**: instantiation  
**Description**: Instantiate get_storage_adaptor: Test Azure adaptor factory.  
**Confidence**: 0.80  
**Tags**: mock  

```python
adaptor = get_storage_adaptor('azure', container='test-container', connection_string='DefaultEndpointsProtocol=https;AccountName=test;AccountKey=key')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cloud_storage.py:71*

### test_s3_upload_file

**Category**: instantiation  
**Description**: Instantiate S3StorageAdaptor: Test S3 file upload.  
**Confidence**: 0.80  
**Tags**: mock  

```python
adaptor = S3StorageAdaptor(bucket='test-bucket')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cloud_storage.py:101*

### test_s3_upload_file

**Category**: instantiation  
**Description**: Instantiate upload_file: Test S3 file upload.  
**Confidence**: 0.80  
**Tags**: mock  

```python
result = adaptor.upload_file(tmp_path, 'test.txt')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cloud_storage.py:110*

### test_s3_download_file

**Category**: instantiation  
**Description**: Instantiate S3StorageAdaptor: Test S3 file download.  
**Confidence**: 0.80  
**Tags**: mock  

```python
adaptor = S3StorageAdaptor(bucket='test-bucket')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cloud_storage.py:129*

### test_s3_download_file

**Category**: instantiation  
**Description**: Instantiate join: Test S3 file download.  
**Confidence**: 0.80  
**Tags**: mock  

```python
local_path = os.path.join(tmp_dir, 'downloaded.txt')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cloud_storage.py:132*

### test_s3_list_files

**Category**: instantiation  
**Description**: Instantiate S3StorageAdaptor: Test S3 file listing.  
**Confidence**: 0.80  
**Tags**: mock  

```python
adaptor = S3StorageAdaptor(bucket='test-bucket')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cloud_storage.py:167*

### test_s3_list_files

**Category**: instantiation  
**Description**: Instantiate list_files: Test S3 file listing.  
**Confidence**: 0.80  
**Tags**: mock  

```python
files = adaptor.list_files('prefix/')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cloud_storage.py:170*

### test_s3_file_exists

**Category**: instantiation  
**Description**: Instantiate S3StorageAdaptor: Test S3 file existence check.  
**Confidence**: 0.80  
**Tags**: mock  

```python
adaptor = S3StorageAdaptor(bucket='test-bucket')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_cloud_storage.py:190*

### test_adaptor_registration

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test that Qdrant adaptor is registered.  
**Expected**: assert adaptor.PLATFORM == 'qdrant'  
**Confidence**: 0.80  

```python
adaptor = get_adaptor('qdrant')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_qdrant_adaptor.py:19*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate get_adaptor: Test formatting SKILL.md as Qdrant points.  
**Expected**: assert 'collection_name' in result  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

adaptor = get_adaptor('qdrant')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_qdrant_adaptor.py:40*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate SkillMetadata: Test formatting SKILL.md as Qdrant points.  
**Expected**: assert 'collection_name' in result  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

metadata = SkillMetadata(name='test_skill', description='Test skill', version='1.0.0')
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_qdrant_adaptor.py:41*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate format_skill_md: Test formatting SKILL.md as Qdrant points.  
**Expected**: assert 'collection_name' in result  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

points_json = adaptor.format_skill_md(skill_dir, metadata)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_qdrant_adaptor.py:43*

### test_format_skill_md

**Category**: instantiation  
**Description**: Instantiate loads: Test formatting SKILL.md as Qdrant points.  
**Expected**: assert 'collection_name' in result  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

result = json.loads(points_json)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_adaptors\test_qdrant_adaptor.py:46*

### test_summarize_reference_basic

**Category**: instantiation  
**Description**: Instantiate LocalSkillEnhancer: Test basic summarization preserves structure  
**Expected**: assert '# Introduction' in summarized  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

enhancer = LocalSkillEnhancer(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_smart_summarization.py:18*

### test_summarize_reference_basic

**Category**: instantiation  
**Description**: Instantiate summarize_reference: Test basic summarization preserves structure  
**Expected**: assert '# Introduction' in summarized  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

summarized = enhancer.summarize_reference(content, target_ratio=0.3)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_smart_summarization.py:46*

### test_summarize_preserves_code_blocks

**Category**: instantiation  
**Description**: Instantiate LocalSkillEnhancer: Test that code blocks are prioritized and preserved  
**Expected**: assert summarized.count('```python') >= 2  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

enhancer = LocalSkillEnhancer(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_smart_summarization.py:57*

### test_summarize_preserves_code_blocks

**Category**: instantiation  
**Description**: Instantiate summarize_reference: Test that code blocks are prioritized and preserved  
**Expected**: assert summarized.count('```python') >= 2  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

summarized = enhancer.summarize_reference(content, target_ratio=0.5)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_smart_summarization.py:88*

### test_summarize_large_content

**Category**: instantiation  
**Description**: Instantiate LocalSkillEnhancer: Test summarization with very large content  
**Expected**: assert summarized_size < original_size  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

enhancer = LocalSkillEnhancer(tmp_path)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_smart_summarization.py:96*

### test_summarize_large_content

**Category**: instantiation  
**Description**: Instantiate join: Test summarization with very large content  
**Expected**: assert summarized_size < original_size  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

content = '\n'.join(sections)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_smart_summarization.py:117*

### test_summarize_large_content

**Category**: instantiation  
**Description**: Instantiate len: Test summarization with very large content  
**Expected**: assert summarized_size < original_size  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

original_size = len(content)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_smart_summarization.py:118*

### test_summarize_large_content

**Category**: instantiation  
**Description**: Instantiate summarize_reference: Test summarization with very large content  
**Expected**: assert summarized_size < original_size  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

summarized = enhancer.summarize_reference(content, target_ratio=0.3)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_smart_summarization.py:121*

### test_package_valid_skill_directory

**Category**: instantiation  
**Description**: Instantiate create_test_skill_directory: Test packaging a valid skill directory  
**Confidence**: 0.80  
**Tags**: unittest  

```python
skill_dir = self.create_test_skill_directory(tmpdir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_package_skill.py:42*

### test_package_valid_skill_directory

**Category**: instantiation  
**Description**: Instantiate package_skill: Test packaging a valid skill directory  
**Confidence**: 0.80  
**Tags**: unittest  

```python
success, zip_path = package_skill(skill_dir, open_folder_after=False, skip_quality_check=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_package_skill.py:44*

### test_package_creates_correct_zip_structure

**Category**: instantiation  
**Description**: Instantiate create_test_skill_directory: Test that packaged zip contains correct files  
**Confidence**: 0.80  
**Tags**: unittest  

```python
skill_dir = self.create_test_skill_directory(tmpdir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_package_skill.py:57*

### test_package_creates_correct_zip_structure

**Category**: instantiation  
**Description**: Instantiate package_skill: Test that packaged zip contains correct files  
**Confidence**: 0.80  
**Tags**: unittest  

```python
success, zip_path = package_skill(skill_dir, open_folder_after=False, skip_quality_check=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_package_skill.py:59*

### test_package_excludes_backup_files

**Category**: instantiation  
**Description**: Instantiate create_test_skill_directory: Test that .backup files are excluded from zip  
**Confidence**: 0.80  
**Tags**: unittest  

```python
skill_dir = self.create_test_skill_directory(tmpdir)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_package_skill.py:79*

### test_package_excludes_backup_files

**Category**: instantiation  
**Description**: Instantiate package_skill: Test that .backup files are excluded from zip  
**Confidence**: 0.80  
**Tags**: unittest  

```python
success, zip_path = package_skill(skill_dir, open_folder_after=False, skip_quality_check=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_package_skill.py:84*

### test_package_nonexistent_directory

**Category**: instantiation  
**Description**: Instantiate package_skill: Test packaging a nonexistent directory  
**Expected**: self.assertFalse(success)  
**Confidence**: 0.80  
**Tags**: unittest  

```python
success, zip_path = package_skill('/nonexistent/path', open_folder_after=False, skip_quality_check=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_package_skill.py:97*

### test_package_directory_without_skill_md

**Category**: instantiation  
**Description**: Instantiate package_skill: Test packaging directory without SKILL.md  
**Confidence**: 0.80  
**Tags**: unittest  

```python
success, zip_path = package_skill(skill_dir, open_folder_after=False, skip_quality_check=True)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_package_skill.py:110*

### test_detect_english

**Category**: instantiation  
**Description**: Instantiate detect: Test English language detection.  
**Expected**: assert lang_info.code == 'en'  
**Confidence**: 0.80  

```python
lang_info = detector.detect(text)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multilang_support.py:30*

### test_detect_spanish

**Category**: instantiation  
**Description**: Instantiate detect: Test Spanish language detection.  
**Expected**: assert lang_info.code == 'es'  
**Confidence**: 0.80  

```python
lang_info = detector.detect(text)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multilang_support.py:42*

### test_detect_french

**Category**: instantiation  
**Description**: Instantiate detect: Test French language detection.  
**Expected**: assert lang_info.code == 'fr'  
**Confidence**: 0.80  

```python
lang_info = detector.detect(text)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multilang_support.py:53*

### test_detect_german

**Category**: instantiation  
**Description**: Instantiate detect: Test German language detection.  
**Expected**: assert lang_info.code == 'de'  
**Confidence**: 0.80  

```python
lang_info = detector.detect(text)
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_multilang_support.py:64*

### test_config_file

**Category**: config  
**Description**: Configuration example: Create a minimal test config file  
**Confidence**: 0.75  
**Tags**: pytest  

```python
# Setup
# Fixtures: tmp_path

config = {'name': 'test-e2e', 'description': 'Test skill for E2E testing', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article', 'title': 'title', 'code_blocks': 'pre'}, 'url_patterns': {'include': ['/docs/'], 'exclude': ['/search', '/404']}, 'categories': {'getting_started': ['intro', 'start'], 'api': ['api', 'reference']}, 'rate_limit': 0.1, 'max_pages': 5}
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_skill_e2e.py:67*

### test_config_file

**Category**: config  
**Description**: Configuration example: Create a minimal test config file  
**Confidence**: 0.75  
**Tags**: pytest  

```python
# Setup
# Fixtures: tmp_path

config = {'name': 'test-cli-e2e', 'description': 'Test skill for CLI E2E testing', 'base_url': 'https://example.com/docs/', 'selectors': {'main_content': 'article', 'title': 'title', 'code_blocks': 'pre'}, 'url_patterns': {'include': ['/docs/'], 'exclude': []}, 'categories': {}, 'rate_limit': 0.1, 'max_pages': 3}
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_skill_e2e.py:317*

### real_test_config

**Category**: config  
**Description**: Configuration example: Create a real minimal config that can be scraped  
**Confidence**: 0.75  
**Tags**: pytest  

```python
# Setup
# Fixtures: tmp_path

config = {'name': 'test-real-e2e', 'description': 'Real E2E test', 'base_url': 'https://httpbin.org/html', 'selectors': {'main_content': 'body', 'title': 'title', 'code_blocks': 'code'}, 'url_patterns': {'include': [], 'exclude': []}, 'categories': {}, 'rate_limit': 0.5, 'max_pages': 1}
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_install_skill_e2e.py:464*

### mock_git_repo

**Category**: config  
**Description**: Configuration example: Create a mock git repository with config files.  
**Confidence**: 0.75  
**Tags**: mock, pytest  

```python
# Setup
# Fixtures: temp_dirs

react_config = {'name': 'react', 'description': 'React framework', 'base_url': 'https://react.dev/'}
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_git_sources.py:45*

### mock_git_repo

**Category**: config  
**Description**: Configuration example: Create a mock git repository with config files.  
**Confidence**: 0.75  
**Tags**: mock, pytest  

```python
# Setup
# Fixtures: temp_dirs

vue_config = {'name': 'vue', 'description': 'Vue framework', 'base_url': 'https://vuejs.org/'}
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_git_sources.py:52*

### test_create_temp_unified_config

**Category**: config  
**Description**: Configuration example: Test creating a unified config from scratch  
**Confidence**: 0.75  

```python
config = {'name': 'test_unified', 'description': 'Test unified config', 'merge_mode': 'rule-based', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com/docs', 'extract_api': True, 'max_pages': 50}, {'type': 'github', 'repo': 'test/repo', 'include_code': True, 'code_analysis_depth': 'surface'}]}
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\src\skill_seekers\cli\test_unified_simple.py:59*

### test_mixed_source_types

**Category**: config  
**Description**: Configuration example: Test config with documentation, GitHub, and PDF sources  
**Confidence**: 0.75  

```python
config = {'name': 'test_mixed', 'description': 'Test mixed sources', 'merge_mode': 'rule-based', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com'}, {'type': 'github', 'repo': 'test/repo'}, {'type': 'pdf', 'path': '/path/to/manual.pdf'}]}
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\src\skill_seekers\cli\test_unified_simple.py:97*

### test_config_validation_errors

**Category**: config  
**Description**: Configuration example: Test that invalid configs are rejected  
**Confidence**: 0.75  

```python
config = {'name': 'test', 'description': 'Test', 'sources': [{'type': 'invalid_type', 'url': 'https://example.com'}]}
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\src\skill_seekers\cli\test_unified_simple.py:131*

### sample_config

**Category**: config  
**Description**: Configuration example: Create a sample config file.  
**Confidence**: 0.75  
**Tags**: pytest  

```python
# Setup
# Fixtures: temp_dirs

config_data = {'name': 'test-framework', 'description': 'Test framework for testing', 'base_url': 'https://test-framework.dev/', 'selectors': {'main_content': 'article', 'title': 'h1', 'code_blocks': 'pre'}, 'url_patterns': {'include': ['/docs/'], 'exclude': ['/blog/', '/search/']}, 'categories': {'getting_started': ['introduction', 'getting-started'], 'api': ['api', 'reference']}, 'rate_limit': 0.5, 'max_pages': 100}
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_fastmcp.py:64*

### unified_config

**Category**: config  
**Description**: Configuration example: Create a sample unified config file.  
**Confidence**: 0.75  
**Tags**: pytest  

```python
# Setup
# Fixtures: temp_dirs

config_data = {'name': 'test-unified', 'description': 'Test unified scraping', 'merge_mode': 'rule-based', 'sources': [{'type': 'documentation', 'base_url': 'https://example.com/docs/', 'extract_api': True, 'max_pages': 10}, {'type': 'github', 'repo': 'test/repo', 'extract_readme': True}]}
```

*Source: C:\Users\Administrator\Desktop\MT5\skill\Skill_Seekers\tests\test_mcp_fastmcp.py:86*

