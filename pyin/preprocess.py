#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rdflib
from rdflib import BNode, URIRef, Variable
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


dddd='#'
bbbb= 'file:///'
dddd= bbbb

def read(x):

	store = OrderedStore()
	gg = Graph(store=store, identifier=dddd)
	g = ConjunctiveGraph(store=store, identifier=dddd)
	g.default_union = False
	gg.parse(x, format='n3')
	ostore = OrderedStore()
	return g, ConjunctiveGraph(store=ostore, identifier=dddd)


@click.command()
@click.option('--kb', type=bool)
@click.argument('input', type=click.File('rb'))
def cli(kb, input):
	g, og=read(input)
	for spo,c in g.store.triples((None, None, None),None):
		s,p,o = spo
		s = fixup(s)
		p = fixup(p)
		o = fixup(o)
		cc = URIRef(c.identifier, base=bbbb)
		spocc = (s,p,o,cc)
        r = "%s %s %s %s .\n" % (s.n3(),p.n3(),o.n3(),
								 ('' if cc == bbbb else cc.n3()))


#	print()
#	print()
	print()
	print()
	for l in (og.serialize(format='nquads')).splitlines():
		print(l.decode('utf8'))


def fixup(o):
	if type(o) == BNode:
		o = Variable(str(o))
	elif isinstance(o, Graph):
		o = URIRef(o.identifier, base=bbbb)
	if type(o) == Variable:
		o = URIRef(o.n3(), base=bbbb)
	return o


if __name__ == "__main__":
	cli()


#from IPython import embed; embed(); exit()


