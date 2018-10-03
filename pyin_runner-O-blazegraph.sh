#!/bin/bash
python3 -O pyin/pyin_main.py "$@"   --sparql_uri http://localhost:9999/blazegraph/sparql  kb_for_external_raw.n3 query_for_external_raw.n3
