"""
Tests for colorize module.
"""

import pytest

from tinty.color_codes import ColorCode
from tinty.tinty import Colorize, ColorizedString


class TestColorize:
    """Test Colorize class."""

    def test_initialization(self):
        """Test Colorize initialization."""
        colorizer = Colorize()
        assert colorizer is not None
        assert colorizer._color_manager is not None

    def test_colorize_with_color_code(self):
        """Test colorizing with ColorCode enum."""
        colorizer = Colorize()

        result = colorizer.colorize("hello", ColorCode.FG_RED)
        assert result == "\033[31mhello\033[0m"

        result = colorizer.colorize("world", ColorCode.BG_BLUE)
        assert result == "\033[44mworld\033[0m"

    def test_colorize_with_string(self):
        """Test colorizing with string color name."""
        colorizer = Colorize()

        result = colorizer.colorize("hello", "red")
        assert result == "\033[31mhello\033[0m"

        result = colorizer.colorize("world", "bg_blue")
        assert result == "\033[44mworld\033[0m"

    def test_colorize_invalid_color(self):
        """Test colorizing with invalid color name."""
        colorizer = Colorize()

        with pytest.raises(ValueError, match="Unknown color: invalid_color"):
            colorizer.colorize("hello", "invalid_color")

    def test_colorize_random(self):
        """Test random colorization."""
        colorizer = Colorize()

        # Test with seed
        result1 = colorizer.colorize_random("hello", 0)
        result2 = colorizer.colorize_random("hello", 0)
        assert result1 == result2  # Should be same with same seed

        # Test without seed
        result3 = colorizer.colorize_random("hello")
        assert result3.startswith("\033[")
        assert result3.endswith("\033[0m")
        assert "hello" in result3

    def test_remove_color(self):
        """Test color removal."""
        colorizer = Colorize()

        colored_text = "\033[31mhello\033[0m world"
        clean_text = colorizer.remove_color(colored_text)
        assert clean_text == "hello world"

    def test_start_color(self):
        """Test start color sequence."""
        colorizer = Colorize()

        assert colorizer.start_color(ColorCode.FG_RED) == "\033[31m"
        assert colorizer.start_color("red") == "\033[31m"

        with pytest.raises(ValueError, match="Unknown color: invalid"):
            colorizer.start_color("invalid")

    def test_end_color(self):
        """Test end color sequence."""
        colorizer = Colorize()
        assert colorizer.end_color() == "\033[0m"

    def test_get_color_names(self):
        """Test getting color names."""
        colorizer = Colorize()
        names = colorizer.get_color_names()

        assert isinstance(names, list)
        assert "red" in names
        assert "fg_red" in names

    def test_dynamic_color_attributes(self):
        """Test dynamic color attribute access."""
        colorizer = Colorize()

        assert colorizer.red == "\033[31m"
        assert colorizer.green == "\033[32m"
        assert colorizer.fg_blue == "\033[34m"

        with pytest.raises(AttributeError):
            _ = colorizer.invalid_color


class TestColorizedString:
    """Test ColorizedString class."""

    def test_initialization(self):
        """Test ColorizedString initialization."""
        cs = ColorizedString("hello")
        assert str(cs) == "hello"
        assert cs._colorizer is not None

    def test_colorize(self):
        """Test colorizing ColorizedString."""
        cs = ColorizedString("hello")

        result = cs.colorize(ColorCode.FG_RED)
        assert isinstance(result, ColorizedString)
        assert str(result) == "\033[31mhello\033[0m"

        result = cs.colorize("blue")
        assert str(result) == "\033[34mhello\033[0m"

    def test_colorize_random(self):
        """Test random colorization of ColorizedString."""
        cs = ColorizedString("hello")

        result1 = cs.colorize_random(0)
        result2 = cs.colorize_random(0)
        assert str(result1) == str(result2)  # Same seed should give same result

        result3 = cs.colorize_random()
        assert isinstance(result3, ColorizedString)
        assert str(result3).startswith("\033[")
        assert str(result3).endswith("\033[0m")

    def test_remove_color(self):
        """Test color removal from ColorizedString."""
        cs = ColorizedString("\033[31mhello\033[0m world")
        clean = cs.remove_color()

        assert isinstance(clean, ColorizedString)
        assert str(clean) == "hello world"

    def test_highlight_simple_pattern(self):
        """Test highlighting with simple pattern."""
        cs = ColorizedString("hello world")

        # Test highlighting 'l' characters
        result = cs.highlight(r"l", ["red"])
        assert isinstance(result, ColorizedString)

        # Should contain color codes
        result_str = str(result)
        assert "\033[31m" in result_str  # Red color
        assert "\033[0m" in result_str  # Reset

    def test_highlight_with_groups(self):
        """Test highlighting with regex groups."""
        cs = ColorizedString("hello world")

        # Test highlighting with groups
        result = cs.highlight(r"(h)(ello)", ["red", "blue"])
        result_str = str(result)

        # Should contain both colors
        assert "\033[31m" in result_str  # Red for first group
        assert "\033[34m" in result_str  # Blue for second group
        assert "\033[0m" in result_str  # Reset

    def test_highlight_multiple_colors(self):
        """Test highlighting with multiple colors."""
        cs = ColorizedString("hello world")

        result = cs.highlight(r"(l)", ["red", "green", "blue"])
        result_str = str(result)

        # Should contain color codes
        assert "\033[" in result_str
        assert "\033[0m" in result_str

    def test_highlight_no_match(self):
        """Test highlighting with no matches."""
        cs = ColorizedString("hello world")

        result = cs.highlight(r"xyz", ["red"])
        assert str(result) == "hello world"  # Should be unchanged

    def test_highlight_at(self):
        """Test highlighting at specific positions."""
        cs = ColorizedString("hello")

        result = cs.highlight_at([0, 2], "fg_yellow")
        result_str = str(result)

        # Should contain yellow color and swap color
        assert "\033[33m" in result_str  # Yellow
        assert "\033[7m" in result_str  # Swap
        assert "\033[0m" in result_str  # Reset

    def test_highlight_at_empty(self):
        """Test highlighting at empty positions."""
        cs = ColorizedString("hello")

        result = cs.highlight_at([], "fg_yellow")
        assert str(result) == "hello"  # Should be unchanged

    def test_highlight_at_out_of_bounds(self):
        """Test highlighting at out of bounds positions."""
        cs = ColorizedString("hello")

        result = cs.highlight_at([10, 20], "fg_yellow")
        assert str(result) == "hello"  # Should be unchanged

    def test_dynamic_color_methods(self):
        """Test dynamic color methods on ColorizedString."""
        cs = ColorizedString("hello")

        red_result = cs.red
        assert isinstance(red_result, ColorizedString)
        assert str(red_result) == "\033[31mhello\033[0m"

        green_result = cs.green
        assert isinstance(green_result, ColorizedString)
        assert str(green_result) == "\033[32mhello\033[0m"

        with pytest.raises(AttributeError):
            _ = cs.invalid_color

    def test_preserve_256_color_foreground(self):
        """Test that 256-color foreground codes are preserved."""
        # ANSI 256-color: ESC[38;5;NmESC[0m where N is 0-255
        text_with_256color = "\x1b[38;5;123mHello\x1b[0m World"
        cs = ColorizedString(text_with_256color)

        # The 256-color code should be preserved
        result = str(cs)
        assert "Hello" in result
        assert "World" in result
        # Should preserve the 256-color sequence, not misinterpret it
        assert "\x1b[5m" not in result  # Should NOT become 'blink'
        assert "\x1b[38;5;123m" in result  # Should preserve 256-color code

    def test_preserve_256_color_background(self):
        """Test that 256-color background codes are preserved."""
        # ANSI 256-color background: ESC[48;5;Nm
        text_with_256color = "\x1b[48;5;200mHello\x1b[0m World"
        cs = ColorizedString(text_with_256color)

        result = str(cs)
        assert "Hello" in result
        assert "\x1b[48;5;200m" in result  # Should preserve 256-color background

    def test_preserve_truecolor_foreground(self):
        """Test that 24-bit truecolor foreground codes are preserved."""
        # ANSI truecolor: ESC[38;2;R;G;Bm
        text_with_truecolor = "\x1b[38;2;255;100;50mHello\x1b[0m World"
        cs = ColorizedString(text_with_truecolor)

        result = str(cs)
        assert "Hello" in result
        assert "\x1b[38;2;255;100;50m" in result  # Should preserve truecolor

    def test_preserve_truecolor_background(self):
        """Test that 24-bit truecolor background codes are preserved."""
        # ANSI truecolor background: ESC[48;2;R;G;Bm
        text_with_truecolor = "\x1b[48;2;100;150;200mHello\x1b[0m World"
        cs = ColorizedString(text_with_truecolor)

        result = str(cs)
        assert "Hello" in result
        assert "\x1b[48;2;100;150;200m" in result  # Should preserve truecolor

    def test_pipeline_composition_with_256_color(self):
        """Test that 256-color codes survive pipeline composition."""
        # Simulate upstream coloring with 256-color, then downstream highlighting
        upstream_colored = "\x1b[38;5;123mHello World\x1b[0m"
        cs = ColorizedString(upstream_colored)

        # Add additional highlighting
        result = cs.highlight(r"World", ["bg_blue"])
        result_str = str(result)

        # Both the original 256-color AND the new bg_blue should be present
        assert "\x1b[38;5;123m" in result_str  # Original 256-color preserved
        assert "\x1b[44m" in result_str  # New background color applied

    def test_extended_colors_with_leading_attributes(self):
        """Extended colors with leading attributes (e.g., reset/bold) are preserved."""
        text = "\x1b[0;38;5;123mHello\x1b[0m"
        cs = ColorizedString(text)
        assert "\x1b[38;5;123m" in str(cs)

        text_bg = "\x1b[1;48;5;200mHello\x1b[0m"
        cs_bg = ColorizedString(text_bg)
        assert "\x1b[48;5;200m" in str(cs_bg)

        text_true = "\x1b[0;38;2;255;100;50mHello\x1b[0m"
        cs_true = ColorizedString(text_true)
        assert "\x1b[38;2;255;100;50m" in str(cs_true)

    def test_combined_extended_foreground_background_preserved(self):
        """Combined fg+bg extended sequences should preserve both channels."""
        text = "\x1b[38;5;123;48;5;231mHello\x1b[0m"
        cs = ColorizedString(text)
        rendered = str(cs)
        assert "\x1b[38;5;123m" in rendered
        assert "\x1b[48;5;231m" in rendered

    def test_highlight_preserves_other_channel_for_extended_colors(self):
        """Changing one channel should not drop the other extended channel."""
        text = "\x1b[38;5;123;48;5;231mHello\x1b[0m"
        cs = ColorizedString(text)

        # Change foreground only
        fg_result = cs.highlight(r"Hello", ["red"])
        fg_str = str(fg_result)
        assert "\x1b[31m" in fg_str
        assert "\x1b[48;5;231m" in fg_str  # Background preserved

        # Change background only
        bg_result = cs.highlight(r"Hello", ["bg_blue"])
        bg_str = str(bg_result)
        assert "\x1b[44m" in bg_str
        assert "\x1b[38;5;123m" in bg_str  # Foreground preserved


class TestHighlightingEdgeCases:
    """Test edge cases for highlighting functionality."""

    def test_highlight_overlapping_groups(self):
        """Test highlighting with overlapping groups."""
        cs = ColorizedString("abcdef")

        # Pattern with two separate groups
        result = cs.highlight(r"(abc)(def)", ["red", "blue"])
        result_str = str(result)

        # Should handle groups properly
        assert "\033[31m" in result_str or "\033[34m" in result_str
        assert "\033[0m" in result_str

    def test_highlight_empty_string(self):
        """Test highlighting empty string."""
        cs = ColorizedString("")

        result = cs.highlight(r".*", ["red"])
        # Empty strings produce empty ranges which are not colored
        assert str(result) == ""

    def test_highlight_special_regex_chars(self):
        """Test highlighting with special regex characters."""
        cs = ColorizedString("hello.world")

        # Literal dot
        result = cs.highlight(r"\.", ["red"])
        result_str = str(result)

        assert "\033[31m" in result_str
        assert "\033[0m" in result_str

    def test_highlight_case_insensitive(self):
        """Test case insensitive highlighting."""
        cs = ColorizedString("Hello World")

        # Should match both 'H' and 'h' patterns
        result = cs.highlight(r"h", ["red"])
        result_str = str(result)

        # Should contain color codes (case insensitive by default)
        assert "\033[31m" in result_str
        assert "\033[0m" in result_str


class TestNamedGroupsNestingDepth:
    """Test nesting depth calculation for named groups and lookarounds."""

    def test_named_groups_get_proper_depth(self):
        """Test that named capturing groups get proper nesting depth.

        This test demonstrates TODO.md issue #2: _calculate_group_nesting_depth
        treats (?P<name>...) as non-capturing, but it actually creates a
        capture group that should have proper depth tracking.
        """
        # Pattern with outer regular group and inner named group
        # (outer (?P<inner>text))
        # Expected: inner named group should have depth=2, outer has depth=1
        text = "outer inner"
        cs = ColorizedString(text)

        # Apply nested pattern: outer group blue, inner named group red
        # If bug exists: inner might not get depth=2, so blue might win
        result = cs.highlight(r"(outer ((?P<word>\w+)))", ["blue", "green", "red"])
        result_str = str(result)

        # "inner" should be red (depth=3 for innermost group)
        # If bug exists, it might be blue or green
        import re

        match = re.search(r"\033\[(\d+)m(inner)", result_str)
        assert match is not None, "Could not find colored 'inner' in output"

        color_code = match.group(1)
        assert color_code == "31", (  # Red is color code 31
            f"Expected 'inner' to be red (31) due to deepest nesting, "
            f"but got color code {color_code}. "
            f"Named groups may not be getting proper nesting depth."
        )

    def test_lookahead_does_not_create_capture_group(self):
        """Test that lookahead assertions don't create capture groups."""
        # Pattern with lookahead: (foo)(?=bar)
        # The lookahead (?=bar) should NOT increment group number
        text = "foobar"
        cs = ColorizedString(text)

        # Color the first (and only) capture group
        result = cs.highlight(r"(foo)(?=bar)", ["red"])
        result_str = str(result)

        # "foo" should be red
        assert "\033[31m" in result_str
        assert "foo" in result_str

    def test_complex_named_groups_with_non_capturing(self):
        """Test complex pattern with mix of named, non-capturing, and regular groups."""
        # Pattern: (outer (?:non-cap (?P<named>inner)))
        # Group 1: outer ... (depth=1)
        # No group for (?:...) - non-capturing
        # Group 2: named group (depth=3, nested inside non-capturing and outer)
        text = "outer non-cap inner"
        cs = ColorizedString(text)

        result = cs.highlight(r"(outer (?:non-cap )(?P<named>inner))", ["blue", "red"])
        result_str = str(result)

        # "inner" should be red (group 2, highest depth)
        import re

        match = re.search(r"\033\[(\d+)m(inner)", result_str)
        assert match is not None

        color_code = match.group(1)
        assert color_code == "31"  # Red
