from weakref import ref as weakref

from pip._vendor.packaging.requirements import URI
from rdflib import URIRef
import rdflib
import sys
import os
import logging
import urllib.parse
from collections import defaultdict
from ordered_rdflib_store import OrderedStore

# #OUTPUT:
# into kbdbg.nt, we should output a valid n3 file with kbdbg2 schema (which is to be defined). 
# lines starting with "#" are n3 comments. 
# "#RESULT:" lines are for univar fronted/runner/tester ("tau")
# the rest of the comment lines are random noise


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


bnode_counter = 0
def bnode():
	global bnode_counter
	bnode_counter += 1
	return "_:bn" + str(bnode_counter)


log, kbdbg = init_logging()


kbdbg("@prefix kbdbg: <http://kbd.bg/#> ")
kbdbg("@prefix : <file:///#> ")
kbdbg("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ")

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
		return str(s.pred) + "(" + printify(s.args, ", ") + ")"

class Graph(list):
	def __str__(s):
		return "{" + printify(s, ". ") + "}"

class Arg:
	def __init__(s, uri, thing, term_idx, arg_idx, is_in_head):
		s.uri = uri
		assert(isinstance(uri, rdflib.term.Identifier))
		s.thing = thing
		assert(isinstance(thing, AtomVar))
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

class AtomVar(Kbdbgable):
	def __init__(s, debug_name, debug_locals):
		super().__init__()
		s.debug_name = debug_name
		if type(debug_locals) == weakref:
			debug_locals = debug_locals()
		s.debug_locals = weakref(debug_locals) if debug_locals != None else None
		if debug_locals != None:
			s.kbdbg_name = debug_locals.kbdbg_frame
		s.kbdbg_name += "_" + urllib.parse.quote_plus(debug_name)
#		kbdbg(":"+x.kbdbg_name + " kbdbg:belongs_to_frame " + ":"+)
#		kbdbg(":"+x.kbdbg_name + " kbdbg:belongs_to_term " + ":"+)
	def recursive_clone(s):
		r = s.__class__(s.debug_name, s.debug_locals)
		r.kbdbg_name = s.kbdbg_name
		return r
	def __short__str__(s):
		return get_value(s).___short__str__()

class Atom(AtomVar):
	def __init__(s, value, debug_locals=None):
		super().__init__(value, debug_locals)
		s.value = value
	def __str__(s):
		return s.kbdbg_name + s.___short__str__()
	def ___short__str__(s):
		return '("'+str(s.value)+'")'
	def rdf_str(s):
		return '"'+str(s.value)+'")'
	def recursive_clone(s):
		r = super().recursive_clone()
		r.value = s.value
		return r

class Var(AtomVar):
	def __init__(s, debug_name, debug_locals=None):
		super().__init__(debug_name, debug_locals)
		s.bound_to = None
	def __str__(s):
		return s.kbdbg_name + s.___short__str__()
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
		if type(y) == Var:
			log("and reverse?")
			for i in y._bind_to(x, _y, _x):
				yield i

	def _bind_to(x, y, _x, _y):
		assert x.bound_to == None
		x.bound_to = y

		uri = emit_binding(_x, _y)

		kbdbg(":"+x.kbdbg_name + " kbdbg:was_bound_to " + ":"+y.kbdbg_name)

		msg = "bound " + str(x) + " to " + str(y)
		log(msg)

		yield msg

		x.bound_to = None
		kbdbg(uri + " kbdbg:was_unbound true;")
		kbdbg(":"+x.kbdbg_name + " kbdbg:was_unbound_from " + ":"+y.kbdbg_name)

def success(msg, _x, _y):
	uri = emit_binding(_x, _y)
	yield msg
	kbdbg(uri + " kbdbg:was_unbound true;")

def fail(_x, _y):
	uri = emit_binding(_x, _y)
	while False:
		yield
	kbdbg(uri + " kbdbg:failed true;")

def emit_binding(_x, _y):
	uri = bnode()
	kbdbg(uri + " a kbdbg:binding; " +
	      "has_source " + arg_text(_x) + "; has_target " + arg_text(_y))
	return uri

def arg_text(x):
	r = "[ kbdbg:frame " + x.thing.debug_locals().kbdbg_frame + "; "
	if x.is_in_head:
		r += "kbdbg:is_in_head true; "
	else:
		r += "kbdbg:term_idx " + str(x.term_idx) + "; "
	r += "kbdbg:arg_idx " + str(x.arg_idx) + "; "
	return r + "]"

def unify(_x, _y):
	assert(isinstance(_x, Arg))
	assert(isinstance(_y, Arg))
	x = get_value(_x.thing)
	y = get_value(_y.thing)
	log("unify " + str(x) + " with " + str(y))
	if x == y:
		return success("same vars", _x, _y)
	if type(x) == Var:
		return x.bind_to(y, _x, _y)
	elif type(y) == Var:
		return y.bind_to(x, _x, _y)
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
		super().__init__()
		s.debug_id = debug_id
		s.debug_last_instance_id = 0
		s.debug_rule = weakref(debug_rule)
		s.kbdbg_frame = kbdbg_frame
		for k,v in initializer.items():
			s[k] = v.__class__(v.debug_name, s)
			#kbdbg(":"+x.kbdbg_name + " kbdbg:belongs_to_frame " + ":"+)

	def __str__(s):
		r = ("locals " + str(s.debug_id) + " of " + str(s.debug_rule()))
		if len(s):
			r += ":\n#" + printify([str(k) + ": " + str(v) for k, v in s.items()], ", ")
		return r

	def __short__str__(s):
		return printify([str(k) + ": " + v.__short__str__() for k, v in s.items()], ", ")

	def new(s, kbdbg_frame):
		log("cloning " + str(s))
		s.debug_last_instance_id += 1
		r = Locals(s, s.debug_rule(), s.debug_last_instance_id, kbdbg_frame)
		log("result: " + str(r))
		return r


def emit_term(t, uri):
	kbdbg(uri + " a kbdbg:term")
	kbdbg(uri + " kbdbg:has_pred " + t.pred.n3())
	kbdbg(uri + " kbdbg:has_args " + emit_args(t.args))

def pr(x):
	print(x.__class__, x.context, x.triple)

for i in (rdflib.store.TripleRemovedEvent, rdflib.store.TripleAddedEvent):
	kbdbg_output_graph.store.dispatcher.subscribe(i, pr)

def emit_args(args):
	c=rdflib.collection.Collection(kbdbg_output_graph, URIRef(bnode()))
	for i in args:
		c.append(i)
	print("i have", kbdbg_output_graph.store.quads)
	return c.n3()

class Rule(Kbdbgable):
	last_frame_id = 0
	def __init__(s, head, body=Graph()):
		super().__init__()
		s.head = head
		s.body = body
		s.locals_template = s.make_locals(head, body, s.kbdbg_name)
		s.ep_heads = []

		kbdbg(":"+s.kbdbg_name + ' a ' + 'kbdbg:rule')
		if s.head:
			head_uri = ":"+s.kbdbg_name + "Head"
			kbdbg(":"+s.kbdbg_name + ' kbdbg:has_head ' + head_uri)
			kbdbg(head_uri + ' kbdbg:has_text "' + urllib.parse.quote_plus(str(s.head)) + '"')
			emit_term(s.head, head_uri)
		if s.body:
			body_uri = s.kbdbg_name + "Body"
			kbdbg(":"+s.kbdbg_name + ' kbdbg:has_body :' + body_uri)
			for i in s.body:
				body_term_uri = ":" + bnode()
				emit_term(i, body_term_uri)
				kbdbg(":"+body_uri + " rdf:first " + body_term_uri)
				body_uri2 = body_uri + "X"
				kbdbg(":"+body_uri + " rdf:rest :" + body_uri2)
				body_uri = body_uri2
			kbdbg(":"+body_uri + " rdf:rest rdf:nil")

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
		Rule.last_frame_id += 1
		frame_id = Rule.last_frame_id
		depth = 0
		generators = []
		max_depth = len(args) + len(s.body) - 1
		kbdbg_name = s.kbdbg_name + "Frame"+str(frame_id)
		locals = s.locals_template.new(kbdbg_name)

		kbdbg(":"+kbdbg_name + " rdf:type kbdbg:frame")

		def desc():
			return ("\n#vvv\n#" + str(s) + "\n" +
			"#args:" + str(args) + "\n" +
			"#locals:" + str(locals) + "\n" +
			"#depth:"+ str(depth) + "/" + str(max_depth)+
			        "\n#^^^")
		kbdbg(":"+kbdbg_name + " kbdbg:is_for_rule :"+s.kbdbg_name)
		log ("entering " + desc())
		while True:
			if len(generators) <= depth:
				generator = None

				if depth < len(args):
					arg_index = depth
					head_uriref = s.head.args[arg_index]
					head_thing = locals[head_uriref]
					generator = unify(args[arg_index], Arg(head_uriref, head_thing, 0, arg_index, True))

				else:
					body_item_index = depth - len(args)
					triple = s.body[body_item_index]
					
					bi_args = []
					for arg_idx, uri in enumerate(triple.args):
						thing = get_value(locals[uri])
						bi_args.append(Arg(uri, thing, body_item_index, arg_idx, False))

					generator = pred(triple.pred, bi_args)
				generators.append(generator)
				log("generators:%s", generators)
			try:
				generators[depth].__next__()
				log ("back in " + desc() + "\n# from sub-rule")
				if (depth < max_depth):
					log ("down")
					depth+=1
				else:
					print ("#NYAN")
					yield locals#this is when it finishes a rule
					log ("re-entering " + desc() + " for more results")
			except StopIteration:
				if (depth > 0):
					log ("back")
					depth-=1
				else:
					log ("rule done")
					break#if it's tried all the possibilities for finishing a rule

	def find_ep(s, args):
		log ("ep check: %s vs..", args)
		for former_args in s.ep_heads:
			log(former_args)
			if ep_match(args, former_args):
				log("..hit")
				return True
		log ("..no match")

	def match(s, args=[]):
		ep_item = []
		for arg in args:
			ep_item.append(Arg(arg.uri, arg.thing.recursive_clone(), arg.term_idx, arg.arg_idx, arg.is_in_head))

		s.ep_heads.append(ep_item)
		for i in s.rule_unify(args):
			s.ep_heads.pop()
			yield i
			s.ep_heads.append(ep_item)
		s.ep_heads.pop()

def ep_match(args_a, args_b):
	assert len(args_a) == len(args_b)
	for i in len(args_a):
		a = args_a[i].thing
		b = args_b[i].thing
		if type(a) != type(b):
			return
		if type(a) == Atom and b.value != a.value:
			return
	kbdbg("EP!")
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
	global preds
	preds = defaultdict(list)
	for r in input_rules:
		preds[r.head.pred].append(r)
	for nyan in Rule(None, input_query).match():
		yield nyan





"""
issues:

the various uris generated, such as :Rule4Frame1_file%3A%2F%2Ftests%2Fsimple%2Fbob2%3FWHO ,
could colide, in case of unlucky names. I should switch to bnode() everywhere.

"""

