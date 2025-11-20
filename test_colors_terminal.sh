#!/bin/bash
# Test if your terminal displays colors correctly

echo "Testing terminal color support..."
echo ""

echo "1. Basic ANSI colors:"
echo -e "\x1b[31mRed foreground\x1b[0m"
echo -e "\x1b[41mRed background\x1b[0m"
echo -e "\x1b[34mBlue foreground\x1b[0m"
echo -e "\x1b[44mBlue background\x1b[0m"
echo ""

echo "2. Combined foreground + background:"
echo -e "\x1b[34m\x1b[41mBlue text on red background\x1b[0m"
echo ""

echo "3. Your actual tinty example:"
echo "hello world" | python -m tinty.cli '(h.(ll))' bg_red,blue
echo ""

echo "4. Same with explicit ANSI codes:"
echo -e "\x1b[41mhe\x1b[0m\x1b[34m\x1b[41mll\x1b[0mo world"
echo ""

echo "If you see colors above, your terminal supports ANSI colors!"
echo "If not, check your terminal settings or try a different terminal."
