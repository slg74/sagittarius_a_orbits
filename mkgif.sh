#!/bin/bash

# convert .mov to .gif
ffmpeg -i sgr_A.mov -pix_fmt rgb8 -r 10 sgr_A.gif && gifsicle -03 sgr_A.gif -o sgr_A.gif
