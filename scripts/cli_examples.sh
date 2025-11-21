#!/bin/bash
echo "hello world" | pipetint "l.*" yellow

echo "hello world" | pipetint "(ll).*(ld)" red,bg_blue blue,bg_red