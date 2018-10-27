# -*- coding: utf-8 -*-

"""PYthon does the input, C++ is the Output
we use pyin for the Rule class to hold data, and for various bits of shared code

"""

import click
from cgen import *
Lines = Collection
import sys
import common
import pyco_builtins
import pyin
from collections import defaultdict, OrderedDict
import rdflib

if sys.version_info.major == 3:
	unicode = str

codes = list()
def string2code(atom):
	atom = str(atom.value)
	if atom in codes:
		return codes
	result = len(codes)
	codes.append(result)
	return result

def make_locals(rule):
		locals_template = []
		consts = []
		locals_map = {}
		consts_map = {}
		for triple in ([rule.head] if rule.head else []) + rule.body:
			for a in triple.args:
				if pyin.is_var(a):
					locals_map[a] = len(locals_template)
					v = pyin.Var(a)
					v.is_bnode = v in rule.existentials
					locals_template.append(v)

				else:
					consts_map[a] = len(consts)
					consts.append(pyin.Atom(a))
		return locals_map, consts_map, locals_template,	consts

def vars_in_original_head(rule):
	result = set()
	for triple in rule.original_head_triples:
		for a in triple.args:
			if pyin.is_var(a):
				result.add(a)
	return result

def max_number_of_existentials_in_single_original_head_triple(rule):
	return max([len([a for a in triple.args if a in rule.existentials]) for triple in rule.original_head_triples])



class Emitter(object):
	do_builtins = False

	def things_literals(s, things):
		r = '['
		for i, thing in enumerate(things):
			r += s.thing_literal(thing)
			if i != len(things) -1:
				r += ','
		r += ']'
		return r

	def thing_literal(s, thing):
		#UNBOUND, CONST, BOUND_BNODE, UNBOUND_BNODE
		if type(thing) == pyin.Var and not thing.is_bnode:
			t = 'UNBOUND'
		elif type(thing) == pyin.Atom:
			t = 'CONST'
		elif thing.is_bnode:
			t = 'UNBOUND_BNODE'
		else: assert False

		if type(thing) == pyin.Atom:
			v = s.emit_const(thing)#+'/*'+str(string2code(thing))+'*/'
		else:
			v = '0'
		return '{' + t + ',' + v + ',0}'

	def emit_const(s,thing):
		code = str(string2code(thing))
		cpp_name = cppize_identifier(str(thing.value))
		s.prologue.append(Statement('static const unsigned '+cpp_name+' = '+code))
		return cpp_name

	def label(s):
		#s.state_index = 0
		return Line("case" +str(s._label) + ":")

	def generate_cpp(s, input_rules, input_query):
		s.prologue = Lines()

		if s.do_builtins:
			pyco_builtins.add_builtins()

		for pred,rules in preds.items():
			for rule in rules:
				rule.locals_map, rule.consts_map, rule.locals_template, rule.consts = make_locals(rule)
				rule.has_body = len(rule.body) != 0
				rule.max_states_len = len(rule.head.args) + max(
					len(rule.body),
					len(vars_in_original_head(rule)) * max_number_of_existentials_in_single_original_head_triple(rule))

		print('#include "pyco_static.cpp"')
		r = Module([
			Lines([
				Statement(
					"static ep_t ep" + str(rule.debug_id)
				) for rule in rules
			]),
			Lines([Statement(pred_func_declaration(pred_name)) for pred_name in preds.keys()]),
			Lines([s.pred(pred, rules) for pred,rules in preds.items()])
		])
		print(s.prologue)
		print(r)


	def pred(s, pred_name, rules):
		s._label = 0
		s.state_index = 0
		max_body_len = max(len(r.body) for r in rules)
		max_states_len = max(r.max_states_len for r in rules)
		return Collection([
			Comment(pred_name),
			Lines(
				[Statement("static Locals " + consts_of_rule(rule.debug_id) + " = " + s.things_literals(rule.consts)) for rule in rules] #/*const*/
			),
			Line(
				pred_func_declaration(pred_name)
			),
			Block(
				[
					Statement('goto case0 + state.entry'),
					s.label(),
					(Statement("state.states.resize(" + str(max_states_len) + ")") if max_states_len else Line()),
					Lines([s.rule(rule) for rule in rules])
				]
			)
		])

	def rule(s, r):
		outer_block = b = Lines()
		b.append(Comment((r)))
		if len(r.locals_template):
			b.append(Statement("state.locals = " + s.things_literals(r.locals_template)))
		if r.head:
			b = s.head(b, r)
		b.append(s.incoming_bnode_block(r))
		b.append(s.body_triples_block(r))
		return outer_block

	def head(s, b, r):
		r.head_args_len = len(r.head.args)
		head_arg_infos = (find_thing(rule.head.args[arg_i], lm, cm) for arg_i in range(r.head_args_len))
		r.head_arg_storages = (x[0] for x in head_arg_infos)
		r.head_arg_indexes = (x[1] for x in head_arg_infos)
		r.head_arg_types = (
			get_type
			(
				fetch_thing
				(
					rule.head.args[i], locals_template, consts, lm, cm
				)
			)
			for i in range(r.head_args_len))
		for arg_i in range(len(r.head.args)):
			name_of_local = r.head.args[arg_i]
			b.append(Comment(name_of_local)),
			b.append(s.unify(
				'&state.incoming['+str(arg_i)+']',
				'&'+local_expr(name_of_local, r)))
			b = nest(b)
		return b

	def unify(s, a, b):
		r = Lines([
			Statement("state.states[" + str(s.state_index) + '] = unify(' + a + ',' + b + ')'),
			Line('while unify_coro(&state.states[' + str(s.state_index) + ']))')])
		s.state_index += 1
		return r

	def body_triples_block(s, r):
		do_ep = (r.head and r.has_body)
		outer_block = b = Lines()
		b.append(Line("if (!cppout_find_ep(&ep"+str(r.debug_id)+", &state.incomings))"))
		b = nest(b)
		if do_ep:
			b.append(push_ep(r))
		for body_triple_index, triple in enumerate(r.body):
			if triple.pred in preds:
				b = s.nest_body_triple_block(r, b, body_triple_index, triple)
		if do_ep:
			b.append(Lines([
				Statement("ASSERT(ep" +str(r.debug_id)+ ".size())'"),
				Statement("ep" +str(r.debug_id)+ ".pop_back()")]))
		b.append(s.do_yield())
		if do_ep:
			b.append(push_ep(r))
		return outer_block

	def nest_body_triple_block(s, r, b, body_triple_index, triple):
		b.append(Comment(triple.str()))
		substate = "state.states["+str(s.state_index)+"]"
		for arg_idx in range(len(triple.args)):
			arg = triple.args[arg_idx]
			b.append(Statement(
				substate + ".incoming["+str(arg_idx)+"]=&"+local_expr(arg, r)))
		b.append(Statement(substate + ".entry = 0"))
		b.append(Line('while('+cppize_identifier(triple.pred) +'(&'+ substate+')'+'!=-1)'))
		b = nest(b)
		return b


	def do_yield(s):
			return Lines(
				[
					s.set_entry(),
					Statement('return state.entry'),
					s.label()
				]
			)

	def do_end(s):
			return Lines(
				[
					Statement('state.entry = -1'),
					Statement('return state.entry'),
				]
			)

	def incoming_bnode_block(s,r):
		b = Lines()
		to_check = [arg for arg in r.head.args if arg in r.existentials]
		if len(to_check) > 1:
			raise Exception("too many existentials")
		if len(to_check):
			b.append(Statement('Thing *local, *value'))
			for arg in to_check:
				b.append(Statement('local = ' + '&'+local_expr(arg, r)))
				b.append(Statement('value = get_value(local)'))
				#b.append(If('(value != local) && (value.type == BNODE) && (value.origin == '+get_origin(rule,arg)+')',
				#			s.incoming_bnode_unifications(r)))
		return b

	def incoming_bnode_unifications(s, r):
		outer_block = b = Block()
		b.append(Statement("Locals *bnode = value.locals"))
		for key, index in r.locals_template.items():
			index = str(index)
			unify('&value['+index+']','&state.locals['+index+']')
			b = nest(b)
			b.append(s.do_yield())
		outer_block.append(s.end())
		return outer_block

	def set_entry(s):
		s._label += 1
		r = Statement('state.entry = case' + str(s._label))
		return r


def local_expr(name, rule):
	if name in rule.locals_map:
		return 'state.locals[' + str(rule.locals_map[name]) + ']'
	elif name in rule.consts_map:
		return consts_of_rule(rule.debug_id) + '[' + str(rule.consts_map[name])+']'

def maybe_getval(t, what):
	"""
	wrap what in get_value() if t != NONE
	"""
	r = ''
	yes = (t != NODE)
	if (yes):
		r += "get_value("
	r += what
	if (yes):
		r += ")"
	return r

def cppize_identifier(i):
	return common.fix_up_identification(common.shorten(i))

def pred_func_declaration(pred_name):
	pred_name = cppize_identifier(pred_name)
	return "static " + pred_name + "(cpppred_state & __restrict__ state)"

def consts_of_rule(rule_index):
	return "consts_of_rule_" + str(rule_index)

def thing_expression(storage, thing_index, rule_index):
	#if (storage == INCOMING):
	#	return "state.incoming["+str(incoming_index)+']';
	if (storage == LOCAL):
		return "(&state.locals["+str(thing_index)+"])"
	if (key == CONST):
		return "(&_consts_of_rule(rule_index)" + "[" + str(thing_index)+"])"

def push_ep(rule):
	return Statement('ep'+str(rule.debug_id)+".push_back(thingthingpair(state.incoming[0], state.incoming[1]))")


def nest(block):
	b = Block()
	block.append(b)
	return b


@click.command()
@click.argument('kb', type=click.File('rb'))
@click.argument('goal', type=click.File('rb'))
@click.option('--identification', default="")
@click.option('--base', default="")
def query_from_files(kb, goal, identification, base):
	global preds
	preds = defaultdict(list)
	pyin.kbdbg_file_name, pyin._rules_file_name, identification, base, this = pyin.set_up(True, identification, base)
	pyin.init_logging()
	common.log = pyin.log
	rules, goal = pyin.load(kb, goal, identification, base)
	for rule in rules:
		preds[rule.head.pred].append(rule)

	e = Emitter()
	e.generate_cpp(rules, goal)


if __name__ == "__main__":
	query_from_files()





"""
todo:
consts can be globals, one for each const, no need for per-rule arrays 


"""
