#!/bin/bash
. pypy2/bin/activate
python -O pyin/pyin_main.py "$@"   kb_for_external_raw.n3 query_for_external_raw.n3
