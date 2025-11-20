"""
Tests for color name normalization.
"""

from tinty import ColorizedString


class TestColorNormalization:
    """Test that both color_bg and bg_color formats work."""

    def test_normalize_red_bg_to_bg_red(self):
        """Test that red_bg is normalized to bg_red."""
        cs = ColorizedString("test")
        normalized = cs._normalize_color_name("red_bg")
        assert normalized == "bg_red"

    def test_normalize_blue_bg_to_bg_blue(self):
        """Test that blue_bg is normalized to bg_blue."""
        cs = ColorizedString("test")
        normalized = cs._normalize_color_name("blue_bg")
        assert normalized == "bg_blue"

    def test_normalize_already_correct_format(self):
        """Test that bg_red stays as bg_red."""
        cs = ColorizedString("test")
        normalized = cs._normalize_color_name("bg_red")
        assert normalized == "bg_red"

    def test_normalize_foreground_unchanged(self):
        """Test that foreground colors are not changed."""
        cs = ColorizedString("test")
        assert cs._normalize_color_name("red") == "red"
        assert cs._normalize_color_name("blue") == "blue"
        assert cs._normalize_color_name("fg_red") == "fg_red"

    def test_normalize_case_insensitive(self):
        """Test that normalization is case insensitive."""
        cs = ColorizedString("test")
        normalized = cs._normalize_color_name("RED_BG")
        assert normalized == "bg_red"

    def test_red_bg_renders_correctly(self):
        """Test that red_bg actually renders with red background."""
        cs = ColorizedString("hello")
        result = cs.highlight(r"hello", ["red_bg"])

        result_str = str(result)

        # Should contain bg_red ANSI code (41)
        assert "\x1b[41m" in result_str
        assert "hello" in result_str

    def test_both_formats_produce_same_output(self):
        """Test that red_bg and bg_red produce identical output."""
        cs = ColorizedString("hello world")

        result1 = cs.highlight(r"hello", ["red_bg"])
        result2 = cs.highlight(r"hello", ["bg_red"])

        # Both should produce identical ANSI output
        assert str(result1) == str(result2)

    def test_mixed_format_colorization(self):
        """Test using both formats in the same highlight."""
        cs = ColorizedString("hello world")

        # Use red_bg for first group, bg_blue for second
        result = cs.highlight(r"(hello) (world)", ["red_bg", "bg_blue"])

        result_str = str(result)

        # Should contain both background colors
        assert "\x1b[41m" in result_str  # bg_red
        assert "\x1b[44m" in result_str  # bg_blue

    def test_normalize_with_foreground_and_background(self):
        """Test normalization doesn't affect fg colors."""
        cs = ColorizedString("test")

        # Background gets normalized
        assert cs._normalize_color_name("red_bg") == "bg_red"

        # Foreground stays the same
        assert cs._normalize_color_name("red") == "red"
        assert cs._normalize_color_name("fg_red") == "fg_red"

    def test_colorize_method_with_red_bg(self):
        """Test that colorize method handles red_bg format."""
        cs = ColorizedString("hello")
        result = cs.colorize("red_bg")

        # Check it was normalized in storage
        assert len(result._color_ranges) == 1
        assert result._color_ranges[0].color == "bg_red"

        # Check it renders correctly
        assert "\x1b[41m" in str(result)
