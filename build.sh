#!/bin/bash

python3 build.py generate
make -f Makefile $1
