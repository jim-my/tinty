#!/usr/bin/env python3
"""Demonstrates nested regex groups with priority-based color nesting."""

from tinty import ColorizedString

print("🎨 Nested Regex Groups - Inner Wins\n")

# Example 1: Basic nesting
text = ColorizedString("hello world")
result = text.highlight(r"(h.(ll))", ["red", "blue"])
print("Pattern: (h.(ll))")
print("Colors:  red, blue")
print(f"Result:  {result}")
print("         ↑   ↑")
print("         red blue (inner wins)\n")

# Example 2: Triple nesting
text2 = ColorizedString("testing")
result2 = text2.highlight(r"(t(e(st))ing)", ["red", "green", "blue"])
print("Pattern: (t(e(st))ing)")
print("Colors:  red, green, blue")
print(f"Result:  {result2}")
print("         ↑  ↑ ↑")
print("         red green blue (deepest wins)")
