import random, time, sys
import rdflib
from rdflib import *
from rdflib.namespace import RDF
from pymantic import sparql
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.collection import Collection

query_lines = """
?f rdf:type kbdbg:frame.
MINUS {?f kbdbg:is_finished true}.
?f kbdbg:is_for_rule ?r.
?b rdf:type kbdbg:binding. ?b kbdbg:has_source ?st. ?st kbdbg:has_frame ?y.
?b kbdbg:has_target ?t.
?t kbdbg:has_frame ?tf. 
""".strip().splitlines()

sp = 'http://192.168.122.108:9999/blazegraph/sparql'

server = sparql.SPARQLServer(sp)
server.post_directly = True
r = server.query("""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX kbdbg: <http://kbd.bg/#> 
PREFIX : <file:///#> 
SELECT ?this WHERE {kbdbg:latest kbdbg:is ?this}""")
r=(r['results']['bindings'])
if not len(r):
	print("no kbdbg:latest")
latest = URIRef(r[0]['this']['value'])

g = rdflib.ConjunctiveGraph(SPARQLStore(sp))
c = Collection(g, g.value(latest))
all_graphs = list(c)

best = []
best_score = 0

random_order_idxs = list(range(0, len(all_graphs)))
random.shuffle(random_order_idxs)

for idx in random_order_idxs:
	graphs = all_graphs[0:idx + 1]
	level = best_score
	while True:
		if level < best_score:
			level += 1
			continue
		start = time.time()
		sys.stdout.write(str(level))
		qqq = ("""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX kbdbg: <http://kbd.bg/#> 
		PREFIX : <file:///#>
		SELECT * 
		"""
		+ '\n'.join(['FROM ' + URIRef(graph).n3() for graph in graphs]) +
		""" 
		WHERE {
		"""+ '\n'.join(query_lines[:level + 1]) +
		"}")
		print(qqq)
		r = server.query(qqq)
		r=r['results']['bindings']

		sys.stdout.write(' ('+str(time.time() - start)[:6].ljust(6,'0') + 's)')
		succ = len(r) > 0
		if succ:
			sf = '[s]'
			if best_score <= level:
				best = []
				best_score = level
			if best_score == level:
				best.append(idx)
		else:
			sf = '[f]'
		print (sf)
		if not succ: break
		level += 1

