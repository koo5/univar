#!/bin/bash

./pyin/tau2.py ./pyin_runner-O-nolog.sh  tests/lists/*    2>&1 |  grep ":test:"
