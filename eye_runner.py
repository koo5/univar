#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess

command = 'docker run -v $(pwd):$(pwd) -w $(pwd) bdevloed/eye kb_for_external_raw.n3 --query query_for_external_euler.n3 --nope'

r = subprocess.Popen(['bash', '-c', command], universal_newlines=True, stdout=subprocess.PIPE)
almost = there = False
for line in r.stdout.readlines():
	#print('xxxx'+line+';;;;')
	if line.startswith('PREFIX'):
		almost = True
	if there:
		if line.startswith('#') or line == '\n':
			there = False
		else:
			print(' RESULT : ' + line.strip())
	if almost and line == '\n':
		there = True


