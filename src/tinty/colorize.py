"""
Core colorization functionality.
"""

import re
from typing import Optional, Union

from .color_codes import ColorCode, ColorManager, color_manager


class Colorize:
    """Main colorization class providing color functionality."""

    def __init__(self, color_manager_instance: Optional[ColorManager] = None) -> None:
        self._color_manager = color_manager_instance or color_manager

    def colorize(self, text: str, color_code: Union[str, ColorCode]) -> str:
        """Colorize text with given color code."""
        if isinstance(color_code, str):
            code = self._color_manager.get_color_code(color_code)
            if code is None:
                raise ValueError(f"Unknown color: {color_code}")
            color_code = code

        return self._color_manager.colorize(text, color_code)

    def colorize_random(self, text: str, code: Optional[int] = None) -> str:
        """Colorize text with random color."""
        color_code = self._color_manager.generate_random_color(code)
        return self._color_manager.colorize(text, color_code)

    def remove_color(self, text: str) -> str:
        """Remove ANSI color codes from text."""
        return self._color_manager.remove_color(text)

    def start_color(self, color_code: Union[str, ColorCode]) -> str:
        """Get ANSI start sequence for color."""
        if isinstance(color_code, str):
            code = self._color_manager.get_color_code(color_code)
            if code is None:
                raise ValueError(f"Unknown color: {color_code}")
            color_code = code

        return self._color_manager.start_color(color_code)

    def end_color(self) -> str:
        """Get ANSI end sequence (reset)."""
        return self._color_manager.end_color()

    def get_color_names(self) -> list[str]:
        """Get all available color names."""
        return self._color_manager.get_color_names()

    def __getattr__(self, name: str) -> str:
        """Dynamic color method support (e.g., colorize.red)."""
        color_code = self._color_manager.get_color_code(name)
        if color_code is not None:
            return self._color_manager.start_color(color_code)

        # Try with fg_ prefix
        color_code = self._color_manager.get_color_code(f"fg_{name}")
        if color_code is not None:
            return self._color_manager.start_color(color_code)

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )


class ColorizedString(str):
    """String subclass with colorization support."""

    def __new__(cls, value: str) -> "ColorizedString":
        return str.__new__(cls, value)

    def __init__(self, value: str) -> None:
        super().__init__()
        self._colorizer = Colorize()
        self._colors_at: dict[int, list[str]] = {}

    def colorize(self, color_code: Union[str, ColorCode]) -> "ColorizedString":
        """Apply color to the string."""
        colored_text = self._colorizer.colorize(str(self), color_code)
        return ColorizedString(colored_text)

    def colorize_random(self, code: Optional[int] = None) -> "ColorizedString":
        """Apply random color to the string."""
        colored_text = self._colorizer.colorize_random(str(self), code)
        return ColorizedString(colored_text)

    def remove_color(self) -> "ColorizedString":
        """Remove color codes from the string."""
        clean_text = self._colorizer.remove_color(str(self))
        return ColorizedString(clean_text)

    def add_color(self, start: int, end: int, color: str) -> None:
        """Add color information for range highlighting."""
        if not color:
            return

        colors = color.split(",")

        if start not in self._colors_at:
            self._colors_at[start] = []
        if end not in self._colors_at:
            self._colors_at[end] = []

        self._colors_at[start].extend(colors)
        self._colors_at[end].insert(0, "no_color")

    def highlight(
        self, pattern: Union[str, re.Pattern], colors: Union[str, list[str]]
    ) -> "ColorizedString":
        """Highlight text matching pattern with given colors."""
        if isinstance(pattern, str):
            pattern = re.compile(pattern, re.IGNORECASE)

        if isinstance(colors, str):
            colors = [colors]

        matches = list(pattern.finditer(str(self)))
        if not matches:
            return ColorizedString(str(self))

        new_self = ColorizedString(str(self))

        # Process matches in reverse order to maintain positions
        for match in reversed(matches):
            if match.lastindex is None or match.lastindex == 0:
                # No groups, highlight entire match
                groups_to_highlight = [0]
            else:
                # Highlight all groups except group 0 (entire match)
                groups_to_highlight = list(range(1, match.lastindex + 1))

            # Sort groups by end position (reverse order)
            groups_data = []
            for grp in groups_to_highlight:
                if match.group(grp) is not None:
                    groups_data.append({
                        "start": match.start(grp),
                        "end": match.end(grp),
                        "group": grp,
                        "text": match.group(grp),
                    })

            groups_data.sort(key=lambda x: (x["end"], x["group"]), reverse=True)

            # Apply colors to each group
            for group_data in groups_data:
                grp = group_data["group"]
                color_index = (grp - 1) % len(colors)
                color = colors[color_index]
                new_self.add_color(group_data["start"], group_data["end"], color)

        # Apply colors
        if new_self._colors_at:
            result = str(new_self)
            for pos in sorted(new_self._colors_at.keys(), reverse=True):
                color_codes = []
                for color_name in new_self._colors_at[pos]:
                    if color_name == "no_color":
                        color_codes.append(new_self._colorizer.end_color())
                    else:
                        try:
                            color_codes.append(
                                new_self._colorizer.start_color(color_name)
                            )
                        except ValueError:
                            continue

                if color_codes:
                    result = result[:pos] + "".join(color_codes) + result[pos:]

            return ColorizedString(result)

        return new_self

    def highlight_at(
        self, positions: list[int], color: str = "fg_yellow"
    ) -> "ColorizedString":
        """Highlight characters at specific positions."""
        if not positions:
            return ColorizedString(str(self))

        result = list(str(self))
        swap_color = self._colorizer.start_color("swapcolor")

        # Apply highlighting in reverse order to maintain positions
        for pos in sorted(set(positions), reverse=True):
            if 0 <= pos < len(result):
                char = result[pos]
                colored_char = f"{self._colorizer.start_color(color)}{swap_color}{char}{self._colorizer.end_color()}"
                result[pos] = colored_char

        return ColorizedString("".join(result))

    def __getattr__(self, name: str) -> "ColorizedString":
        """Dynamic color methods for strings (e.g., "text".red())."""
        color_code = self._colorizer._color_manager.get_color_code(name)
        if color_code is not None:
            return self.colorize(color_code)

        # Try with fg_ prefix
        color_code = self._colorizer._color_manager.get_color_code(f"fg_{name}")
        if color_code is not None:
            return self.colorize(color_code)

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )


# Global colorize instance
colorize = Colorize()
