#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rdflib
from rdflib import BNode, URIRef
from rdflib.graph import QuotedGraph, ConjunctiveGraph, Graph
from ordered_rdflib_store import OrderedStore
import click


def my_n3(self):
	"""Return an n3 identifier for the Graph"""
	return self.identifier.n3()
QuotedGraph.n3 = my_n3


from rdflib.plugins.parsers import notation3
def my_id(self):
	return BNode('Formula%s' % self.number)
notation3.Formula.id = my_id
del my_id



@click.group()
def cli():
    pass




def read(x):
	store = OrderedStore()
	gg = Graph(store=store, identifier='#')
	g = ConjunctiveGraph(store=store, identifier='#')
	g.default_union = False
	gg.parse(x, format='n3')
	return g


@click.command()
@click.argument('kb', type=click.File('rb'))
def kb(kb):
	g=read(kb)
	for l in (g.serialize(format='nquads')).splitlines():
		print(l)

	ostore = OrderedStore()
	og = ConjunctiveGraph(store=ostore, identifier='#')

	print(list(g.contexts(None)))

	implies = rdflib.URIRef("http://www.w3.org/2000/10/swap/log#implies")
	global_facts = URIRef('#global_facts')
	og.add((URIRef('#empty_graph'), implies, global_facts))

	for c in g.contexts(None):
		print ('context:', c)
		for spo in g.triples((None, None, None, c)):
			s,p,o = spo
			print('spo:', spo)
			if type(s) == BNode:
				s = URIRef('?' + str(s))
			if type(o) == BNode:
				o = URIRef('?' + str(o))
			cc = global_facts if (c.identifier == URIRef('#')) else c
			og.add((s,p,o,cc))

	print()
	print()
	print()
	print()
	for l in (og.serialize(format='nquads')).splitlines():
		print(l.decode('utf8'))


#from IPython import embed; embed(); exit()

@click.command()
@click.argument('goal', type=click.File('rb'))
def goal(goal):
	pass

cli.add_command(kb)
cli.add_command(goal)



if __name__ == "__main__":
	cli()


#from IPython import embed; embed(); exit()


