#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
	global gv_output_file
	if len(sys.argv) == 2:
		fn = sys.argv[1]
	else:
		fn = 'kbdbg.n3'
	input_file = open(fn)
	lines = []
	#os.system("rm -f kbdbg"+fn+'\\.*')

	g = Graph(OrderedStore())
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
		g.parse(data=i, format='n3')

		output_file_name = fn + '_' + str(step).zfill(5) + '.n3'
		try:
			os.unlink(output_file_name)
		except FileNotFoundError:
			pass

		output_file = open(output_file_name, 'w')
		output_file.write(i)
		output_file.close()
		steps.append(output_file_name)


	q1 = """
?kbdbg log:includes {:f a kbdbg:frame.}.
?kbdbg log:notIncludes {:f kbdbg:is_finished true.}
?kbdbg log:includes {:f kbdbg:is_for_rule :r.}.
?kbdbg log:includes {?b a kbdbg:binding. ?b kbdbg:has_source [kbdbg:has_frame ?y].}.
?kbdbg log:includes {?b kbdbg:has_target ?t.}.
?kbdbg log:includes {?t kbdbg:has_frame ?tf.}. 
"""
	full_q_lines = q1.splitlines(q1)

	longest = len(full_q_lines) + 1

	for i in range(1, longest):
		lines = full_q_lines[:i]

		vars = re.findall("\\?[azAZ09_]", q1)
		q0 = """
@prefix log: <http://www.w3.org/2000/10/swap/log#>.    
@prefix kbdbg: <http://kbd.bg/#> .
@prefix : <file:///#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
{
@forAll """ + ','.join(vars) + """.
{<file:///home/koom/univar/kbdbg.n3> log:semantics ?kbdbg .
	"""
		q2 = "} => {("
		q2 += ' '.join(vars)
		q2 += ') a :result}.

		qf_name = 'query'+str(i)+'.n3'
		qf = open(qf_name,'w')
		qf.write(q0+'\n'.join(lines)+q2)
		qf.close()

	best = 0
	for step in steps:
		for i in range(1, longest, -1):
			o = subprocess.check_output(['~/sw/swap/cwm.py', output_file_name, '--filter=' + filter_file_name])
			succ = (len(o.splitlines()) > 3)
			if succ:
				print('step ', step, 'q ', i)
				if best < i:
					best = i
				break
	print ('best', best)


if __name__ == '__main__':
	run()



#from IPython import embed;embed()