#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rdflib
from ordered_rdflib_store import OrderedStore

from pyin import *

import click

@click.command()
@click.argument('kb', type=click.File('rb'))
@click.argument('goal', type=click.File('rb'))
def query_from_files(kb, goal):
	kb_stream, goal_stream = kb, goal

	implies = rdflib.URIRef("http://www.w3.org/2000/10/swap/log#implies")

	store = OrderedStore()
	kb_graph = rdflib.Graph(store=store, identifier='@default')
	kb_conjunctive = rdflib.ConjunctiveGraph(store=store)
	kb_graph.parse(kb_stream, format='nquads')
	#exit()
	rules = []

	for s,p,o in kb_graph.triples((None, None, None)):

	#	print (s,p,o)
	#exit()
	#if False:

		if p != implies:
			_g = Graph()
			_t = Triple((p), [(s), (o)])
			rules.append(Rule(_t, _g))
		else:
			for head_triple in kb_conjunctive.triples((None, None, None), o):
				#print()
				#print(head_triple, "<=")
				body = Graph()
				for body_triple in kb_conjunctive.triples((None, None, None), s):
					#print(body_triple)
					body.append(Triple((body_triple[1]), [(body_triple[0]), (body_triple[2])]))
				rules.append(Rule(Triple((head_triple[1]), [(head_triple[0]), (head_triple[2])]), body))

	goal_rdflib_graph = rdflib.Graph(store=OrderedStore())

	goal_rdflib_graph.parse(goal_stream, format='nquads')

	goal = Graph()
	for s,p,o in goal_rdflib_graph.triples((None, None, None)):
		goal.append(Triple((p), [(s), (o)]))

	def substitute(node, locals):
		if node in locals:
			v = get_value(locals[node])
			if type(v) == Var:
				return node
			elif type(v) == Atom:
				return v.value
			else:
				666
		return node

	for i in query(rules, goal):
		o = ' RESULT : '
		for triple in goal:
			#from IPython import embed; embed()
			#n1 = substitute(triple.args[0], i)
			#from IPython import embed; embed()
			o += substitute(triple.args[0], i).n3() + " " + substitute((triple.pred), i).n3() + " " + substitute(triple.args[1], i).n3() + "."
			print(o)
		print (i.__short__str__())
		print ()



if __name__ == "__main__":
	query_from_files()
