#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import time, os
import common
from rdflib.plugins.parsers import notation3
notation3.RDFSink.newList = common.newList
import subprocess
import click
from click import echo, style
from enum import Enum
import rdflib
from rdflib import URIRef, BNode, Variable
from rdflib.plugins.parsers import notation3
from ordered_rdflib_store import OrderedStore
from itertools import chain


class Mode(Enum):
	none = 0
	kb = 1
	query = 2
	shouldbe = 3

result_marker = ' RESULT :'
query_number = 6666666
identification = '?'
results_limit = 50
mode = Mode.none
prefixes = []
results = []
buffer = []
output = ''
fn = '?'

@click.command()#readable=True, exists=True, dir_okay=False
@click.argument('command', type=click.Path(), required=True)
@click.argument('files', nargs=-1, type=click.Path(allow_dash=True, readable=True, exists=True, dir_okay=False), required=True)
@click.option('--only-id', type=click.INT)
def tau(command, files, only_id):
	global mode, buffer, prefixes, output, fn, identification, query_number, base, already_failed_because_no_more_results, results
	for fn in files:
		echo(fn+':test:')
		query_number = None
		results = []
		base = fn
		identification = None
		mode = Mode.none
		prefixes = ['@prefix : <file://>.\n']
		output = ''
		buffer = []
		for line_number, l in enumerate(do_includes(fn)):
			line_number += 1
			l_stripped = l.strip()
			if mode == Mode.none:
				if l.startswith('@prefix') or l.startswith('@keywords'):
					prefixes.append(l)
					continue
				elif l_stripped == '':
					continue
				elif l_stripped.startswith('#'):
					continue
				elif l_stripped == 'thatsall':
					if only_id != None and only_id != query_number:
						continue
					if already_failed_because_no_more_results:
						continue
					if len(results) != 0:
						print('expecting 0 but ' +str(len(results)) + ' results remaining')
						fail()
					else:
						success()
					continue
				elif l_stripped.startswith('--limit'):
					print('-- limit is todo')
					continue
				elif l_stripped == 'shouldbetrue':
					if only_id == None or only_id == query_number:
						shouldbe_graph = parse(data=out, identifier='file://'+base, publicID='file://'+base)
						check_result(results, shouldbe_graph)
					continue
				try:
					mode = Mode[l_stripped]
				except KeyError:
					fail()
					echo("can't make sense of line " + str(line_number) + ':')
					echo(l)
					echo('please make sense and try again')
					fail()
					exit()
			else:
				if l_stripped == 'fin.':
					if mode == Mode.kb:
						kb_raw_text = grab_buffer()
						mode = Mode.none
						continue
					elif mode == Mode.query:
						results = []
						if query_number == None:
							query_number = 0
						else:
							query_number = query_number + 1
						if only_id != None and only_id != query_number:
							buffer = []
							mode = Mode.none
							continue
						already_failed_because_no_more_results = False
						set_new_identification()
						identify()
						trace_output_path = common.trace_output_path(identification)
						os.system('mkdir -p '+trace_output_path)

						with open(trace_output_path+'kb_for_external_raw.n3', 'w') as f:
							f.write(kb_raw_text)

						euler_buffer = ''.join(buffer)
						euler_formula = '{' + euler_buffer + '} <= {' + euler_buffer + '}.'
						with open(trace_output_path+'query_for_external_euler.n3', 'w') as f:
							f.write(''.join(prefixes) + euler_formula)
						write_out(trace_output_path+'query_for_external_raw.n3')
						cccc= ' '.join([
							command, ' --identification ', identification, ' --base ', base,
							trace_output_path + 'kb_for_external_raw.n3', trace_output_path+ 'query_for_external_raw.n3'
						])
						print(cccc)
						popen = None
						def exit_gracefully(signum, frame):
							exit_gracefully2()
						def exit_gracefully2():
							print('exit_gracefully..')
							print('exit_gracefully..')
							print('exit_gracefully..')
							popen.terminate()
						import atexit
						atexit.register(exit_gracefully2)
						import signal
						signal.signal(signal.SIGTERM, exit_gracefully)
						signal.signal(signal.SIGILL, exit_gracefully)
						signal.signal(signal.SIGQUIT, exit_gracefully)
						signal.signal(signal.SIGINT, exit_gracefully)
						signal.signal(signal.SIGABRT, exit_gracefully)
						signal.signal(signal.SIGPIPE, exit_gracefully)
						#signal.signal(signal.SIGCHLD, exit_gracefully)
						try:
							#print('popen..')
							popen = subprocess.Popen(['bash', '-c', cccc], universal_newlines=True, stdout=subprocess.PIPE, bufsize=1)
							popen_output = ''
							#print('poll..')
							while popen.poll() == None:
								process_output(popen.stdout.readline())
							if not popen.stdout.closed:
								process_output(popen.stdout.readline())
							if popen.returncode:
								fail()
								print_kwrite_link()
							continue
						except e:
							print(e)
					elif mode == Mode.shouldbe:
						if only_id != None and only_id != query_number:
							buffer = []
							mode = Mode.none
							continue
						shouldbe_graph = parse(data=buffer_text(), identifier='file://'+base, publicID='file://'+base)
						check_result(results, shouldbe_graph)
						buffer = []
						mode = Mode.none
						continue
				buffer.append(l)
		if buffer != []:
			echo('file not ended properly?')
			fail()
			exit()
	echo(":test:that's all, folks")

def do_includes(fn):
	result = []
	for l in open(fn).readlines():
		match = re.match(r"^@include (.*)", l)
		if match:
			result += do_includes(os.path.dirname(fn) + '/' + match.groups()[0])
		else:
			result.append(l)
	return result

def process_output(output_line):
	print(output_line)
	if output_line.startswith(result_marker):
		if len(results) > results_limit:
			print("more than ", results_limit, " results, ignoring")
		else:
			results.append(output_line[len(result_marker):])


def check_result(results, shouldbe_graph):
	global already_failed_because_no_more_results
	l1 = len(shouldbe_graph)
	l2 = len(results)
	print('expected:')
	aa = []
	for at in list(shouldbe_graph.triples((None, None, None))):
		aa.append((at[0], common.un_move_me_ize_pred(at[1]), at[2]))
	for a in aa:
		print(a[0].n3(), a[1].n3(), a[2].n3())
	print('.')
	if not l1 and not l2:
		success()
		return
	if not len(results):
		already_failed_because_no_more_results = True
		echo('no more results')
		fail()
		print_kwrite_link()
		return
	result_to_parse = results.pop(0)
	#print('result_to_parse',result_to_parse,';')
	result_graph = parse(data=''.join(prefixes+[result_to_parse]), identifier=base, publicID=base)
	cmp = do_results_comparison(aa, result_graph)
	if cmp == True:
		success()
		return
	else:
		fail()
		echo(cmp)
		print_kwrite_link()

def parse(data, identifier, publicID):
	try:
		graph = rdflib.Graph(store=OrderedStore(), identifier=identifier)
		graph.parse(data=data, format='n3', publicID=publicID)
	except notation3.BadSyntax as e:
		echo(':test:parsing failed in:')
		echo(data)
		echo(str(e))
		fail()
	return graph

def set_new_identification():
	global identification
	identification = common.fix_up_identification(fn + '_' + str(query_number if query_number != None else 0))

def print_graph(g):
	for i in g.triples((None, None, None)):
		print(i)

def do_results_comparison(aa, b):
	#echo ('compare_results ' + str((a,b)))
#	print('expected:')
#	print_graph(a)
#	print('got:')
#	print_graph(b)
#	print('.')
	correspondences = {}

	bb = list(b.triples((None, None, None)))

	print('got:')
	for a in b:
		print(a[0].n3(), a[1].n3(), a[2].n3())
	print('.')

	if len(aa) != len(bb):
		return "len "+str(len(aa)) +' != len ' + str(len(bb))
	for i,at in enumerate(aa):
		bt = bb[i]
		for ti, an in enumerate(at):
			bn = bt[ti]
			if type(an) == URIRef and type(bn) == URIRef:
				if str(an) == str(bn):
					continue
				return str(an) + ' != ' + str(bn)
			if type(an) == URIRef or type(bn) == URIRef:
				return str(an) + ' != ' + str(bn)
			if an in correspondences:
				if bn == correspondences[an]:
					continue
				return str(bn) + ' != ' + str(correspondences[an])
			correspondences[an] = bn
	return True

def timestamp():
	return '%10.2f ' % time.time()

def success():
	echo(timestamp()+identification+":test:...ok")

def fail():
	echo(timestamp()+(identification if identification else fn)+":test:...FAIL:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(:(")

def identify():
	echo(timestamp()+identification+":test:")

def buffer_text():
	return ''.join(chain(prefixes, buffer))

def grab_buffer():
	global buffer
	r = buffer_text()
	buffer = []
	return r

def write_out(fn):
	global mode, out
	out = grab_buffer()
	with open(fn, 'w') as f:
		f.write(out)
	mode = Mode.none

def print_kwrite_link():
	#echo("kwrite " + common.kbdbg_file_name(identification))
	pass

if __name__ == "__main__":
	tau()

#from IPython import embed; embed()
# + ' kb_for_external_raw.n3 query_for_external_raw.n3'
