import rdflib
from rdflib import URIRef
from collections import defaultdict


rdf = rdflib.RDF
ed = rdflib.Namespace('http://ed.en')


class Bg:
	def __init__(s, store):
		s.eden = rdflib.Graph(store)

	s.last_id = defaultdict(1)
	def new(s, kind):
		s.last_id[kind] += 1
		id = kind + str(s.last_id[kind])
		s.eden.add((URIRef(id), rdf.type, ed[kind]))
		return id

	def add_triple(s, spo):
		t = s.new('triple')
		s.eden.add(t, rdf.a, ed.triple)
		su,pr,ob = spo
		s.eden.add(t, has_s, su)
		s.eden.add(t, has_p, pr)
		s.eden.add(t, has_b, ob)
		return t

	def add_rule(s, head, body):
		t = s.new('rule')
		def add(meat, identification):
			if meat:
				h = s.new('term_list')
				s.eden.add((t, ed[identification], h))
				c=rdflib.collection.Collection(s.eden, URIRef(h))
				for i in meat:
					c.add(s.add_triple(i))
		add(head, 'has_head')
		add(body, 'has_body')








