import rdflib
from rdflib.plugins.parsers import notation3
notation3.RDFSink.newList = common.newList
import logging

log = logging.getLogger().debug



shortenings = {}
def shorten(term):
	# todo ? use https://github.com/RDFLib/rdflib/blob/master/docs/namespaces_and_bindings.rst instead
	s = str(term)
	for i in '/:#?':
		p = s.rfind(i)
		if p != -1:
			s = s[p:]
	if s in shortenings and shortenings[s] != term:
		return str(term)
	shortenings[s] = term
	return s

def traverse(item):
	for i in iter(item):
		for j in iter(i):
			yield j

def join_generators(a, b):
	for i in a:
		for j in b:
			yield True

def kbdbg_file_path(fn):
	return 'runs/'+fn+ '/'

def kbdbg_file_name(fn):
	return kbdbg_file_path(fn) + fn

def fix_up_identification(i):
	return "".join([ch if ch.isalnum() else "_" for ch in i])

pyin_prefixes = """
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix kbdbg: <http://kbd.bg/#> 
prefix : <file:///#> 
"""

def newList(self, n, f):
	nil = self.newSymbol('http://www.w3.org/1999/02/22-rdf-syntax-ns#nil')

	if len(n) == 0 or not n:
		return nil

	first = self.newSymbol(
		'http://www.w3.org/1999/02/22-rdf-syntax-ns#first')
	rest = self.newSymbol(
		'http://www.w3.org/1999/02/22-rdf-syntax-ns#rest')

	if hasattr(self.graph, 'last_n3_syntax_list_id'):
		list_id = self.graph.last_n3_syntax_list_id + 1
	else:
		list_id = 0
	self.graph.last_n3_syntax_list_id = list_id

	def make_bnode(idx):
		return rdflib.BNode('l' + str(list_id) + '_' + str(idx))

	r = None
	next = None
	for idx, i in enumerate(n):
		if next == None:
			a = make_bnode(idx)
		else:
			a = next
		if r == None:
			r = a
		self.makeStatement((f, first, a, i))
		if idx == len(n) - 1:
			next = nil
		else:
			next = make_bnode(idx + 1)
		self.makeStatement((f, rest, a, next))

	return r



	common.load(kb, goal, identification, base)

	base = 'file://'  + base
	identification = common.fix_up_identification(identification)
	fn = 'kbdbg'+identification+'.n3'
	outpath = common.kbdbg_file_path(fn)
	pyin.kbdbg_file_name = common.kbdbg_file_name(fn)
	pyin._rules_file_name = pyin.kbdbg_file_name + '_rules'
	subprocess.call(['rm', '-f', pyin._rules_file_name])
	os.system('mkdir -p '+outpath)
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
			body = Graph()
			for body_triple in [fixup(x) for x in kb_conjunctive.triples((None, None, None, s))]:
				body.append(Triple((fixup3(body_triple[1])), [fixup3(body_triple[0]), fixup3(body_triple[2])]))
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

