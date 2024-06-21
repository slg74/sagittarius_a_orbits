#!/bin/bash

# REQUIREMENTS - ffmpeg, gifsicle
# Linux: sudo apt-get install ffmpeg gifsicle -y
# MacOS: brew install ffmpeg gifsicle

# convert .mov to .gif
ffmpeg -i sgr_A.mov -pix_fmt rgb8 -r 10 sgr_A.gif && gifsicle -03 sgr_A.gif -o sgr_A.gif
