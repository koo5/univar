reset; env PYTHONUNBUFFERED=1 ./pyin/tau2.py  --only-id 0     "./pyco_runner.sh --nolog 0  --novalgrind true --nodebug true  --notrace false --trace_proof 0 --oneword false  --profile false   " tests/clean/zzpanla/hello0c     2>&1 | tee runs/(date "+%F-%H-%M-%S") | tee runs/last_full

