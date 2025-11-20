"""
Tests for CLI module.
"""

import io
import re
from unittest.mock import MagicMock, patch

import pytest

from tinty.cli import create_parser, list_colors, main, process_line


class TestCreateParser:
    """Test argument parser creation."""

    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None
        assert parser.description is not None

    def test_parser_defaults(self):
        """Test parser default values."""
        parser = create_parser()
        args = parser.parse_args(["hello", "red"])

        assert args.pattern == "hello"
        assert args.colors == ["red"]
        assert args.list_colors is False
        assert args.verbose is False
        assert args.case_sensitive is False

    def test_parser_optional_args(self):
        """Test parser optional arguments."""
        parser = create_parser()

        # Test list colors
        args = parser.parse_args(["--list-colors"])
        assert args.list_colors is True

        # Test verbose
        args = parser.parse_args(["pattern", "--verbose"])
        assert args.verbose is True

        # Test case sensitive
        args = parser.parse_args(["pattern", "--case-sensitive"])
        assert args.case_sensitive is True

    def test_parser_no_args(self):
        """Test parser with no arguments."""
        parser = create_parser()
        args = parser.parse_args([])

        assert args.pattern == "(.*)"
        assert args.colors == ["black,bg_yellow,swapcolor"]


class TestListColors:
    """Test list_colors function."""

    def test_list_colors_output(self):
        """Test that list_colors produces output."""
        # Capture stdout
        captured_output = io.StringIO()

        with patch("sys.stdout", captured_output):
            list_colors()

        output = captured_output.getvalue()

        # Should contain expected sections
        assert "Available colors:" in output

        # Should contain some specific colors with their values
        assert "fg_red: 31" in output
        assert "bg_blue: 44" in output


class TestProcessLine:
    """Test process_line function."""

    def test_process_line_basic(self):
        """Test basic line processing."""
        pattern = re.compile(r"l", re.IGNORECASE)
        colors = ["red"]

        result = process_line("hello world\n", pattern, colors)

        # Should contain color codes
        assert "\033[31m" in result  # Red color
        assert "\033[0m" in result  # Reset

        # Check that original text is preserved when colors are removed
        from tinty import ColorizedString

        cs = ColorizedString(result)
        assert cs.remove_color() == "hello world"

    def test_process_line_no_match(self):
        """Test line processing with no match."""
        pattern = re.compile(r"xyz", re.IGNORECASE)
        colors = ["red"]

        result = process_line("hello world\n", pattern, colors)

        # Should be unchanged (except newline removal)
        assert result == "hello world"

    def test_process_line_multiple_colors(self):
        """Test line processing with multiple colors."""
        pattern = re.compile(r"(h)(ello)", re.IGNORECASE)
        colors = ["red", "blue"]

        result = process_line("hello world\n", pattern, colors)

        # Should contain both colors
        assert "\033[31m" in result or "\033[34m" in result
        assert "\033[0m" in result

    def test_process_line_verbose(self):
        """Test line processing with verbose output."""
        pattern = re.compile(r"l", re.IGNORECASE)
        colors = ["red"]

        # Capture stderr
        captured_stderr = io.StringIO()

        with patch("sys.stderr", captured_stderr):
            process_line("hello world\n", pattern, colors, verbose=True)

        stderr_output = captured_stderr.getvalue()

        # Should contain verbose information
        assert "Original:" in stderr_output
        assert "Pattern:" in stderr_output
        assert "Colors:" in stderr_output


class TestMain:
    """Test main function."""

    def test_main_help_no_stdin(self):
        """Test main shows help when no stdin and no args."""
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True

            with patch("sys.argv", ["tinty"]):
                with patch("tinty.cli.create_parser") as mock_parser:
                    mock_parser_instance = MagicMock()
                    mock_parser.return_value = mock_parser_instance
                    mock_parser_instance.parse_args.return_value = MagicMock(
                        pattern="(.*)",
                        colors=["black,bg_yellow,swapcolor"],
                        list_colors=False,
                    )

                    main()
                    mock_parser_instance.print_help.assert_called_once()

    def test_main_list_colors(self):
        """Test main with list colors option."""
        with patch("sys.argv", ["tinty", "--list-colors"]):
            with patch("tinty.cli.list_colors") as mock_list_colors:
                main()
                mock_list_colors.assert_called_once()

    def test_main_invalid_regex(self):
        """Test main with invalid regex pattern."""
        with patch("sys.argv", ["tinty", "[invalid"]):
            with patch("sys.stdin", io.StringIO("test input\n")):
                with patch("sys.exit", side_effect=SystemExit(1)) as mock_exit:
                    with pytest.raises(SystemExit):
                        main()
                    mock_exit.assert_called_once_with(1)

    def test_main_process_input(self):
        """Test main processing input."""
        test_input = "hello world\ntest line\n"

        with patch("sys.argv", ["tinty", "l", "red"]):
            with patch("sys.stdin", io.StringIO(test_input)):
                with patch("sys.stdout", io.StringIO()) as mock_stdout:
                    main()

                    output = mock_stdout.getvalue()

                    # Should contain color codes
                    assert "\033[31m" in output  # Red color
                    assert "\033[0m" in output  # Reset

                    # Check that original text is preserved when colors are removed
                    from tinty import ColorizedString

                    cs = ColorizedString(output)
                    cleaned_output = cs.remove_color()
                    assert "hello world" in cleaned_output
                    assert "test line" in cleaned_output

    def test_main_keyboard_interrupt(self):
        """Test main handles keyboard interrupt."""
        with patch("sys.argv", ["tinty", "test"]):
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.__iter__.side_effect = KeyboardInterrupt()

                with patch("sys.exit") as mock_exit:
                    main()
                    mock_exit.assert_called_once_with(1)

    def test_main_broken_pipe(self):
        """Test main handles broken pipe."""
        with patch("sys.argv", ["tinty", "test"]):
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.__iter__.side_effect = BrokenPipeError()

                with patch("sys.exit") as mock_exit:
                    main()
                    mock_exit.assert_called_once_with(0)

    def test_main_case_sensitive(self):
        """Test main with case sensitive option."""
        test_input = "Hello World\n"

        with patch("sys.argv", ["tinty", "h", "red", "--case-sensitive"]):
            with patch("sys.stdin", io.StringIO(test_input)):
                with patch("sys.stdout", io.StringIO()) as mock_stdout:
                    main()

                    output = mock_stdout.getvalue()

                    # Should not match 'H' with pattern 'h' in case sensitive mode
                    # So 'H' should not be colored, output should be exactly
                    # "Hello World"
                    assert output.strip() == "Hello World"

    def test_main_verbose(self):
        """Test main with verbose option."""
        test_input = "hello world\n"

        with patch("sys.argv", ["tinty", "l", "red", "--verbose"]):
            with patch("sys.stdin", io.StringIO(test_input)):
                with patch("sys.stdout", io.StringIO()):
                    with patch("sys.stderr", io.StringIO()) as mock_stderr:
                        main()

                        stderr_output = mock_stderr.getvalue()

                        # Should contain verbose output
                        assert "Original:" in stderr_output
                        assert "Pattern:" in stderr_output
                        assert "Colors:" in stderr_output


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def test_cli_basic_usage(self):
        """Test basic CLI usage."""
        test_input = "hello world\n"

        with patch("sys.argv", ["tinty", "l", "red"]):
            with patch("sys.stdin", io.StringIO(test_input)):
                with patch("sys.stdout", io.StringIO()) as mock_stdout:
                    main()

                    output = mock_stdout.getvalue()

                    # Should colorize 'l' characters
                    assert "\033[31m" in output
                    assert "\033[0m" in output

                    # Check that original text is preserved when colors are removed
                    from tinty import ColorizedString

                    cs = ColorizedString(output)
                    assert "hello world" in cs.remove_color()

    def test_cli_multiple_colors(self):
        """Test CLI with multiple colors."""
        test_input = "hello world\n"

        with patch("sys.argv", ["tinty", "(h)(ello)", "red", "blue"]):
            with patch("sys.stdin", io.StringIO(test_input)):
                with patch("sys.stdout", io.StringIO()) as mock_stdout:
                    main()

                    output = mock_stdout.getvalue()

                    # Should contain color codes
                    assert "\033[" in output
                    assert "\033[0m" in output

                    # Check that original text is preserved when colors are removed
                    from tinty import ColorizedString

                    cs = ColorizedString(output)
                    assert "hello world" in cs.remove_color()

    def test_cli_default_pattern(self):
        """Test CLI with default pattern."""
        test_input = "hello world\n"

        with patch("sys.argv", ["tinty"]):
            with patch("sys.stdin", io.StringIO(test_input)):
                with patch("sys.stdout", io.StringIO()) as mock_stdout:
                    main()

                    output = mock_stdout.getvalue()

                    # Should colorize entire line with default colors
                    assert "\033[" in output
                    assert "\033[0m" in output

                    # Check that original text is preserved when colors are removed
                    from tinty import ColorizedString

                    cs = ColorizedString(output)
                    assert "hello world" in cs.remove_color()

    def test_cli_no_match(self):
        """Test CLI with pattern that doesn't match."""
        test_input = "hello world\n"

        with patch("sys.argv", ["tinty", "xyz"]):
            with patch("sys.stdin", io.StringIO(test_input)):
                with patch("sys.stdout", io.StringIO()) as mock_stdout:
                    main()

                    output = mock_stdout.getvalue()

                    # Should output original text without colors
                    assert output.strip() == "hello world"
                    assert "\033[" not in output

    def test_cli_piping_with_no_color(self):
        """Test piping a colored string to a no_color command."""
        from tinty import ColorizedString

        # Simulate the first command's output
        colored_input = "he\033[31m\033[44mllo wor\033[0m\033[34m\033[41mld\033[0m\n"

        with patch("sys.argv", ["tinty", ".*", "no_color"]):
            with patch("sys.stdin", io.StringIO(colored_input)):
                with patch("sys.stdout", io.StringIO()) as mock_stdout:
                    main()

                    output = mock_stdout.getvalue()

                    # Should output original text without colors
                    cleaned = ColorizedString(output).remove_color().strip()
                    assert cleaned == "hello world"

    def test_cli_replace_all_flag(self):
        """Test --replace-all flag clears previous colors."""
        from tinty import ColorizedString

        # Simulate colored input from previous pipeline stage
        colored_input = "\033[31mhello\033[0m world\n"

        with patch("sys.argv", ["tinty", "--replace-all", "world", "blue"]):
            with patch("sys.stdin", io.StringIO(colored_input)):
                with patch("sys.stdout", io.StringIO()) as mock_stdout:
                    main()

                    output = mock_stdout.getvalue()

                    # Should only have blue on "world", "hello" should have no color
                    assert "\033[34m" in output  # Blue color
                    assert "world" in output
                    # Original red color should be gone
                    cleaned = ColorizedString(output).remove_color().strip()
                    assert cleaned == "hello world"

    def test_cli_replace_all_verbose(self):
        """Test --replace-all with verbose output."""
        colored_input = "\033[31mhello\033[0m world\n"

        argv = ["tinty", "--replace-all", "--verbose", "world", "blue"]
        with patch("sys.argv", argv):
            with patch("sys.stdin", io.StringIO(colored_input)):
                with patch("sys.stdout", io.StringIO()):
                    with patch("sys.stderr", io.StringIO()) as mock_stderr:
                        main()

                        stderr_output = mock_stderr.getvalue()

                        # Should contain replace all message
                        assert "Replace all: True" in stderr_output
                        assert "cleared previous colors" in stderr_output
