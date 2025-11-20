#!/bin/bash
# Demonstrates pipeline - later commands have higher priority

echo "🔗 Pipeline - Later Commands Override Earlier Ones"
echo ""

echo "Example 1: Sequential highlighting"
echo "Command: echo 'hello world' | tinty 'hello' red | tinty 'world' blue"
echo "Result:  "
echo "hello world" | tinty 'hello' red | tinty 'world' blue
echo "         'hello' is red, 'world' is blue"
echo ""

echo "Example 2: Overlapping patterns"
echo "Command: echo 'hello world' | tinty 'hello' red | tinty 'llo w' green"
echo "Result:  "
echo "hello world" | tinty 'hello' red | tinty 'llo w' green
echo "         'llo w' overrides red (higher priority)"
echo ""

echo "Example 3: Full override"
echo "Command: echo 'hello world' | tinty 'hello' red | tinty '.*' blue"
echo "Result:  "
echo "hello world" | tinty 'hello' red | tinty '.*' blue
echo "         Everything is blue (latest wins)"
