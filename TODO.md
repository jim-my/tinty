# Review Notes

1. Priority calculation flattens pipeline stage, nesting depth, and application order into a single integer. After ~1 000 applications, the `application_order` term spills into the depth space, letting shallow highlights override earlier nested ones. Store priority as tuples or cap the order term so depth always wins. (See `src/tinty/tinty.py:11-27` and `src/tinty/tinty.py:538-552`.)
2. `_calculate_group_nesting_depth` treats every `(?` as non-capturing, so named groups and lookarounds never get proper depths. Switch to a regex AST (e.g., `sre_parse`) or a smarter tokenizer so inner named groups still outrank their parents. (`src/tinty/tinty.py:455-466`.)
3. Color aliases promised in the docs (`red_bg`, `bold`, etc.) fail through the public APIs. Normalize names in `Colorize`/`ColorString` (or expand `_color_map`) so CLI, `colored()/txt()`, and `C.*` all accept the advertised spellings. (`src/tinty/tinty.py:42-68`, `src/tinty/enhanced.py:39-161`.)
4. `_parse_ansi` only preserves known 16-color SGR codes; 256-color/truecolor sequences and other escape codes vanish, breaking pipelines that already contain rich colors. Teach `ColorizedString` to retain unknown ANSI segments so later stages don’t strip upstream styling. (`src/tinty/tinty.py:143-214`.)
5. `tinty` is currently unique as a CLI filter that composes regex-based highlights with nested priority rules; keep leaning into that niche while adding broader ANSI and platform support to stay competitive with richer frameworks.
6. CLI enhancement: add a `--unbuffered` (line-buffered stdout) flag so users don't need external `stdbuf` when piping real-time logs. Document that the flag forces line flushing; the name aligns with tools like `python -u` and `stdbuf --output=0`.

# Technical Debt

- `sre_parse` is deprecated (Python 3.11+). Monitor for removal in future Python versions; may need to migrate to a third-party regex parsing library. See `src/tinty/tinty.py:10-15`.
