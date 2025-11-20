# Color Nesting Documentation

This document contains the new sections to add to README.md for the color nesting feature.

## Feature List Addition

Add to the "✨ Features" section:

```markdown
- **🎨 Smart Color Nesting**: Automatic priority-based rendering without manual z-index
- **🔍 ANSI-Aware Matching**: Patterns match original text, ignoring color codes
- **🎯 Channel Isolation**: Foreground, background, and attributes work independently
```

## New Section: Advanced Color Nesting

Add after "Pattern Highlighting" section:

```markdown
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

## Real-World Use Cases

### Log File Highlighting

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

### Syntax Highlighting with Context

```python
code = "def hello_world():"
result = (ColorizedString(code)
    .highlight(r'\b(def)\b', ['blue'])           # Keywords
    .highlight(r'[a-z_]+\w*(?=\()', ['green'])   # Function names
)
print(result)
# Keywords and functions properly colored even when overlapping
```

### Multi-Stage Processing

```bash
# Stage 1: Highlight errors in red
cat log.txt | tinty 'ERROR|CRITICAL' red > /tmp/colored.txt

# Stage 2: Add blue highlighting for timestamps (higher priority)
cat /tmp/colored.txt | tinty '\d{2}:\d{2}:\d{2}' blue

# Result: Both colors preserved, timestamps override errors if overlapping
```
```

## CLI Section Update

Replace the CLI section with:

```markdown
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
```
```

## Screenshots to Generate

Create these visual examples:

1. **nested-groups.png**: Show `(h.(ll))` pattern with different colors
2. **channel-isolation.png**: Show bg + fg coexisting
3. **pipeline-demo.png**: Show multi-stage piping
4. **both-formats.png**: Show bg_red and red_bg producing identical output
