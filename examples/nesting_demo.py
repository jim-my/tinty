#!/usr/bin/env python3
"""
Demo of the new color nesting and priority system.

This demonstrates:
1. Nested regex groups with automatic priority
2. Channel isolation (fg vs bg colors can coexist)
3. Pattern matching against original text (ignoring ANSI codes)
4. Proper color nesting without manual z-index
"""

from pipetint import ColorizedString

print("=" * 60)
print("PIPETINT COLOR NESTING DEMO")
print("=" * 60)
print()

# Demo 1: Nested regex groups
print("1. Nested Regex Groups - Inner group wins")
print("-" * 60)
cs = ColorizedString("hello world")
result = cs.highlight(r"(h.(ll))", ["red", "blue"])
print("Pattern: (h.(ll)) with colors [red, blue]")
print("Text: 'hello world'")
print(f"Result: {result}")
print("Explanation: 'he' is red (group 1), 'll' is blue (group 2, higher priority)")
print()

# Demo 2: Channel isolation (bg + fg)
print("2. Channel Isolation - Foreground and Background coexist")
print("-" * 60)
result = cs.highlight(r"(h.(ll))", ["bg_red", "blue"])
print("Pattern: (h.(ll)) with colors [bg_red, blue]")
print("Text: 'hello world'")
print(f"Result: {result}")
print(
    "Explanation: 'he' has red background, 'll' has BOTH red background AND blue foreground"
)
print()

# Demo 3: Pattern matching ignores ANSI codes
print("3. Pattern Matching Ignores ANSI Codes")
print("-" * 60)
# Create text with ANSI codes in it
colored_input = ColorizedString("H\x1b[31mello\x1b[0m World")
print("Input with ANSI: 'H\\x1b[31mello\\x1b[0m World'")
print(f"Original text: '{colored_input._original_text}'")
result = colored_input.highlight(r"Hello", ["green"])
print(f"After highlighting 'Hello' with green: {result}")
print("Explanation: Pattern matched 'Hello' even with ANSI codes in between")
print()

# Demo 4: Overlapping colors with priority
print("4. Overlapping Colors - Later wins in same channel")
print("-" * 60)
cs = ColorizedString("hello world")
result = cs.colorize("red")  # Entire string red
result = result.highlight(r"world", ["blue"])  # 'world' blue (higher priority)
print("Step 1: Make entire string red")
print("Step 2: Highlight 'world' with blue")
print(f"Result: {result}")
print("Explanation: 'hello ' is red, 'world' is blue (later application wins)")
print()

# Demo 5: Complex nesting with 3 levels
print("5. Triple Nesting")
print("-" * 60)
cs = ColorizedString("abcdefgh")
result = cs.highlight(r"(a(b(c)d)e)", ["red", "blue", "green"])
print("Pattern: (a(b(c)d)e) with colors [red, blue, green]")
print("Text: 'abcdefgh'")
print(f"Result: {result}")
print("Explanation: 'a'=red, 'b'=blue, 'c'=green (innermost), 'd'=blue, 'e'=red")
print()

# Demo 6: Chaining multiple colors from different channels
print("6. Chaining Different Channels")
print("-" * 60)
cs = ColorizedString("Important!")
result = cs.red.bg_yellow.underline
print("Text: 'Important!'")
print("Chaining: .red.bg_yellow.underline")
print(f"Result: {result}")
print("Explanation: Red text + yellow background + underline all coexist")
print()

# Demo 7: Pipeline simulation
print("7. Pipeline Simulation (Pattern matching across pipes)")
print("-" * 60)
cs = ColorizedString("error: file not found")
result = cs.highlight(r"error", ["red"])
print("Step 1: Highlight 'error' in red")
print(f"Result: {result}")
result2 = result.highlight(r"file", ["yellow"])
print("Step 2: Highlight 'file' in yellow (on already-colored text)")
print(f"Result: {result2}")
print(
    "Explanation: Both patterns matched against original text 'error: file not found'"
)
print()

print("=" * 60)
print("All demos completed!")
print("=" * 60)
