#!/usr/bin/env python3
"""
PipeTint Quickstart Example

This example demonstrates the modern, production-safe colorization API.
All monkey patching has been removed for safety and reliability.
"""

import pathlib
import sys

# Add src to path for running from examples directory
sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "src"))

# Import the enhanced, production-safe API
from pipetint import C, ColorString, colored, txt


def main():
    """Demonstrate the modern colorize API."""

    print("🎨 PipeTint - Modern Production-Safe API")
    print("=" * 45)
    print()

    # 1. Factory Functions
    print("1. Factory Functions:")
    print(f"   {colored('Success').green()}")
    print(f"   {txt('Warning').yellow()}")
    print()

    # 2. Operator Chaining (Pathlib-inspired)
    print("2. Operator Chaining (Pathlib-inspired):")
    print(f"   {colored('Error') | 'red' | 'bright'}")
    print(f"   {txt('Info') >> 'blue' >> 'underline'}")
    print()

    # 3. Global Convenience Object
    print("3. Global Convenience Object:")
    print(f"   {C.green('✓ Tests passing')}")
    print(f"   {C.red('✗ Build failed')}")
    print(f"   {C('Processing...').cyan()}")
    print()

    # 4. Method Chaining
    print("4. Method Chaining:")
    print(f"   {ColorString('CRITICAL').red().bold().bg_white()}")
    print(f"   {colored('Highlighted').yellow().bg_blue()}")
    print()

    # 5. Real-world Examples
    print("5. Real-world Examples:")

    # Log levels
    print("   Log Levels:")
    print(f"     {C('DEBUG', 'dim')} - Application started")
    print(f"     {colored('INFO').blue()} - User logged in")
    print(f"     {txt('WARNING') | 'yellow' | 'bright'} - Memory usage high")
    print(f"     {ColorString('ERROR').red().bold()} - Database connection failed")
    print()

    # CLI output
    print("   CLI Status:")
    print(f"     {C.green('✓')} File saved successfully")
    print(f"     {C.yellow('⚠')} Configuration outdated")
    print(f"     {C.red('✗')} Permission denied")
    print()

    # Code highlighting
    print("   Code Highlighting:")
    code = colored("def").blue() + " " + colored("main").green() + "():"
    print(f"     {code}")
    print()

    # Complex chaining
    print("6. Complex Chaining:")
    complex_example = colored("SYSTEM ALERT").red().bold().bg_white() | "blink"
    print(f"   {complex_example}")
    print()

    print(colored("✨ Modern API - Production Safe & Highly Usable! ✨").green().bold())


if __name__ == "__main__":
    main()
