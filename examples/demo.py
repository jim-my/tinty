#!/usr/bin/env python3
"""
Demo script showing tinty library functionality.
"""

from tinty import Colorize, ColorizedString


def demo_basic_colorization():
    """Demonstrate basic colorization."""
    print("=== Basic Colorization ===")

    colorizer = Colorize()

    # Basic colors
    print(colorizer.colorize("Red text", "red"))
    print(colorizer.colorize("Green text", "green"))
    print(colorizer.colorize("Blue background", "bg_blue"))

    # Styles
    print(colorizer.colorize("Bold text", "bright"))
    print(colorizer.colorize("Underlined text", "underline"))

    print()


def demo_colorized_string():
    """Demonstrate ColorizedString usage."""
    print("=== ColorizedString ===")

    text = ColorizedString("Hello World")

    # Method chaining
    print(text.red)
    print(text.bg_yellow)
    print(text.underline)

    # Combine with regular strings
    print(str(text.red) + " and " + str(ColorizedString("more text").blue))

    print()


def demo_pattern_highlighting():
    """Demonstrate pattern highlighting."""
    print("=== Pattern Highlighting ===")

    text = ColorizedString("Hello World! This is a test.")

    # Highlight all 'l' characters
    print("Highlight 'l':", text.highlight(r"l", ["red"]))

    # Highlight words
    print("Highlight words:", text.highlight(r"\w+", ["blue"]))

    # Highlight with groups
    print("Highlight groups:", text.highlight(r"(H)(ello)", ["red", "green"]))

    # Case-insensitive highlighting
    print("Case insensitive:", text.highlight(r"hello", ["yellow"]))

    print()


def demo_position_highlighting():
    """Demonstrate position-based highlighting."""
    print("=== Position Highlighting ===")

    text = ColorizedString("Hello World")

    # Highlight specific positions
    print("Positions [0, 6]:", text.highlight_at([0, 6], "yellow"))
    print("Positions [1, 2, 3]:", text.highlight_at([1, 2, 3], "red"))

    print()


def demo_color_removal():
    """Demonstrate color removal."""
    print("=== Color Removal ===")

    # Create colored text
    colored_text = ColorizedString("Colored text").red
    print("Colored:", colored_text)

    # Remove colors
    clean_text = ColorizedString(str(colored_text)).remove_color()
    print("Clean:", clean_text)

    print()


def demo_random_colors():
    """Demonstrate random colorization."""
    print("=== Random Colors ===")

    colorizer = Colorize()

    # Random colors with seed (reproducible)
    for i in range(5):
        colored = colorizer.colorize_random(f"Text {i}", i)
        print(f"Seed {i}: {colored}")

    # Random colors without seed
    for i in range(3):
        colored = colorizer.colorize_random(f"Random {i}")
        print(f"Random: {colored}")

    print()


def demo_modern_api():
    """Demonstrate modern production-safe API."""
    print("=== Modern Production-Safe API ===")

    from tinty import colored, txt, C, RED, BLUE, UNDERLINE, YELLOW
    
    # Type-safe constants (recommended)
    print(colored("Red text") | RED)
    print(txt("Blue background") | BLUE)  
    print(colored("Underlined") | UNDERLINE)
    
    # Global convenience object
    print(C.red("Also red text"))
    print(C("Flexible") | BLUE | UNDERLINE)

    # Highlight method available on ColorString
    result = colored("Hello World").highlight(r"l", [YELLOW])
    print(result)

    print()


def demo_complex_example():
    """Demonstrate complex usage."""
    print("=== Complex Example ===")

    # Simulate log output
    log_lines = [
        "2024-01-01 10:00:00 INFO: Application started",
        "2024-01-01 10:00:01 DEBUG: Loading configuration",
        "2024-01-01 10:00:02 WARNING: Config file not found, using defaults",
        "2024-01-01 10:00:03 ERROR: Database connection failed",
        "2024-01-01 10:00:04 INFO: Retrying connection...",
    ]

    for line in log_lines:
        colored_line = ColorizedString(line)

        # Highlight log levels
        colored_line = colored_line.highlight(r"(INFO)", ["green"])
        colored_line = colored_line.highlight(r"(DEBUG)", ["blue"])
        colored_line = colored_line.highlight(r"(WARNING)", ["yellow"])
        colored_line = colored_line.highlight(r"(ERROR)", ["red"])

        # Highlight timestamps
        colored_line = colored_line.highlight(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", ["cyan"]
        )

        print(colored_line)

    print()


def main():
    """Run all demos."""
    print("🎨 Tinty Library Demo")
    print("=" * 50)

    demo_basic_colorization()
    demo_colorized_string()
    demo_pattern_highlighting()
    demo_position_highlighting()
    demo_color_removal()
    demo_random_colors()
    demo_modern_api()
    demo_complex_example()

    print("Demo complete! 🎉")


if __name__ == "__main__":
    main()
