#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import subprocess
import re
import os
import sys
import logging
import urllib.parse
import rdflib
from rdflib import Graph
from rdflib.namespace import Namespace
from rdflib.namespace import RDF
from rdflib.collection import Collection
from ordered_rdflib_store import OrderedStore

kbdbg = Namespace('http://kbd.bg/#')

def run():
	os.system('rm -rf filter/*')



	q1 = """
	?kbdbg log:includes {:f a kbdbg:frame.}.
	?kbdbg log:notIncludes {:f kbdbg:is_finished true.}.
	?kbdbg log:includes {:f kbdbg:is_for_rule :r.}.
	?kbdbg log:includes {?b a kbdbg:binding. ?b kbdbg:has_source [kbdbg:has_frame ?y].}.
	?kbdbg log:includes {?b kbdbg:has_target ?t.}.
	?kbdbg log:includes {?t kbdbg:has_frame ?tf.}. 
	"""
	full_q_lines = q1.strip().splitlines()

	filters = []

	for i in range(len(full_q_lines), 0, -1):
		lines = full_q_lines[:i]
		qqq = '\n'.join(lines)
		vars = re.findall(".:[a-zA-Z0-9_]*", qqq)
		vars = set([x[1:] for x in filter(lambda x: not x[0].isalnum() and not (x[0] in '_'), vars)])
		q0 = """
@prefix log: <http://www.w3.org/2000/10/swap/log#>.    
@prefix kbdbg: <http://kbd.bg/#> .
@prefix : <file:///#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@forAll """ + ','.join(vars) + """.
{<file:///home/koom/univar/kbdbg.n3> log:semantics ?kbdbg .
	
	
	"""
		q2 = "\n\n\n} => {("
		q2 += ' '.join(vars)
		q2 += ') a :result}.'

		qf_name = 'filter/query'+str(i)+'.n3'
		qf = open(qf_name,'w')
		qf.write(q0+qqq+q2)
		qf.close()
		filters.append((i, qf_name))



	if len(sys.argv) == 2:
		fn = sys.argv[1]
	else:
		fn = 'kbdbg.n3'
	input_file = open(fn)

	lines = []
	prefixes = []
	steps = []
	while True:
		l = input_file.readline()
		if l == "":
			break
		if l.startswith("#step"):
			step = int(l[5:l.find(' ')])
		elif l.startswith('@prefix'):
			prefixes.append(l)
			continue
		else:
			lines.append(l)
			continue

		i = "".join(prefixes+lines)

		output_file_name = 'filter/'+fn + '_' + str(step).zfill(5) + '.n3'
		try:
			os.unlink(output_file_name)
		except FileNotFoundError:
			pass

		output_file = open(output_file_name, 'w')
		output_file.write(i)
		output_file.close()
		steps.append(output_file_name)

	filters = list(reversed(filters))

	sys.stdout.write('[ ]')
	try:
		best = None
		best_score = 0
		for step in steps:

			for i, query in filters:
				start = time.time()
				if i < best_score:
					continue
				print('best_score', best_score, 'best', best, 'step', step, 'filter', query)
				cmd = ['/home/koom/sw/swap/cwm.py', step, '--filter=' + query]
				o = subprocess.check_output(cmd)
				sys.stdout.write('('+str(time.time() - start).ljust(20,'0') + 's)')
				succ = (len(o.splitlines()) > 3)
				if succ:
					sys.stdout.write('[s]')
					if best_score < i:
						best = query
						best_score = i
				else:
					sys.stdout.write('[f]')
					break

	except subprocess.CalledProcessError as e:
		print(e.output)
	print('kthxbye')

if __name__ == '__main__':
	run()



#from IPython import embed;embed()