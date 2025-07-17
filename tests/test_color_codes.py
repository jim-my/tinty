"""
Tests for color codes module.
"""

from tinty.color_codes import ColorCode, ColorManager, color_manager


class TestColorCode:
    """Test ColorCode enum."""

    def test_color_code_values(self):
        """Test that color codes have correct values."""
        assert ColorCode.NO_COLOR == 0
        assert ColorCode.RESET == 0
        assert ColorCode.BRIGHT == 1
        assert ColorCode.FG_RED == 31
        assert ColorCode.FG_GREEN == 32
        assert ColorCode.BG_RED == 41
        assert ColorCode.BG_GREEN == 42

    def test_color_code_names(self):
        """Test color code names."""
        assert ColorCode.FG_RED.name == "FG_RED"
        assert ColorCode.BG_BLUE.name == "BG_BLUE"


class TestColorManager:
    """Test ColorManager class."""

    def test_initialization(self):
        """Test ColorManager initialization."""
        cm = ColorManager()
        assert cm is not None
        assert cm._color_map is not None

    def test_color_map_construction(self):
        """Test color map is built correctly."""
        cm = ColorManager()

        # Test that fg_ colors have aliases
        assert cm.get_color_code("red") == ColorCode.FG_RED
        assert cm.get_color_code("fg_red") == ColorCode.FG_RED
        assert cm.get_color_code("blue") == ColorCode.FG_BLUE
        assert cm.get_color_code("fg_blue") == ColorCode.FG_BLUE

    def test_get_color_code(self):
        """Test getting color codes by name."""
        cm = ColorManager()

        # Test valid colors
        assert cm.get_color_code("red") == ColorCode.FG_RED
        assert cm.get_color_code("RED") == ColorCode.FG_RED  # Case insensitive
        assert cm.get_color_code("fg_red") == ColorCode.FG_RED
        assert cm.get_color_code("bg_red") == ColorCode.BG_RED

        # Test invalid color
        assert cm.get_color_code("invalid_color") is None

    def test_start_color(self):
        """Test ANSI start sequence generation."""
        cm = ColorManager()

        assert cm.start_color(ColorCode.FG_RED) == "\033[31m"
        assert cm.start_color(ColorCode.BG_BLUE) == "\033[44m"
        assert cm.start_color(ColorCode.BRIGHT) == "\033[1m"

    def test_end_color(self):
        """Test ANSI end sequence generation."""
        cm = ColorManager()
        assert cm.end_color() == "\033[0m"

    def test_colorize(self):
        """Test text colorization."""
        cm = ColorManager()

        result = cm.colorize("hello", ColorCode.FG_RED)
        assert result == "\033[31mhello\033[0m"

        result = cm.colorize("world", ColorCode.BG_BLUE)
        assert result == "\033[44mworld\033[0m"

    def test_get_foreground_colors(self):
        """Test getting foreground colors."""
        cm = ColorManager()
        fg_colors = cm.get_foreground_colors()

        assert "fg_red" in fg_colors
        assert "fg_green" in fg_colors
        assert "fg_blue" in fg_colors
        assert "bg_red" not in fg_colors

        # Excluded colors
        assert "fg_black" not in fg_colors
        assert "fg_darkgray" not in fg_colors

    def test_get_background_colors(self):
        """Test getting background colors."""
        cm = ColorManager()
        bg_colors = cm.get_background_colors()

        assert "bg_red" in bg_colors
        assert "bg_green" in bg_colors
        assert "bg_blue" in bg_colors
        assert "fg_red" not in bg_colors

    def test_get_all_colors(self):
        """Test getting all colors."""
        cm = ColorManager()
        all_colors = cm.get_all_colors()

        fg_colors = cm.get_foreground_colors()
        bg_colors = cm.get_background_colors()

        assert len(all_colors) == len(fg_colors) + len(bg_colors)
        assert all(color in all_colors for color in fg_colors)
        assert all(color in all_colors for color in bg_colors)

    def test_generate_random_color(self):
        """Test random color generation."""
        cm = ColorManager()

        # Test with seed
        color1 = cm.generate_random_color(0)
        color2 = cm.generate_random_color(0)
        assert color1 == color2  # Should be same with same seed

        # Test without seed
        color3 = cm.generate_random_color()
        assert isinstance(color3, ColorCode)
        assert color3 in [
            ColorCode.FG_LIGHTRED,
            ColorCode.FG_GREEN,
            ColorCode.FG_BLUE,
            ColorCode.FG_MAGENTA,
            ColorCode.FG_CYAN,
            ColorCode.FG_DARKGRAY,
            ColorCode.FG_LIGHTGREEN,
            ColorCode.FG_LIGHTYELLOW,
            ColorCode.FG_LIGHTBLUE,
            ColorCode.FG_LIGHTMAGENTA,
        ]

    def test_remove_color(self):
        """Test ANSI color removal."""
        cm = ColorManager()

        # Test basic color removal
        colored_text = "\033[31mhello\033[0m"
        clean_text = cm.remove_color(colored_text)
        assert clean_text == "hello"

        # Test multiple colors
        colored_text = "\033[31mred\033[0m \033[32mgreen\033[0m"
        clean_text = cm.remove_color(colored_text)
        assert clean_text == "red green"

        # Test text without colors
        plain_text = "hello world"
        clean_text = cm.remove_color(plain_text)
        assert clean_text == "hello world"

    def test_get_color_names(self):
        """Test getting color names."""
        cm = ColorManager()
        names = cm.get_color_names()

        assert isinstance(names, list)
        assert len(names) > 0
        assert "red" in names
        assert "fg_red" in names
        assert "bg_red" in names


class TestGlobalColorManager:
    """Test global color manager instance."""

    def test_global_instance(self):
        """Test that global instance is available."""
        assert color_manager is not None
        assert isinstance(color_manager, ColorManager)

    def test_global_instance_functionality(self):
        """Test global instance works correctly."""
        result = color_manager.colorize("test", ColorCode.FG_RED)
        assert result == "\033[31mtest\033[0m"
