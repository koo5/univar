#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import common
import subprocess
import click
from click import echo, style
from enum import Enum, auto
import rdflib
from rdflib import URIRef, BNode, Variable
from ordered_rdflib_store import OrderedStore
from itertools import chain


class Mode(Enum):
	none = auto()
	kb = auto()
	query = auto()
	shouldbe = auto()

identification = '?'
mode = Mode.none
prefixes = []
buffer = []
output = ''
fn = '?'

@click.command()
@click.argument('command', type=click.Path(readable=True, exists=True, dir_okay=False), required=True)
@click.argument('files', nargs=-1, type=click.Path(allow_dash=True, readable=True, exists=True, dir_okay=False), required=True)

def tau(command, files):
	global mode, buffer, prefixes, output, fn, identification
	query_counter = 0
	for fn in files:
		echo(fn+':')
		query_counter = 0
		results = []
		base = fn
		remaining_results = []
		mode = Mode.none
		prefixes = []
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
					if len(remaining_results) != 0:
						fail(str(len(remaining_results)) + ' results remaining')
					else:
						success()
					continue
				elif l_stripped.startswith('--limit'):
					continue
				try:
					mode = Mode[l_stripped]
				except KeyError:
					fail()
					echo("can't make sense of line " + str(line_number) + ':')
					echo(l)
					echo('please make sense and try again')
					fail()
			else:
				if l_stripped == 'fin.':
					if mode == Mode.kb:
						write_out('kb_for_external_raw.n3')
						continue
					elif mode == Mode.query:
						write_out('query_for_external_raw.n3')
						identification = common.fix_up_identification(fn + '_' + str(query_counter))
						identify()
						r = subprocess.run(['bash', '-c', command + ' --identification ' + identification + ' --base ' + base],
							universal_newlines=True, stdout=subprocess.PIPE)
						if r.returncode != 0:
							fail()
							print_kwrite_link()
						else:
							for output_line in r.stdout.splitlines():
								echo(output_line)
								result_marker = ' RESULT :'
								if output_line.startswith(result_marker):
									results.append(output_line[len(result_marker):])
						query_counter += 1
						continue
					elif mode == Mode.shouldbe:

						shouldbe_graph = rdflib.Graph(store=OrderedStore(), identifier='file://'+base)
						shouldbe_graph.parse(data=grab_buffer(), format='n3', publicID='file://'+base)

						l1 = len(shouldbe_graph)
						l2 = len(results)
						if not l1 and not l2:
							success()
							mode = Mode.none
							buffer = []
							continue

						if not len(results):
							echo('no more results')
							fail()
							print_kwrite_link()
							mode = Mode.none
							buffer = []
							continue

						result_graph = rdflib.Graph(store=OrderedStore(), identifier=base)
						result_graph.parse(data=results.pop(0), format='n3', publicID=base)

						cmp = do_results_comparison(shouldbe_graph, result_graph)
						if cmp == True:
							success()
						else:
							fail()
							echo(cmp)
							print_kwrite_link()
						mode = Mode.none
						continue
				buffer.append(l)
		if buffer != []:
			echo('file not ended properly?')
			exit(1)


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
	return str(round(time.perf_counter(), 3)).ljust(10) + ' '

def success():
	echo(timestamp()+identification+":test:PASS")

def fail():
	echo(timestamp()+identification+":test:FAIL")

def identify():
	echo(timestamp()+identification+":test:")

def grab_buffer():
	global buffer
	r = ''.join(chain(prefixes, buffer))
	buffer = []
	return r

def write_out(fn):
	global mode
	with open(fn, 'w') as f:
		f.write(grab_buffer())
	mode = Mode.none

def print_kwrite_link():
	echo("kwrite " + common.kbdbg_file_name(identification))

if __name__ == "__main__":
	tau()

#from IPython import embed; embed()
# + ' kb_for_external_raw.n3 query_for_external_raw.n3'
