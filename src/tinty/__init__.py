"""
Colorize - A Python library for terminal text colorization and highlighting.

This library provides ANSI color code functionality for Python strings,
similar to the Ruby colorize gem.

Enhanced API for production use:
    from colorize import colored, C, ColorString

    # Fluent chaining
    colored("hello").red().bold()

    # Operator chaining
    colored("world") | "blue" | "underline"

    # Global convenience object
    C.red("hello")
    C("hello").red().bold()

Legacy API (still supported):
    from colorize import Colorize, ColorizedString

    colorizer = Colorize()
    colored_text = colorizer.colorize("hello", "red")
"""

# Enhanced production-safe API (recommended)
from .colors import *  # noqa: F403,F401
from .enhanced import (
    C,
    ColorContext,
    ColorString,
    colored,
    txt,
)

# Legacy API (backward compatibility)
from .color_codes import ColorCode, ColorManager, color_manager
from .colorize import Colorize, ColorizedString, colorize
# Note: string_extensions module removed - use enhanced API or core classes directly

__version__ = "0.1.0"

# Export enhanced API as primary interface
from .colors import __all__ as _colors_all

__all__ = [
    # Enhanced API (recommended)
    "C",
    "ColorContext", 
    "ColorString",
    "colored",
    "txt",
    # Legacy API (backward compatibility)
    "ColorCode",
    "ColorManager",
    "Colorize",
    "ColorizedString",
    "color_manager",
    "colorize",
] + _colors_all
