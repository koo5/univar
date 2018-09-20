import itertools
from weakref import ref as weakref
from rdflib import URIRef
import rdflib
import time
import sys
import os
import logging
import urllib.parse
from collections import defaultdict, OrderedDict
from ordered_rdflib_store import OrderedStore
from common import shorten, traverse, join_generators

dbg = True
nolog = False
nokbdbg = False

kbdbg_prefix = URIRef('http://kbd.bg/#')

# #OUTPUT:
# lines starting with "#" are n3 comments.
# "#RESULT:" lines are for univar fronted/runner/tester ("tau")
# the rest of the comment lines are random noise

log, kbdbg_text = 666,666

def init_logging():
	global log, kbdbg_text

	logging.getLogger('pymantic.sparql').setLevel(logging.INFO)

	formatter = logging.Formatter('#%(message)s')
	console_debug_out = logging.StreamHandler()
	console_debug_out.setFormatter(formatter)
	
	logger1=logging.getLogger()
	logger1.addHandler(console_debug_out)
	logger1.setLevel(logging.DEBUG)#INFO)#

	try:
		os.unlink(kbdbg_file_name)
	except FileNotFoundError:
		pass
	kbdbg_out = logging.FileHandler(kbdbg_file_name)
	kbdbg_out.setLevel(logging.DEBUG)
	kbdbg_out.setFormatter(logging.Formatter('%(message)s.'))
	logger2=logging.getLogger("kbdbg")
	logger2.addHandler(kbdbg_out)

	log, kbdbg_text = logger1.debug, logger2.info

	nokbdbg or kbdbg_text("@prefix kbdbg: <http://kbd.bg/#> ")
	nokbdbg or kbdbg_text("@prefix : <file:///#> ")
	nokbdbg or kbdbg_text("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ")
	print("#this should be first line of merged stdout+stderr after @prefix lines, use PYTHONUNBUFFERED=1")


pool = None

def kbdbg(text, default = False):
	kbdbg_text(text)
	if pool:
		pool.submit(server.update, """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX kbdbg: <http://kbd.bg/#> 
PREFIX : <file:///#> 
INSERT {""" + ("Graph " + (step_graph_name(global_step_counter) + "{") if not default else "") +
	text + "." +
	("}." if not default else "") +
	"} WHERE {}")


def step_graph_name(idx):
	return this + '_' + str(idx)

def step_list_item(idx):
	return step_graph_name(idx) + "_list_item"

def kbdbg_graph_first():
	kbdbg(step_list_item(global_step_counter) + " rdf:first " + step_graph_name(global_step_counter))

global_step_counter = 0
def step():
	global global_step_counter
	kbdbg_text("#step"+str(global_step_counter) + " a kbdbg:step")
	kbdbg(step_list_item(global_step_counter) + " rdf:rest " + step_list_item(global_step_counter + 1))
	global_step_counter += 1
	kbdbg_graph_first()


bnode_counter = 0
def bn():
	global bnode_counter
	bnode_counter += 1
	return  ':bn' + str(bnode_counter)


def printify(iterable, separator, shortener = lambda x:x):
	r = ""
	last = len(iterable) - 1
	for i, x in enumerate(iterable):
		if type(x) == str:
			r += shortener(x)
		else:
			r += x.str(shortener)
		if i != last:
			r += separator
	return r


class Triple():
	def __init__(s, pred, args):
		s.pred = pred
		s.args = args
		for a in args:
			if type(a) == rdflib.URIRef:
				if '?' in str(a):
					raise 666

	def str(s, shortener = lambda x:x):
		if len(s.args) == 2:
			return shortener(s.args[0].n3()) + " " + shortener(s.pred.n3()) + " " + shortener(s.args[1].n3()) + "."
		return shortener(str(s.pred)) + "(" + printify(s.args, ", ", shortener) + ")"

class Graph(list):
	def str(s, shortener = lambda x:x):
		return "{" + printify(s, ". ", shortener) + "}"

class Arg:
	def __init__(s, uri, thing, frame, term_idx, arg_idx, is_in_head):
		s.uri = uri
		assert(isinstance(uri, rdflib.term.Identifier))
		s.thing = thing
		assert(isinstance(thing, (AtomVar)))
		s.frame = frame
		assert((type(frame) == str) or (type(frame) == URIRef))
		s.term_idx = term_idx
		#assert(isinstance(term_idx, (str, int)))
		s.arg_idx = arg_idx
		#assert(isinstance(arg_idx, int))
		s.is_in_head = is_in_head
		#assert(isinstance(is_in_head, (bool, str)))

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
		s.kbdbg_name = URIRef
		s.items = []


class Locals(OrderedDict):

	bnode_or_locals = 'bnode'

	def __init__(s, initializer, debug_rule, debug_id = 0, kbdbg_frame=None):
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

	def new(s, kbdbg_frame):
		nolog or log("cloning " + str(s))
		s.debug_last_instance_id += 1
		return Locals(s, s.debug_rule(), s.debug_last_instance_id, kbdbg_frame)


	def __str__(s):
		r = (s.bnode_or_locals + str(s.debug_id) + " of " + str(s.debug_rule()))
		if len(s):
			r += ":\n#" + printify([k.n3() + ": " + (str(v)) for k, v in s.items()], ", ")
		return r

	def emit(s):
		kbdbg(rdflib.URIRef(s.kbdbg_name).n3() + " rdf:type kbdbg:" + s.bnode_or_locals)
		kbdbg(rdflib.URIRef(s.kbdbg_name).n3() + " kbdbg:has_parent " + rdflib.URIRef(s.kbdbg_frame).n3())
		items = []
		for k, v in s.items():
			if not is_var(k): continue
			uri = bn()
			items.append(uri)
			if isinstance(k, rdflib.Variable):
				sss = k.n3()
			else:
				sss = k
			kbdbg(uri + ' kbdbg:has_name ' + rdflib.Literal(sss).n3())
			kbdbg(uri + " kbdbg:has_value_description " + rdflib.Literal(v.kbdbg_name).n3())
			kbdbg(uri + " kbdbg:has_value " + rdflib.Literal(v.__short__str__()).n3())
		kbdbg(rdflib.URIRef(s.kbdbg_name).n3() + " kbdbg:has_items " + emit_list(items))

	def __short__str__(s):
		return "["+printify([str(k) + ": " + (v.__short__str__()) for k, v in s.items() if (type(k) != URIRef)], ", ")+']'



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
	def str(s, shortener = lambda x:x):
		if type(s.kbdbg_name) == URIRef:
			xxx = s.kbdbg_name.n3()
		else:
			xxx= s.kbdbg_name
		return (shortener(xxx) if dbg else '') + s.___short__str__()
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
		s.bnode = None

	def str(s, shortener = lambda x:x):
		if type(s.kbdbg_name) == URIRef:
			xxx = shortener(s.kbdbg_name.n3())
		else:
			xxx = shortener(s.kbdbg_name)
		if s.bnode:
			xxx += '['
			for k,v in s.bnode.items():
				if v != s:
					xxx += str(shortener(k)) + ' --->>> '
					if (type(v) == Var) and v.bnode and (s in v.bnode.values()):
						xxx += '[recursive]'
					else:
					    xxx += shortener(str(v))
					xxx += '\n'
			xxx += ']'
		return (xxx if dbg else '') + s.___short__str__()
		# + " in " + str(s.debug_locals())
	def ___short__str__(s):
		r = ''
		if s.bnode:
			r +=  '[bnode]'
		if s.bound_to:
			return r + ' = ' + (s.bound_to.__short__str__())
		else:
			return r + '(free)'

	def recursive_clone(s):
		r = super().recursive_clone()
		if s.bound_to:
			r.bound_to = s.bound_to.recursive_clone()
		r.bnode = s.bnode
		if s.bnode:
			r.is_a_bnode_from_original_rule = s.is_a_bnode_from_original_rule
			r.is_from_name = s.is_from_name
		return r

	def bind_to(x, y, orig):
		assert x.bound_to == None
		x.bound_to = y
		msg = "bound " + str(x) + " to " + str(y)
		nolog or log(msg)
		uri = bn()
		emit_binding(uri, orig)
		step()
		yield msg
		x.bound_to = None
		kbdbg(uri + " kbdbg:was_unbound true")
		step()


def success(msg, orig, uri = None):
		if uri == None:
			uri = bn()
		emit_binding(uri, orig)
		step()
		kbdbg(uri + " kbdbg:message " + rdflib.Literal(msg).n3())
		yield msg
		kbdbg(uri + " kbdbg:was_unbound true")
		step()

def fail(msg, orig, uri = None):
		if uri == None:
			uri = bn()
		if uri == ':bn167':
			print(uri)
		emit_binding(uri, orig)
		kbdbg(uri + " kbdbg:failed true")
		kbdbg(uri + " kbdbg:message " + rdflib.Literal(msg).n3())
		while False:
			yield msg
		step()

def emit_binding(uri, _x_y):
	_x, _y = _x_y
	kbdbg(uri + " rdf:type kbdbg:binding")
	kbdbg(uri + " kbdbg:has_source " + emit_arg(_x))
	kbdbg(uri + " kbdbg:has_target " + emit_arg(_y))

def emit_arg(x):
	r = bn()
	kbdbg(r + " rdf:type kbdbg:arg")
	kbdbg(r + " kbdbg:has_frame " + x.frame.n3())
	if type(x.is_in_head) == bool:
		if x.is_in_head:
			kbdbg(r + " kbdbg:is_in_head true")
	else:
		if x.is_in_head == 'bnode':
			kbdbg(r + ' kbdbg:is_bnode true')
	if x.term_idx != None:
		if type(x.term_idx) == int:
			t = str(x.term_idx)
		elif type(x.term_idx) == rdflib.Variable:
			t = rdflib.Literal('?' + str(x.term_idx)).n3()
		else:
			t = rdflib.Literal(x.term_idx).n3()
		kbdbg(r + ' kbdbg:term_idx ' + t)
	if x.arg_idx != None:
		kbdbg(r + ' kbdbg:arg_idx ' + str(x.arg_idx))
	return r




def unify(_x, _y):
	assert(isinstance(_x, Arg))
	assert(isinstance(_y, Arg))
	x = get_value(_x.thing)
	y = get_value(_y.thing)
	return unify2(_x, _y, x, y)

def unify2(arg_x, arg_y, val_x, val_y):
	xy = (arg_x, arg_y)
	yx = (arg_y, arg_x)

	log("unify " + str(val_x) + " with " + str(val_y))
	if id(val_x) == id(val_y):
		r = success("same things", xy)
	elif type(val_x) == Var and not val_x.bnode:
		r = val_x.bind_to(val_y, xy)
	elif type(val_y) == Var and not val_y.bnode:
		r = val_y.bind_to(val_x, yx)

	elif type(val_y) == Var and type(val_x) == Var and val_x.is_a_bnode_from_original_rule == val_y.is_a_bnode_from_original_rule and val_x.is_from_name == val_y.is_from_name:
		r = val_y.bind_to(val_x, yx)

	#elif type(val_x) == Var and type(val_y) == Atom :
	#	r = val_x.bind_to(val_y, xy)
	#elif type(val_y) == Var and type(val_x) == Atom:
	#	r = val_y.bind_to(val_x, yx)

	elif type(val_x) == Atom and type(val_y) == Atom:
		if val_x.value == val_y.value:
			r = success("same consts", xy)
		else:
			r = fail("different consts: %s %s" % (val_x.value, val_y.value), xy)
	else:
		r = fail("different things: %s %s" % (val_x, val_y), xy)
	return r

def get_value(x):
	if type(x) == Atom:
		return x
	v = x.bound_to
	if v:
		return get_value(v)
	else:
		return x

def is_var(x):
	return type(x) == rdflib.Variable


class Rule(Kbdbgable):
	last_frame_id = 0
	def __init__(singleton, original_head, head, body=Graph()):
		super().__init__()
		singleton.head = head
		singleton.body = body
		singleton.original_head = id(original_head)
		singleton.original_head_ref = original_head #prevent gc
		singleton.original_head_triples = original_head[:]
		singleton.locals_template = singleton.make_locals(singleton.original_head_triples, body, singleton.kbdbg_name)
		singleton.ep_heads = []

		with open(_rules_file_name, 'a') as ru:
			ru.write(singleton.kbdbg_name + ":"+ singleton.__str__(shorten) + '\n')

		kbdbg(":"+singleton.kbdbg_name + ' rdf:type ' + 'kbdbg:rule')
		if singleton.head:
			head_uri = ":"+singleton.kbdbg_name + "Head"
			kbdbg(":"+singleton.kbdbg_name + ' kbdbg:has_head ' + head_uri)
			emit_term(singleton.head, head_uri)
		if singleton.body:
			body_uri = singleton.kbdbg_name + "Body"
			kbdbg(":"+singleton.kbdbg_name + ' kbdbg:has_body :' + body_uri)
			for i in singleton.body:
				body_term_uri = bn()
				emit_term(i, body_term_uri)
				kbdbg(":"+body_uri + " rdf:first " + body_term_uri)
				body_uri2 = body_uri + "X"
				kbdbg(":"+body_uri + " rdf:rest :" + body_uri2)
				body_uri = body_uri2
			kbdbg(":"+body_uri + " rdf:rest rdf:nil")
		kbdbg(":"+singleton.kbdbg_name + ' kbdbg:has_original_head ' + rdflib.Literal(str(singleton.original_head)).n3())

	def __str__(singleton, shortener = lambda x:x):
		return "{" + (singleton.head.str(shortener) if singleton.head else '') + "} <= " + (singleton.body.str(shortener)  if singleton.body else '{}')

	def make_locals(singleton, head, body, kbdbg_rule):
		locals = Locals({}, singleton)
		locals.kbdbg_frame = "locals_template_for_" + kbdbg_rule
		for triple in (head if head else []) + body:
			for a in triple.args:
				if is_var(a):
					x = Var(a, locals)
				else:
					x = Atom(a, locals)
				locals[a] = x
		return locals

	def rule_unify(singleton, parent, args):
		Rule.last_frame_id += 1
		frame_id = Rule.last_frame_id
		depth = 0
		generators = []
		kbdbg_name = rdflib.URIRef(singleton.kbdbg_name + "Frame"+str(frame_id),base=kbdbg_prefix)
		locals = singleton.locals_template.new(kbdbg_name)
		locals.kbdbg_name = URIRef(kbdbg_name + ("_locals"))
		uuu = kbdbg_name.n3()
		kbdbg(uuu + " rdf:type kbdbg:frame")
		kbdbg(uuu + " kbdbg:is_for_rule :"+singleton.kbdbg_name)
		if parent:
			kbdbg(uuu + " kbdbg:has_parent " + parent.n3())

		existentials = get_existentials(singleton.original_head_triples, singleton.body)
		def desc():
			return ("#vvv\n#" + #str(singleton) + "\n" +
			kbdbg_name.n3() + '\n' +
			"#args:" + str(args) + "\n" +
			"#locals:" + locals.__short__str__() + "\n" +
			"#depth:"+ str(depth) + "/" + str(max_depth)+"\n#entering^^^")

		max_depth = len(args)  + len(singleton.body) - 1

		log ("entering:" + desc())

		for e in existentials:
			locals[e].bnode = locals
			locals[e].is_a_bnode_from_original_rule = singleton.original_head
			locals[e].is_from_name = e

		incoming_bnode_unifications = []

		if len(existentials):
			locals.emit()

		while True:

			if len(generators) <= depth:
				if depth < len(args):
					arg_index = depth
					head_uriref = singleton.head.args[arg_index]
					head_thing = locals[head_uriref]
					generator = unify(args[arg_index], Arg(head_uriref, head_thing, head_thing.debug_locals().kbdbg_frame if dbg else None, 0, arg_index, True))
					head_thing.arg_index = arg_index
				elif len(incoming_bnode_unifications):
					assert depth < len(args) + len(incoming_bnode_unifications)
					ua,ub = incoming_bnode_unifications[depth - len(args)]
					generator = unify(ua, ub)
				else:
					assert depth < len(args) + len(singleton.body)
					body_item_index = depth - len(args)
					triple = singleton.body[body_item_index]
					bi_args = []
					for arg_idx, uri in enumerate(triple.args):
						thing = locals[uri]
						bi_args.append(Arg(uri, get_value(thing), thing.debug_locals().kbdbg_frame if dbg else None, body_item_index, arg_idx, False))
					generator = pred(triple.pred, kbdbg_name, bi_args)
				generators.append(generator)
				nolog or log("generators:%s", generators)
			try:
				generators[depth].__next__()
			except StopIteration:
				nolog or log ("back")
				generators.pop()
				depth-=1
				if depth == -1:
					nolog or log ("rule done")
					step()
					break
				continue
			log ("back in " + desc() + "\n# from sub-rule")
			if depth == len(args) - 1:
				incoming_bnode_unifications = []
				for k,v in locals.items():
					vv = get_value(v)
					if vv != v and type(vv) == Var and vv.bnode and vv.is_a_bnode_from_original_rule == singleton.original_head and k == vv.is_from_name:
						log('its a bnode')
						b = vv.bnode
						for k,v in b.items():
							if not is_var(k): continue
							incoming_bnode_unifications.append((
								Arg(k, locals[k], locals.kbdbg_name, k, 0, 'bnode'),
								Arg(k, b[k], b.kbdbg_name, k, 0, 'bnode')))


				if len(incoming_bnode_unifications):
					max_depth = len(args) + len(incoming_bnode_unifications) - 1
				else:
					max_depth = len(args) + len(singleton.body) - 1
			if (depth < max_depth):
				log ("down")
				depth+=1
			else:
				yield locals
				log ("re-entering " + desc() + " for more results")
		kbdbg(kbdbg_name.n3() + " kbdbg:is_finished true")


	def match(s, parent = None, args=[]):
		head = EpHead()
		for arg in args:
			assert arg.thing == get_value(arg.thing)
			head.items.append(Arg(arg.uri, arg.thing.recursive_clone(), arg.thing.debug_locals().kbdbg_frame, arg.term_idx, arg.arg_idx, arg.is_in_head))
		s.ep_heads.append(head)
		for i in s.rule_unify(parent, args):
			s.ep_heads.pop()
			yield i
			s.ep_heads.append(head)
		s.ep_heads.pop()

	def find_ep(s, args):
		nolog or log ("ep check: %s vs..", args)
		for head in s.ep_heads:
			if ep_match(args, head.items):
				kbdbg(bn() + ' rdf:type kbdbg:ep_match')
				return True
		nolog or log ("..no ep match")

def get_existentials(heads, body):
	"""gets all the names of existentials"""
	vars = []
	for head in heads:
		if head:
			for i_idx, i in enumerate(head.args):
				if is_var(i):
					if i not in vars:
						vars.append(i)
	for i in body:
		for j in i.args:
			if is_var(j):
				if j in vars:
					vars.remove(j)
	log ("existentials:" + ' '.join(v.n3() for v in vars))
	return vars

def ep_match(args_a, args_b):
	assert len(args_a) == len(args_b)
	for i in range(len(args_a)):
		a = args_a[i].thing
		b = args_b[i].thing
		if type(a) != type(b):
			return
		if type(a) == Var:
			if a.bnode and not b.bnode or b.bnode and not a.bnode:
				return
			if a.bnode and b.bnode:
				if a.is_a_bnode_from_original_rule != b.is_a_bnode_from_original_rule or a.is_from_name != b.is_from_name:
					return
		if type(a) == Atom and b.value != a.value:
			return
	nolog or log("EP!")
	return True


def pred(p, parent, args):
	for a in args:
		assert(isinstance(a, Arg))
		assert(isinstance(a.thing, (AtomVar, )))
		assert get_value(a.thing) == a.thing

	if p not in preds:
		log (str(p) + " not in preds")
		for i in preds:
			log("is " + str(i) + "?")
			log(i == p)

	for rule in preds[p]:
		if(rule.find_ep(args)):
			continue
		for i in rule.match(parent, args):
			yield i

def query(input_rules, input_query):
	global preds, dbg
	dbg = not nolog or not nokbdbg
	kbdbg(this + " rdf:value " + step_list_item(0))
	kbdbg_graph_first()
	preds = defaultdict(list)
	for r in input_rules:
		preds[r.head.pred].append(r)
	query_rule = Rule([], None, input_query)
	step()
	for i, locals in enumerate(query_rule.match()):
		uri = ":result" + str(i)
		kbdbg(uri + " rdf:type kbdbg:result")
		terms = [substitute_term(term, locals) for term in input_query]
		result_terms_uri = emit_list(emit_terms(terms))
		kbdbg(uri + " rdf:value " + result_terms_uri)
		yield terms
		printed = []
		for t in terms:
			for a in t.args:
				if a in printed: continue
				if a not in locals:	continue
				v = get_value(locals[a])
				if type(v) == Var and v.bnode:
					log(str(a) + ':')
					log(print_bnode(v.bnode))
					printed.append(a)

		#log(print_proof(..))

		kbdbg(uri + " kbdbg:was_unbound true")

#def print_proof(indent, rules, substs):
#	for rule in rules:
#		log(' '*indent +


def emit_list(l):
	r = uri = bn()
	for idx, i in enumerate(l):
		if type(i) == str:
			v = i
		elif isinstance(i, rdflib.Variable):
			v = rdflib.Literal('?' + str(i)).n3()
		elif not isinstance(i, rdflib.Graph):
			v = i.n3()
		else:
			v = rdflib.URIRef(i.identifier).n3()
		kbdbg(uri + " rdf:first " + v)
		if type(i) == rdflib.BNode:
			kbdbg(i.n3() + ' kbdbg:comment "thats a bnode from the kb input graph, a subj or an obj of an implication. fixme."')
		if idx != len(l) - 1:
			uri2 = uri + "X"
		else:
			uri2 = 'rdf:nil'
		kbdbg(uri + " rdf:rest " + uri2)
		uri = uri2
	return r

def print_bnode(v):
	r = ''
	r += '[\n'
	for k,vv in v.items():
		if v != vv:
			r += str(k) + ' --->>> ' + (get_value(vv).__short__str__()) + '\n'
	r += ']'
	return r

def substitute_term(term, locals):
	return Triple(term.pred, [substitute(x, locals) for x in term.args])

def substitute(node, locals):
	assert(isinstance(node, rdflib.term.Identifier))
	if node in locals:
		v = get_value(locals[node])
		#if type(v) == Var and v.bnode:
		#	log(print_bnode(v.bnode))
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



def emit_terms(terms):
	c=[]
	for i in terms:
		c.append(emit_term(i, bn()))
	return c

def emit_term(t, uri):
	kbdbg(uri + " rdf:type kbdbg:term")
	kbdbg(uri + " kbdbg:has_pred " + t.pred.n3())
	kbdbg(uri + " kbdbg:has_args " + emit_list(t.args))
	return uri

