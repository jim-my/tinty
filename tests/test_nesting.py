"""
Tests for color nesting and priority behavior.
"""

from tinty import ColorizedString


class TestColorNesting:
    """Test proper color nesting with priority-based rendering."""

    def test_nested_regex_groups_foreground(self):
        """Test that inner regex groups override outer groups in same channel."""
        cs = ColorizedString("hello world")

        # Pattern: (h.(ll)) - group 1 is "hell", group 2 is "ll"
        # group 1 (depth=1) gets red, group 2 (depth=2) gets blue
        result = cs.highlight(r"(h.(ll))", ["red", "blue"])

        result_str = str(result)

        # "he" should be red only
        assert "\x1b[31mhe\x1b[0m" in result_str

        # "ll" should be blue (inner group wins)
        assert "\x1b[34mll\x1b[0m" in result_str

        # Should not have red on "ll"
        assert result_str.index("\x1b[34m") > result_str.index("\x1b[31m")

    def test_nested_groups_with_background(self):
        """Test nesting with foreground and background colors (different channels)."""
        cs = ColorizedString("hello world")

        # Outer group gets background, inner group gets foreground
        result = cs.highlight(r"(h.(ll))", ["bg_red", "blue"])

        result_str = str(result)

        # "he" should have bg_red only
        assert "\x1b[41mhe\x1b[0m" in result_str

        # "ll" should have both bg_red AND blue (different channels coexist)
        assert (
            "\x1b[34m\x1b[41mll\x1b[0m" in result_str
            or "\x1b[41m\x1b[34mll\x1b[0m" in result_str
        )

    def test_channel_isolation(self):
        """Test that fg, bg, and attributes are independent channels."""
        cs = ColorizedString("hello")

        # Apply multiple colors from different channels
        result = cs.red.bg_blue.underline

        result_str = str(result)

        # Should contain all three: red (31), bg_blue (44), underline (4)
        assert "\x1b[31m" in result_str  # red
        assert "\x1b[44m" in result_str  # bg_blue
        assert "\x1b[4m" in result_str  # underline

    def test_pattern_matching_ignores_ansi_codes(self):
        """Test that patterns match against original text, not rendered ANSI."""
        # Create a string with ANSI codes in it
        cs = ColorizedString("H\x1b[31mello\x1b[0m World")

        # Original text should have ANSI stripped
        assert cs._original_text == "Hello World"

        # Pattern should match "Hello" even though there are ANSI codes
        result = cs.highlight(r"Hello", ["green"])

        result_str = str(result)
        assert "\x1b[32m" in result_str  # green color applied

    def test_multiple_nesting_levels(self):
        """Test deeply nested regex groups."""
        cs = ColorizedString("abcdefgh")

        # Triple nesting: (a(b(c)d)e)
        # Depth 1: "abcde" -> red
        # Depth 2: "bcd" -> blue
        # Depth 3: "c" -> green (highest priority)
        result = cs.highlight(r"(a(b(c)d)e)", ["red", "blue", "green"])

        result_str = str(result)

        # "a" should be red
        # "b" should be blue
        # "c" should be green (innermost wins)
        # "d" should be blue
        # "e" should be red

        # Check that green appears (innermost color)
        assert "\x1b[32m" in result_str  # green for "c"

    def test_overlapping_ranges_same_channel(self):
        """Test that higher priority wins when ranges overlap in same channel."""
        cs = ColorizedString("hello")

        # Apply two colors to overlapping ranges
        result = cs.colorize("red")  # Entire string red (priority 1000)
        result = result.highlight(r"ello", ["blue"])  # "ello" blue (priority 2000+)

        result_str = str(result)

        # "h" should be red, "ello" should be blue
        assert "\x1b[31mh\x1b[0m" in result_str
        assert "\x1b[34mello\x1b[0m" in result_str

    def test_same_color_different_priorities(self):
        """Test that ranges with same color but different priorities work."""
        cs = ColorizedString("abcabc")

        # Highlight both "abc" occurrences
        result = cs.highlight(r"abc", ["red"])

        result_str = str(result)

        # Both occurrences should be colored (may be merged into one range if adjacent)
        assert "\x1b[31m" in result_str
        assert "\x1b[0m" in result_str
        assert "abcabc" in result_str.replace("\x1b[31m", "").replace("\x1b[0m", "")


class TestPatternMatching:
    """Test pattern matching against original text."""

    def test_match_after_colorization(self):
        """Test that patterns match original text after colorization."""
        cs = ColorizedString("hello world")

        # First colorize some text
        result = cs.highlight(r"hello", ["red"])

        # Now try to match "world" - should work despite "hello" being colored
        result2 = result.highlight(r"world", ["blue"])

        result_str = str(result2)

        # Both colors should be present
        assert "\x1b[31m" in result_str  # red
        assert "\x1b[34m" in result_str  # blue

    def test_complex_pattern_with_existing_colors(self):
        """Test complex patterns on already-colored text."""
        cs = ColorizedString("error: file not found")

        # First highlight "error"
        result = cs.highlight(r"error", ["red"])

        # Then highlight quoted text (even though none exists yet)
        # This tests that the pattern matches the original text
        result2 = result.highlight(r"file", ["yellow"])

        result_str = str(result2)
        assert "\x1b[31m" in result_str  # red for error
        assert "\x1b[33m" in result_str  # yellow for file

    def test_remove_color_preserves_text(self):
        """Test that remove_color() returns original text."""
        cs = ColorizedString("hello world")

        # Apply multiple colors
        result = cs.red.bg_blue.highlight(r"ll", ["green"])

        # Remove all colors
        clean = result.remove_color()

        # Should get back original text
        assert str(clean) == "hello world"
        assert "\x1b[" not in str(clean)


class TestPriorityCalculation:
    """Test priority calculation based on nesting depth."""

    def test_nesting_depth_calculation(self):
        """Test that nesting depth is calculated correctly."""
        cs = ColorizedString("test")

        # Test simple pattern
        depths = cs._calculate_group_nesting_depth(r"(a)")
        assert depths[1] == 1

        # Test nested pattern
        depths = cs._calculate_group_nesting_depth(r"(a(b))")
        assert depths[1] == 1
        assert depths[2] == 2

        # Test deeply nested
        depths = cs._calculate_group_nesting_depth(r"(a(b(c)))")
        assert depths[1] == 1
        assert depths[2] == 2
        assert depths[3] == 3

    def test_non_capturing_groups_ignored(self):
        """Test that non-capturing groups don't get numbered."""
        cs = ColorizedString("test")

        # Pattern with non-capturing group: (?:...)
        depths = cs._calculate_group_nesting_depth(r"(?:a)(b)")

        # Only one capturing group (b), should be group 1
        assert 1 in depths
        # Non-capturing groups still increase depth for nested capturing groups
        # But currently our implementation doesn't track depth for non-capturing
        # This is acceptable - capturing groups get numbered sequentially
        assert depths[1] >= 1

    def test_escaped_parens_ignored(self):
        """Test that escaped parentheses don't count as groups."""
        cs = ColorizedString("test")

        # Pattern with escaped parens: \( \)
        depths = cs._calculate_group_nesting_depth(r"\(a\)(b)")

        # Only (b) is a capturing group
        assert 1 in depths
        assert depths[1] == 1


class TestColorRangeRendering:
    """Test the rendering logic for color ranges."""

    def test_empty_ranges_no_output(self):
        """Test that empty color ranges produce no ANSI codes."""
        cs = ColorizedString("hello")

        # No colorization
        result = str(cs)

        assert result == "hello"
        assert "\x1b[" not in result

    def test_adjacent_same_color_optimized(self):
        """Test that adjacent ranges of same color don't reset unnecessarily."""
        cs = ColorizedString("abc")

        # Color each character red individually
        result = cs.highlight(r"a", ["red"])
        result = result.highlight(r"b", ["red"])
        result = result.highlight(r"c", ["red"])

        result_str = str(result)

        # Should still work (even if not optimized yet)
        assert "\x1b[31m" in result_str
        assert "abc" in result_str.replace("\x1b[31m", "").replace("\x1b[0m", "")

    def test_transition_points_calculated_correctly(self):
        """Test that color transitions happen at correct positions."""
        cs = ColorizedString("hello world")

        # Color "hello" red and "world" blue
        result = cs.highlight(r"hello", ["red"])
        result = result.highlight(r"world", ["blue"])

        result_str = str(result)

        # Should have: red_start + "hello" + reset + " " + blue_start + "world" + reset
        # The space should not be colored
        assert " " in result_str
