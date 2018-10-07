#!/bin/bash
python -O pyin/pyin_main.py  --nolog true  "$@"   kb_for_external_raw.n3 query_for_external_raw.n3
