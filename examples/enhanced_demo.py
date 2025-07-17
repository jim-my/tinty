#!/usr/bin/env python3
"""
Demonstration of the enhanced colorize API.

This script showcases the new production-safe, high-usability colorization
patterns inspired by Pathlib's elegant design.
"""

import pathlib
import sys

# Add src to path for running from examples directory
sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "src"))

from tinty import C, ColorString, colored, txt


def demo_basic_usage():
    """Demonstrate basic usage patterns."""
    print("=== Basic Usage ===")

    # Factory functions
    print(colored("Hello World").red())
    print(txt("Hello World").blue().bold())

    # Direct ColorString usage
    print(ColorString("Hello World").green().underline())

    # Global convenience object
    print(C.yellow("Hello World"))
    print(C("Hello World").magenta().dim())

    print()


def demo_operator_chaining():
    """Demonstrate operator chaining (Pathlib-inspired)."""
    print("=== Operator Chaining (Pathlib-inspired) ===")

    # Using | operator (like Pathlib's /)
    print(colored("Error:") | "red" | "bright" | "bg_white")
    print(txt("Warning:") | "yellow" | "bright")
    print(ColorString("Info:") | "blue" | "dim")

    # Using >> operator
    print(colored("Success") >> "green" >> "bright" >> "underline")

    # Mixing operators
    print(((colored("Mixed") | "red") >> "bright") | "bg_yellow")

    print()


def demo_method_chaining():
    """Demonstrate fluent method chaining."""
    print("=== Method Chaining ===")

    print(colored("Red Bold Underlined").red().bold().underline())
    print(txt("Blue Background Yellow").blue().bg_yellow())
    print(ColorString("All Styles").green().bold().bg_white().blink())

    # Complex chaining
    result = colored("Complex Example").red().bold().bg_yellow().underline()
    print(result)

    print()


def demo_global_object():
    """Demonstrate global C object usage."""
    print("=== Global Object Usage ===")

    # Direct color application
    print(C.red("Direct red"))
    print(C.blue("Direct blue"))
    print(C.bg_green("Background green"))

    # Factory mode with chaining
    print(C("Factory mode").yellow().bold())
    print(C("More chaining") | "cyan" | "underline")

    # Direct colorization
    print(C("Direct colorization", "magenta"))

    print()


def demo_real_world_examples():
    """Demonstrate real-world usage scenarios."""
    print("=== Real-World Examples ===")

    # Log levels
    print(f"{C.dim('DEBUG')} - Debug message")
    print(f"{C.blue('INFO')} - Information message")
    print(f"{C.yellow('WARNING')} - Warning message")
    print(f"{C.red('ERROR')} - Error message")
    print(f"{colored('CRITICAL').red().bold().bg_white()} - Critical message")

    print()

    # CLI output
    print(f"{colored('✓').green()} Success: Operation completed")
    print(f"{colored('✗').red()} Error: Operation failed")
    print(f"{colored('⚠').yellow()} Warning: Deprecated feature")

    print()

    # Code syntax highlighting simulation
    print(f"{C.blue('def')} {C.green('hello_world')}():")
    hello_world_str = colored('"Hello, World!"').yellow()
    print(f"    {C.blue('print')}({hello_world_str})")

    print()


def demo_advanced_features():
    """Demonstrate advanced features."""
    print("=== Advanced Features ===")

    # Text highlighting
    text = "The quick brown fox jumps over the lazy dog"
    highlighted = colored(text).highlight(r"(quick|fox|lazy)", ["red", "blue", "green"])
    print(f"Highlighted: {highlighted}")

    # Position-based highlighting
    position_highlight = colored("Hello World").highlight_at([0, 6], "bg_yellow")
    print(f"Position highlight: {position_highlight}")

    # Color removal
    colored_text = colored("Colored text").red().bold()
    clean_text = colored_text.remove_color()
    print(f"Original: {colored_text}")
    print(f"Cleaned: {clean_text}")

    print()


def demo_multiple_interfaces():
    """Demonstrate using multiple interfaces together."""
    print("=== Multiple Interface Compatibility ===")

    # Mix different approaches
    header = colored("=== SYSTEM STATUS ===").blue().bold()
    cpu_ok = C.green("✓ CPU: OK")
    memory_warn = txt("⚠ Memory: 85%") | "yellow" | "bright"
    disk_error = ColorString("✗ Disk: FULL").red().bold().bg_white()

    print(header)
    print(cpu_ok)
    print(memory_warn)
    print(disk_error)

    print()


def demo_performance_showcase():
    """Demonstrate that chaining is efficient."""
    print("=== Performance Showcase ===")

    # Show that each operation returns a new ColorString
    base = colored("test")
    print(f"Base: {base} (id: {id(base)})")

    step1 = base.red()
    print(f"Red: {step1} (id: {id(step1)})")

    step2 = step1.bold()
    print(f"Bold: {step2} (id: {id(step2)})")

    step3 = step2 | "underline"
    print(f"Underlined: {step3} (id: {id(step3)})")

    print("Each operation creates a new object (functional approach)")
    print()


def demo_comparison_with_legacy():
    """Compare new API with legacy API."""
    print("=== Comparison: New vs Legacy API ===")

    # Legacy way (still works)
    from tinty import Colorize

    colorizer = Colorize()
    legacy_result = colorizer.colorize("Legacy API", "red")
    print(f"Legacy: {legacy_result}")

    # New way - multiple options
    print(f"Enhanced 1: {colored('Enhanced API').red()}")
    print(f"Enhanced 2: {C.red('Enhanced API')}")
    print(f"Enhanced 3: {txt('Enhanced API') | 'red'}")

    print("New API provides multiple intuitive interfaces!")
    print()


def main():
    """Run all demonstrations."""
    print(colored("Colorize Enhanced API Demonstration").green().bold().underline())
    print()

    demo_basic_usage()
    demo_operator_chaining()
    demo_method_chaining()
    demo_global_object()
    demo_real_world_examples()
    demo_advanced_features()
    demo_multiple_interfaces()
    demo_performance_showcase()
    demo_comparison_with_legacy()

    print(colored("Demo completed! 🎉").green().bold())


if __name__ == "__main__":
    main()
