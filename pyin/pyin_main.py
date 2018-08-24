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


server, this = None, None


@click.command()
@click.argument('kb', type=click.File('rb'))
@click.argument('goal', type=click.File('rb'))
@click.option('--nokbdbg', default=False)
@click.option('--nolog', default=False)
@click.option('--visualize', default=False)
@click.option('--sparql', default=False)
@click.option('--identification', default="")
def query_from_files(kb, goal, nokbdbg, nolog, visualize, sparql, identification):
	global server, this
	if sparql:
		pyin.pool = ThreadPoolExecutor(8)#max_workers = , thread_name_prefix='sparql_updater'
		server = sparql.SPARQLServer('http://192.168.122.108:9999/blazegraph/sparql')
		server.update("""CLEAR GRAPHS""")
		pyin.server = server
	this = ":"+str(datetime.datetime.now()).replace(':', '-').replace('.', '-').replace(' ', '-')
	pyin.this = this
	identification = "".join([ch if ch.isalnum() else "_" for ch in identification])
	fn = 'kbdbg'+identification+'.n3'
	outpath = 'visualizations/'+fn+ '/'
	pyin.kbdbg_file_name = outpath + fn
	pyin._rules_file_name = pyin.kbdbg_file_name + '_rules'
	subprocess.call(['rm', '-f', pyin._rules_file_name])
	os.system('mkdir -p '+outpath)
	pyin.nolog = nolog
	pyin.nokbdbg = nokbdbg
	pyin.init_logging()

	if sparql:
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
	kb_graph = rdflib.Graph(store=store, identifier='file:///')
	kb_conjunctive = rdflib.ConjunctiveGraph(store=store, identifier='file:///')
	kb_graph.parse(kb_stream, format='nquads')

	print('---kb:')
	for l in (og.serialize(format='nquads')).splitlines():
		print(l.decode('utf8'))
	print('---')

	def fixup2(o):
		if type(o) == rdflib.BNode:
			return rdflib.Variable(str(o))
		return o

	def fixup(spo):
		s,p,o = spo
		return (fixup(s), fixup(p), fixup(o))

	rules = []
	kb_graph_triples = [fixup(x) for x in kb_graph.triples((None, None, None))]
	facts = [Triple(x[1],[x[0],x[2]]) for x in kb_graph_triples]
	for s,p,o in kb_graph_triples:
		_t = Triple(p, [s, o])
		rules.append(Rule(facts, _t, Graph()))
		if p == implies:
			head_triples = [fixup(x) for x in kb_conjunctive.triples((None, None, None), o)]
			head_triples_triples = [Triple(x[1],[x[0],x[2]]) for x in head_triples]
			for head_triple in head_triples:
				body = Graph()
				for body_triple in [fixup(x) for x in kb_conjunctive.triples((None, None, None), s)]:
					body.append(Triple((body_triple[1]), [(body_triple[0]), (body_triple[2])]))
				rules.append(Rule(head_triples_triples, Triple((head_triple[1]), [(head_triple[0]), (head_triple[2])]), body))

	goal_rdflib_graph = rdflib.Graph(store=OrderedStore(), identifier='file:///')
	goal_rdflib_graph.parse(goal_stream, format='nquads')
	goal = Graph()
	for s,p,o in goal_rdflib_graph.triples((None, None, None)):
		goal.append(Triple((p), [(s), (o)]))

	for result in query(rules, goal):
		print ()
		o = ' RESULT : '
		for triple in result:
			o += triple.str()
		print (o)

	if sparql:
		server.update("""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX kbdbg: <http://kbd.bg/#> 
		PREFIX : <file:///#> 
		INSERT {""" + this + " kbdbg:is kbdbg:done} WHERE {}""")

	if visualize:
		os.system('pypy3.5 -O pyin/kbdbg2graphviz.py ' + pyin.kbdbg_file_name)


	if sparql:
		pyin.pool.shutdown()

if __name__ == "__main__":
	query_from_files()

#from IPython import embed; embed()
