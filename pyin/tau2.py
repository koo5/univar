#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
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

query_number = 6666666
identification = '?'
mode = Mode.none
prefixes = []
buffer = []
output = ''
fn = '?'

@click.command()#readable=True, exists=True, dir_okay=False
@click.argument('command', type=click.Path(), required=True)
@click.argument('files', nargs=-1, type=click.Path(allow_dash=True, readable=True, exists=True, dir_okay=False), required=True)
@click.option('--only-id', type=click.INT)
def tau(command, files, only_id):
	global mode, buffer, prefixes, output, fn, identification, query_number, base
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
		for line_number, l in enumerate(open(fn).readlines()):
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
					if len(results) != 0:
						print('expecting 0 but ' +str(len(results)) + ' results remaining')
						fail()
					else:
						success()
					continue
				elif l_stripped.startswith('--limit'):
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
						write_out('kb_for_external_raw.n3')
						continue
					elif mode == Mode.query:
						if query_number == None:
							query_number = 0
						else:
							query_number = query_number + 1
						if only_id != None and only_id != query_number:
							buffer = []
							mode = Mode.none
							continue

						euler_buffer = ''.join(buffer)
						euler_formula = '{' + euler_buffer + '} <= {' + euler_buffer + '}.'
						with open('query_for_external_euler.n3', 'w') as f:
							f.write(''.join(prefixes) + euler_formula)
						write_out('query_for_external_raw.n3')
						set_new_identification()
						identify()
						try:
							r = subprocess.Popen(['bash', '-c', command + ' --identification ' + identification + ' --base ' + base],
											 universal_newlines=True, stdout=subprocess.PIPE)
						except CalledProcessError as e:
							fail()
							print_kwrite_link()
						else:
							ssss = r.stdout
							for output_line in ssss.read().splitlines():
								echo('ooo'+output_line)
								result_marker = ' RESULT :'
								if output_line.startswith(result_marker):
									results.append(output_line[len(result_marker):])
						continue
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

def check_result(results, shouldbe_graph):
	l1 = len(shouldbe_graph)
	l2 = len(results)
	if not l1 and not l2:
		success()
		return
	if not len(results):
		echo('no more results')
		fail()
		print_kwrite_link()
		return
	result_to_parse = results.pop(0)
	#print('result_to_parse',result_to_parse,';')
	result_graph = parse(data=''.join(prefixes+[result_to_parse]), identifier=base, publicID=base)
	cmp = do_results_comparison(shouldbe_graph, result_graph)
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
	identification = common.fix_up_identification(fn + '_' + str(query_number))

def print_graph(g):
	for i in g.triples((None, None, None)):
		print(i)

def do_results_comparison(a, b):
	#echo ('compare_results ' + str((a,b)))
	print('expected:')
	print_graph(a)
	print('got:')
	print_graph(b)
	print('.')
	correspondences = {}
	aa = list(a.triples((None, None, None)))
	bb = list(b.triples((None, None, None)))
	bb.reverse()
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
	echo(timestamp()+identification+":test:PASS")

def fail():
	echo(timestamp()+(identification if identification else fn)+":test:FAIL")

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
	echo("kwrite " + common.kbdbg_file_name(identification))

if __name__ == "__main__":
	tau()

#from IPython import embed; embed()
# + ' kb_for_external_raw.n3 query_for_external_raw.n3'
