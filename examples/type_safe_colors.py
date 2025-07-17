#!/usr/bin/env python3
"""
Type-Safe Color Constants Example

Demonstrates the benefits of using type-safe color constants instead of string literals.
This provides better IDE support, autocompletion, and type checking.
"""

import pathlib
import sys

# Add src to path for running from examples directory
sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "src"))

from tinty import (
    BG_BLUE,
    BG_WHITE,
    BG_YELLOW,
    BLUE,
    BOLD,
    BRIGHT,
    C,
    CYAN,
    GREEN,
    RED,
    UNDERLINE,
    WHITE,
    YELLOW,
    colored,
    txt,
)


def main():
    """Demonstrate type-safe color constants."""
    
    print("🎨 Type-Safe Color Constants Demo")
    print("=" * 40)
    print()

    print("## Old Way (String Literals) - Prone to Errors:")
    print('colored("Error") | "red" | "typo"  # "typo" would cause runtime error')
    print('txt("Success") >> "grean"          # "grean" typo not caught')
    print()

    print("## New Way (Type-Safe Constants) - IDE Support & Type Checking:")
    print()

    # Error messages
    print("### Error Messages:")
    error1 = colored("CRITICAL ERROR") | RED | BOLD | BG_WHITE
    error2 = txt("ERROR") >> RED >> BRIGHT
    print(f"Critical: {error1}")
    print(f"Error:    {error2}")
    print()

    # Success messages  
    print("### Success Messages:")
    success1 = colored("✓ SUCCESS") | GREEN | BOLD
    success2 = txt("✓ COMPLETED") >> GREEN >> BRIGHT
    print(f"Success:   {success1}")
    print(f"Completed: {success2}")
    print()

    # Warning messages
    print("### Warning Messages:")
    warning1 = colored("⚠ WARNING") | YELLOW | BOLD
    warning2 = txt("⚠ CAUTION") >> YELLOW >> BRIGHT >> BG_BLUE
    print(f"Warning: {warning1}")
    print(f"Caution: {warning2}")
    print()

    # Info messages
    print("### Info Messages:")
    info1 = colored("ℹ INFO") | BLUE | UNDERLINE
    info2 = txt("ℹ NOTICE") >> CYAN >> BOLD
    print(f"Info:   {info1}")
    print(f"Notice: {info2}")
    print()

    # Complex chaining
    print("### Complex Styling:")
    complex_msg = (colored("SYSTEM ALERT")
                  | RED 
                  | BOLD 
                  | BG_YELLOW
                  | UNDERLINE)
    print(f"Alert: {complex_msg}")
    print()

    # Global C object with constants
    print("### Using Global C Object:")
    print(f"Direct:  {C.red('Hello')} {C.green('World')}")
    print(f"Factory: {C('Hello') | BLUE | BOLD} {C('World') | GREEN}")
    print()

    # Mixed approaches
    print("### Mixed Method + Constant Chaining:")
    mixed1 = colored("Mixed").red() | BOLD | BG_WHITE
    mixed2 = txt("Hybrid").blue() >> BRIGHT >> UNDERLINE
    print(f"Mixed:  {mixed1}")
    print(f"Hybrid: {mixed2}")
    print()

    print("## Benefits of Type-Safe Constants:")
    print("✓ IDE autocompletion")
    print("✓ Type checking catches typos")
    print("✓ Better refactoring support")
    print("✓ Self-documenting code")
    print("✓ No runtime errors from typos")
    print()

    print(colored("🚀 Enhanced type safety with beautiful colors! 🚀") | GREEN | BOLD)


if __name__ == "__main__":
    main()