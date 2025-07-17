"""
Tests for type-safe color constants.
"""

import pytest

from tinty import (
    BG_BLUE,
    BG_RED,
    BG_WHITE,
    BG_YELLOW,
    BLUE,
    BOLD,
    BRIGHT,
    C,
    GREEN,
    RED,
    YELLOW,
    colored,
    txt,
)
from tinty.colors import ALL_COLORS, BACKGROUND_COLORS, FOREGROUND_COLORS, STYLES


class TestColorConstants:
    """Test color constants work with enhanced API."""

    def test_colored_with_constants(self):
        """Test colored() function with type-safe constants."""
        result = colored("Error") | RED | BRIGHT | BG_WHITE
        assert isinstance(result, str)
        assert "\033[31m" in str(result)  # Red
        assert "\033[1m" in str(result)   # Bright
        assert "\033[107m" in str(result)  # BG_WHITE (bright white)

    def test_txt_with_constants(self):
        """Test txt() function with type-safe constants."""
        result = txt("Success") >> GREEN >> BOLD
        assert isinstance(result, str)
        assert "\033[32m" in str(result)  # Green
        assert "\033[1m" in str(result)   # Bold

    def test_c_object_with_constants(self):
        """Test global C object works with constants."""
        # Direct color application
        result = C.red("hello")
        assert "\033[31m" in result

        # Factory pattern with constants
        result = C("hello") | BLUE | BG_YELLOW
        assert "\033[34m" in str(result)  # Blue
        assert "\033[43m" in str(result)  # BG_YELLOW

    def test_mixed_chaining(self):
        """Test mixing method calls and constant chaining."""
        result = colored("Mixed").red() | BRIGHT | BG_BLUE
        assert "\033[31m" in str(result)  # Red
        assert "\033[1m" in str(result)   # Bright
        assert "\033[44m" in str(result)  # BG_BLUE

    def test_constant_values(self):
        """Test that constants have correct string values."""
        assert RED == "fg_red"
        assert GREEN == "fg_green"
        assert BLUE == "fg_blue"
        assert YELLOW == "fg_yellow"
        
        assert BG_WHITE == "bg_white"
        assert BG_BLUE == "bg_blue"
        
        assert BRIGHT == "bright"
        assert BOLD == "bright"  # Alias

    def test_all_constants_work(self):
        """Test that all color constants work with the API."""
        for color in [RED, GREEN, BLUE]:
            result = colored("test") | color
            assert "\033[" in str(result)
            assert "\033[0m" in str(result)

        for bg_color in [BG_WHITE, BG_BLUE]:
            result = colored("test") | bg_color
            assert "\033[" in str(result)
            assert "\033[0m" in str(result)

        for style in [BRIGHT, BOLD]:
            result = colored("test") | style
            assert "\033[" in str(result)
            assert "\033[0m" in str(result)

    def test_constant_collections(self):
        """Test that constant collections are properly defined."""
        assert len(FOREGROUND_COLORS) == 16
        assert len(BACKGROUND_COLORS) == 16
        assert len(STYLES) == 9
        assert len(ALL_COLORS) == len(FOREGROUND_COLORS) + len(BACKGROUND_COLORS) + len(STYLES)

        # Verify some constants are in the right collections
        assert RED in FOREGROUND_COLORS
        assert BG_RED in BACKGROUND_COLORS
        assert BRIGHT in STYLES

    def test_type_safety_example(self):
        """Test example showing type safety benefits."""
        # This would fail type checking with string literals:
        # colored("Error") | "red" | "typo"  # "typo" is not a valid color
        
        # But this works with constants and provides autocompletion:
        result = colored("Error") | RED | BRIGHT
        assert "\033[31m" in str(result)
        assert "\033[1m" in str(result)

    def test_constants_with_legacy_api(self):
        """Test that constants work with legacy API too."""
        from tinty import Colorize, ColorizedString
        
        colorizer = Colorize()
        result = colorizer.colorize("hello", RED)
        assert "\033[31m" in result

        cs = ColorizedString("world")
        result = cs.colorize(BLUE)
        assert "\033[34m" in str(result)


class TestConstantUsagePatterns:
    """Test various usage patterns with constants."""

    def test_error_message_pattern(self):
        """Test typical error message styling."""
        error = colored("ERROR") | RED | BOLD | BG_WHITE
        assert all(code in str(error) for code in ["\033[31m", "\033[1m", "\033[107m"])

    def test_success_message_pattern(self):
        """Test typical success message styling."""
        success = txt("SUCCESS") >> GREEN >> BRIGHT
        assert "\033[32m" in str(success)
        assert "\033[1m" in str(success)

    def test_warning_message_pattern(self):
        """Test typical warning message styling."""
        warning = colored("WARNING") | YELLOW | BOLD
        assert "\033[33m" in str(warning)
        assert "\033[1m" in str(warning)

    def test_info_message_pattern(self):
        """Test typical info message styling."""
        info = txt("INFO") >> BLUE
        assert "\033[34m" in str(info)

    def test_chaining_multiple_constants(self):
        """Test chaining many constants together."""
        # Test | operator chaining
        result1 = colored("Complex") | RED | BRIGHT | BG_YELLOW
        assert "\033[31m" in str(result1)  # Red
        assert "\033[1m" in str(result1)   # Bright
        assert "\033[43m" in str(result1)  # BG_YELLOW
        
        # Test >> operator chaining  
        result2 = txt("Another") >> BLUE >> BOLD
        assert "\033[34m" in str(result2)  # Blue
        assert "\033[1m" in str(result2)   # Bold

    def test_constants_are_immutable(self):
        """Test that constants maintain their values."""
        original_red = RED
        
        # Use the constant
        result = colored("test") | RED
        assert "\033[31m" in str(result)
        
        # Constant should be unchanged
        assert RED == original_red
        assert RED == "fg_red"