import subprocess, os, sys, logging
from time import sleep
import datetime
from weakref import ref as weakref
from rdflib import URIRef
import rdflib
from ordered_rdflib_store import OrderedStore
try:
	from urllib.parse import quote_plus
except ImportError:
	from urllib import quote_plus
from collections import defaultdict, OrderedDict
from common import pyin_prefixes as prefixes
from common import shorten, un_move_me_ize_pred
import common



nolog = False
kbdbg_prefix = URIRef('http://kbd.bg/#')
log, kbdbg_text = 666,666
pool = None
futures = []

if sys.version_info.major == 3:
	unicode = str


to_submit_default = ''
to_submit_graph = ''


def kbdbg(text, default = False):
	global to_submit_default, to_submit_graph
	if default:
		kbdbg_text(text+'.')
	else:
		kbdbg_text(text+'.')#.ljust(100) + '<'+step_graph_name(global_step_counter)+'>' )# i think ill just output the sparql alongside
	if pool:
		if default:
			to_submit_default += text+'. '
		else:
			to_submit_graph += text+'. '

all_updates = ''

def submit_kbdbg():
	global to_submit_graph, all_updates

	check_futures()

	qs = pool._work_queue.qsize()
	while qs > 100:
		print("sleeping "+str(qs - 100))
		sleep (qs - 100)
		qs = pool._work_queue.qsize()

	if to_submit_graph != '':
		all_updates +="INSERT DATA {Graph <" + step_graph_name(global_step_counter) + "> {" + to_submit_graph +'}};'

	to_submit_graph = ''

	if len(all_updates) > 100000:
		flush_sparql_updates()

def flush_sparql_updates():
	global all_updates, to_submit_default
	if not pool: return
	futures.append(pool.submit(server.update, prefixes + all_updates))
	all_updates = ''
	if to_submit_default != '':
		futures.append(pool.submit(server.update, prefixes + "INSERT DATA {Graph " + default_graph + " {" + to_submit_default +"}};"))
		to_submit_default = ''


def step_graph_name(idx):
	return this + '_' + str(idx).rjust(10,'0')

def step_list_item(idx):
	if idx == 0:
		return this
	return step_graph_name(idx) + "_list_item"

def kbdbg_graph_first():
	kbdbg('<'+step_list_item(global_step_counter) + "> rdf:first <" + step_graph_name(global_step_counter)+'>', True)

global_step_counter = 0
def step():
	global global_step_counter
	if not nolog:
		kbdbg_text("#step"+str(global_step_counter))
		if pool:
			submit_kbdbg()
		kbdbg_graph_first()
		kbdbg('<'+step_list_item(global_step_counter) + "> rdf:rest <" + step_list_item(global_step_counter + 1)+'>', True)
	global_step_counter += 1
	#if step % 10000 == 0:


bnode_counter = 0
def bn():
	global bnode_counter
	bnode_counter += 1
	return  ':bn' + str(bnode_counter)


def printify(iterable, separator, shortener = lambda x:x):
	r = ""
	last = len(iterable) - 1
	for i, x in enumerate(iterable):
		if isinstance(x, (str,unicode)):
			r += shortener(x)
		else:
			r += x.str(shortener)
		if i != last:
			r += separator
	return r


class Triple(object):
	def __init__(s, pred, args):
		s.pred = pred
		s.args = args

	def str(s, shortener = lambda x:x):
		if len(s.args) == 2:
			return shortener(s.args[0].n3()) + " " + shortener(s.pred.n3()) + " " + shortener(s.args[1].n3()) + " . "
		return shortener(str(s.pred)) + "(" + printify(s.args, ", ", shortener) + ")"

class Graph(list):
	def str(s, shortener = lambda x:x):
		return "{" + printify(s, ". ", shortener) + "}"

class Arg(object):
	def __init__(s, uri, thing, frame, term_idx, arg_idx, is_in_head):
		s.uri = uri
		assert(isinstance(uri, rdflib.term.Identifier))
		s.thing = thing
		assert(isinstance(thing, (AtomVar)))
		s.frame = frame
		assert((type(frame) in (str, URIRef, bool)))
		s.term_idx = term_idx
		#assert(isinstance(term_idx, (str, int)))
		s.arg_idx = arg_idx
		#assert(isinstance(arg_idx, int))
		s.is_in_head = is_in_head
		#assert(isinstance(is_in_head, (bool, str)))

class Kbdbgable(object):
	last_instance_debug_id = 0
	def __init__(s):
		s.__class__.last_instance_debug_id += 1
		s.debug_id = s.__class__.last_instance_debug_id
		s.kbdbg_name = s.__class__.__name__ + str(s.debug_id)

class EpHead(Kbdbgable):
	def __init__(s):
		if not nolog:
			Kbdbgable.__init__(s)
			s.kbdbg_name = ':' + s.kbdbg_name
		s.items = []


class Locals(OrderedDict):
	bnode_or_locals = 'bnode'
	def __init__(s, initializer, debug_rule, debug_id = 0, kbdbg_frame=None):
		OrderedDict.__init__(s)
		s.debug_id = debug_id
		s.debug_last_instance_id = 0
		s.debug_rule = weakref(debug_rule)
		s.kbdbg_frame = kbdbg_frame
		for k,v in initializer.items():
			if type(v) is Var:
				s[k] = Var(nolog or (v.debug_name + "_clone"), nolog or weakref(s))
			else:
				s[k] = Atom(v.value, nolog or weakref(s))

	def new(s, kbdbg_frame):
		nolog or log("cloning " + str(s))
		s.debug_last_instance_id += 1
		return Locals(s, s.debug_rule(), s.debug_last_instance_id, kbdbg_frame)


	def __str__(s):
		r = (s.bnode_or_locals + str(s.debug_id) + " of " + str(s.debug_rule()))
		if len(s):
			rr = []
			for k, v in s.items():
				kk = k.n3()
				rr.append(str(kk) + ": " + str(v))
			r += ":\n#" + printify(rr, ", ")
		return r

	def emit(s):
		kbdbg(rdflib.URIRef(s.kbdbg_name).n3() + " rdf:type kbdbg:" + s.bnode_or_locals)
		kbdbg(rdflib.URIRef(s.kbdbg_name).n3() + " kbdbg:has_parent " + rdflib.URIRef(s.kbdbg_frame).n3())
		items = []
		for k, v in s.items():
			if not is_var(k): continue
			uri = bn()
			items.append(uri)
			if type(k) is rdflib.Variable:
				sss = k.n3()
			else:
				sss = k
			kbdbg(uri + ' kbdbg:has_name ' + rdflib.Literal(sss).n3())
			kbdbg(uri + " kbdbg:has_value_description " + rdflib.Literal(v.kbdbg_name).n3())
			kbdbg(uri + " kbdbg:has_value " + rdflib.Literal(v.__short__str__()).n3())
		kbdbg(rdflib.URIRef(s.kbdbg_name).n3() + " kbdbg:has_items " + emit_list(items))

	def __short__str__(s):
		return "["+printify([str(k) + ": " + (v.__short__str__()) for k, v in s.items() if (not isinstance(k, URIRef))], ", ")+']'



class AtomVar(Kbdbgable):
	def __init__(s, debug_name, debug_locals):
		s.debug_name = debug_name
		if not nolog:
			Kbdbgable.__init__(s)
			if isinstance(debug_locals, weakref):
				s.debug_locals = debug_locals
			elif debug_locals == None:
				s.debug_locals = None
			else:
				s.debug_locals = weakref(debug_locals)
			if s.debug_locals != None:
				s.kbdbg_name = s.debug_locals().kbdbg_frame
			assert(debug_name != None)
			s.kbdbg_name += "_" + quote_plus(debug_name)

	def __short__str__(s):
		return get_value(s).___short__str__()


class Atom(AtomVar):
	def __init__(s, value, debug_locals=None):
		AtomVar.__init__(s,value, debug_locals)
		assert(isinstance(value, rdflib.term.Identifier))
		s.value = value
	def str(s, shortener = lambda x:x):
		if isinstance(s.kbdbg_name, URIRef):
			xxx = s.kbdbg_name.n3()
		else:
			xxx= s.kbdbg_name
		return (shortener(xxx) if dbg else '') + s.___short__str__()
	def ___short__str__(s):
		return '("'+str(s.value)+'")'
	def rdf_str(s):
		return '"'+str(s.value)+'")'
	def recursive_clone(s):
		r = Atom(s.value, nolog or s.debug_locals)
		r.value = s.value
		if not nolog:
			r.kbdbg_name = s.kbdbg_name
		return r


class Var(AtomVar):
	"""
	doc:
	besides constants and variables, we have a new type of Thing, we use the Var class, but
	we set three new attributes on it: .bnode, .is_a_bnode_from_original_rule, .is_from_name
	"""
	def __init__(s, debug_name=None, debug_locals=None):
		AtomVar.__init__(s,debug_name, debug_locals)
		s.bound_to = None #for pyin
		s.bnode = lambda: None  #for pyin
		s.is_bnode = False #for pyco

	def str(s, shortener = lambda x:x):
		if isinstance(s.kbdbg_name,URIRef):
			xxx = shortener(s.kbdbg_name.n3())
		else:
			xxx = shortener(s.kbdbg_name)
		if s.bnode():
			xxx += '['
			for k,v in s.bnode().items():
				if v != s:
					xxx += str(shortener(k)) + ' --->>> '
					if isinstance(v, Var) and v.bnode() and (s in v.bnode().values()):
						xxx += '[recursive]'
					else:
					    xxx += shortener(str(v))
					xxx += '\n'
			xxx += ']'
		return (xxx if dbg else '') + s.___short__str__()
		# + " in " + str(s.debug_locals())
	def ___short__str__(s):
		r = ''
		if s.bnode():
			r +=  '[bnode]'
		if s.bound_to:
			return r + ' = ' + (s.bound_to.__short__str__())
		else:
			return r + '(free)'

	def recursive_clone(s):
		r = Var(nolog or s.debug_name, nolog or s.debug_locals)
		if not nolog:
			r.kbdbg_name = s.kbdbg_name
		if s.bound_to:
			r.bound_to = s.bound_to.recursive_clone()
		r.bnode = weakref(s.bnode()) if s.bnode() else lambda: None
		if s.bnode():
			r.is_a_bnode_from_original_rule = s.is_a_bnode_from_original_rule
			r.is_from_name = s.is_from_name
		return r

	def bind_to(x, y, orig):
		assert x.bound_to == None
		x.bound_to = y
		if not nolog:
			msg = "bound " + str(x) + " to " + str(y)
			nolog or log(msg)
			uri = bn()
			emit_binding(uri, orig)
			#step()
		yield nolog or msg
		x.bound_to = None
		if not nolog:
			kbdbg(uri + " kbdbg:was_unbound true")
			#step()


def success(msg, orig, uri = None):
		if not nolog:
			if uri == None:
				uri = bn()
			log(uri)
			emit_binding(uri, orig)
			kbdbg(uri + " kbdbg:message " + rdflib.Literal(msg).n3())
			#step()
		yield msg
		if not nolog:
			kbdbg(uri + " kbdbg:was_unbound true")
			#step()

def fail(msg, orig, uri = None):
		if not nolog:
			if uri == None:
				uri = bn()
			emit_binding(uri, orig)
			kbdbg(uri + " kbdbg:failed true")
			kbdbg(uri + " kbdbg:message " + rdflib.Literal(msg).n3())
		while False:
			yield msg
		if not nolog:
			#step()
			kbdbg(uri + " kbdbg:was_unbound true")

def emit_binding(uri, _x_y):
	_x, _y = _x_y
	kbdbg(uri + " rdf:type kbdbg:binding")
	kbdbg(uri + " kbdbg:has_source " + emit_arg(_x))
	kbdbg(uri + " kbdbg:has_target " + emit_arg(_y))

def emit_arg(x):
	r = bn()
	kbdbg(r + " rdf:type kbdbg:arg")
	kbdbg(r + " kbdbg:has_frame " + x.frame.n3())
	if isinstance(x.is_in_head, bool):
		if x.is_in_head:
			kbdbg(r + " kbdbg:is_in_head true")
	else:
		if x.is_in_head == 'bnode':
			kbdbg(r + ' kbdbg:is_bnode true')
	if x.term_idx != None:
		if isinstance(x.term_idx, int):
			t = str(x.term_idx)
		elif isinstance(x.term_idx, rdflib.Variable):
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
	"""
	doc:
	in addition to the usual stuff:
	a bnode binds to another bnode, if they both come from the same original rule, and from the same variable name
	variables bind to bnodes just like to constants, constants and variables dont unify
	"""
	xy = (arg_x, arg_y)
	yx = (arg_y, arg_x)
	nolog or log("unify " + str(val_x) + " with " + str(val_y))
	if val_x is val_y:
		return success("same things", xy)
	x_is_var = type(val_x) is Var
	y_is_var = type(val_y) is Var
	if x_is_var and not val_x.bnode():
		return val_x.bind_to(val_y, xy)
	elif y_is_var and not val_y.bnode():
		return val_y.bind_to(val_x, yx)
	elif y_is_var and x_is_var and val_x.is_a_bnode_from_original_rule == val_y.is_a_bnode_from_original_rule and val_x.is_from_name == val_y.is_from_name:
		return val_y.bind_to(val_x, yx)
	elif type(val_x) is Atom and type(val_y) is Atom:
		if val_x.value == val_y.value:
			return success("same consts", xy)
		else:
			return fail(nolog or ("different consts: %s %s" % (val_x.value, val_y.value)), xy)
	else:
		return fail(nolog or ("different things: %s %s" % (val_x, val_y)), xy)

def get_value(x):
	if type(x) is Atom:
		return x
	v = x.bound_to
	if v:
		return get_value(v)
	else:
		return x

def is_var(x):
	return type(x) is rdflib.Variable


class Rule(Kbdbgable):

	last_frame_id = 0
	emitted_formulas = {}
	def __init__(singleton, original_head, head_idx, body=Graph()):
		Kbdbgable.__init__(singleton)
		assert type(head_idx) == int or head_idx == None
		singleton.head_idx = head_idx
		if head_idx != None:
			singleton.head = original_head[head_idx]
		else:
			singleton.head = None
		singleton.body = body
		if body == None:
			singleton.body = []
		"""	doc:
		I call original-rule the possibly-multiple-triples-in-head rule that is our input,
		original_head is the original rule's head
		A rule has a set of existentials, which are all the vars that dont appear in the body, only in the head.
		"""
		singleton.original_head = id(original_head)
		singleton.original_head_ref = original_head #prevent gc
		singleton.original_head_triples = original_head[:]
		singleton.locals_template = singleton.make_locals(singleton.original_head_triples, body, singleton.kbdbg_name)
		singleton.ep_heads = []
		nolog or log(singleton.kbdbg_name + ":")
		singleton.existentials = get_existentials_names(singleton.original_head_triples, singleton.body)
		singleton.head_vars = get_head_vars( singleton.original_head_triples)

		with open(_rules_file_name, 'a') as ru:
			ru.write(singleton.kbdbg_name + ":"+ singleton.__str__(shorten) + '\n')

		nolog or kbdbg(":"+singleton.kbdbg_name + ' rdf:type ' + 'kbdbg:rule')
		if not nolog:
			if singleton.head:
				head_uri = ":"+singleton.kbdbg_name + "Head"
				kbdbg(":"+singleton.kbdbg_name + ' kbdbg:has_head ' + head_uri)
				emit_term(singleton.head, head_uri)
				kbdbg(":"+singleton.kbdbg_name + ' kbdbg:has_head_idx ' + str(head_idx))
			try:
				emitted_body = Rule.emitted_formulas[id(singleton.original_head)]
			except KeyError:
				emitted_body = Rule.emitted_formulas[id(singleton.original_head)] = emit_list(emit_terms(singleton.body), ':'+singleton.kbdbg_name + "Body")
			kbdbg(":"+singleton.kbdbg_name + ' kbdbg:has_body ' + emitted_body)
			try:
				emitted_original_head = Rule.emitted_formulas[singleton.original_head]
			except KeyError:
				emitted_original_head = Rule.emitted_formulas[singleton.original_head] = emit_list(emit_terms(singleton.original_head_triples), ':'+singleton.kbdbg_name + "OriginalHead")
			kbdbg(":"+singleton.kbdbg_name + ' kbdbg:has_original_head ' + emitted_original_head)

	def __str__(singleton, shortener = lambda x:x):
		return "{" + (
			(singleton.head.str(shortener) +
			((' , original head:' + singleton.original_head_ref.str(shortener))
			if len(singleton.original_head_ref) > 1 else ''))
			if singleton.head else '') + "} <= " + (singleton.body.str(shortener)  if singleton.body else '{}')

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
		PY3 = sys.version_info.major == 3
		depth = 0
		generators = []
		if not nolog:
			Rule.last_frame_id += 1
			frame_id = Rule.last_frame_id
			kbdbg_name = rdflib.URIRef(singleton.kbdbg_name + "Frame"+str(frame_id),base=kbdbg_prefix)
		locals = singleton.locals_template.new(nolog or kbdbg_name)
		if not nolog:
			locals.kbdbg_name = URIRef(kbdbg_name + ("_locals"))
			uuu = kbdbg_name.n3()
			kbdbg(uuu + " rdf:type kbdbg:frame")
			kbdbg(uuu + " kbdbg:is_for_rule :"+singleton.kbdbg_name)
			if parent:
				kbdbg(uuu + " kbdbg:has_parent " + parent.n3())
			def desc():
				return ("#vvv\n#" + #str(singleton) + "\n" +
				kbdbg_name.n3() + '\n' +
				"#args:" + str(args) + "\n" +
				"#locals:" + locals.__short__str__() + "\n" +
				"#depth:"+ str(depth) + "/" + str(max_depth)+"\n#entering^^^")
		max_depth = len(args)  + len(singleton.body) - 1
		nolog or log ("entering:" + desc())
		"""
		doc:
		when a rule with existentials is invoked, its locals are set up as usual, except that bnodes
		are Vars with 3 new attributes: 
		
		the .bnode attribute points to locals of the rule that created the bnode.
		each locals contain all the existentials of the original rule, even those that didnt appear in that
		particular rule's head
		"""
		for e in singleton.existentials:
			locals[e].bnode = weakref(locals)
			locals[e].is_a_bnode_from_original_rule = singleton.original_head
			locals[e].is_from_name = e
		incoming_bnode_unifications = []
		if not nolog:
			if len(singleton.existentials):
				locals.emit()
		while True:
			if len(generators) <= depth:
				if depth < len(args):
					"""
					doc:
					A rule with existentials first unifies the incoming arguments with its local variables as usual.
					This means that if some of the parameters are bnodes from same original_rule, from same name,
					then the local bnode binds to the incoming one."""
					arg_index = depth
					head_uriref = singleton.head.args[arg_index]
					head_thing = locals[head_uriref]
					generator = unify(args[arg_index], Arg(head_uriref, head_thing, nolog or head_thing.debug_locals().kbdbg_frame, singleton.head_idx, arg_index, True))
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
						bi_args.append(Arg(uri, get_value(thing), nolog or thing.debug_locals().kbdbg_frame, body_item_index, arg_idx, False))
					step()
					generator = pred(triple.pred, nolog or kbdbg_name, bi_args)
				if PY3:
					generators.append(generator.__next__)
				else:
					generators.append(generator.next)
				nolog or log("generators:%s", generators)
			try:
				generators[depth]()
			except StopIteration:
				nolog or log ("back")
				generators.pop()
				depth-=1
				if depth == -1:
					if not nolog:
						log ("rule done")
					step()
					break
				continue
			nolog or log ("back in " + desc() + "\n# from sub-rule")
			if depth == len(args) - 1:
				"""	
				After rule head unifications, local bnodes are checked to see if they are bound to incoming bnodes.
				If so, the body is not entered, and instead, the locals of the bnode are unified the this rule's locals.
				then we yield.
				
				if no incoming bnodes are found after head unification, we proceed with the body as usual.
				"""
				incoming_bnode_unifications = []
				for k,v in locals.items():
					vv = get_value(v)
					if vv != v and type(vv) is Var and vv.bnode() and vv.is_a_bnode_from_original_rule == singleton.original_head and k == vv.is_from_name:
						nolog or log('its a bnode')
						b = vv.bnode()
						for k,v in b.items():
							if not is_var(k): continue
							incoming_bnode_unifications.append((
								Arg(k, locals[k], nolog or locals.kbdbg_name, k, 0, 'bnode'),
								Arg(k, b[k], nolog or b.kbdbg_name, k, 0, 'bnode')))
				if len(incoming_bnode_unifications):
					max_depth = len(args) + len(incoming_bnode_unifications) - 1
				else:
					max_depth = len(args) + len(singleton.body) - 1
			if (depth < max_depth):
				nolog or log ("down")
				depth+=1
			else:
				yield locals
				nolog or log ("re-entering " + desc() + " for more results")
		nolog or kbdbg(kbdbg_name.n3() + " kbdbg:is_finished true")



	def match(s, parent = None, args=[]):
		head = EpHead()
		for arg in args:
			assert arg.thing == get_value(arg.thing)
			head.items.append(Arg(arg.uri, arg.thing.recursive_clone(), nolog or arg.thing.debug_locals().kbdbg_frame, arg.term_idx, arg.arg_idx, arg.is_in_head))

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
				nolog or kbdbg(bn() + ' rdf:type kbdbg:ep_match')
				return True
		nolog or log ("..no ep match")

def get_existentials_names(heads, body):
	body_vars = []
	for i in body:
		for j in i.args:
			if is_var(j):
				body_vars.append(j)
	vars = set()
	for head in heads:
		if head:
			for i in head.args:
				if is_var(i) and i not in body_vars and i.islower():
					vars.add(i)
	vars = list(vars)
	nolog or log ("existentials:" + ' '.join(v.n3() for v in vars))
	return vars

def get_head_vars(heads):
	vars = set()
	for head in heads:
		if head:
			for i in head.args:
				if is_var(i) :
					vars.add(i)
	return vars

def ep_match(args_a, args_b):
	assert len(args_a) == len(args_b)
	for i in range(len(args_a)):
		a = args_a[i].thing
		b = args_b[i].thing
		#log("YYY %s %s", str(type(a)), str(type(b)))
		#log("YYY %s %s", str(a.__class__), str(b.__class__))
		if a.__class__ != b.__class__:
			return
		if type(a) is Var:
			if a.bnode() and not b.bnode() or b.bnode() and not a.bnode():
				return
			if a.bnode() and b.bnode():
				if a.is_a_bnode_from_original_rule != b.is_a_bnode_from_original_rule or a.is_from_name != b.is_from_name:
					return
				"""doc:	two bnodes with same original rule and same name make an ep match"""
		if type(a) is Atom and b.value != a.value:
			return
	nolog or log("EP!")
	return True


def pred(p, parent, args):
	if not nolog:
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

def query(input_rules, query_rule, goal_graph):
	global preds, dbg
	nolog or kbdbg('<'+this + "> rdf:value <" + step_list_item(0)+'>')
	nolog or kbdbg_graph_first()
	preds = defaultdict(list)
	for r in input_rules:
		preds[r.head.pred].append(r)
	step()
#	tracemalloc.start()
	for i, locals in enumerate(query_rule.match()):
		uri = ":result" + str(i)
		nolog or kbdbg(uri + " rdf:type kbdbg:result")
		terms = substitute_graph(goal_graph, locals)
		if not nolog:
			result_terms_uri = emit_list(emit_terms(terms))
			kbdbg(uri + " rdf:value " + result_terms_uri)
		yield terms
		if not nolog:
			printed = []
			for t in terms:
				for a in t.args:
					if a in printed: continue
					if a not in locals:	continue
					v = get_value(locals[a])
					if isinstance(v, Var) and v.bnode():
						log(str(a) + ':')
						log(print_bnode(v.bnode()))
						printed.append(a)
		#log(print_proof(..))
		nolog or kbdbg(uri + " kbdbg:was_unbound true")
	nolog or flush_sparql_updates()

#def print_proof(indent, rules, substs):
#	for rule in rules:
#		log(' '*indent +

def emit_list(l, uri=None):
	if uri == None:
		uri = bn()
	r = uri
	for idx, i in enumerate(l):
		if type(i) in (unicode, str):
			v = i
		elif isinstance(i, rdflib.Variable):
			v = rdflib.Literal('?' + str(i)).n3()
		elif not isinstance(i, rdflib.Graph):
			v = i.n3()
		else:
			v = rdflib.URIRef(i.identifier).n3()
		kbdbg(uri + " rdf:first " + v)
		if isinstance(i, rdflib.BNode):
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

def substitute_graph(graph, locals):
	return [substitute_term(term, locals) for term in graph]

def substitute_term(term, locals):
	return Triple(term.pred, [substitute(x, locals) for x in term.args])

def substitute(node, locals):
	assert(isinstance(node, rdflib.term.Identifier))
	if node in locals:
		v = get_value(locals[node])
		#if type(v) == Var and v.bnode:
		#	log(print_bnode(v.bnode))
		if isinstance(v, Var):
			r = node
		elif isinstance(v, Atom):
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

def check_futures():
	nolog or log('len(futures):'+str(len(futures)))
	#nolog or log('len(futures):'+str(len(pool.)))

	while True:
		if len(futures) == 0: return
		f = futures[0]
		f.result()
		if f.done():
			futures.remove(f)
		else:
			return

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
	except:
		pass
	kbdbg_out = logging.FileHandler(kbdbg_file_name)
	kbdbg_out.setLevel(logging.DEBUG)
	kbdbg_out.setFormatter(logging.Formatter('%(message)s'))
	logger2=logging.getLogger("kbdbg")
	logger2.addHandler(kbdbg_out)

	log, kbdbg_text = logger1.debug, logger2.info

	if not nolog:
		for line in prefixes.strip().splitlines():
			kbdbg_text('@'+line+'.')
	#print("#this should be first line of merged stdout+stderr after @prefix lines, use PYTHONUNBUFFERED=1")





def set_up(identification, base):
	identification = common.fix_up_identification(identification)
	outpath = common.trace_output_path(identification)
	fn = 'kbdbg'+identification+'.n3'
	base = 'file://'  + base
	this = "http://kbd.bg/run"+str(datetime.datetime.now()).replace(':', '-').replace('.', '-').replace(' ', '-')
	kbdbg_fn = common.kbdbg_file_name(identification, fn)
	rules_fn = kbdbg_fn + '_rules'
	subprocess.call(['rm', '-f', rules_fn])
	os.system('mkdir -p '+outpath)
	return kbdbg_fn, rules_fn, identification, base, this, outpath


def load(kb, goal, identification, base):

	kb_stream, goal_stream = kb, goal
	implies = rdflib.URIRef("http://www.w3.org/2000/10/swap/log#implies")
	store = OrderedStore()
	kb_graph = rdflib.Graph(store=store, identifier=base)
	kb_conjunctive = rdflib.ConjunctiveGraph(store=store, identifier=base)
	kb_graph.parse(kb_stream, format='n3', publicID=base)
	if not nolog:
		log('---kb:')
		try:
			for l in kb_graph.serialize(format='n3').splitlines():
				log(l.decode('utf8'))
		except Exception as e:
			log(str(e))
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
			return rdflib.Variable(str(o.lower()))
		return o
	def fixup(spo):
		s,p,o = spo
		return (fixup2(s), fixup2(p), fixup2(o))
	rules = []
	head_triples_triples_id = 0
	kb_graph_triples = [fixup(x) for x in kb_graph.triples((None, None, None))]
	facts = Graph(Triple(un_move_me_ize_pred(fixup3(x[1])),[fixup3(x[0]),fixup3(x[2])]) for x in kb_graph_triples)
	facts.id=head_triples_triples_id
	head_triples_triples_id += 1
	for kb_graph_triple_idx,(s,p,o) in enumerate(kb_graph_triples):
		rules.append(Rule(facts, kb_graph_triple_idx, Graph()))
		if p == implies:
			body = Graph()
			head_triples = [fixup(x) for x in kb_conjunctive.triples((None, None, None, o))]
			head_triples_triples = Graph()
			for triple in [Triple(fixup3(x[1]),[fixup3(x[0]),fixup3(x[2])]) for x in head_triples]:
				move = False
				if triple.pred == URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#move_me_to_body_first'):
					triple.pred = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#first')
					move = True
				if triple.pred == URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#move_me_to_body_rest'):
					triple.pred = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#rest')
					move = True
				if move:
					body.append(triple)
				else:
					head_triples_triples.append(triple)
			head_triples_triples.id=head_triples_triples_id
			head_triples_triples_id += 1
			for body_triple in [fixup(x) for x in kb_conjunctive.triples((None, None, None, s))]:
				body.append(Triple((un_move_me_ize_pred(fixup3(body_triple[1]))), [fixup3(body_triple[0]), fixup3(body_triple[2])]))
			#body.reverse()
			to_expand = []
			for triple in head_triples_triples + body:
				for thing in triple.args:
					if type(thing) == rdflib.Variable:
						if str(thing).endswith('_'):
							to_expand.append(thing)
			for thing in to_expand:
				body.insert(0,Triple(rdflib.RDF.first, [thing, rdflib.Variable(str(thing)[:-1]+'f')]))
				body.insert(0,Triple(rdflib.RDF.rest , [thing, rdflib.Variable(str(thing)[:-1]+'r')]))
			if len(head_triples_triples) > 1:
				with open(_rules_file_name, 'a') as ru:
					ru.write(head_triples_triples.str(shorten) + " <= " + body.str(shorten) + ":\n")
			for head_triple_idx in range(len(head_triples_triples)):
				rules.append(Rule(head_triples_triples, head_triple_idx, body))

	goal_rdflib_graph = rdflib.ConjunctiveGraph(store=OrderedStore(), identifier=base)
	goal_rdflib_graph.parse(goal_stream, format='n3', publicID=base)

	if not nolog:
		log('---goal:')
		try:
			for l in goal_rdflib_graph.serialize(format='n3').splitlines():
				log(l.decode('utf8'))
		except Exception as e:
			log(str(e))
		log('---goal nq:')
		for l in goal_rdflib_graph.serialize(format='nquads').splitlines():
			log(l.decode('utf8'))
		log('---')

	goal = Graph()
	for s,p,o in [fixup(x) for x in goal_rdflib_graph.triples((None, None, None, None))]:
		goal.append(Triple(un_move_me_ize_pred(fixup3(p)), [fixup3(s), fixup3(o)]))
	#goal.reverse()
	query_rule = Rule([], None, goal)
	return rules, query_rule, goal






#import gc
#gc.set_debug(gc.DEBUG_LEAK)

#import tracemalloc
#import gc
#import objgraph
#from IPython import embed; embed();exit()
#snapshot1 = tracemalloc.take_snapshot()
#objgraph.show_growth(limit=3)

# gc.collect()
# snapshot2 = tracemalloc.take_snapshot()
# top_stats = snapshot2.compare_to(snapshot1, 'lineno')
# nolog or log("[ Top 5 differences ]")
# for stat in top_stats[:50]:
# 	nolog or log(stat)

#print("[ Top ]")
#objgraph.show_growth()
