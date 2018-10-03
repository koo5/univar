#!/bin/bash
python3 -O pyin/preprocess.py --kb true      kb_for_external_raw.n3 >    kb_for_external.nq
python3 -O pyin/preprocess.py --kb false  query_for_external_raw.n3 > query_for_external.nq
