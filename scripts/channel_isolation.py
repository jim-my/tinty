#!/usr/bin/env python3
"""Demonstrates channel isolation - foreground and background work independently."""

from tinty import ColorizedString

print("🎯 Channel Isolation - Foreground + Background Coexist\n")

# Example 1: Background + Foreground
text = ColorizedString("hello world")
result = text.highlight(r"(h.(ll))", ["bg_red", "blue"])
print("Pattern: (h.(ll))")
print("Colors:  bg_red, blue")
print(f"Result:  {result}")
print("         'he' = red background only")
print("         'll' = red background + blue foreground\n")

# Example 2: Multiple channels
text2 = ColorizedString("test")
result2 = text2.highlight(r"(t(e)st)", ["bg_yellow", "blue", "bold"])
print("Pattern: (t(e)st)")
print("Colors:  bg_yellow, blue, bold")
print(f"Result:  {result2}")
print("         't' and 'st' = yellow background")
print("         'e' = yellow bg + blue fg + bold")
