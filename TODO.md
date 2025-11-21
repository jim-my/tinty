# Review Notes

All initial review items have been addressed:

1. ✅ **Priority overflow** - Fixed with tuple-based priority `(pipeline_stage, nesting_depth, application_order)` (PR #4)
2. ✅ **Named groups nesting** - Fixed using `sre_parse` for proper regex AST parsing (PR #5)
3. ✅ **Color aliases** - Added `red_bg`, `bold`, `inverse`, `strike`, etc. aliases (PR #6)
4. ✅ **256-color/truecolor + passthrough support** - `_parse_ansi` now keeps extended colors and replays unknown SGR codes so upstream styling survives re-rendering
5. ℹ️ **Strategic direction** - tinty is a unique CLI filter for regex-based highlights with nested priority rules
6. ✅ **--unbuffered CLI flag** - Added `-u`/`--unbuffered` for line-buffered output (PR #7)

# Technical Debt

- `sre_parse` is deprecated (Python 3.11+). Monitor for removal in future Python versions; may need to migrate to a third-party regex parsing library. See `src/tinty/tinty.py:10-15`.
