make with_marpa
env ASAN_OPTIONS="symbolize=1,detect_leaks=0,strict_init_order=1,check_initialization_order=1,verbosity=1" ./tau --silence addrules --silence readcurly --silence N3 --level 0 run tests/dunno/WZPqyt9r.tau
