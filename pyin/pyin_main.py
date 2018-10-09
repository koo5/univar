# -*- coding: utf-8 -*-
from pymantic import sparql
from concurrent.futures import ThreadPoolExecutor
import subprocess
import pyin
from pyin import *
import datetime
import rdflib
from ordered_rdflib_store import OrderedStore
import click
from rdflib.namespace import RDF
import common
from common import shorten
from rdflib.plugins.parsers import notation3
notation3.RDFSink.newList = common.newList

server, this = None, None

default_graph = '<http://kbd.bg/#runs>'
pyin.default_graph = default_graph


@click.command()
@click.argument('kb', type=click.File('rb'))
@click.argument('goal', type=click.File('rb'))
@click.option('--nokbdbg', default=False)
@click.option('--nolog', default=False, type=bool)
@click.option('--visualize', default=False)
@click.option('--sparql_uri', default='', help='for example http://localhost:9999/blazegraph/sparql')
@click.option('--identification', default="")
@click.option('--base', default="")
def query_from_files(kb, goal, nokbdbg, nolog, visualize, sparql_uri, identification, base):
	#print('base', base)
	base = 'file://'  + base
	global server, this
	if sparql_uri != '':
		pyin.pool = ThreadPoolExecutor()#max_workers = , thread_name_prefix='sparql_updater'
		server = sparql.SPARQLServer(sparql_uri)
		server.update("""CLEAR GRAPHS""")
		pyin.server = server
	this = "http://kbd.bg/run"+str(datetime.datetime.now()).replace(':', '-').replace('.', '-').replace(' ', '-')
	pyin.this = this
	identification = common.fix_up_identification(identification)
	fn = 'kbdbg'+identification+'.n3'
	outpath = common.kbdbg_file_path(fn)
	pyin.kbdbg_file_name = common.kbdbg_file_name(fn)
	pyin._rules_file_name = pyin.kbdbg_file_name + '_rules'
	subprocess.call(['rm', '-f', pyin._rules_file_name])
	os.system('mkdir -p '+outpath)
	pyin.nolog = nolog
	pyin.init_logging()
	log = pyin.log
	if sparql_uri != '':
		new = """kbdbg:latest kbdbg:is <""" + this + ">"
		pyin.kbdbg(new, default=True)
		uuu = (pyin.prefixes +
		#WITH """ + default_graph + """
		"""DELETE {kbdbg:latest kbdbg:is ?x} WHERE {kbdbg:latest kbdbg:is ?x}""")
		server.update(uuu)
		pyin.kbdbg_text('#'+uuu)

	if identification != "":
		nolog or pyin.kbdbg('<'+this +"> kbdbg:has_run_identification " + rdflib.Literal(identification).n3(), True)

	kb_stream, goal_stream = kb, goal
	implies = rdflib.URIRef("http://www.w3.org/2000/10/swap/log#implies")
	store = OrderedStore()
	kb_graph = rdflib.Graph(store=store, identifier=base)
	kb_conjunctive = rdflib.ConjunctiveGraph(store=store, identifier=base)
	kb_graph.parse(kb_stream, format='n3', publicID=base)

	if not nolog:
		log('---kb:')
		for l in kb_graph.serialize(format='n3').splitlines():
			log(l.decode('utf8'))
		log('---kb quads:')
		for l in kb_conjunctive.serialize(format='nquads').splitlines():
			log(l.decode('utf8'))
		log('---')

	def fixup3(o):
		if isinstance(o, rdflib.Graph):
			return URIRef(o.identifier)
		return o

	def fixup2(o):
		if type(o) == rdflib.BNode:
			return rdflib.Variable(str(o))
		return o

	def fixup(spo):
		s,p,o = spo
		return (fixup2(s), fixup2(p), fixup2(o))

	rules = []
	kb_graph_triples = [fixup(x) for x in kb_graph.triples((None, None, None))]
	facts = [Triple(fixup3(x[1]),[fixup3(x[0]),fixup3(x[2])]) for x in kb_graph_triples]
	for kb_graph_triple_idx,(s,p,o) in enumerate(kb_graph_triples):
		_t = Triple(p, [s, o])
		rules.append(Rule(facts, kb_graph_triple_idx, Graph()))
		if p == implies:
			head_triples = [fixup(x) for x in kb_conjunctive.triples((None, None, None, o))]
			head_triples_triples = Graph([Triple(fixup3(x[1]),[fixup3(x[0]),fixup3(x[2])]) for x in head_triples])
			#head_triples_triples = reorder_lists(head_triples_triples)

			body = Graph()
			for body_triple in [fixup(x) for x in kb_conjunctive.triples((None, None, None, s))]:
				body.append(Triple((fixup3(body_triple[1])), [fixup3(body_triple[0]), fixup3(body_triple[2])]))

			#body = reorder_lists(body)

			if len(head_triples_triples) > 1:
				with open(pyin._rules_file_name, 'a') as ru:
					ru.write(head_triples_triples.str(shorten) + " <= " + body.str(shorten) + ":\n")

			for head_triple_idx in range(len(head_triples_triples)):
				rules.append(Rule(head_triples_triples, head_triple_idx, body))

	goal_rdflib_graph = rdflib.ConjunctiveGraph(store=OrderedStore(), identifier=base)
	goal_rdflib_graph.parse(goal_stream, format='n3', publicID=base)
	goal = Graph()
	
	if not nolog:
		log('---goal:')
		for l in goal_rdflib_graph.serialize(format='n3').splitlines():
			log(l.decode('utf8'))
		log('---goal nq:')
		for l in goal_rdflib_graph.serialize(format='nquads').splitlines():
			log(l.decode('utf8'))
		log('---')

	for s,p,o in [fixup(x) for x in goal_rdflib_graph.triples((None, None, None, None))]:
		goal.append(Triple(fixup3(p), [fixup3(s), fixup3(o)]))

	for result in query(rules, goal):
		print ()

		r = ''
		for triple in result:
			r += triple.str()
		print(' RESULT :' + r)
		print(' step :' + str(pyin.global_step_counter))
		nolog or pyin.kbdbg_text('#result: ' + r)
	print(' steps :' + str(pyin.global_step_counter))


	if sparql_uri != '':
		pyin.kbdbg("<" + this + "> kbdbg:is kbdbg:done", default=True)
		pyin.flush_sparql_updates()


	if sparql_uri != '':
		pyin.pool.shutdown()


if __name__ == "__main__":
	query_from_files()






"""
def reorder_lists(g):
	r = Graph()
	backburner = []
	for t in g:
		if t.pred == RDF.first:
			backburner.append(t)
		else:
			r.append(t)
	for t in backburner:
		r.append(t)
	return r
"""



#from IPython import embed; embed()
