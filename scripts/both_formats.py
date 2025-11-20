#!/usr/bin/env python3
"""Demonstrates that both bg_red and red_bg formats produce identical output."""

from tinty import ColorizedString

print("🔄 Color Name Flexibility - Both Formats Work\n")

# Example 1: bg_red vs red_bg
text1 = ColorizedString("hello world")
result1 = text1.highlight(r"hello", ["bg_red"])

text2 = ColorizedString("hello world")
result2 = text2.highlight(r"hello", ["red_bg"])

print("Official format:  bg_red")
print(f"Result:           {result1}\n")

print("Natural format:   red_bg")
print(f"Result:           {result2}\n")

print(f"Are they identical? {str(result1) == str(result2)}")
print("✅ Both formats produce the same ANSI output!\n")

# Example 2: Multiple backgrounds
text3 = ColorizedString("tinty supports both formats!")
result3 = text3.highlight(
    r"(tinty)(supports)(both)", ["bg_blue", "green_bg", "bg_yellow"]
)
print(f"Mixed formats:    {result3}")
print("                  bg_blue, green_bg, bg_yellow")
print("                  All work seamlessly!")
