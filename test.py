#!/usr/bin/env python
from colorize import BLUE, UNDERLINE, colored, txt

# Highlight search terms
text = "The quick brown fox jumps over the lazy dog"
highlighted = colored(text).highlight(r"(quick)|(fox)|(lazy)", ["red", "blue", "green"])
print(highlighted)


colored("hello").red().bold()
rs = txt("world") | "blue" | "underline"
print(rs)

rs2 = txt("world") | BLUE | UNDERLINE
print(rs2)
