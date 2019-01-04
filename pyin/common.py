import rdflib

nolog = False

mmtbf = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#move_me_to_body_first')
mmtbr = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#move_me_to_body_rest')

def un_move_me_ize_pred(x):
	if x == mmtbf:
		return rdflib.namespace.RDF.first
	if x == mmtbr:
		return rdflib.namespace.RDF.rest
	return x

import logging

log = logging.getLogger().debug



#Key: 		String
#Value:		String
shortenings = {}


#String -> String
"""forall s : String, shorten(s) contains at most one occurrence of a character
from '/:#?', and if it does it will be at the beginning of shorten(s)
"""
def shorten(term):
	#return term
	# todo ? use https://github.com/RDFLib/rdflib/blob/master/docs/namespaces_and_bindings.rst instead
	#copy value of "term" into a new string stored in "s"
	term_str = str(term)
	s = term_str

	#Find the last occurrence of any of the characters in '/:#?' in s and
	#give back the rest of the string from that last occurrence til the end
	#inclusive of final special character
	for i in '/:#?':
		p = s.rfind(i)
		if p != -1:
			s = s[p:]

	#return "term" if it's shortening is already taken by
	#a member of the equivalence class other than "term" itself 

	#if s in shortenings and shortenings[s] != term_str:
	#	print(term_str + ' shortens to ' + s +' , but that was already used for ' + shortenings[s])
	#	return term_str

	#note: redundant in the case that shortenings[s] == term
	shortenings[s] = term_str

	#print('shortened '+term_str + ' to ' + s)

	return s




def traverse(item):
	for i in iter(item):
		for j in iter(i):
			yield j

def join_generators(a, b):
	for i in a:
		for j in b:
			yield True

def trace_output_path(identification):
	return 'runs/'+identification+ '/'

def kbdbg_file_name(identification, fn):
	return trace_output_path(identification) + fn

#Identifiers table
# Key: 		String
# Value: 	String
fixed_upings = {}

# String -> String
def fix_up_identification(i):
	#replace non-alphanumeric characters in i with "_"
	r =  "".join([ch if ch.isalnum() else "_" for ch in i])

	#recursively stick "_2"s on the end until you have an unused identifier
	if r in fixed_upings:
		if fixed_upings[r] != i:
			return fix_up_identification(r + "_2")
	else:
		fixed_upings[r] = i

	#but this will come up with a new fix_uping even if you pass it the
	#same identifier with non-alnum chars ?
	
	return r

pyin_prefixes = """
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix kbdbg: <http://kbd.bg/#> 
prefix : <file:///#> 
"""



def newList(self, n, f):
	nil = self.newSymbol('http://www.w3.org/1999/02/22-rdf-syntax-ns#nil')

	if len(n) == 0 or not n:
		return nil

	#mmtb means must_move_to_body, done in pyco.py
	first = mmtbf
	rest = mmtbr

	if hasattr(self.graph, 'last_n3_syntax_list_id'):
		list_id = self.graph.last_n3_syntax_list_id + 1
	else:
		list_id = 0
	self.graph.last_n3_syntax_list_id = list_id

	def make_bnode(idx):
		return rdflib.BNode('l' + str(list_id) + '_' + str(idx))

	r = None
	next = None

	result = []

	for idx, i in enumerate(n):
		if next == None:
			a = make_bnode(idx)
		else:
			a = next
		if r == None:
			r = a
		result.append((f, first, a, i))
		if idx == len(n) - 1:
			next = nil
		else:
			next = make_bnode(idx + 1)
		result.append((f, rest, a, next))

	for i in reversed(result):
		self.makeStatement(i)
	return r
