#!/bin/bash
# Demonstrates pipeline - later commands have higher priority

echo "🔗 Pipeline - Later Commands Override Earlier Ones"
echo ""

echo "Example 1: Sequential highlighting"
echo "Command: echo 'hello world' | pipetint 'hello' red | pipetint 'world' blue"
echo "Result:  "
echo "hello world" | pipetint 'hello' red | pipetint 'world' blue
echo "         'hello' is red, 'world' is blue"
echo ""

echo "Example 2: Overlapping patterns"
echo "Command: echo 'hello world' | pipetint 'hello' red | pipetint 'llo w' green"
echo "Result:  "
echo "hello world" | pipetint 'hello' red | pipetint 'llo w' green
echo "         'llo w' overrides red (higher priority)"
echo ""

echo "Example 3: Full override"
echo "Command: echo 'hello world' | pipetint 'hello' red | pipetint '.*' blue"
echo "Result:  "
echo "hello world" | pipetint 'hello' red | pipetint '.*' blue
echo "         Everything is blue (latest wins)"
echo ""

echo "Example 4: Using --replace-all to clear previous colors"
echo "Command: echo 'hello world' | pipetint 'hello' red | pipetint --replace-all 'world' blue"
echo "Result:  "
echo "hello world" | pipetint 'hello' red | pipetint --replace-all 'world' blue
echo "         Only 'world' is blue (red was cleared)"
