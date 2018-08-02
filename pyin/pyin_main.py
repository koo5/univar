#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymantic import sparql

server = sparql.SPARQLServer('http://192.168.122.108:9999/blazegraph/sparql')

server.update("""CLEAR GRAPHS""")


server.update("""
PREFIX dc: <http://purl.org/dc/elements/1.1/>
INSERT DATA
{ 
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix kbdbg: <http://kbd.bg/#> .
@prefix : <file:///#> .
_:x rdf:type rdf:Statement .
_:x rdf:subject :Tolkien .
_:x rdf:predicate :wrote .
_:x rdf:object :LordOfTheRings .
_:x <http://kbd.bg/#has_step> 1.
}
""")

server.update("""
PREFIX dc: <http://purl.org/dc/elements/1.1/>
INSERT DATA
{ 
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix kbdbg: <http://kbd.bg/#> .
@prefix : <file:///#> .
_:x rdf:type rdf:Statement .
_:x rdf:subject :Tolkien .
_:x rdf:predicate :wrote .
_:x rdf:object :LordOfTheRings .
_:x <http://kbd.bg/#has_step> 1.
}
""")




result = server.query('select * where { ?s ?p ?o }')
for b in result['results']['bindings']:
    print ("%s %s %s"% (b['s']['value'], b['p']['value'], b['o']['value']))

import rdflib
from ordered_rdflib_store import OrderedStore

import pyin
from pyin import *

import click

@click.command()
@click.argument('kb', type=click.File('rb'))
@click.argument('goal', type=click.File('rb'))
@click.option('--nokbdbg', default=False)
@click.option('--nolog', default=False)
@click.option('--visualize', default=False)
@click.option('--identification', default="")
def query_from_files(kb, goal, nokbdbg, nolog, visualize, identification):
	identification = "".join([ch if ch.isalnum() else "_" for ch in identification])
	fn = 'kbdbg'+identification+'.n3'
	outpath = 'visualizations/'+fn+ '/'
	pyin.kbdbg_file_name = outpath + fn
	os.system('mkdir -p '+outpath)
	pyin.nolog = nolog
	pyin.nokbdbg = nokbdbg
	pyin.init_logging()
	if identification != "":
		pyin.kbdbg(": kbdbg:has_run_identification " + rdflib.Literal(identification).n3())

#	kb=  open('kb_for_external.nq', 'rb')
#	goal=open('query_for_external.nq', 'rb')

	kb_stream, goal_stream = kb, goal

	implies = rdflib.URIRef("http://www.w3.org/2000/10/swap/log#implies")

	store = OrderedStore()
	kb_graph = rdflib.Graph(store=store, identifier='@default')
	kb_conjunctive = rdflib.ConjunctiveGraph(store=store)
	kb_graph.parse(kb_stream, format='nquads')
	#exit()
	rules = []

	"""
	--------
	kb:
	?x y ?z. 
	query:
	...
	--------
	--------
	?x y ?z. 
	?z w a.
	--------
	
	
	"""

	kb_graph_triples = list(kb_graph.triples((None, None, None)))
	facts = [Triple(x[1],[x[0],x[2]]) for x in kb_graph_triples]
	for s,p,o in kb_graph_triples:
		_t = Triple(p, [s, o])
		rules.append(Rule(facts, _t, Graph()))
		if p == implies:
			head_triples = list(kb_conjunctive.triples((None, None, None), o))
			head_triples_triples = [Triple(x[1],[x[0],x[2]]) for x in head_triples]
			for head_triple in head_triples:
				body = Graph()
				for body_triple in kb_conjunctive.triples((None, None, None), s):
					body.append(Triple((body_triple[1]), [(body_triple[0]), (body_triple[2])]))
				rules.append(Rule(head_triples_triples, Triple((head_triple[1]), [(head_triple[0]), (head_triple[2])]), body))

	goal_rdflib_graph = rdflib.Graph(store=OrderedStore())

	goal_rdflib_graph.parse(goal_stream, format='nquads')

	goal = Graph()
	for s,p,o in goal_rdflib_graph.triples((None, None, None)):
		goal.append(Triple((p), [(s), (o)]))

	for result in query(rules, goal):
		print ()
		o = ' RESULT : '
		for triple in result:
			o += str(triple)
		print (o)

	if visualize:
		os.system('python3 -O pyin/kbdbg2graphviz.py ' + pyin.kbdbg_file_name)


if __name__ == "__main__":
	query_from_files()
	"""
	try:
		query_from_files()
	except:
		import kbdbg2graphviz
		kbdbg2graphviz.run()
		raise
	"""


#from IPython import embed; embed()
