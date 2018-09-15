#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import subprocess
import click
from click import echo
from enum import Enum, auto


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
	for fn in files:
		prefixes = []
		if buffer != []:
			echo('previous file not ended properly?')
			exit(1)
		mode = Mode.none
		output = ''
		for line_number, l in enumerate(open(fn).readlines()):
			line_number += 1
			if mode == Mode.none:
				if l.startswith('@prefix'):
					prefixes.append(l)
					continue
				try:
					mode = Mode[l.strip()]
				except KeyError:
					echo("can't make sense of line " + str(line_number) + ':')
					echo(line)
					echo('please make sense and try again')
					exit(1)
			else:
				l_stripped = l.strip()
				if l_stripped == 'fin.':
					if mode == Mode.kb:
						with open('kb_for_external_raw.n3', 'w') as f:
							f.write(''.join(buffer))
						buffer = []
						mode = Mode.none
						continue
					elif mode == Mode.query:
						with open('query_for_external_raw.n3', 'w') as f:
							f.write(''.join(buffer))
						buffer = []
						mode = Mode.none
						r = subprocess.run(['bash', '-c', command],
							universal_newlines=True, stdout=subprocess.PIPE)
						print(r.returncode, r.stdout)
						continue
					elif mode == Mode.shouldbe:
						

				buffer.append(l)


if __name__ == "__main__":
	tau()

#from IPython import embed; embed()
# + ' kb_for_external_raw.n3 query_for_external_raw.n3'
