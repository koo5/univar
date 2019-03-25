#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import requests


input_file_name = sys.argv[1]
output_file_name = sys.argv[2]


data = open(input_file_name).readlines()


#frame = "https://raw.githubusercontent.com/koo5/univar/master/kbdbg2jsonld/frame.jsonld"
frame = "http://localhost:2999/frame.jsonld"

def req(ddd):
	r = requests.post("http://localhost:3000/convert", data={'frame':frame,'n3': ddd})
	if r.status_code == 200:
		pass
		#print(r.content)
		#print(json.dumps(json.loads(r.content.decode('utf-8')), indent=2))

	if r.status_code == 500:
		#resp = json.dumps(json.loads(r.content.decode('utf-8')), indent=2)
		resp=r.content
		print(resp, file=sys.stderr)
		print(r.status_code, r.reason, file=sys.stderr)
		return False
	open(output_file_name, 'w').write(json.dumps(json.loads(r.content.decode('utf-8')), indent=2))
	return True


if False:
	for i in range(len(data)):
		print(i)
		ddd = '\n'.join(data[0:i+1])
		if not req(ddd):
			print("error at line "+str(i))
			exit(1)

		
else:
	req('\n'.join(data))
