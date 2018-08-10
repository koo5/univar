#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random, time, sys
import rdflib
from rdflib import *
from rdflib.namespace import RDF
from pymantic import sparql
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.collection import Collection

import logging
logging.getLogger('sparql').setLevel(logging.INFO)
logging.getLogger().setLevel(logging.INFO)

#?goal rdf:type kbdbg:frame. MINUS {?goal kbdbg:is_finished true}. ?goal kbdbg:is_for_rule ?r.

query_lines = """

?b0 rdf:type kbdbg:binding. 
?b0 kbdbg:has_source ?s0. 
?s0 kbdbg:has_frame ?f0. 
?f0 kbdbg:is_for_rule :Rule2. 
?b0 kbdbg:has_target ?t0. 
?t0 kbdbg:has_frame ?f1. 
?f1 kbdbg:is_for_rule :Rule10.

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
	exit()
latest = URIRef(r[0]['this']['value'])
print ('latest is ' + latest.n3())

r = server.query("""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX kbdbg: <http://kbd.bg/#> 
PREFIX : <file:///#> 
SELECT * WHERE {""" + latest.n3() + """ kbdbg:is kbdbg:done}""")
if not len(r['results']['bindings']):
	print(latest + " kbdbg:is kbdbg:done not found")
	exit()

all_graphs = []
print('getting list of step graphs')
g = rdflib.ConjunctiveGraph(SPARQLStore(sp))
for i in Collection(g, g.value(latest)):
	all_graphs.append(i)
	sys.stdout.write(str(i) + ' ')
print('ok')
best = []
best_score = 0

random_order_idxs = list(range(0, len(all_graphs)))
random.shuffle(random_order_idxs)

for idx in random_order_idxs:
	graphs = all_graphs[0:idx + 1]
	level = best_score
	if level == 0:
		level = 1
	while True:
		if level < best_score:
			level = best_score
			continue
		start = time.time()
		sys.stdout.write('L'+str(level) + ' ' + str(idx).ljust(6))
		qqq = ("""
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX kbdbg: <http://kbd.bg/#> 
		PREFIX : <file:///#>
		SELECT * 
		"""
		+ '\n'.join(['FROM ' + URIRef(graph).n3() for graph in graphs]) +
		""" 
		WHERE {
		"""+ '\n'.join(query_lines[:level]) +
		"}")
		#print(qqq)
		r = server.query(qqq)
		r=r['results']['bindings']

		sys.stdout.write(' ...('+str(time.time() - start)[:6].ljust(6,'0') + 's)')
		succ = len(r) > 0
		if succ:
			sf = '[s]'
			if best_score < level:
				best = []
				best_score = level
			if best_score == level:
				best.append(idx)
		else:
			sf = '[f]'
		print (sf)
		if not succ:
			break
		elif level == len(query_lines):
			break
		level += 1
print ('best score: ' + str(best_score))
print ('best levels: ' + str(best))
