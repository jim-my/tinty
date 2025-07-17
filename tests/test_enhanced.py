"""
Tests for the enhanced colorization API.
"""

from tinty.enhanced import C, ColorContext, ColorString, colored, txt


class TestColorString:
    """Test ColorString class functionality."""

    def test_initialization(self):
        """Test ColorString initialization."""
        cs = ColorString("hello")
        assert str(cs) == "hello"
        assert isinstance(cs, str)
        assert isinstance(cs, ColorString)

    def test_empty_initialization(self):
        """Test ColorString with empty string."""
        cs = ColorString()
        assert str(cs) == ""
        assert isinstance(cs, ColorString)

    def test_colorize_method(self):
        """Test basic colorize method."""
        cs = ColorString("hello")
        result = cs.colorize("red")

        assert isinstance(result, ColorString)
        assert str(result) == "\033[31mhello\033[0m"

    def test_method_chaining(self):
        """Test method chaining."""
        cs = ColorString("hello")
        result = cs.red().bold()

        assert isinstance(result, ColorString)
        assert "\033[31m" in str(result)  # Red color
        assert "\033[1m" in str(result)  # Bold/bright

    def test_operator_chaining_pipe(self):
        """Test operator chaining with |."""
        cs = ColorString("hello")
        result = cs | "red" | "bright"

        assert isinstance(result, ColorString)
        assert "\033[31m" in str(result)  # Red color
        assert "\033[1m" in str(result)  # Bold/bright

    def test_operator_chaining_rshift(self):
        """Test operator chaining with >>."""
        cs = ColorString("hello")
        result = cs >> "red" >> "bright"

        assert isinstance(result, ColorString)
        assert "\033[31m" in str(result)  # Red color
        assert "\033[1m" in str(result)  # Bold/bright

    def test_mixed_chaining(self):
        """Test mixing method and operator chaining."""
        cs = ColorString("hello")
        result = (cs.red() | "bright") >> "underline"

        assert isinstance(result, ColorString)
        assert "\033[31m" in str(result)  # Red color
        assert "\033[1m" in str(result)  # Bold/bright
        assert "\033[4m" in str(result)  # Underline

    def test_foreground_colors(self):
        """Test all foreground color methods."""
        cs = ColorString("test")

        colors = {
            "red": "\033[31m",
            "green": "\033[32m",
            "blue": "\033[34m",
            "yellow": "\033[33m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[97m",
            "black": "\033[30m",
        }

        for color_name, ansi_code in colors.items():
            result = getattr(cs, color_name)()
            assert isinstance(result, ColorString)
            assert ansi_code in str(result)
            assert str(result).endswith("\033[0m")  # Reset at end

    def test_background_colors(self):
        """Test background color methods."""
        cs = ColorString("test")

        bg_colors = {
            "bg_red": "\033[41m",
            "bg_green": "\033[42m",
            "bg_blue": "\033[44m",
        }

        for color_name, ansi_code in bg_colors.items():
            result = getattr(cs, color_name)()
            assert isinstance(result, ColorString)
            assert ansi_code in str(result)

    def test_text_styles(self):
        """Test text style methods."""
        cs = ColorString("test")

        styles = {
            "bold": "\033[1m",
            "bright": "\033[1m",
            "dim": "\033[2m",
            "underline": "\033[4m",
            "blink": "\033[5m",
        }

        for style_name, ansi_code in styles.items():
            result = getattr(cs, style_name)()
            assert isinstance(result, ColorString)
            assert ansi_code in str(result)

    def test_complex_chaining(self):
        """Test complex chaining scenarios."""
        cs = ColorString("hello world")

        # Chain multiple colors and styles
        result = cs.red().bold().bg_yellow() | "underline"

        assert isinstance(result, ColorString)
        result_str = str(result)

        # Should contain multiple ANSI codes
        assert "\033[31m" in result_str  # Red
        assert "\033[1m" in result_str  # Bold
        assert "\033[43m" in result_str  # BG Yellow
        assert "\033[4m" in result_str  # Underline

    def test_remove_color(self):
        """Test color removal."""
        cs = ColorString("hello")
        colored = cs.red().bold()
        clean = colored.remove_color()

        assert isinstance(clean, ColorString)
        assert str(clean) == "hello"

    def test_highlight(self):
        """Test text highlighting."""
        cs = ColorString("hello world")
        result = cs.highlight(r"wor", ["blue"])

        assert isinstance(result, ColorString)
        assert "\033[34m" in str(result)  # Blue color

    def test_highlight_at(self):
        """Test position-based highlighting."""
        cs = ColorString("hello")
        result = cs.highlight_at([0, 2])  # Highlight 'h' and 'l'

        assert isinstance(result, ColorString)
        assert "\033[33m" in str(result)  # Default yellow


class TestFactoryFunctions:
    """Test factory functions."""

    def test_colored_function(self):
        """Test colored() factory function."""
        result = colored("hello")

        assert isinstance(result, ColorString)
        assert str(result) == "hello"

    def test_colored_chaining(self):
        """Test chaining with colored()."""
        result = colored("hello").red().bold()

        assert isinstance(result, ColorString)
        assert "\033[31m" in str(result)
        assert "\033[1m" in str(result)

    def test_colored_operators(self):
        """Test operator chaining with colored()."""
        result = colored("hello") | "red" | "bright"

        assert isinstance(result, ColorString)
        assert "\033[31m" in str(result)
        assert "\033[1m" in str(result)

    def test_txt_function(self):
        """Test txt() factory function."""
        result = txt("hello")

        assert isinstance(result, ColorString)
        assert str(result) == "hello"

    def test_txt_chaining(self):
        """Test chaining with txt()."""
        result = txt("world").blue() | "underline"

        assert isinstance(result, ColorString)
        assert "\033[34m" in str(result)
        assert "\033[4m" in str(result)


class TestColorContext:
    """Test ColorContext class."""

    def test_context_initialization(self):
        """Test ColorContext initialization."""
        ctx = ColorContext()
        assert ctx is not None

    def test_direct_color_methods(self):
        """Test direct color method calls."""
        ctx = ColorContext()

        result = ctx.red("hello")
        assert isinstance(result, str)
        assert result == "\033[31mhello\033[0m"

    def test_factory_mode(self):
        """Test factory mode (no color parameter)."""
        ctx = ColorContext()

        result = ctx("hello")
        assert isinstance(result, ColorString)
        assert str(result) == "hello"

    def test_direct_mode(self):
        """Test direct mode (with color parameter)."""
        ctx = ColorContext()

        result = ctx("hello", "red")
        assert isinstance(result, str)
        assert result == "\033[31mhello\033[0m"

    def test_factory_chaining(self):
        """Test chaining from factory mode."""
        ctx = ColorContext()

        result = ctx("hello").red().bold()
        assert isinstance(result, ColorString)
        assert "\033[31m" in str(result)
        assert "\033[1m" in str(result)

    def test_dynamic_color_methods(self):
        """Test dynamic color method generation."""
        ctx = ColorContext()

        # Test various colors
        colors = ["red", "green", "blue", "yellow", "bg_red", "bright"]

        for color in colors:
            method = getattr(ctx, color)
            assert callable(method)

            result = method("test")
            assert isinstance(result, str)
            assert "\033[" in result  # Contains ANSI escape sequence


class TestGlobalObject:
    """Test global C object."""

    def test_global_c_exists(self):
        """Test that global C object exists."""
        assert C is not None
        assert isinstance(C, ColorContext)

    def test_global_c_direct_colors(self):
        """Test C direct color methods."""
        result = C.red("hello")
        assert isinstance(result, str)
        assert result == "\033[31mhello\033[0m"

    def test_global_c_factory(self):
        """Test C as factory function."""
        result = C("hello")
        assert isinstance(result, ColorString)
        assert str(result) == "hello"

    def test_global_c_direct(self):
        """Test C direct colorization."""
        result = C("hello", "blue")
        assert isinstance(result, str)
        assert result == "\033[34mhello\033[0m"

    def test_global_c_chaining(self):
        """Test C factory chaining."""
        result = C("hello").green() | "bright"
        assert isinstance(result, ColorString)
        assert "\033[32m" in str(result)
        assert "\033[1m" in str(result)


class TestUsagePatterns:
    """Test realistic usage patterns."""

    def test_pathlib_like_chaining(self):
        """Test Pathlib-inspired chaining patterns."""
        # Similar to Path("/") / "home" / "user"
        result = colored("Error:") | "red" | "bright"

        assert isinstance(result, ColorString)
        assert "\033[31m" in str(result)
        assert "\033[1m" in str(result)

    def test_mixed_api_usage(self):
        """Test mixing different API styles."""
        # Using multiple interfaces together
        error_msg = C("ERROR:", "red")
        warning_msg = colored("WARNING").yellow().bold()
        info_msg = txt("INFO") >> "blue"

        assert "ERROR:" in error_msg
        assert "\033[31m" in error_msg

        assert isinstance(warning_msg, ColorString)
        assert "\033[33m" in str(warning_msg)

        assert isinstance(info_msg, ColorString)
        assert "\033[34m" in str(info_msg)

    def test_real_world_scenarios(self):
        """Test real-world usage scenarios."""
        # Log level coloring
        levels = {
            "DEBUG": C("DEBUG", "dim"),
            "INFO": colored("INFO").blue(),
            "WARNING": txt("WARNING") | "yellow" | "bright",
            "ERROR": ColorString("ERROR").red().bold().bg_white(),
        }

        for level, colored_level in levels.items():
            level_str = str(colored_level)
            assert level in level_str
            assert "\033[" in level_str  # Has ANSI codes

    def test_performance_chaining(self):
        """Test that chaining doesn't create excessive objects."""
        # Each operation should return a new ColorString
        base = colored("test")
        step1 = base.red()
        step2 = step1.bold()
        step3 = step2 | "underline"

        # Each should be a different object
        assert base is not step1
        assert step1 is not step2
        assert step2 is not step3

        # But all should be ColorString instances
        assert all(isinstance(obj, ColorString) for obj in [base, step1, step2, step3])


class TestBackwardCompatibility:
    """Test that new API doesn't break existing functionality."""

    def test_can_import_legacy_api(self):
        """Test that legacy API still works."""
        from tinty import Colorize, ColorizedString
        from tinty.colorize import colorize  # Import the function directly

        # Test legacy colorizer
        colorizer = Colorize()
        result = colorizer.colorize("hello", "red")
        assert result == "\033[31mhello\033[0m"

        # Test legacy ColorizedString
        cs = ColorizedString("hello")
        result = cs.colorize("blue")
        assert "\033[34m" in str(result)

        # Test legacy function
        result = colorize.colorize("hello", "green")
        assert result == "\033[32mhello\033[0m"

    def test_legacy_and_enhanced_interop(self):
        """Test that legacy and enhanced APIs can work together."""
        from tinty.colorize import colorize

        # Use legacy function result with enhanced API
        legacy_result = colorize.colorize("hello", "red")
        enhanced = colored(legacy_result).bold()

        assert isinstance(enhanced, ColorString)
        assert "\033[31m" in str(enhanced)  # Original red
        assert "\033[1m" in str(enhanced)  # Added bold
