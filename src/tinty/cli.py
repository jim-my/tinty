"""Command-line interface for colorize."""

import argparse
import contextlib
import re
import sys

from .tinty import Colorize, ColorizedString


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="Colorize text from stdin using ANSI color codes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage="echo 'text' | tinty [PATTERN] [COLORS...]\n       tinty --list-colors",
        epilog="""
Examples:
  echo "hello world" | tinty 'l.*' yellow
  echo "hello world" | tinty '(ll).*(ld)' red,bg_blue blue,bg_red
  echo "hello world" | tinty '(l).*(ld)' red bg_red
  tinty --list-colors
        """,
    )

    parser.add_argument(
        "pattern",
        nargs="?",
        default="(.*)",
        metavar="PATTERN",
        help="Regular expression pattern to match text (default: match all)",
    )

    parser.add_argument(
        "colors",
        nargs="*",
        default=["black,bg_yellow,swapcolor"],
        metavar="COLORS",
        help="Color names to apply to matched groups (default: black,bg_yellow,swapcolor)",
    )

    parser.add_argument(
        "--list-colors", action="store_true", help="List all available colors and exit"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Make pattern matching case sensitive",
    )

    parser.add_argument(
        "--replace-all",
        action="store_true",
        help="Clear all previous colors before applying new ones (useful in pipelines)",
    )

    parser.add_argument(
        "-u",
        "--unbuffered",
        action="store_true",
        help="Force line-buffered output (flush after each line). "
        "Useful for real-time log streaming without external tools like stdbuf.",
    )

    return parser


def list_colors():
    """List all available colors."""
    colorizer = Colorize()

    print("Available colors:")
    print()
    color_map = colorizer._color_manager._color_map
    for name, code in sorted(color_map.items()):
        print(f"  {name}: {code.value}")


def process_line(
    line: str,
    pattern: re.Pattern,
    color_groups: list[list[str]],
    verbose: bool = False,
    replace_all: bool = False,
) -> str:
    """Process a single line of input.

    Args:
        line: Input line to process
        pattern: Compiled regex pattern
        color_groups: List of color lists, one per capture group.
                      e.g., [['red', 'bold'], ['blue']] means group 1 gets red+bold,
                      group 2 gets blue.
        verbose: Enable verbose output
        replace_all: Clear previous colors before applying new ones
    """
    # Remove trailing newline for processing
    line = line.rstrip("\n")

    # Create ColorizedString from input
    colored_str = ColorizedString(line)

    # If replace_all is True, clear all existing colors by creating
    # a new ColorizedString from the original text only
    if replace_all:
        colored_str = ColorizedString(
            value=colored_str._original_text,
            original_text=colored_str._original_text,
            color_ranges=[],
            pipeline_stage=0,
            raw_sequences=[],
        )

    # Apply colors layer by layer
    # Each "layer" takes the nth color from each group
    max_colors = max((len(g) for g in color_groups), default=0)
    result = colored_str
    for layer in range(max_colors):
        layer_colors = []
        for group_colors in color_groups:
            if layer < len(group_colors):
                layer_colors.append(group_colors[layer])
            else:
                # No more colors for this group, use empty string to skip
                layer_colors.append("")
        result = result.highlight(pattern, layer_colors)

    if verbose:
        print(f"Original: {colored_str._original_text}", file=sys.stderr)
        print(f"Pattern: {pattern.pattern}", file=sys.stderr)
        print(f"Color groups: {color_groups}", file=sys.stderr)
        if replace_all:
            print("Replace all: True (cleared previous colors)", file=sys.stderr)

    return str(result)


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle special commands
    if args.list_colors:
        list_colors()
        return

    # Handle help when no stdin and using default arguments
    if (
        sys.stdin.isatty()
        and args.pattern == "(.*)"
        and args.colors == ["black,bg_yellow,swapcolor"]
    ):
        parser.print_help()
        return

    # Compile regex pattern
    flags = 0 if args.case_sensitive else re.IGNORECASE
    try:
        pattern = re.compile(args.pattern, flags)
    except re.error:
        sys.exit(1)

    # Parse colors - each argument is a group of colors for one capture group
    # e.g., ['red,bold', 'blue'] -> [['red', 'bold'], ['blue']]
    # This means group 1 gets red+bold, group 2 gets blue
    color_groups = []
    for color_arg in args.colors:
        group_colors = [c.strip() for c in color_arg.split(",") if c.strip()]
        color_groups.append(group_colors)

    # Configure line-buffered output if requested
    # Uses contextlib.suppress for cleaner handling of missing reconfigure method
    if args.unbuffered:
        with contextlib.suppress(AttributeError):
            sys.stdout.reconfigure(line_buffering=True)  # type: ignore[union-attr]

    # Process input
    try:
        for line in sys.stdin:
            result = process_line(
                line, pattern, color_groups, args.verbose, args.replace_all
            )
            print(result)
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        # Handle broken pipe gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
