#!/bin/bash

# clean temp files 
echo "Cleaning the project..."

# remove the build directory, binaries, and deb package 
rm -rf temp
rm -f shodansvc-v1.0.0.deb
