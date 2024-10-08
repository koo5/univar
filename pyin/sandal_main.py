#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import rdflib
from ordered_rdflib_store import OrderedStore
import sandal
import pyin


implies = rdflib.URIRef("http://www.w3.org/2000/10/swap/log#implies")


@click.command()
@click.argument('kb', type=click.File('rb'))
@click.argument('goal', type=click.File('rb'))
@click.option('--nokbdbg', default=False)
@click.option('--nolog', default=False)
def query_from_files(kb, goal, nokbdbg, nolog):
	
	pyin.nolog = nolog
	pyin.nokbdbg = nokbdbg

	store = OrderedStore()

	kb_graph = rdflib.Graph(store=store, identifier='@default')
	kb_conjunctive = rdflib.ConjunctiveGraph(store=store)
	kb_graph.parse(kb, format='nquads')

	rules = []



	for s,p,o in kb_graph.triples((None, None, None)):
		_t = Triple(p, [s, o])
		rules.append(Rule(kb_graph, _t, Graph()))
		if p == implies:
			head_triples = kb_conjunctive.triples((None, None, None), o)
			for head_triple in head_triples:
				body = Graph()
				for body_triple in kb_conjunctive.triples((None, None, None), s):
					body.append(Triple((body_triple[1]), [(body_triple[0]), (body_triple[2])]))
				rules.append(Rule(head_triples, Triple((head_triple[1]), [(head_triple[0]), (head_triple[2])]), body))

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



if __name__ == "__main__":
	query_from_files()


#from IPython import embed; embed()
