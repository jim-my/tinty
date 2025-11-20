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
