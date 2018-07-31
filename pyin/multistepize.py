#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import subprocess
import re
import os
import sys
import multiprocessing
from rdflib.namespace import Namespace

kbdbg = Namespace('http://kbd.bg/#')

def run():
	os.system('rm -rf filter/*')

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

		output_file_name = fn + '_' + str(step).zfill(5) + '.n3'
		output_file_path = 'filter/'+ output_file_name
		try:
			os.unlink(output_file_path)
		except FileNotFoundError:
			pass

		output_file = open(output_file_path, 'w')
		output_file.write(i)
		output_file.close()


		q1 = """
		:kbdbg log:includes {:f a kbdbg:frame.}.
		:kbdbg log:notIncludes {:f kbdbg:is_finished true.}.
		:kbdbg log:includes {:f kbdbg:is_for_rule :r.}.
		:kbdbg log:includes {:b a kbdbg:binding. :b kbdbg:has_source [kbdbg:has_frame :y].}.
		:kbdbg log:includes {:b kbdbg:has_target :t.}.
		:kbdbg log:includes {:t kbdbg:has_frame :tf.}. 
		"""
		full_q_lines = q1.strip().splitlines()

		filters = []

		for i in range(len(full_q_lines), 0, -1):
			q_lines = full_q_lines[:i]
			qqq = '\n'.join(q_lines)
			vars = re.findall(".:[a-zA-Z0-9_]*", qqq)
			vars = set([x[1:] for x in filter(lambda x: not x[0].isalnum() and not (x[0] in '_'), vars)])
			vars.add(':kbdbg')
			q0 = """@prefix log: <http://www.w3.org/2000/10/swap/log#> .    
@prefix kbdbg: <http://kbd.bg/#> .
@prefix : <file:///#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@forAll """ + ','.join(vars) + """.
	{<""" + output_file_name + """> log:semantics :kbdbg .
		
		
		"""
			q2 = "\n\n\n} => {("
			q2 += ' '.join(vars)
			q2 += ') a :result}.'

			qf_name = output_file_path + '.query'+str(i)+'.n3'
			qf = open(qf_name,'w')
			qf.write(q0+qqq+q2)
			qf.close()
			filters.append((i, qf_name))
		steps.append((output_file_name, reversed(filters)))

	#filters = list(reversed(filters))
	#with multiprocessing.Pool(8) as p:
	#https://stackoverflow.com/questions/3033952/threading-pool-similar-to-the-multiprocessing-pool

	#from concurrent.futures import ThreadPoolExecutor
	#pool = ThreadPoolExecutor(max_workers = 4)

	random_order_steps = steps[:]
	import random
	random.shuffle(random_order_steps)
	try:
		best = []
		best_score = 0
		for step, filters in random_order_steps:
			for i, query in filters:
				if i < best_score:
					continue
				start = time.time()
				desc = ' '.join([query])
				sys.stdout.write(desc)
				cmd = ['/usr/bin/python', '-O', '/home/koom/sw/swap/cwm.py', 'empty.n3', '--filter=' + query]
				o = subprocess.check_output(cmd)
				sys.stdout.write(' ('+str(time.time() - start).ljust(20,'0') + 's)')
				succ = (len(o.splitlines()) > 3)
				if succ:
					sf = '[s]'
					if best_score <= i:
						best = []
						best_score = i
					if best_score == i:
						best.append(step)
				else:
					sf = '[f]'
				print (sf)
				if not succ: break

	except subprocess.CalledProcessError as e:
		print(e.output)
	print('kthxbye')

if __name__ == '__main__':
	run()



#from IPython import embed;embed()