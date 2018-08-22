#!/bin/bash
./preprocess.sh
python3 -O pyin/pyin_main.py "$@"   kb_for_external.nq query_for_external.nq
