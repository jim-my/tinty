# Tinty

Tinty is a tiny Python library for terminal text colorization and highlighting, inspired by the Ruby colorize gem. Now with a modern, production-safe API featuring Pathlib-inspired operator chaining!

![CI](https://github.com/jim-my/colorize/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/jim-my/colorize/branch/main/graph/badge.svg)](https://codecov.io/gh/jim-my/colorize)
[![PyPI version](https://badge.fury.io/py/tinty.svg)](https://badge.fury.io/py/tinty)
[![Python versions](https://img.shields.io/pypi/pyversions/tinty.svg)](https://pypi.org/project/tinty)

## ✨ Features

- **🔒 Production Safe**: No monkey patching or global state pollution
- **🎯 Multiple APIs**: Choose your preferred style - fluent, functional, or global
- **🔗 Pathlib-inspired**: Elegant operator chaining with `|` and `>>` operators
- **🌈 Comprehensive**: Support for all ANSI colors, backgrounds, and text styles
- **🎨 Smart Color Nesting**: Automatic priority-based rendering without manual z-index
- **🔍 ANSI-Aware Matching**: Patterns match original text, ignoring color codes
- **🎯 Channel Isolation**: Foreground, background, and attributes work independently
- **⚡ High Performance**: Efficient implementation with minimal overhead
- **🧪 Well Tested**: Comprehensive test suite with 100+ tests
- **📦 Zero Dependencies**: Pure Python implementation
- **🖥️ Cross Platform**: Works on Linux, macOS, and Windows
- **🛠️ CLI Tool**: Command-line interface for colorizing text

## 🚀 Installation

```bash
pip install tinty
```

## 🖼️ See It In Action

**Simple API, beautiful results:**

```python
print(colored("Success") | GREEN | BOLD)
print(colored("Warning") | YELLOW)
print(colored("Error") | RED | BOLD)
print(colored("Info") | BLUE)
```
![Basic Colors Example](https://raw.githubusercontent.com/jim-my/tinty/main/docs/images/basic-colors.png)

**CLI pattern highlighting:**

```bash
echo "hello world" | tinty "l.*" yellow
echo "hello world" | tinty "(ll).*(ld)" red,bg_blue blue,bg_red
```
![CLI Examples](https://raw.githubusercontent.com/jim-my/tinty/main/docs/images/cli-examples.png)

**Complex styling made easy:**

```python
print(colored("SYSTEM ALERT") | RED | BOLD | BG_WHITE)
print(str(colored("DEBUG") | DIM) + " - Application started")
print(str(colored("INFO") | BLUE) + " - User logged in")
print(str(colored("WARNING") | YELLOW | BOLD) + " - Memory usage high")
print(str(colored("ERROR") | RED | BOLD) + " - Database connection failed")
```
![Complex Styling](https://raw.githubusercontent.com/jim-my/tinty/main/docs/images/complex-styling.png)

**Regex pattern highlighting:**

```python
text = "The quick brown fox jumps over the lazy dog"
highlighted = colored(text).highlight(r"(quick)|(fox)|(lazy)", ["red", "blue", "green"])
print(highlighted)
```
![Pattern Highlighting](https://raw.githubusercontent.com/jim-my/tinty/main/docs/images/pattern-highlighting.png)

## 🎨 Quick Start

### Modern Enhanced API (Recommended)

```python
from tinty import colored, C, txt, RED, GREEN, BLUE, YELLOW, BOLD, BG_WHITE, UNDERLINE

# Type-safe constants with operator chaining (RECOMMENDED)
print(colored("Success") | GREEN | BOLD)
print(txt("Warning") | YELLOW)
print(colored("Error") | RED | BOLD | BG_WHITE)
print(txt("Info") >> BLUE >> UNDERLINE)

# Global convenience object with constants
print(C("✓ Tests passing") | GREEN)
print(C("✗ Build failed") | RED)
print(C("Processing...") | BLUE | BOLD)

# Legacy method chaining (still works but uses internal string literals)
print(colored("Success").green().bold())
print(txt("Warning").yellow())
```

### Real-World Examples

```python
from tinty import (
    colored, C, txt, ColorString,
    RED, GREEN, BLUE, YELLOW, BOLD, DIM, BG_WHITE, BLINK
)

# Log levels with type-safe constants
print(C("DEBUG") | DIM + " - Application started")
print(colored("INFO") | BLUE + " - User logged in")
print(txt("WARNING") | YELLOW | BOLD + " - Memory usage high")
print(ColorString("ERROR") | RED | BOLD + " - Database connection failed")

# CLI status indicators (direct color methods still work)
print(f"{C.green('✓')} File saved successfully")
print(f"{C.yellow('⚠')} Configuration outdated")
print(f"{C.red('✗')} Permission denied")

# Complex chaining with constants
alert = (colored("SYSTEM ALERT")
         | RED
         | BOLD
         | BG_WHITE
         | BLINK)
print(alert)
```

### Pattern Highlighting

```python
from tinty import colored

# Highlight search terms
text = "The quick brown fox jumps over the lazy dog"
highlighted = colored(text).highlight(r"(quick)|(fox)|(lazy)", ["red", "blue", "green"])
print(highlighted)

# Syntax highlighting
code = "def hello_world():"
result = colored(code).highlight(r"\b(def)\b", ["blue"])
print(result)
```

## 🎨 Advanced: Color Nesting & Priority

Tinty intelligently handles overlapping colors with automatic priority resolution:

### Nested Regex Groups

Inner (more specific) capture groups automatically override outer ones:

```python
from tinty import ColorizedString

text = ColorizedString("hello world")

# Pattern: (h.(ll)) creates two groups
# - Group 1: "hell" (outer) → red
# - Group 2: "ll" (inner, higher priority) → blue
result = text.highlight(r'(h.(ll))', ['red', 'blue'])
print(result)
# Output: "he" is red, "ll" is blue (inner wins)
```

**Priority Rules:**
1. **Pipeline stage**: Later commands override earlier ones
2. **Nesting depth**: Inner regex groups override outer groups
3. **Application order**: Later applications win within same depth

### Channel Isolation

Foreground, background, and attributes are independent channels that can coexist:

```python
text = ColorizedString("hello world")

# Background and foreground don't conflict!
result = text.highlight(r'(h.(ll))', ['bg_red', 'blue'])
print(result)
# Output: "he" has red background
#         "ll" has BOTH red background AND blue foreground
```

**Available Channels:**
- **Foreground (fg)**: Text color (red, blue, green, etc.)
- **Background (bg)**: Background color (bg_red, bg_blue, etc.)
- **Attributes (attr)**: Bold, underline, dim, etc.

### ANSI-Aware Pattern Matching

Patterns always match the original text, even if it contains ANSI codes:

```python
# Text with existing ANSI codes
colored_text = ColorizedString("H\x1b[31mello\x1b[0m World")

# Pattern still matches "Hello" ignoring the ANSI codes in between
result = colored_text.highlight(r'Hello', ['green'])
print(result)
# Works! Pattern matched the original text "Hello World"
```

### Color Name Flexibility

Both `bg_red` and `red_bg` formats are supported:

```python
# These are equivalent:
text.highlight(r'hello', ['bg_red'])    # Official format
text.highlight(r'hello', ['red_bg'])    # Natural format (auto-normalized)
```

### CLI Examples with Nesting

```bash
# Nested groups - inner blue wins over outer red
echo "hello world" | tinty '(h.(ll))' red,blue

# Background + foreground coexist (different channels)
echo "hello world" | tinty '(h.(ll))' bg_red,blue
# Result: "he" = red background
#         "ll" = red background + blue foreground

# Pipeline - later commands have higher priority
echo "hello world" | tinty 'hello' red | tinty 'world' blue
# Result: "hello" is red, "world" is blue

# Pipeline with --replace-all to clear previous colors
echo "hello world" | tinty 'hello' red | tinty --replace-all 'world' blue
# Result: Only "world" is blue (red cleared)

# Both color formats work
echo "hello" | tinty 'hello' bg_red     # Official
echo "hello" | tinty 'hello' red_bg     # Natural (auto-normalized)
```

### Advanced Pattern Control

Control priority through regex structure:

```bash
# Want inner group to have higher priority?
# Put it deeper in the nesting:
echo "hello" | tinty '(he(ll)o)' red,blue
# Result: "he" and "o" are red, "ll" is blue (deeper nesting)

# Want same priority? Use sibling groups:
echo "hello" | tinty '(he)(ll)' red,blue
# Result: Both at same depth, order determines priority
```

### Real-World Use Cases

#### Log File Highlighting

```python
from tinty import ColorizedString

log = "ERROR: Connection failed at 10:30:45"
result = (ColorizedString(log)
    .highlight(r'ERROR', ['red', 'bold'])      # Priority 1
    .highlight(r'\d{2}:\d{2}:\d{2}', ['blue']) # Priority 2
)
print(result)
# "ERROR" is red+bold, timestamp is blue
```

#### Syntax Highlighting with Context

```python
code = "def hello_world():"
result = (ColorizedString(code)
    .highlight(r'\b(def)\b', ['blue'])           # Keywords
    .highlight(r'[a-z_]+\w*(?=\()', ['green'])   # Function names
)
print(result)
# Keywords and functions properly colored even when overlapping
```

#### Multi-Stage Processing

```bash
# Stage 1: Highlight errors in red
cat log.txt | tinty 'ERROR|CRITICAL' red > /tmp/colored.txt

# Stage 2: Add blue highlighting for timestamps (higher priority)
cat /tmp/colored.txt | tinty '\d{2}:\d{2}:\d{2}' blue

# Result: Both colors preserved, timestamps override errors if overlapping
```

## 📋 Available Colors and Styles

### Foreground Colors
`red`, `green`, `blue`, `yellow`, `magenta`, `cyan`, `white`, `black`, `lightred`, `lightgreen`, `lightblue`, `lightyellow`, `lightmagenta`, `lightcyan`, `lightgray`, `darkgray`

### Background Colors
`bg_red`, `bg_green`, `bg_blue`, `bg_yellow`, `bg_magenta`, `bg_cyan`, `bg_white`, `bg_black`, `bg_lightred`, `bg_lightgreen`, `bg_lightblue`, `bg_lightyellow`, `bg_lightmagenta`, `bg_lightcyan`, `bg_lightgray`, `bg_darkgray`

### Text Styles
`bright`/`bold`, `dim`, `underline`, `blink`, `invert`/`swapcolor`, `hidden`, `strikethrough`

## 🔒 Type-Safe Color Constants (New!)

Use constants instead of error-prone string literals:

```python
from tinty import colored, RED, GREEN, BLUE, YELLOW, BOLD, BG_WHITE

# ✅ Type-safe with IDE autocompletion and error checking
error_msg = colored("CRITICAL") | RED | BOLD | BG_WHITE
success_msg = colored("SUCCESS") | GREEN | BOLD
warning_msg = colored("WARNING") | YELLOW

# ❌ Error-prone string literals
error_msg = colored("CRITICAL") | "red" | "typo"  # Runtime error!
```

**Benefits:**
- 🔍 **IDE Autocompletion**: Get suggestions for valid colors
- 🛡️ **Type Checking**: Catch typos at development time
- 📝 **Self-Documenting**: Clear, readable code
- 🔄 **Refactoring Safe**: Rename constants across codebase
- ⚡ **No Runtime Errors**: Invalid colors caught early

**Available Constants:**
- **Colors**: `RED`, `GREEN`, `BLUE`, `YELLOW`, `MAGENTA`, `CYAN`, `WHITE`, `BLACK`
- **Light Colors**: `LIGHTRED`, `LIGHTGREEN`, `LIGHTBLUE`, etc.
- **Backgrounds**: `BG_RED`, `BG_GREEN`, `BG_BLUE`, etc.
- **Styles**: `BOLD`, `BRIGHT`, `DIM`, `UNDERLINE`, `BLINK`, `INVERT`

## 🎭 API Styles

Choose the style that fits your needs:

### 1. Type-Safe Constants (Recommended)
```python
from tinty import colored, txt, RED, BLUE, BOLD, UNDERLINE

colored("hello") | RED | BOLD
txt("world") | BLUE | UNDERLINE
```

### 2. Global Object with Constants
```python
from tinty import C, RED, BOLD

C.red("hello")              # Direct color method
C("hello") | RED | BOLD     # Factory with type-safe constants
C("hello", "red")           # Direct colorization (legacy)
```

### 3. Enhanced ColorString with Constants
```python
from tinty import ColorString, RED, BOLD, BG_YELLOW

ColorString("hello") | RED | BOLD | BG_YELLOW
```

### 4. Legacy Method Chaining (Still Supported)
```python
from tinty import colored, txt

# Method chaining (uses internal string literals)
colored("hello").red().bold()
txt("world").blue().underline()

# Mixed with operators (not recommended - inconsistent)
colored("Mixed").red() | "bright"
```

## 🛠️ Command Line Interface

### Basic Usage

```bash
# Simple pattern matching
echo "hello world" | tinty 'l' red

# Pattern groups
echo "hello world" | tinty '(h.*o).*(w.*d)' red blue
```

### Advanced: Nested Colors

```bash
# Nested regex groups - inner wins
echo "hello world" | tinty '(h.(ll))' red,blue
# Output: "he" is red, "ll" is blue (inner group has higher priority)

# Channel isolation - foreground + background
echo "hello world" | tinty '(h.(ll))' bg_red,blue
# Output: "he" = red bg, "ll" = red bg + blue fg

# Color name formats (both work)
echo "hello" | tinty 'hello' bg_red    # Official format
echo "hello" | tinty 'hello' red_bg    # Natural format (auto-normalized)

# Space or comma-separated colors
echo "test" | tinty '(t)(e)' red,blue   # Comma-separated
echo "test" | tinty '(t)(e)' red blue   # Space-separated
```

### Options

```bash
# List all available colors
tinty --list-colors

# Case sensitive matching
echo "Hello World" | tinty --case-sensitive 'Hello' green

# Verbose mode (debugging)
echo "test" | tinty --verbose 'test' red

# Clear all previous colors before applying new ones
echo "hello world" | tinty 'hello' red | tinty --replace-all 'world' blue
# Result: Only "world" is blue, "hello" has no color
```


## 🔄 Legacy API (Still Supported)

The original API remains fully supported for backward compatibility:

```python
from tinty import Colorize, ColorizedString

# Original Colorize class
colorizer = Colorize()
print(colorizer.colorize("hello", "red"))

# Original ColorizedString
cs = ColorizedString("hello")
print(cs.colorize("blue"))
```

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tinty

# Run specific test file
pytest tests/test_enhanced.py
```

### Code Quality

```bash
# Format and lint
ruff format --preview .
ruff check --preview .

# Type checking
mypy src/

# Run pre-commit hooks
pre-commit run --all-files
```

## 📖 Examples

See the `examples/` directory for more comprehensive examples:

- `examples/quickstart.py` - Basic usage patterns
- `examples/enhanced_demo.py` - Full enhanced API demonstration
- `examples/nesting_demo.py` - Color nesting and priority examples

## Version Management

This project uses automated versioning via git tags:

- Versions are managed by `setuptools-scm` based on git tags
- `poetry-dynamic-versioning` integrates this with Poetry builds
- To release: `git tag v1.2.3 && git push --tags`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Make sure to:

1. Run the pre-commit hooks: `pre-commit run --all-files`
2. Add tests for new features
3. Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the Ruby [colorize](https://github.com/fazibear/colorize) gem
- Built with modern Python best practices
- Designed for production safety and developer experience
