#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import subprocess
import click
from click import echo, style
from enum import Enum, auto
import rdflib
from ordered_rdflib_store import OrderedStore
from itertools import chain


class Mode(Enum):
	none = auto()
	kb = auto()
	query = auto()
	shouldbe = auto()

mode = Mode.none
prefixes = []
buffer = []
output = ''

@click.command()
@click.argument('command')
@click.argument('files', nargs=-1, type=click.Path(allow_dash=True, readable=True), required=True)

def tau(command, files):
	global mode, buffer, prefixes, output
	query_counter = 0
	for fn in files:
		base = 'file://'  + fn
		identification = fn + '_' + str(query_counter)
		prefixes = []
		if buffer != []:
			echo('previous file not ended properly?')
			exit(1)
		mode = Mode.none
		output = ''
		for line_number, l in enumerate(open(fn).readlines()):
			line_number += 1
			l_stripped = l.strip()
			if mode == Mode.none:
				if l.startswith('@prefix'):
					prefixes.append(l)
					continue
				elif l_stripped == '':
					continue
				elif l_stripped == 'thatsall':
					if len(remaining_results) != 0:
						fail(str(len(remaining_results)) + ' results remaining')
				try:
					mode = Mode[l_stripped]
				except KeyError:
					echo("can't make sense of line " + str(line_number) + ':')
					echo(l)
					echo('please make sense and try again')
					exit(1)
			else:
				if l_stripped == 'fin.':
					if mode == Mode.kb:
						write_out('kb_for_external_raw.n3')
						continue
					elif mode == Mode.query:
						write_out('query_for_external_raw.n3')
						r = subprocess.run(['bash', '-c', command],
							universal_newlines=True, stdout=subprocess.PIPE)
						result_stdout = ''
						if r.returncode != 0:
							echo("ERR")
							echo("kwrite " + kbdbg_file_name)
							result_stdout = r.stdout
						query_counter += 1
						continue
					elif mode == Mode.shouldbe:
						shouldbe_graph = rdflib.Graph(store=OrderedStore(), identifier=base)
						result_graph = rdflib.Graph(store=OrderedStore(), identifier=base)
						result_graph.parse(data=result_stdout, format='n3', publicID=base)
						shouldbe_graph.parse(data=grab_buffer(), format='n3', publicID=base)
						compare_results(shouldbe_graph, result_graph)
						mode = Mode.none
						continue
				buffer.append(l)


def compare_results(a,b):
	echo ('compare_results ' + str((a,b)))


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


if __name__ == "__main__":
	tau()

#from IPython import embed; embed()
# + ' kb_for_external_raw.n3 query_for_external_raw.n3'
