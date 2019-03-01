#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import requests


f = '../runs/tests_clean_zzpanla_ldl0_1_0/kbdbgtests_clean_zzpanla_ldl0_1_0.n3'
f = 'DATA'
data = open(f).readlines()


frame = "https://raw.githubusercontent.com/koo5/univar/master/kbdbg2jsonld/frame.jsonld"
frame = "http://localhost:4444/frame.jsonld"

def req(ddd):
	r = requests.post("http://localhost:3000/convert", data={'frame':frame,'n3': ddd})
	if r.status_code == 200:
		#print(r.content)
		print(json.dumps(json.loads(r.content.decode('utf-8')), indent=2))

	if r.status_code == 500:
		#resp = json.dumps(json.loads(r.content.decode('utf-8')), indent=2)
		resp=r.content
		print(resp, file=sys.stderr)
		print(r.status_code, r.reason, file=sys.stderr)
		return False
	return True


#if True:
if False:
	for i in range(len(data)):
		print(i)
		ddd = '\n'.join(data[0:i+1])
		if not req(ddd):
			print("error at line "+str(i))
			exit(1)

		
else:
	req('\n'.join(data))
