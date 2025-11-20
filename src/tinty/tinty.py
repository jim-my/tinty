"""
Core colorization functionality with deferred rendering and proper color nesting.
"""

import re
from dataclasses import dataclass
from typing import Optional, Union

from .color_codes import ColorCode, ColorManager, color_manager

# Priority calculation constants
PIPELINE_STAGE_MULTIPLIER = 1_000_000
NESTING_DEPTH_MULTIPLIER = 1_000

# ANSI SGR code constants for extended colors
ANSI_FG_256_CODE = 38
ANSI_BG_256_CODE = 48
ANSI_256_COLOR_TYPE = 5
ANSI_TRUE_COLOR_TYPE = 2
ANSI_256_COLOR_MIN_PARAMS = 3
ANSI_TRUE_COLOR_MIN_PARAMS = 5


@dataclass
class ColorRange:
    """Represents a range of text with a specific color applied.

    Priority is calculated as:
    priority = (pipeline_stage * 1M) + (nesting_depth * 1K) + application_order

    This ensures:
    - Later pipeline stages override earlier ones
    - More nested regex groups override less nested ones
    - Later applications override earlier ones at same depth
    """

    start: int  # Position in original text (inclusive)
    end: int  # Position in original text (exclusive)
    color: str  # Color name (e.g., 'red', 'bg_blue', 'bold')
    priority: int = 0  # Higher priority wins within same channel
    pipeline_stage: int = 0  # Which pipeline stage this was applied in


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
    """String subclass with colorization support using deferred rendering.

    This class stores the original text and a list of color ranges separately.
    When converted to string, it renders the colors using ANSI codes with proper
    nesting support based on priority.
    """

    def __new__(
        cls,
        value: str,
        original_text: Optional[str] = None,  # noqa: ARG004
        color_ranges: Optional[list[ColorRange]] = None,  # noqa: ARG004
        pipeline_stage: int = 0,  # noqa: ARG004
    ) -> "ColorizedString":
        # If value has ANSI codes, we'll parse them in __init__
        # Parameters needed to match __init__ signature
        return str.__new__(cls, value)

    def __init__(
        self,
        value: str,
        original_text: Optional[str] = None,
        color_ranges: Optional[list[ColorRange]] = None,
        pipeline_stage: int = 0,
    ) -> None:
        super().__init__()
        self._colorizer = Colorize()
        self._next_priority = 0

        # If original_text provided, use it; otherwise parse from value
        if original_text is not None:
            self._original_text = original_text
            self._color_ranges = color_ranges or []
            self._pipeline_stage = pipeline_stage
        else:
            # Parse ANSI codes from value to extract original text and ranges
            self._original_text, self._color_ranges = self._parse_ansi(value)
            # If we parsed any ranges from ANSI codes, we're in a pipeline
            # Start at stage 1 so new highlights have higher priority
            if pipeline_stage == 0 and self._color_ranges:
                self._pipeline_stage = 1
            else:
                self._pipeline_stage = pipeline_stage

        # Legacy support for old _colors_at API (will be removed)
        self._colors_at: dict[int, list[str]] = {}

    @staticmethod
    def _detect_extended_colors(
        codes: list[int],
    ) -> list[tuple[str, str]]:
        """Detect extended color sequences anywhere in the parameter list.

        Scans the entire codes list for 256-color and truecolor subsequences.
        A single CSI can contain multiple colors (e.g., fg and bg together).

        Returns:
            List of (color_name, channel) tuples for each detected color
        """
        results = []
        i = 0

        while i < len(codes):
            # Check for 256-color: 38;5;N (fg) or 48;5;N (bg)
            if i + 2 < len(codes):
                if codes[i] == ANSI_FG_256_CODE and codes[i + 1] == ANSI_256_COLOR_TYPE:
                    # Foreground 256-color
                    color_code = f"38;5;{codes[i + 2]}"
                    results.append((f"__raw_ansi_fg__:{color_code}", "fg"))
                    i += 3
                    continue
                if codes[i] == ANSI_BG_256_CODE and codes[i + 1] == ANSI_256_COLOR_TYPE:
                    # Background 256-color
                    color_code = f"48;5;{codes[i + 2]}"
                    results.append((f"__raw_ansi_bg__:{color_code}", "bg"))
                    i += 3
                    continue

            # Check for truecolor: 38;2;R;G;B (fg) or 48;2;R;G;B (bg)
            if i + 4 < len(codes):
                if (
                    codes[i] == ANSI_FG_256_CODE
                    and codes[i + 1] == ANSI_TRUE_COLOR_TYPE
                ):
                    # Foreground truecolor
                    color_code = f"38;2;{codes[i + 2]};{codes[i + 3]};{codes[i + 4]}"
                    results.append((f"__raw_ansi_fg__:{color_code}", "fg"))
                    i += 5
                    continue
                if (
                    codes[i] == ANSI_BG_256_CODE
                    and codes[i + 1] == ANSI_TRUE_COLOR_TYPE
                ):
                    # Background truecolor
                    color_code = f"48;2;{codes[i + 2]};{codes[i + 3]};{codes[i + 4]}"
                    results.append((f"__raw_ansi_bg__:{color_code}", "bg"))
                    i += 5
                    continue

            # Not an extended color, move to next parameter
            i += 1

        return results

    @staticmethod
    def _close_and_start_color(
        channel: str,
        color_name: str,
        pos: int,
        active_colors: dict[str, tuple[str, int]],
        ranges: list[ColorRange],
    ) -> None:
        """Close previous color in channel (if any) and start new color."""
        # Close previous color in this channel if any
        if channel in active_colors:
            prev_color, start_pos = active_colors[channel]
            if start_pos < pos:
                ranges.append(
                    ColorRange(
                        start=start_pos,
                        end=pos,
                        color=prev_color,
                        priority=0,
                        pipeline_stage=0,
                    )
                )

        # Start new color in this channel
        active_colors[channel] = (color_name, pos)

    def _parse_ansi(self, text: str) -> tuple[str, list[ColorRange]]:
        """Parse ANSI codes from text to extract original text and color ranges.

        Returns:
            (original_text, color_ranges) where original_text has ANSI codes removed
        """
        # Pattern to match ANSI escape sequences
        ansi_pattern = re.compile(r"\x1b\[([0-9;]+)m")

        # Build reverse mapping: ANSI code -> color name
        code_to_color = {}
        for color_name, code_obj in self._colorizer._color_manager._color_map.items():
            code_to_color[code_obj.value] = color_name

        original_text = []
        ranges: list[ColorRange] = []
        active_colors: dict[
            str, tuple[str, int]
        ] = {}  # channel -> (color_name, start_pos)
        pos = 0

        # Split text into segments (text and ANSI codes)
        last_end = 0
        for match in ansi_pattern.finditer(text):
            # Add text before this ANSI code
            segment = text[last_end : match.start()]
            if segment:
                original_text.append(segment)
                pos += len(segment)

            # Parse ANSI code
            code_str = match.group(1)
            codes = [int(c) for c in code_str.split(";") if c]

            # Process codes sequentially to maintain order (reset before color, etc.)
            idx = 0
            while idx < len(codes):
                # Check for extended color sequences at current position
                # 256-color: 38;5;N or 48;5;N
                if idx + 2 < len(codes):
                    if (
                        codes[idx] == ANSI_FG_256_CODE
                        and codes[idx + 1] == ANSI_256_COLOR_TYPE
                    ):
                        # Foreground 256-color
                        color_code = f"38;5;{codes[idx + 2]}"
                        color_name = f"__raw_ansi_fg__:{color_code}"
                        ColorizedString._close_and_start_color(
                            "fg", color_name, pos, active_colors, ranges
                        )
                        idx += 3
                        continue
                    if (
                        codes[idx] == ANSI_BG_256_CODE
                        and codes[idx + 1] == ANSI_256_COLOR_TYPE
                    ):
                        # Background 256-color
                        color_code = f"48;5;{codes[idx + 2]}"
                        color_name = f"__raw_ansi_bg__:{color_code}"
                        ColorizedString._close_and_start_color(
                            "bg", color_name, pos, active_colors, ranges
                        )
                        idx += 3
                        continue

                # Truecolor format: 38;2;R;G;B (foreground) or 48;2;R;G;B (background)
                if idx + 4 < len(codes):
                    if (
                        codes[idx] == ANSI_FG_256_CODE
                        and codes[idx + 1] == ANSI_TRUE_COLOR_TYPE
                    ):
                        # Foreground truecolor
                        color_code = (
                            f"38;2;{codes[idx + 2]};{codes[idx + 3]};{codes[idx + 4]}"
                        )
                        color_name = f"__raw_ansi_fg__:{color_code}"
                        ColorizedString._close_and_start_color(
                            "fg", color_name, pos, active_colors, ranges
                        )
                        idx += 5
                        continue
                    if (
                        codes[idx] == ANSI_BG_256_CODE
                        and codes[idx + 1] == ANSI_TRUE_COLOR_TYPE
                    ):
                        # Background truecolor
                        color_code = (
                            f"48;2;{codes[idx + 2]};{codes[idx + 3]};{codes[idx + 4]}"
                        )
                        color_name = f"__raw_ansi_bg__:{color_code}"
                        ColorizedString._close_and_start_color(
                            "bg", color_name, pos, active_colors, ranges
                        )
                        idx += 5
                        continue

                # Standard codes (reset, basic colors, attributes)
                code = codes[idx]
                if code == 0:
                    # Reset - close all active colors
                    for color_name, start_pos in active_colors.values():
                        if start_pos < pos:
                            ranges.append(
                                ColorRange(
                                    start=start_pos,
                                    end=pos,
                                    color=color_name,
                                    priority=0,  # Parsed from input, pipeline_stage=0
                                    pipeline_stage=0,
                                )
                            )
                    active_colors = {}
                elif code in code_to_color:
                    # Start a new color
                    color_name = code_to_color[code]
                    channel = self._get_color_channel(color_name)
                    ColorizedString._close_and_start_color(
                        channel, color_name, pos, active_colors, ranges
                    )

                idx += 1

            last_end = match.end()

        # Add remaining text after last ANSI code
        if last_end < len(text):
            segment = text[last_end:]
            original_text.append(segment)
            pos += len(segment)

        # Close any remaining active colors
        for color_name, start_pos in active_colors.values():
            if start_pos < pos:
                ranges.append(
                    ColorRange(
                        start=start_pos,
                        end=pos,
                        color=color_name,
                        priority=0,
                        pipeline_stage=0,
                    )
                )

        return "".join(original_text), ranges

    def _normalize_color_name(self, color_name: str) -> str:  # noqa: PLR6301
        """Normalize color names to standard format.

        Converts red_bg -> bg_red, etc.
        """
        color_lower = color_name.lower()

        # Convert color_bg format to bg_color format
        if color_lower.endswith("_bg") and not color_lower.startswith("bg_"):
            # Extract color part (everything except _bg suffix)
            color_part = color_lower[:-3]  # Remove '_bg'
            return f"bg_{color_part}"

        return color_name

    def _get_color_channel(self, color_name: str) -> str:  # noqa: PLR6301
        """Determine which channel a color belongs to: 'fg', 'bg', or 'attr'."""
        color_lower = color_name.lower()
        # Check for raw ANSI passthrough codes
        if color_lower.startswith("__raw_ansi_fg__:"):
            return "fg"
        if color_lower.startswith("__raw_ansi_bg__:"):
            return "bg"
        # Check for background colors (support both bg_red and red_bg formats)
        if color_lower.startswith("bg_") or color_lower.endswith("_bg"):
            return "bg"
        if color_lower in {
            "bright",
            "dim",
            "underline",
            "blink",
            "strikethrough",
            "bold",
            "invert",
            "swapcolor",
            "hidden",
        }:
            return "attr"
        return "fg"

    def _render(self) -> str:
        """Render the original text with color ranges applied as ANSI codes.

        This handles proper nesting by:
        1. Finding all transition points (where any range starts/ends)
        2. For each segment, determining active colors by priority within each channel
        3. Outputting appropriate ANSI codes and text
        """
        if not self._color_ranges:
            return self._original_text

        # Find all transition points
        transitions = {0, len(self._original_text)}
        for range_ in self._color_ranges:
            transitions.add(range_.start)
            transitions.add(range_.end)

        sorted_transitions = sorted(transitions)

        # Build output segment by segment
        result_parts = []
        current_colors: dict[str, Optional[str]] = {
            "fg": None,
            "bg": None,
            "attr": None,
        }

        for i in range(len(sorted_transitions) - 1):  # noqa: PLR1702
            start_pos = sorted_transitions[i]
            end_pos = sorted_transitions[i + 1]

            if start_pos == end_pos:
                continue

            # Find active colors at this position (highest priority in each channel)
            active_ranges = [
                r for r in self._color_ranges if r.start <= start_pos < r.end
            ]

            # Group by channel and pick highest priority
            new_colors: dict[str, Optional[str]] = {
                "fg": None,
                "bg": None,
                "attr": None,
            }
            for channel in ["fg", "bg", "attr"]:
                channel_ranges = [
                    r
                    for r in active_ranges
                    if self._get_color_channel(r.color) == channel
                ]
                if channel_ranges:
                    # Pick highest priority
                    best = max(channel_ranges, key=lambda r: r.priority)
                    new_colors[channel] = best.color

            # Output ANSI codes if colors changed
            if new_colors != current_colors:
                codes = []

                # Build combined ANSI code for all active colors
                for channel in ["fg", "bg", "attr"]:
                    color_name = new_colors[channel]
                    if color_name:
                        # Check for raw ANSI passthrough
                        if color_name.startswith(
                            "__raw_ansi_fg__:"
                        ) or color_name.startswith("__raw_ansi_bg__:"):
                            # Extract the raw ANSI code sequence
                            raw_code = color_name.split(":", 1)[1]
                            codes.append(f"\x1b[{raw_code}m")
                        else:
                            try:
                                # Normalize color name (e.g., red_bg -> bg_red)
                                normalized = self._normalize_color_name(color_name)
                                codes.append(self._colorizer.start_color(normalized))
                            except ValueError:
                                # Invalid color name, skip
                                pass

                # Always reset if we had any previous colors, then apply new ones
                # This ensures clean state
                if current_colors != {"fg": None, "bg": None, "attr": None}:
                    result_parts.append(self._colorizer.end_color())

                # Apply new color codes
                if codes:
                    result_parts.extend(codes)

                current_colors = new_colors

            # Output text segment
            result_parts.append(self._original_text[start_pos:end_pos])

        # Reset at end if we have active colors
        if current_colors != {"fg": None, "bg": None, "attr": None}:
            result_parts.append(self._colorizer.end_color())

        return "".join(result_parts)

    def __str__(self) -> str:
        """Convert to string by rendering color ranges."""
        return self._render()

    def colorize(self, color_code: Union[str, ColorCode]) -> "ColorizedString":
        """Apply color to the entire string."""
        if isinstance(color_code, ColorCode):
            color_name = color_code.name.lower()
        else:
            color_name = str(color_code)

        # Normalize color name (e.g., red_bg -> bg_red)
        color_name = self._normalize_color_name(color_name)

        # Create new ColorRange for entire text
        priority = (
            self._pipeline_stage * PIPELINE_STAGE_MULTIPLIER
            + NESTING_DEPTH_MULTIPLIER  # depth=1 for whole-string colorization
            + self._next_priority
        )

        new_range = ColorRange(
            start=0,
            end=len(self._original_text),
            color=color_name,
            priority=priority,
            pipeline_stage=self._pipeline_stage,
        )

        # Create new ColorizedString with added range
        new_ranges = self._color_ranges.copy()
        new_ranges.append(new_range)

        result = ColorizedString(
            value=self._original_text,  # Not rendered yet
            original_text=self._original_text,
            color_ranges=new_ranges,
            pipeline_stage=self._pipeline_stage,
        )
        result._next_priority = self._next_priority + 1

        return result

    def colorize_random(self, code: Optional[int] = None) -> "ColorizedString":
        """Apply random color to the string."""
        random_color = self._colorizer._color_manager.generate_random_color(code)
        return self.colorize(random_color)

    def remove_color(self) -> "ColorizedString":
        """Remove all color codes and return plain text."""
        # Just return the original text without any color ranges
        return ColorizedString(
            value=self._original_text,
            original_text=self._original_text,
            color_ranges=[],
            pipeline_stage=self._pipeline_stage,
        )

    def _calculate_group_nesting_depth(  # noqa: PLR6301
        self, pattern_str: str
    ) -> dict[int, int]:
        """Calculate nesting depth for each capture group in a regex pattern.

        Returns a dict mapping group number to nesting depth.
        Group 0 (entire match) has depth 0, first-level groups have depth 1, etc.
        """
        depth_map = {0: 0}  # Group 0 is the entire match
        current_depth = 0
        group_num = 0
        i = 0

        while i < len(pattern_str):
            char = pattern_str[i]

            # Skip escaped characters
            if char == "\\" and i + 1 < len(pattern_str):
                i += 2
                continue

            # Skip character classes
            if char == "[":
                i += 1
                while i < len(pattern_str) and pattern_str[i] != "]":
                    if pattern_str[i] == "\\" and i + 1 < len(pattern_str):
                        i += 2
                    else:
                        i += 1
                i += 1
                continue

            # Handle opening parenthesis
            if char == "(":
                # Check if it's a non-capturing group
                if i + 1 < len(pattern_str) and pattern_str[i + 1] == "?":
                    # Non-capturing group, don't increment group_num
                    # But still increase depth for nested groups
                    current_depth += 1
                else:
                    # Capturing group
                    current_depth += 1
                    group_num += 1
                    depth_map[group_num] = current_depth

            elif char == ")":
                current_depth -= 1

            i += 1

        return depth_map

    def highlight(
        self, pattern: Union[str, re.Pattern], colors: Union[str, list[str]]
    ) -> "ColorizedString":
        """Highlight text matching pattern with given colors.

        Matches against the original text (ignoring any existing ANSI codes).
        Inner (more nested) groups have higher priority than outer groups.
        """
        if isinstance(colors, str):
            colors = [colors]

        # Compile pattern if needed
        if isinstance(pattern, str):
            pattern_str = pattern
            pattern_obj = re.compile(pattern, re.IGNORECASE)
        else:
            pattern_obj = pattern
            pattern_str = pattern.pattern

        # Calculate nesting depth for each group
        nesting_depths = self._calculate_group_nesting_depth(pattern_str)

        # Match against original text (not rendered ANSI string!)
        matches = list(pattern_obj.finditer(self._original_text))
        if not matches:
            # No matches, return self unchanged
            return ColorizedString(
                value=self._original_text,
                original_text=self._original_text,
                color_ranges=self._color_ranges.copy(),
                pipeline_stage=self._pipeline_stage,
            )

        # Collect new color ranges from all matches
        new_ranges = self._color_ranges.copy()

        # Get number of groups from pattern
        num_groups = pattern_obj.groups

        for match in matches:
            if num_groups == 0:
                # No groups, highlight entire match (group 0)
                groups_to_highlight = [0]
            else:
                # Highlight all capturing groups (not group 0)
                groups_to_highlight = list(range(1, num_groups + 1))

            # Create ColorRange for each group
            for grp in groups_to_highlight:
                if match.group(grp) is None:
                    continue

                # Determine color for this group
                color_index = 0 if grp == 0 else (grp - 1) % len(colors)
                color = colors[color_index]

                # Normalize color name (e.g., red_bg -> bg_red)
                color = self._normalize_color_name(color)

                # Calculate priority based on nesting depth
                # For group 0 (entire match with no groups), use depth 1
                nesting_depth = 1 if grp == 0 else nesting_depths.get(grp, 1)

                priority = (
                    self._pipeline_stage * PIPELINE_STAGE_MULTIPLIER
                    + nesting_depth * NESTING_DEPTH_MULTIPLIER
                    + self._next_priority
                )

                # Create range
                new_range = ColorRange(
                    start=match.start(grp),
                    end=match.end(grp),
                    color=color,
                    priority=priority,
                    pipeline_stage=self._pipeline_stage,
                )
                new_ranges.append(new_range)
                self._next_priority += 1

        # Return new ColorizedString with added ranges
        result = ColorizedString(
            value=self._original_text,
            original_text=self._original_text,
            color_ranges=new_ranges,
            pipeline_stage=self._pipeline_stage,
        )
        result._next_priority = self._next_priority

        return result

    def highlight_at(
        self, positions: list[int], color: str = "fg_yellow"
    ) -> "ColorizedString":
        """Highlight characters at specific positions in the original text."""
        if not positions:
            return ColorizedString(
                value=self._original_text,
                original_text=self._original_text,
                color_ranges=self._color_ranges.copy(),
                pipeline_stage=self._pipeline_stage,
            )

        # Normalize color name
        color = self._normalize_color_name(color)

        new_ranges = self._color_ranges.copy()

        # Create a ColorRange for each character position
        # Use high priority so they override existing colors
        for pos in sorted(set(positions)):
            if 0 <= pos < len(self._original_text):
                # Calculate priority
                priority = (
                    self._pipeline_stage * PIPELINE_STAGE_MULTIPLIER
                    + 2 * NESTING_DEPTH_MULTIPLIER  # depth=2 for individual chars
                    + self._next_priority
                )

                # Create range for single character
                new_range = ColorRange(
                    start=pos,
                    end=pos + 1,
                    color=color,
                    priority=priority,
                    pipeline_stage=self._pipeline_stage,
                )
                new_ranges.append(new_range)
                self._next_priority += 1

                # Also add swapcolor attribute
                swap_range = ColorRange(
                    start=pos,
                    end=pos + 1,
                    color="swapcolor",
                    priority=priority,
                    pipeline_stage=self._pipeline_stage,
                )
                new_ranges.append(swap_range)

        result = ColorizedString(
            value=self._original_text,
            original_text=self._original_text,
            color_ranges=new_ranges,
            pipeline_stage=self._pipeline_stage,
        )
        result._next_priority = self._next_priority

        return result

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
