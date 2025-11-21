#!/usr/bin/env python3
"""
Sync examples between README.md and script files to ensure consistency.
This script is the single source of truth for all visual examples.
"""

import re
from pathlib import Path

# Define examples as the single source of truth
EXAMPLES = {
    "basic_colors": {
        "imports": "from pipetint import BLUE, BOLD, GREEN, RED, YELLOW, colored",
        "code_lines": [
            'print(colored("Success") | GREEN | BOLD)',
            'print(colored("Warning") | YELLOW)',
            'print(colored("Error") | RED | BOLD)',
            'print(colored("Info") | BLUE)',
        ],
        "readme_description": "Simple API, beautiful results:",
        "readme_subset": [0, 1, 2, 3],  # Show all 4 lines in README
    },
    "cli_examples": {
        "bash_lines": [
            'echo "hello world" | pipetint "l.*" yellow',
            "",
            'echo "hello world" | pipetint "(ll).*(ld)" red,bg_blue blue,bg_red',
        ],
        "readme_description": "CLI pattern highlighting:",
        "readme_subset": [0, 2],  # Show only the second line in README
    },
    "complex_styling": {
        "imports": "from pipetint import BG_WHITE, BLUE, BOLD, DIM, RED, YELLOW, colored",
        "code_lines": [
            'print(colored("SYSTEM ALERT") | RED | BOLD | BG_WHITE)',
            'print(str(colored("DEBUG") | DIM) + " - Application started")',
            'print(str(colored("INFO") | BLUE) + " - User logged in")',
            'print(str(colored("WARNING") | YELLOW | BOLD) + " - Memory usage high")',
            'print(str(colored("ERROR") | RED | BOLD) + " - Database connection failed")',
        ],
        "readme_description": "Complex styling made easy:",
        "readme_subset": [0, 1, 2, 3, 4],  # Show alert, debug, and error
    },
    "pattern_highlighting": {
        "imports": "from pipetint import colored",
        "code_lines": [
            'text = "The quick brown fox jumps over the lazy dog"',
            'highlighted = colored(text).highlight(r"(quick)|(fox)|(lazy)", ["red", "blue", "green"])',
            "print(highlighted)",
        ],
        "readme_description": "Regex pattern highlighting:",
        "readme_subset": [0, 1, 2],  # Show all lines
    },
}


def generate_script_files():
    """Generate Python/bash script files for termshot."""
    scripts_dir = Path("scripts")
    scripts_dir.mkdir(exist_ok=True)

    for name, config in EXAMPLES.items():
        if name == "cli_examples":
            # Generate bash script
            bash_content = "#!/bin/bash\n" + "\n".join(config["bash_lines"])
            (scripts_dir / f"{name}.sh").write_text(bash_content, encoding="utf-8")
        else:
            # Generate Python script
            lines = [config["imports"], ""] + config["code_lines"]
            py_content = "\n".join(lines) + "\n"
            (scripts_dir / f"{name}.py").write_text(py_content, encoding="utf-8")


def update_readme():
    """Update README.md with consistent examples."""
    readme_path = Path("README.md")
    readme_content = readme_path.read_text(encoding="utf-8")

    # Pattern to match each example section
    for name, config in EXAMPLES.items():
        if name == "cli_examples":
            # Handle bash examples
            pattern = rf"(\*\*{re.escape(config['readme_description'])}\*\*\s*\n\n```bash\n)(.*?)(\n```)"
            code_lines = [config["bash_lines"][i] for i in config["readme_subset"]]
            replacement = rf"\g<1>{chr(10).join(code_lines)}\g<3>"
        else:
            # Handle Python examples
            pattern = rf"(\*\*{re.escape(config['readme_description'])}\*\*\s*\n\n```python\n)(.*?)(\n```)"
            code_lines = [config["code_lines"][i] for i in config["readme_subset"]]
            replacement = rf"\g<1>{chr(10).join(code_lines)}\g<3>"

        readme_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)

    readme_path.write_text(readme_content, encoding="utf-8")


def main():
    """Main function to sync all examples."""
    print("🔄 Generating script files from examples...")
    generate_script_files()

    print("📝 Updating README.md with consistent examples...")
    update_readme()

    print("✅ All examples are now synchronized!")


if __name__ == "__main__":
    main()
