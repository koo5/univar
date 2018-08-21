#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rdflib
from rdflib import BNode
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
	gg.parse(x, format='n3')
	return g


@click.command()
@click.argument('kb', type=click.File('rb'))
def kb(kb):
	g=read(kb)
	g.serialize('x', format='nquads')
	#from IPython import embed; embed(); exit()
	#kb_graph_triples = list(g.triples((None, None, None)))
	#for spo in kb_graph_triples:
#		o.add()
		#if spo[1] ==


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


