"""Command-line interface for colorize."""

import argparse
import contextlib
import re
import sys

from .core import Colorize, ColorizedString


def _create_help_examples() -> str:
    """Create colorized examples for CLI help."""
    # Example 1: Simple highlighting
    ex1 = ColorizedString("ERROR: Connection failed").highlight(r"ERROR", ["red"])

    # Example 2: Success highlighting
    ex2 = ColorizedString("SUCCESS: Task completed").highlight(r"SUCCESS", ["green"])

    # Example 3: Nested groups showing priority
    ex3 = ColorizedString("hello world").highlight(r"(h.(ll))", ["red", "blue"])

    # Example 4: Background colors
    ex4_tmp = ColorizedString("WARN: Check logs").highlight(r"WARN", ["black"])
    ex4 = ex4_tmp.highlight(r"WARN", ["bg_yellow"])

    # Example 5: Multiple capture groups (log parsing)
    ex5 = ColorizedString(
        "2024-01-15 ERROR: Connection timeout at server.py:42"
    ).highlight(
        r"(\d{4}-\d{2}-\d{2}).*?(ERROR|WARN|INFO).*?([a-z_]+\.py:\d+)",
        ["cyan", "red", "yellow"],
    )

    # Example 6: Pipeline composition
    ex6_tmp1 = ColorizedString("ERROR: Connection failed at 10:30:45").highlight(
        r"ERROR", ["red"]
    )
    ex6_tmp2 = ex6_tmp1.highlight(r"ERROR", ["bold"])
    ex6 = ex6_tmp2.highlight(r"\d{2}:\d{2}:\d{2}", ["blue"])

    return f"""
Examples:
  # Highlight errors in red
  $ echo "ERROR: Connection failed" | pipetint 'ERROR' red
  {ex1}

  # Highlight success in green
  $ echo "SUCCESS: Task completed" | pipetint 'SUCCESS' green
  {ex2}

  # Nested groups - inner color wins
  $ echo "hello world" | pipetint '(h.(ll))' red,blue
  {ex3}

  # Background + foreground
  $ echo "WARN: Check logs" | pipetint 'WARN' black,bg_yellow
  {ex4}

  # Multiple patterns - log parsing with 3 groups (date, level, location)
  $ echo "2024-01-15 ERROR: Connection timeout at server.py:42" | \\
      pipetint '(\\d{{4}}-\\d{{2}}-\\d{{2}}).*?(ERROR|WARN|INFO).*?([a-z_]+\\.py:\\d+)' \\
      cyan red yellow
  {ex5}

  # Pipeline composition - colors preserved across stages
  $ echo "ERROR: Connection failed at 10:30:45" | \\
      pipetint 'ERROR' red,bold | \\
      pipetint '\\d{{2}}:\\d{{2}}:\\d{{2}}' blue
  {ex6}

  # List all available colors
  $ pipetint --list-colors
        """


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="Colorize text from stdin using ANSI color codes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage="echo 'text' | pipetint [PATTERN] [COLORS...]\n       pipetint --list-colors",
        epilog=_create_help_examples(),
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
        help="Colors for each capture group. Use commas to combine multiple colors "
        "for one group (e.g., red,bold). Default: black,bg_yellow,swapcolor",
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
    """List all available colors with visual demonstrations."""
    colorizer = Colorize()

    # Header
    header = ColorizedString("Available Colors").colorize("bold")
    print(header)
    print("=" * 60)
    print()

    color_map = colorizer._color_manager._color_map

    # Group colors by type (only user-facing ones)
    foreground = []
    background = []
    styles = []

    # Define text style names as a set for efficient lookup
    text_styles = {
        "bold",
        "bright",
        "dim",
        "underline",
        "blink",
        "invert",
        "swapcolor",
        "hidden",
        "strikethrough",
    }

    for name in sorted(color_map.keys()):
        # Skip internal color names (fg_, bg_ prefixed duplicates)
        if name.startswith("fg_") or name.endswith("_bg"):
            continue

        if name.startswith("bg_"):
            background.append(name)
        elif name in text_styles:
            styles.append(name)
        else:
            foreground.append(name)

    # Display foreground colors with color blocks
    if foreground:
        section_title = ColorizedString("Foreground Colors").colorize("bold")
        print(section_title)
        print("-" * 60)
        for name in foreground:
            # Show colored block and the text "This is <color>"
            block = ColorizedString("████").colorize(name)
            demo_text = ColorizedString(f"This is {name}").colorize(name)
            print(f"  {block}  {demo_text}")
        print()

    # Display background colors with colored blocks
    if background:
        section_title = ColorizedString("Background Colors").colorize("bold")
        print(section_title)
        print("-" * 60)
        for name in background:
            # Show background colored block with black text
            block_tmp = ColorizedString("████").colorize(name)
            block = block_tmp.colorize("black")
            # Show text with background
            demo_tmp = ColorizedString(f"This is {name}").colorize(name)
            demo_text = demo_tmp.colorize("black")
            print(f"  {block}  {demo_text}")
        print()

    # Display text styles
    if styles:
        section_title = ColorizedString("Text Styles").colorize("bold")
        print(section_title)
        print("-" * 60)
        for name in styles:
            # Show the style applied to sample text
            demo = ColorizedString(f"This is {name}").colorize(name)
            print(f"  {demo}")
        print()

    # Footer with usage hint
    print("=" * 60)
    hint = ColorizedString("Usage: pipetint 'pattern' <color>").colorize("dim")
    print(hint)


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

    # Apply colors layer by layer across all groups
    # Each layer takes the nth color from each group
    # Inner groups have higher nesting priority within each layer
    # Empty colors are skipped in highlight() so they don't override
    max_colors = max((len(g) for g in color_groups), default=0)
    result = colored_str
    for layer in range(max_colors):
        layer_colors = []
        for group_colors in color_groups:
            if layer < len(group_colors):
                layer_colors.append(group_colors[layer])
            else:
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
