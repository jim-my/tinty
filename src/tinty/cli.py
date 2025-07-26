"""Command-line interface for colorize."""

import argparse
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
