#!/bin/bash

python3 build.py update
make -f Makefile $1
