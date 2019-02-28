#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import requests


f = '../runs/tests_clean_zzpanla_ldl0_1_0/kbdbgtests_clean_zzpanla_ldl0_1_0.n3'
f = 'DATA'
data = open(f).readlines()


frame = "https://github.com/koo5/univar/tree/master/kbdbg2jsonld/frame.jsonld"


def req(ddd):
	r = requests.post("http://localhost:3000/convert", data={'frame':frame,'n3': ddd})
	if r.status_code == 200:
		print(r.content)
	if r.status_code == 500:
		
		import json
		resp = json.s(r.content.decode('utf-8'), indent=2)
		
		print(resp, file=sys.stderr)
		print(r.status_code, r.reason, file=sys.stderr)
		return False
	return True


if True:
	for i in range(len(data)):
		print(i)
		ddd = data[0:i+1]
		if not req(ddd):
			print("error at line "+str(i))
			exit(1)

		
else:
	req(data)
