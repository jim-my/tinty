"""
Command-line interface for colorize.
"""

import argparse
import builtins
import contextlib
import re
import sys

from .colorize import Colorize, ColorizedString


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="Colorize text from stdin using ANSI color codes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  echo "hello world" | colorize 'l.*,' yellow
  echo "hello world" | colorize '(ll).*(ld)' red:bg_blue blue:bg_red
  echo "hello world" | colorize '(l).*(ld)' red bg_red
  echo "hello world" | colorize --list-colors
        """,
    )

    parser.add_argument(
        "pattern",
        nargs="?",
        default="(.*)",
        help="Regular expression pattern to match (default: match all)",
    )

    parser.add_argument(
        "colors",
        nargs="*",
        default=["black:bg_yellow:swapcolor"],
        help="Colors to apply to matched groups (default: black:bg_yellow:swapcolor)",
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

    return parser


def list_colors():
    """List all available colors."""
    colorizer = Colorize()
    color_names = colorizer.get_color_names()

    print("Available colors:")
    print()
    # Group colors by type
    fg_colors = [name for name in color_names if name.startswith("fg_")]
    bg_colors = [name for name in color_names if name.startswith("bg_")]
    styles = [name for name in color_names if not name.startswith(("fg_", "bg_"))]

    print("Foreground colors:")
    for color in sorted(fg_colors):
        # Show color name with actual color
        with contextlib.suppress(Exception):
            colored_text = ColorizedString(color).colorize(color)
            print(f"  {colored_text}")

    print("\nBackground colors:")
    for color in sorted(bg_colors):
        with contextlib.suppress(Exception):
            colored_text = ColorizedString(color).colorize(color)
            print(f"  {colored_text}")

    print("\nStyles:")
    for style in sorted(styles):
        with contextlib.suppress(builtins.BaseException):
            colored_text = ColorizedString(style).colorize(style)
            print(f"  {colored_text}")

    aliases = [
        name
        for name in color_names
        if not name.startswith(("fg_", "bg_")) and name not in styles
    ]
    if aliases:
        print("\nColor aliases:")
        for alias in sorted(aliases):
            with contextlib.suppress(builtins.BaseException):
                colored_text = ColorizedString(alias).colorize(alias)
                print(f"  {colored_text}")


def process_line(
    line: str, pattern: re.Pattern, colors: list[str], verbose: bool = False
) -> str:
    """Process a single line of input."""
    # Remove trailing newline for processing
    line = line.rstrip("\n")

    colored_str = ColorizedString(line)
    result = colored_str.highlight(pattern, colors)

    if verbose:
        print(f"Original: {line}", file=sys.stderr)
        print(f"Pattern: {pattern.pattern}", file=sys.stderr)
        print(f"Colors: {colors}", file=sys.stderr)

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
        and args.colors == ["black:bg_yellow:swapcolor"]
    ):
        parser.print_help()
        return

    # Compile regex pattern
    flags = 0 if args.case_sensitive else re.IGNORECASE
    try:
        pattern = re.compile(args.pattern, flags)
    except re.error:
        sys.exit(1)

    # Process input
    try:
        for line in sys.stdin:
            result = process_line(line, pattern, args.colors, args.verbose)
            print(result)
            sys.stdout.flush()
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        # Handle broken pipe gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
