#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
dd = open('../runs/tests_clean_zzpanla_ldl0_1_0/kbdbgtests_clean_zzpanla_ldl0_1_0.n3').readlines()
for i in range(len(dd)):
	print(i)
	ddd = dd[0:i+1]
	r = requests.post("http://localhost:3000/convert", data={'n3': '\n'.join(ddd)})
	if r.status_code == 500:
		print(r.content)
		print(r.status_code, r.reason)
		print("error at line "+str(i))
	#print(r.status_code, r.reason)
