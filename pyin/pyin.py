from weakref import ref as weakref
from rdflib import URIRef
import rdflib
import time
import sys
import os
import logging
import urllib.parse
from collections import defaultdict
from ordered_rdflib_store import OrderedStore

dbg = True
nolog = False
nokbdbg = False

# #OUTPUT:
# into kbdbg.nt, we should output a valid n3 file with kbdbg2 schema (which is to be defined). 
# lines starting with "#" are n3 comments. 
# "#RESULT:" lines are for univar fronted/runner/tester ("tau")
# the rest of the comment lines are random noise

#for i in (rdflib.store.TripleRemovedEvent, rdflib.store.TripleAddedEvent):
#	kbdbg_output_graph.store.dispatcher.subscribe(i, pr)

def init_logging():
	formatter = logging.Formatter('#%(message)s')
	console_debug_out = logging.StreamHandler()
	console_debug_out.setFormatter(formatter)
	
	logger1=logging.getLogger()
	logger1.addHandler(console_debug_out)
	logger1.setLevel(logging.DEBUG)

	kbdbg_file_name = 'kbdbg.n3'
	try:
		os.unlink(kbdbg_file_name)
	except FileNotFoundError:
		pass
	kbdbg_out = logging.FileHandler(kbdbg_file_name)
	kbdbg_out.setLevel(logging.DEBUG)
	kbdbg_out.setFormatter(logging.Formatter('%(message)s.'))
	logger2=logging.getLogger("kbdbg")
	logger2.addHandler(kbdbg_out)

	return logger1.debug, logger2.info


global_step_counter = 0
def step():
	global global_step_counter
	nokbdbg or kbdbg("#step"+str(global_step_counter) + " a kbdbg:step")
	global_step_counter += 1
	if global_step_counter == 18:
		print(55)

bnode_counter = 0
def bnode():
	global bnode_counter
	bnode_counter += 1
	return  '_:bn' + str(bnode_counter)


log, kbdbg = init_logging()


nokbdbg or kbdbg("@prefix kbdbg: <http://kbd.bg/#> ")
nokbdbg or kbdbg("@prefix : <file:///#> ")
nokbdbg or kbdbg("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ")

print("#this should be first line of merged stdout+stderr after @prefix lines, use PYTHONUNBUFFERED=1")



#having this one, global, instance will hopefully let us avoid accidentally creating identical bnodes in the output
kbdbg_output_store = OrderedStore()
kbdbg_output_graph = rdflib.Graph(kbdbg_output_store)


def printify(iterable, separator):
	r = ""
	last = len(iterable) - 1
	for i, x in enumerate(iterable):
		r += str(x)
		if i != last:
			r += separator
	return r

class Triple():
	def __init__(s, pred, args):
		s.pred = pred
		s.args = args
	def __str__(s):
		if len(s.args) == 2:
			return s.args[0].n3() + " " + s.pred.n3() + " " + s.args[1].n3() + "."
		return str(s.pred) + "(" + printify(s.args, ", ") + ")"

class Graph(list):
	def __str__(s):
		return "{" + printify(s, ". ") + "}"

class Arg:
	def __init__(s, uri, thing, frame, term_idx, arg_idx, is_in_head):
		s.uri = uri
		assert(isinstance(uri, rdflib.term.Identifier))
		s.thing = thing
		assert(isinstance(thing, AtomVar))
		s.frame = frame
		assert(not dbg or (type(frame) == str))
		s.term_idx = term_idx
		assert(isinstance(term_idx, int))
		s.arg_idx = arg_idx
		assert(isinstance(arg_idx, int))
		s.is_in_head = is_in_head
		assert(isinstance(is_in_head, bool))

class Kbdbgable():
	last_instance_debug_id = 0
	def __init__(s):
		s.__class__.last_instance_debug_id += 1
		s.debug_id = s.__class__.last_instance_debug_id
		s.kbdbg_name = s.__class__.__name__ + str(s.debug_id)

class EpHead(Kbdbgable):
	def __init__(s):
		super().__init__()
		s.kbdbg_name = ':' + s.kbdbg_name
		s.items = []

class AtomVar(Kbdbgable):
	def __init__(s, debug_name, debug_locals):
		if dbg:
			super().__init__()
			s.debug_name = debug_name
			if type(debug_locals) == weakref:
				s.debug_locals = debug_locals
			elif debug_locals == None:
				s.debug_locals = None
			else:
				s.debug_locals = weakref(debug_locals)
			if s.debug_locals != None:
				s.kbdbg_name = s.debug_locals().kbdbg_frame
			assert(debug_name)
			s.kbdbg_name += "_" + urllib.parse.quote_plus(debug_name)
	#		nokbdbg or kbdbg(":"+x.kbdbg_name + " kbdbg:belongs_to_frame " + ":"+)
	#		nokbdbg or kbdbg(":"+x.kbdbg_name + " kbdbg:belongs_to_term " + ":"+)
	def recursive_clone(s):
		if type(s) == Atom:
			r = Atom(s.value, s.debug_locals if dbg else None)
		else:
			assert type(s) == Var
			r = Var(s.debug_name if dbg else None, s.debug_locals if dbg else None)
		if dbg:
			r.kbdbg_name = s.kbdbg_name
		return r
	def __short__str__(s):
		return get_value(s).___short__str__()

class Atom(AtomVar):
	def __init__(s, value, debug_locals=None):
		if dbg:
			super().__init__(value, debug_locals)
		assert(isinstance(value, rdflib.term.Identifier))
		s.value = value
	def __str__(s):
		return (s.kbdbg_name if dbg else '') + s.___short__str__()
	def ___short__str__(s):
		return '("'+str(s.value)+'")'
	def rdf_str(s):
		return '"'+str(s.value)+'")'
	def recursive_clone(s):
		r = super().recursive_clone()
		r.value = s.value
		return r

class Var(AtomVar):
	def __init__(s, debug_name=None, debug_locals=None):
		if dbg:
			super().__init__(debug_name, debug_locals)
		s.bound_to = None
	def __str__(s):
		return (s.kbdbg_name if dbg else '') + s.___short__str__()
		# + " in " + str(s.debug_locals())
	def ___short__str__(s):
		if s.bound_to:
			return ' = ' + (s.bound_to.__short__str__())
		else:
			return '(free)'
	def recursive_clone(s):
		r = super().recursive_clone()
		if s.bound_to:
			r.bound_to = s.bound_to.recursive_clone()
		return r
	def bind_to(x, y, _x, _y):
		for i in x._bind_to(y, _x, _y):
			yield i
		#if type(y) == Var:
		#	log("and reverse?")
		#	for i in y._bind_to(x, _y, _x):
		#		yield i

	def _bind_to(x, y, _x, _y):
		assert x.bound_to == None
		x.bound_to = y

		uri = emit_binding(_x, _y)

		#nokbdbg or kbdbg(x.kbdbg_name + " kbdbg:was_bound_to " + y.kbdbg_name)

		msg = "bound " + str(x) + " to " + str(y)
		nolog or log(msg)

		yield msg

		x.bound_to = None
		nokbdbg or kbdbg(uri + " kbdbg:was_unbound true;")
		step()
		#nokbdbg or kbdbg(x.kbdbg_name + " kbdbg:was_unbound_from " + y.kbdbg_name)

def success(msg, _x, _y):
	uri = emit_binding(_x, _y)
	yield msg
	nokbdbg or kbdbg(uri + " kbdbg:was_unbound true")
	step()

def fail(_x, _y):
	uri = emit_binding(_x, _y, True)
	while False:
		yield
	nokbdbg or kbdbg(uri + " kbdbg:failed true")
	step()

def emit_binding(_x, _y, is_failed = False):
	uri = bnode()
	nokbdbg or kbdbg(uri + " a kbdbg:binding; " +
	      "kbdbg:has_source " + arg_text(_x) + "; kbdbg:has_target " + arg_text(_y) +
	      (";kbdbg:is_failed true" if is_failed else ""))
	step()
	return uri

def arg_text(x):
	r = "[ kbdbg:has_frame " + x.frame + "; "
	if x.is_in_head:
		r += "kbdbg:is_in_head true; "
	else:
		r += "kbdbg:term_idx " + str(x.term_idx) + "; "
	r += "kbdbg:arg_idx " + str(x.arg_idx)
	return r + "]"

def unify(_x, _y):
	assert(isinstance(_x, Arg))
	assert(isinstance(_y, Arg))
	x = get_value(_x.thing)
	y = get_value(_y.thing)
	nolog or log("unify " + str(x) + " with " + str(y))
	if x == y:
		return success("same vars", _x, _y)
	if type(x) == Var:
		return x.bind_to(y, _x, _y)
	elif type(y) == Var:
		return y.bind_to(x, _y, _x)
	elif x.value == y.value:
		return success("same consts", _x, _y)
	else:
		return fail(_x, _y)

def get_value(x):
	asst(x)
	if type(x) == Atom:
		return x
	v = x.bound_to
	if v:
		return get_value(v)
	else:
		return x

def is_var(x):
	#return x.startswith('?')
	#from IPython import embed; embed()
	if type(x) == rdflib.URIRef and '?' in str(x): #str(x).startswith('?'):
		return True
	if type(x) == str and '?' in x:
		raise "this still happens?"
		return True
	return False

class Locals(dict):
	def __init__(s, initializer, debug_rule, debug_id = 0, kbdbg_frame=None):
		if dbg:
			super().__init__()
			s.debug_id = debug_id
			s.debug_last_instance_id = 0
			s.debug_rule = weakref(debug_rule)
			s.kbdbg_frame = kbdbg_frame
		for k,v in initializer.items():
			if type(v) == Var:
				s[k] = Var(v.debug_name + "_clone", s)
			else:
				s[k] = Atom(v.value, s)
			#nokbdbg or kbdbg(":"+x.kbdbg_name + " kbdbg:belongs_to_frame " + ":"+)

	def __str__(s):
		r = ("locals " + str(s.debug_id) + " of " + str(s.debug_rule()))
		if len(s):
			r += ":\n#" + printify([str(k) + ": " + str(v) for k, v in s.items()], ", ")
		return r

	def emit(s):
		kbdbg(s.kbdbg_name + " rdf:type kbdbg:locals")
		kbdbg(s.kbdbg_name + " kbdbg:has_frame " + s.kbdbg_frame)
		for k, v in s.items():
			kbdbg(s.kbdbg_name + " kbdbg:has_var [kbdbg:has_name " + rdflib.Literal(k) +
			      " kdbdb:has_value " + v.kbdg_name)

	def __short__str__(s):
		return printify([str(k) + ": " + v.__short__str__() for k, v in s.items()], ", ")

	def new(s, kbdbg_frame):
		nolog or log("cloning " + str(s))
		if dbg:
			s.debug_last_instance_id += 1
		r = Locals(s, s.debug_rule() if dbg else None, s.debug_last_instance_id if dbg else None, kbdbg_frame)
		nolog or log("result: " + str(r))
		return r

def new_bnode(locals, idx):
	r = Locals({}, s.debug_rule() if dbg else None, s.debug_last_instance_id if dbg else None, "bnode" + str(idx) + "_" + locals.kbdbg_name)
	for k,v in s.iteritems():
		r[k] = get_value(v).recursive_clone()#not really recursive

def emit_terms(terms):
	c=[]
	for i in terms:
		c.append(emit_term(i, bnode()))
	return c

def emit_term(t, uri):
	nokbdbg or kbdbg(uri + " a kbdbg:term")
	nokbdbg or kbdbg(uri + " kbdbg:has_pred " + t.pred.n3())
	nokbdbg or kbdbg(uri + " kbdbg:has_args " + emit_args(t.args))
	return uri

def pr(x):
	print(x.__class__, x.context, x.triple)

def emit_args(args):
	#c=rdflib.collection.Collection(kbdbg_output_graph, URIRef(bnode()))
	#for i in args:
	#	c.append(i)
	#return c.n3()
	r = '('
	for i in args:
		r += i.n3()
	r += ')'
	return r

class Rule(Kbdbgable):
	last_frame_id = 0
	def __init__(s, original_head, head, body=Graph()):
		super().__init__()
		s.head = head
		s.body = body
		s.original_head = original_head
		s.locals_template = s.make_locals(head, body, s.kbdbg_name)
		s.ep_heads = []

		nokbdbg or kbdbg(":"+s.kbdbg_name + ' a ' + 'kbdbg:rule')
		if s.head:
			head_uri = ":"+s.kbdbg_name + "Head"
			nokbdbg or kbdbg(":"+s.kbdbg_name + ' kbdbg:has_head ' + head_uri)
			nokbdbg or kbdbg(head_uri + ' kbdbg:has_text "' + urllib.parse.quote_plus(str(s.head)) + '"')
			emit_term(s.head, head_uri)
		if s.body:
			body_uri = s.kbdbg_name + "Body"
			nokbdbg or kbdbg(":"+s.kbdbg_name + ' kbdbg:has_body :' + body_uri)
			for i in s.body:
				body_term_uri = ":" + bnode()
				emit_term(i, body_term_uri)
				nokbdbg or kbdbg(":"+body_uri + " rdf:first " + body_term_uri)
				body_uri2 = body_uri + "X"
				nokbdbg or kbdbg(":"+body_uri + " rdf:rest :" + body_uri2)
				body_uri = body_uri2
			nokbdbg or kbdbg(":"+body_uri + " rdf:rest rdf:nil")

	def __str__(s):
		return "{" + str(s.head) + "} <= " + str(s.body)

	def make_locals(s, head, body, kbdbg_rule):
		locals = Locals({}, s)
		locals.kbdbg_frame = "locals_template_for_" + kbdbg_rule
		for triple in ([head] if head else []) + body:
			for a in triple.args:
				if is_var(a):
					x = Var(a, locals)
				else:
					x = Atom(a, locals)
				locals[a] = x
		return locals

	def rule_unify(s, args):

		def desc():
			return ("\n#vvv\n#" + str(s) + "\n" +
			"#args:" + str(args) + "\n" +
			"#locals:" + str(locals) + "\n" +
			"#depth:"+ str(depth) + "/" + str(max_depth)+
			        "\n#^^^")

		Rule.last_frame_id += 1
		frame_id = Rule.last_frame_id
		depth = 0
		generators = []
		max_depth = len(args) + len(s.body) - 1
		kbdbg_name = rdflib.Literal(s.kbdbg_name + "Frame"+str(frame_id)).n3()
		locals = s.locals_template.new(kbdbg_name)

		nokbdbg or kbdbg(kbdbg_name + " rdf:type kbdbg:frame; kbdbg:is_for_rule :"+s.kbdbg_name)
		nolog or log ("entering " + desc())


		while True:
			if len(generators) <= depth:
				generator = None
				if depth < len(args):
					arg_index = depth
					head_uriref = s.head.args[arg_index]
					head_thing = locals[head_uriref]
					generator = unify(args[arg_index], Arg(head_uriref, head_thing, head_thing.debug_locals().kbdbg_frame if dbg else None, 0, arg_index, True))

				else:
					body_item_index = depth - len(args)
					triple = s.body[body_item_index]

					bi_args = []
					for arg_idx, uri in enumerate(triple.args):
						thing = locals[uri]
						bi_args.append(Arg(uri, get_value(thing), thing.debug_locals().kbdbg_frame if dbg else None, body_item_index, arg_idx, False))

					generator = pred(triple.pred, bi_args)
				generators.append(generator)
				nolog or log("generators:%s", generators)
			try:
				generators[depth].__next__()
				nolog or log ("back in " + desc() + "\n# from sub-rule")
				if (depth < max_depth):
					nolog or log ("down")
					depth+=1
				else:
					#print ("#NYAN")




					"""generate blank nodes:
					go through all variables"""
					for j,i in enumerate(s.get_existentials()):
						v = locals[i]
						v.is_a_bnode_from_rule = s.original_head
						v.bnode_locals = new_bnode(locals)
						nokbdbg or kbdbg(i.kbdbg_name + " kbdbg:has_existential_locals " + v.bnode_locals)





					yield locals#this is when it finishes a rule
					nolog or log ("re-entering " + desc() + " for more results")
			except StopIteration:
				if (depth > 0):
					nolog or log ("back")
					generators.pop()
					depth-=1
				else:
					nolog or log ("rule done")
					break#if it's tried all the possibilities for finishing a rule

	def get_existentials(s):
		vars = []
		if s.head:
			for i in s.head.args:
				if is_var(i):
					vars.append(i)
			for i in s.body:
				for j in i.args:
					if is_var(j):
						if j in vars:
							vars.remove(j)
		return vars

	def match(s, args=[]):
		#ttt = time.clock()
		#print ("TTT", ttt)
		#if ttt > 1:
			#while True:
			#	print("end")
		#return
		head = EpHead()
		for arg in args:
			head.items.append(Arg(arg.uri, arg.thing.recursive_clone(), arg.thing.debug_locals().kbdbg_frame if dbg else None, arg.term_idx, arg.arg_idx, arg.is_in_head))
		s.ep_heads.append(head)
		for i in s.rule_unify(args):
			s.ep_heads.pop()
			yield i
			s.ep_heads.append(head)
		s.ep_heads.pop()

	def find_ep(s, args):
		nolog or log ("ep check: %s vs..", args)
		for head in s.ep_heads:
			if ep_match(args, head.items):
				nokbdbg or kbdbg(bnode() + ' a kbdbg:ep_match')
				return True
		nolog or log ("..no match")

def ep_match(args_a, args_b):
	assert len(args_a) == len(args_b)
	for i in range(len(args_a)):
		a = args_a[i].thing
		b = args_b[i].thing
		if type(a) != type(b):
			return
		if type(a) == Atom and b.value != a.value:
			return
	nolog or log("EP!")
	return True

def asst(x):
	if type(x) == tuple:
		for i in x:
			asst(i)
	else:
		assert type(x) in [Var, Atom]

def pred(p, args):
	for a in args:
		assert(isinstance(a, Arg))
		assert(isinstance(a.thing, AtomVar))
		assert get_value(a.thing) == a.thing

	for rule in preds[p]:
		if(rule.find_ep(args)):
			continue
		for i in rule.match(args):
			yield i

def query(input_rules, input_query):
	global preds, dbg
	dbg = not nolog or not nokbdbg
	preds = defaultdict(list)
	for r in input_rules:
		preds[r.head.pred].append(r)
	step()
	for i, locals in enumerate(Rule([], None, input_query).match()):
		uri = ":result" + str(i)
		terms = [substitute_term(term, locals) for term in input_query]
		nokbdbg or kbdbg(uri + " a kbdbg:result; rdf:value (" + " ".join(emit_terms(terms)) + ')')
		nokbdbg or kbdbg(uri + " kbdbg:was_unbound true")
		yield terms

def substitute_term(term, locals):
	return Triple(term.pred, [substitute(x, locals) for x in term.args])

def substitute(node, locals):
	assert(isinstance(node, rdflib.term.Identifier))
	if node in locals:
		v = get_value(locals[node])
		if type(v) == Var:
			r = node
		elif type(v) == Atom:
			r = v.value
		else:
			assert False
	else:
		r = node
	assert(isinstance(r, rdflib.term.Identifier))
	return r




"""
issues:

the various uris generated, such as :Rule4Frame1_file%3A%2F%2Ftests%2Fsimple%2Fbob2%3FWHO ,
could colide, in case of unlucky names. I should switch to bnode() everywhere.

"""

"""
def iteritems(x):
	"""