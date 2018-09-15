#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pymantic import sparql
from concurrent.futures import ThreadPoolExecutor
import subprocess
import pyin
from pyin import *
import datetime
import rdflib
from ordered_rdflib_store import OrderedStore
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

@click.command()
@click.argument('command', default="")
@click.argument('files', nargs=-1, type=click.Path())

def tau(command, files):
	for fn in files:
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
				if l.strip() == 'fin.':
					if mode == Mode.kb:
						with open('kb_for_external_raw.n3') as f:
							f.write(buffer)
					elif mode == Mode.query:
						with open('query_for_external_raw.n3') as f:
							f.write(buffer)
						os.system(command + ' kb_for_external_raw.n3 query_for_external_raw.n3')




				buffer.append(l)



	os.system('mkdir -p '+outpath)
	pyin.nolog = nolog
	pyin.nokbdbg = nokbdbg
	pyin.init_logging()
	log = pyin.log
	if sparql_uri != '':
		server.update("""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX kbdbg: <http://kbd.bg/#> 
		PREFIX : <file:///#> 
		DELETE {kbdbg:latest kbdbg:is ?x} 
		WHERE {kbdbg:latest kbdbg:is ?x}""")

		server.update("""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX kbdbg: <http://kbd.bg/#> 
		PREFIX : <file:///#> 
		INSERT {kbdbg:latest kbdbg:is """ + this + "} WHERE {}""")

	if identification != "":
		pyin.kbdbg(": kbdbg:has_run_identification " + rdflib.Literal(identification).n3())

	kb_stream, goal_stream = kb, goal
	implies = rdflib.URIRef("http://www.w3.org/2000/10/swap/log#implies")
	store = OrderedStore()
	kb_graph = rdflib.Graph(store=store, identifier=base)
	kb_conjunctive = rdflib.ConjunctiveGraph(store=store, identifier=base)
	kb_graph.parse(kb_stream, format='n3', publicID=base)

	log('---kb:')
	for l in kb_graph.serialize(format='n3').splitlines():
		log(l.decode('utf8'))
	log('---kb quads:')
	for l in kb_conjunctive.serialize(format='nquads').splitlines():
		log(l.decode('utf8'))
	log('---')

	def fixup3(o):
		if isinstance(o, rdflib.Graph):
			return URIRef(o.identifier)
		return o

	def fixup2(o):
		if type(o) == rdflib.BNode:
			return rdflib.Variable(str(o))
		return o

	def fixup(spo):
		s,p,o = spo
		return (fixup2(s), fixup2(p), fixup2(o))

	rules = []
	kb_graph_triples = [fixup(x) for x in kb_graph.triples((None, None, None))]
	facts = [Triple(fixup3(x[1]),[fixup3(x[0]),fixup3(x[2])]) for x in kb_graph_triples]
	for s,p,o in kb_graph_triples:
		_t = Triple(p, [s, o])
		rules.append(Rule(facts, _t, Graph()))
		if p == implies:
			head_triples = [fixup(x) for x in kb_conjunctive.triples((None, None, None, o))]
			head_triples_triples = [Triple(fixup3(x[1]),[fixup3(x[0]),fixup3(x[2])]) for x in head_triples]
			for head_triple in head_triples:
				body = Graph()
				for body_triple in [fixup(x) for x in kb_conjunctive.triples((None, None, None, s))]:
					body.append(Triple((fixup3(body_triple[1])), [fixup3(body_triple[0]), fixup3(body_triple[2])]))
				rules.append(Rule(head_triples_triples, Triple(fixup3(head_triple[1]), [fixup3(head_triple[0]), fixup3(head_triple[2])]), body))

	goal_rdflib_graph = rdflib.ConjunctiveGraph(store=OrderedStore(), identifier=base)
	goal_rdflib_graph.parse(goal_stream, format='n3', publicID=base)
	goal = Graph()

	log('---goal:')
	for l in goal_rdflib_graph.serialize(format='n3').splitlines():
		log(l.decode('utf8'))
	log('---goal nq:')
	for l in goal_rdflib_graph.serialize(format='nquads').splitlines():
		log(l.decode('utf8'))
	log('---')

	for s,p,o in [fixup(x) for x in goal_rdflib_graph.triples((None, None, None, None))]:
		goal.append(Triple(fixup3(p), [fixup3(s), fixup3(o)]))

	for result in query(rules, goal):
		print ()

		r = ''
		for triple in result:
			r += triple.str()
		print(' RESULT :' + r)
		pyin.kbdbg('#result: ' + r)

	if sparql_uri != '':
		server.update("""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX kbdbg: <http://kbd.bg/#> 
		PREFIX : <file:///#> 
		INSERT {""" + this + " kbdbg:is kbdbg:done} WHERE {}""")

	if visualize:
		os.system('pypy3.5 -O pyin/kbdbg2graphviz.py ' + pyin.kbdbg_file_name)


	if sparql_uri != '':
		pyin.pool.shutdown()

if __name__ == "__main__":
	tau()

#from IPython import embed; embed()
