import rdflib
from rdflib import URIRef
from collections import defaultdict


rdf = rdflib.RDF
ed = rdflib.Namespace('http://ed.en')


class Bg:
	def __init__(s, store):
		s.eden = rdflib.Graph(store)

	s.last_id = defaultdict(1)
	def new_id(s, kind):
		s.last_id[kind] += 1
		id = kind + str(s.last_id[kind])
		s.eden.add((URIRef(id), rdf.type, ed[kind]))
		return id

	def add_triple(s, spo):
		t = new_id('triple')
		eden.add(t, rdf.a, ed.triple)
		su,pr,ob = spo
		eden.add(t, has_s, su)
		eden.add(t, has_p, pr)
		eden.add(t, has_b, ob)
		return t

	def add_rule(s, head, body):
		t = new_id('rule')
		if head:





