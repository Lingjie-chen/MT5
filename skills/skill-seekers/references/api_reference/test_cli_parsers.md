# API Reference: test_cli_parsers.py

**Language**: Python

**Source**: `tests\test_cli_parsers.py`

---

## Classes

### TestParserRegistry

Test parser registry functionality.

**Inherits from**: (none)

#### Methods

##### test_all_parsers_registered(self)

Test that all 19 parsers are registered.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_get_parser_names(self)

Test getting list of parser names.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_all_parsers_are_subcommand_parsers(self)

Test that all parsers inherit from SubcommandParser.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_all_parsers_have_required_properties(self)

Test that all parsers have name, help, description.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_all_parsers_have_add_arguments_method(self)

Test that all parsers implement add_arguments.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_no_duplicate_parser_names(self)

Test that all parser names are unique.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestParserCreation

Test parser creation functionality.

**Inherits from**: (none)

#### Methods

##### test_scrape_parser_creates_subparser(self)

Test that ScrapeParser creates valid subparser.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_github_parser_creates_subparser(self)

Test that GitHubParser creates valid subparser.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_package_parser_creates_subparser(self)

Test that PackageParser creates valid subparser.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_register_parsers_creates_all_subcommands(self)

Test that register_parsers creates all 19 subcommands.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestSpecificParsers

Test specific parser implementations.

**Inherits from**: (none)

#### Methods

##### test_scrape_parser_arguments(self)

Test ScrapeParser has correct arguments.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_github_parser_arguments(self)

Test GitHubParser has correct arguments.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_package_parser_arguments(self)

Test PackageParser has correct arguments.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_analyze_parser_arguments(self)

Test AnalyzeParser has correct arguments.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### TestBackwardCompatibility

Test backward compatibility with old CLI.

**Inherits from**: (none)

#### Methods

##### test_all_original_commands_still_work(self)

Test that all original commands are still registered.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### test_command_count_matches(self)

Test that we have exactly 19 commands (same as original).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |



