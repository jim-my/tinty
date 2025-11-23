# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-01-23

### Added

- **Enhanced CLI Help with Colored Examples** (#10)
  - TTY-aware colored help examples (shows colors in terminals, plain text when piped)
  - Redesigned `--list-colors` with visual formatting and grouped sections
  - Helper functions for displaying foreground colors, background colors, and text styles
  - Special handling for hidden style to show readable description
  - Complete style alias grouping (bold, inverse, reverse, swap, strike)
  - 8 new screenshots integrated into README documentation

- **Color Removal and HTML Output Formats** (#11)
  - `--remove-color` / `--strip-color` flags to strip ANSI codes from input
  - `--output-format` option supporting three formats:
    - `ansi`: Default terminal output with ANSI color codes
    - `plain`: Plain text with all colors removed
    - `html`: HTML output with inline CSS styles
  - `ansi_to_html()` function for converting ANSI codes to HTML
    - Proper handling of compound ANSI codes (e.g., `\x1b[1;31m`)
    - XSS prevention with HTML escaping
    - Newline-to-`<br>` conversion for web rendering
  - New example scripts: `color_removal.py` and `color_removal_cli.sh`

### Documentation

- Added color removal section to README with CLI and Python API examples
- Added 8 terminal screenshots throughout README sections
- New example scripts demonstrating color removal functionality
- Updated help text with real-world usage examples

### Tests

- Added 3 comprehensive integration tests for color removal and HTML output
- All 177 tests passing (174 from v2.0.2 + 3 new)

### Refactoring

- Extracted `_print_result()` helper function to reduce code complexity
- Extracted color display functions for better organization
- Reduced cyclomatic complexity in `main()` function

---

## [2.0.2] - 2025-01-22

### Refactoring

- Renamed internal module from `pipetint.tinty` to `pipetint.core` for clarity
- Cleaned up all remaining `tinty` references in codebase
  - Updated CI/CD configuration (pytest coverage)
  - Updated pre-commit hooks and gitignore
  - Updated documentation, examples, and test scripts
  - Deleted legacy `src/tinty.egg-info` directory

### Build

- Updated `poetry.lock` to reflect package name change
- Regenerated documentation screenshots

**Note:** All 174 tests passing. No functional changes.

---

## [2.0.1] - 2025-01-22

### Documentation

- Fixed remaining capitalized Tinty → PipeTint references in README and documentation
- Updated all GitHub repository URLs from jim-my/tinty to jim-my/pipetint
- Updated CHANGELOG comparison URLs to point to pipetint repository
- Updated README badges to point to pipetint repository

---

## [2.0.0] - 2025-01-22

### 💥 BREAKING CHANGES

This release renames the package from "tinty" to "pipetint" to avoid conflicts with existing projects and better reflect the tool's purpose.

**Migration Guide:**

1. **Uninstall old package:**
   ```bash
   pip uninstall tinty
   ```

2. **Install new package:**
   ```bash
   pip install pipetint
   ```

3. **Update imports:**
   ```python
   # Old
   from tinty import ColorizedString, colored

   # New
   from pipetint import ColorizedString, colored
   ```

4. **Update CLI usage:**
   ```bash
   # Old
   echo "test" | tinty 'pattern' red

   # New
   echo "test" | pipetint 'pattern' red
   ```

5. **Update git remote (for contributors):**
   ```bash
   git remote set-url origin git@github.com:jim-my/pipetint.git
   ```

### Changed

- Package renamed from `tinty` to `pipetint`
- CLI command renamed from `tinty` to `pipetint`
- GitHub repository renamed to `jim-my/pipetint`
- All imports changed from `from tinty` to `from pipetint`

**Note:** All functionality remains identical - this is purely a naming change.

---

## [1.0.0] - 2025-01-20

### 🎉 First Stable Release

This release marks PipeTint as production-ready with a stable API and unique features not found in any other terminal colorizer.

### ✨ Unique Features

- **Smart Color Nesting**: Automatic priority-based rendering without manual z-index configuration
- **Pipeline Composition**: Colors preserved across pipeline stages with intelligent priority resolution
- **Channel Isolation**: Foreground, background, and attributes work independently
- **ANSI-Aware Pattern Matching**: Patterns match original text, ignoring existing ANSI codes

### 🎯 Production Ready

- 143 comprehensive tests with full coverage
- Type hints throughout the codebase
- Zero dependencies - pure Python implementation
- Comprehensive documentation with real-world examples
- Published to PyPI and TestPyPI

### 📝 API Commitment

With v1.0.0, we commit to:
- Semantic versioning for all future releases
- Backwards compatibility for all public APIs
- Deprecation warnings before removing features
- Clear migration guides for breaking changes (if any in v2.0+)

---

## [0.2.0] - 2025-01-20

### Added

- **Color Nesting with Priority-Based Rendering** (#1)
  - Automatic priority calculation based on pipeline stage, nesting depth, and application order
  - Channel isolation (foreground, background, attributes)
  - Deferred rendering architecture with ColorRange dataclass
  - Nesting depth calculation for regex capture groups

- **ANSI Code Parsing for Pipeline Support**
  - Full ANSI escape sequence parsing to reconstruct ColorRange objects
  - Reverse mapping from ANSI codes to color names
  - Automatic pipeline stage incrementing for proper priority
  - Colors preserved across pipeline stages

- **Color Name Normalization**
  - Support for both `bg_red` and `red_bg` formats
  - Automatic normalization to standard format
  - Case-insensitive color name handling

- **--replace-all CLI Flag**
  - Explicit control to clear all previous colors before applying new ones
  - Useful for starting fresh in pipeline stages
  - Verbose mode shows when colors are cleared

### Documentation

- Comprehensive README updates with Advanced Color Nesting section
- Real-world use cases (log highlighting, syntax highlighting, multi-stage processing)
- CLI examples with nesting patterns
- Screenshot generation scripts
- NESTING_DOCS.md with detailed examples

### Tests

- 16 new tests for color nesting behavior
- 10 new tests for color name normalization
- 2 new tests for --replace-all flag
- All 143 tests passing (131 original + 12 new)

---

## [0.1.10] - 2024-XX-XX

### Changed

- Updated help message formatting
- Improved CLI error handling

---

## [0.1.9] - 2024-XX-XX

### Changed

- Version bump for distribution updates

---

## [0.1.4] - 2024-XX-XX

### Changed

- Version bump and version file generation fixes

---

## [0.1.3] - 2024-XX-XX

### Added

- Initial public release with basic colorization features
- CLI tool for pattern-based text colorization
- Python library with multiple API styles
- Type-safe color constants
- Pattern highlighting with regex support
- Comprehensive test suite

### Features

- Multiple APIs (fluent, functional, global)
- Pathlib-inspired operator chaining
- Support for all ANSI colors, backgrounds, and text styles
- Zero dependencies
- Cross-platform support

---

[2.1.0]: https://github.com/jim-my/pipetint/compare/v2.0.2...v2.1.0
[2.0.2]: https://github.com/jim-my/pipetint/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/jim-my/pipetint/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/jim-my/pipetint/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/jim-my/pipetint/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/jim-my/pipetint/compare/v0.1.10...v0.2.0
[0.1.10]: https://github.com/jim-my/pipetint/compare/v0.1.9...v0.1.10
[0.1.9]: https://github.com/jim-my/pipetint/compare/v0.1.4...v0.1.9
[0.1.4]: https://github.com/jim-my/pipetint/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/jim-my/pipetint/releases/tag/v0.1.3
