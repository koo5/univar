#!/bin/bash
source venv/bin/activate
pypy -O pyin/pyin_main.py "$@" --visualize true  kb_for_external.nq query_for_external.nq 
