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

import rdflib
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


