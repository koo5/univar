# -*- coding: utf-8 -*-

"""PYthon does the input, C++ is the Output
we use pyin for the Rule class to hold data, and for various bits of shared code

"""


from cgen import *
#Module and Collection are both just a bunch of lines, but more appropriate name for my use is...
Lines = Collection

import click
import sys, os
import common
import pyco_builtins
import pyin
from collections import defaultdict, OrderedDict
import memoized
import rdflib

if sys.version_info.major == 3:
	unicode = str

def make_locals(rule):
	locals_template = []
	consts = []
	locals_map = {}
	consts_map = {}
	for triple in rule.original_head_triples + rule.body:
		for a in triple.args:
			if pyin.is_var(a):
				if a not in locals_map:
					locals_map[a] = len(locals_template)
					v = pyin.Var(a)
					v.is_bnode = a in rule.existentials
					locals_template.append(v)
			else:
				if a not in consts_map:
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
	codes = OrderedDict()
	bnode_origin_counter = 0

	@memoized.memoized
	def get_bnode_origin(s, orig_rule_id, name):
		global bnode_origin_counter
		assert(type(name) == str)
		r = 'r'+str(orig_rule_id)+'bn'+cppize_identifier(name)
		s.prologue.append(Statement('static const BnodeOrigin '+r+' = '+str(s.bnode_origin_counter)))
		s.bnode_origin_counter += 1
		return r

	def string2code(s,a):
		codes = s.codes
		atom = str(a.value)
		if atom in codes:
			return codes[atom][1]
		code = str(len(codes))
		cpp_name = cppize_identifier(atom)
		s.prologue.append(Statement('static const unsigned '+cpp_name+' = '+code))
		kind = "URI" if type(a.value) == rdflib.URIRef else "STRING"
		codes[atom] = kind,cpp_name, code
		return cpp_name

	def get_prologue(s):
		return Lines([
			s.prologue,
			Statement('vector<Constant> strings {' + ",".join(
				['Constant('+kind+',"'+string+'")' for string,(kind,_,_) in s.codes.items()]
			) + '}')])


	def things_literals(s, rule, things):
		result = '{'
		for i, thing in enumerate(things):
			result += s.thing_literal(rule, thing)
			if i != len(things) -1:
				result += ',\n'
		result += '}'
		return result

	def thing_literal(s, r, thing):
		if type(thing) == pyin.Var and not thing.is_bnode:
			t = 'UNBOUND'
			v = '.binding = (Thing*)0'
		elif type(thing) == pyin.Atom:
			t = 'CONST'
			v = '.string_id = ' + s.string2code(thing)
		elif thing.is_bnode:
			t = 'BNODE'
			v = ".origin = " + s.get_bnode_origin(r.original_head_ref.id, str(thing.debug_name))
		return 'Thing{' + t + ',' + v + '}'

	def label(s):
		return Line("case" +str(s._label) + ":;")

	def generate_cpp(s, goal, goal_graph):
		s.prologue = Lines()
		s.prologue.append(Line('#include "pyin/pyco_static.cpp"'))
		if s.do_builtins:
			pyco_builtins.add_builtins()
		all_rules = []
		for pred,rules in preds.items():
			all_rules.extend(rules)
		all_rules.append(goal)
		for rule in all_rules:
			rule.locals_map, rule.consts_map, rule.locals_template, rule.consts = make_locals(rule)
			rule.has_body = len(rule.body) != 0
			""" so, the cpppred_state struct has a vector of states,
			used for both head-unification and for calling other rules,
			so this is the number of generators that this rule will need at once, at most"""
			rule.max_states_len = (len(rule.head.args) if rule.head else 0) + len(rule.body)
			#put under "with_assert" ? running python with -O would do that
			assert not rule.head or (len(rule.head.args) == 2)
			#gotcha; is args just the vars? no its args in the meaning of term with args
		del pred,rules,rule
		r = Module(
		[
			Lines([
				Statement(
					"static ep_table ep" + str(rule.debug_id)
				) for rule in all_rules if rule != goal]),
			Lines([Statement(pred_func_declaration('pred_'+pred_name)+"__attribute__ ((unused))")
				   for pred_name in preds.keys()]),
			Lines([s.pred(pred, rules) for pred,rules in list(preds.items()) + [[None, [goal]]]]),
			s.print_result(goal, goal_graph)
		])
		return str(s.get_prologue()) + '\n' + str(r)

	def substituted_arg(s, r, arg):
		if type(arg) == rdflib.Literal:
			return Statement('cout << "\\\\"' + str(arg) +'\\\\" "')
		if type(arg) == rdflib.URIRef:
			return Statement('cout << "<' + str(arg) +'> "')
		if type(arg) == rdflib.Variable:
			return Lines([
				Statement('v = get_value(&state.locals['+str(r.locals_map[arg])+'])'),
				If('v->type == CONST',
					If ('strings[v->string_id].first == URI',
						Statement('cout <<  "<" << strings[v->string_id].second << "> "'),
						Statement('cout << "\\"" << strings[v->string_id].second << "\\" "')
					),
					Statement('cout << "?' + str(arg) +' "'))
				])
		else: ararrr


	def print_result(s, r, goal_graph):
		outer_block = b = Lines()
		b.append(Line('void print_result(cpppred_state &state)'))
		b = nest(b)
		b.append(Statement('cout << " RESULT : "'))
		b.append(Statement('Thing *v;(void)v'))
		for term in goal_graph:
			b.append(s.substituted_arg(r, term.args[0]))
			b.append(Statement('cout << "<' + str(term.pred) + '> "'))
			b.append(s.substituted_arg(r, term.args[1]))
			b.append(Statement('cout << ". "'))
		b.append(Statement('cout << endl'))
		return outer_block

	def pred(s, pred_name, rules):
		s._label = 0
		s.state_index = 0
		max_body_len = max(len(r.body) for r in rules)
		max_states_len = max(r.max_states_len for r in rules)
		return Collection([
			Comment(pred_name if pred_name else 'query'),
			Lines(
				[Statement("static Locals " + consts_of_rule(rule.debug_id) + s.things_literals(666, rule.consts)) for rule in rules] #/*const*/
			),
			Line(
				pred_func_declaration(('pred_'+pred_name) if pred_name else 'query')
			),
			Block(
				[
					Statement('goto *(((char*)&&case0) + state.entry)'),
					s.label(),
					(Statement("state.states.resize(" + str(max_states_len) + ")") if max_states_len else Line()),
					Lines([s.rule(rule) for rule in rules]),
					Statement('return 0')
				]
			)
		])

	def rule(s, r):
		if len(r.existentials) > 1:
			raise Exception("too many existentials in " + str(r) +" : " + str(r.existentials))
		outer_block = b = Lines()
		b.append(Comment((r)))
		if len(r.locals_template):
			b.append(Statement("state.locals = " + s.things_literals(r, r.locals_template)))
		if r.head:
			b = s.head(b, r)
		else:
			b.append(s.body_triples_block(r))
		return outer_block

	def head(s, b, r):
		outer_block = b
		todo = []
		for arg_i, arg in enumerate(r.head.args):
			if arg in r.existentials:
				todo.append((arg_i, arg))
		for arg_i, arg in enumerate(r.head.args):
			if arg not in r.existentials:
				todo.append((arg_i, arg))
		for arg_i, arg in todo:
			other_arg_idx, other_arg = todo[1]
			arg_expr = 'state.incoming['+str(arg_i)+']'
			other_arg_expr = 'state.incoming['+str(other_arg_idx)+']'
			if arg in r.existentials:
				b.append(Line("if (*get_value("+arg_expr+") == "+s.thing_literal(r, r.locals_template[r.locals_map[arg]	])+")"))
				b = nest(b)
				if other_arg in r.locals_map:
					b.append(s.unify('state.incoming['+str(other_arg_idx)+']', '('+str(r.locals_map[other_arg]-r.locals_map[arg])+')+get_value('+arg_expr+')'))
				else:
					b.append(s.unify('state.incoming['+str(arg_i)+']', '(&'+local_expr(other_arg, r)+')'))
				b = nest(b)
				b.append(s.do_yield())
				outer_block.append(Line('else'))
				b = nest(outer_block)
		s.state_index = 0
		for arg_i, arg in enumerate(r.head.args):
			b.append(Comment(arg))
			b.append(s.unify(
				'(state.incoming['+str(arg_i)+'])',
				'&('+local_expr(arg, r)+')'))
			b = nest(b)
		b.append(s.body_triples_block(r))
		return outer_block

	def unify(s, a, b):
		r = Lines([
			Statement("state.states[" + str(s.state_index) + '].entry = 0'),
			Statement("state.states[" + str(s.state_index) + '].incoming[0] = get_value('+a+')'),
			Statement("state.states[" + str(s.state_index) + '].incoming[1] = get_value('+b+')'),
			Line('while(unify(state.states[' + str(s.state_index) + ']))')])
		s.state_index += 1
		return r

	def body_triples_block(s, r):
		dont_yield = False
		do_ep = (r.head and r.has_body)
		outer_block = b = Lines()
		if do_ep:
			b.append(Statement("state.ep = ep_head(*get_value(state.incoming[0]), *get_value(state.incoming[1]))"))
			b.append(Line("if (!find_ep(&ep"+str(r.debug_id)+", state.ep))"))
			inner_block = b = nest(b)
			b.append(push_ep(r))
		for body_triple_index, triple in enumerate(r.body):
			if triple.pred in preds:
				b = s.nest_body_triple_block(r, b, body_triple_index, triple)
			else:
				dont_yield = True
				break
		if not dont_yield:
			if do_ep:
				b.append(Lines([
					Statement("ASSERT(ep" +str(r.debug_id)+ ".size())"),
					Statement("ep" +str(r.debug_id)+ ".pop_back()")]))
			b.append(s.do_yield())
			if do_ep:
				b.append(push_ep(r))
				inner_block.append(Statement("ep" +str(r.debug_id)+ ".pop_back()"))
		return outer_block

	def nest_body_triple_block(s, r, b, body_triple_index, triple):
		b.append(Comment(triple.str()))
		substate = "state.states["+str(s.state_index)+"]"
		for arg_idx in range(len(triple.args)):
			arg = triple.args[arg_idx]
			b.append(Statement(
				substate + ".incoming["+str(arg_idx)+"]=get_value(&"+local_expr(arg, r)+')'))
		b.append(Statement(substate + ".entry = 0"))
		b.append(Line('while('+cppize_identifier('pred_'+triple.pred) +'('+ substate+')'+'!=0)'))
		b = nest(b)
		s.state_index += 1
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

	def set_entry(s):
		s._label += 1
		r = Statement('state.entry = ((char*)&&case' + str(s._label) + ') - ((char*)&&case0)')
		return r


def local_expr(name, rule):
	if name in rule.locals_map:
		return 'state.locals[' + str(rule.locals_map[name]) + ']'
	elif name in rule.consts_map:
		return consts_of_rule(rule.debug_id) + '[' + str(rule.consts_map[name])+']'

def maybe_get_value(t, what):
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


def cppize_identifier(i: str) -> str:
	return common.fix_up_identification(common.shorten(i))

#String -> String
def pred_func_declaration(pred_name):
	pred_name = cppize_identifier(pred_name)
	return "static size_t " + pred_name + "(cpppred_state & __restrict__ state)"

def consts_of_rule(rule_index):
	return "consts_of_rule_" + str(rule_index)

def push_ep(rule):
	return Statement('ep'+str(rule.debug_id)+".push_back(state.ep)")


def nest(block):
	b = Block()
	block.append(b)
	return b


@click.command()
@click.argument('kb', type=click.File('rb'))
@click.argument('goal', type=click.File('rb'))
@click.option('--identification', default="")
@click.option('--base', default="")
@click.option('--nolog', default=False, type=bool)
def query_from_files(kb, goal, identification, base, nolog):
	global preds
	preds = defaultdict(list)
	pyin.kbdbg_file_name, pyin._rules_file_name, identification, base, this = pyin.set_up(True, identification, base)
	pyin.nolog = nolog
	pyin.init_logging()
	common.log = pyin.log
	rules, query_rule, goal_graph = pyin.load(kb, goal, identification, base)
	for rule in rules:
		preds[rule.head.pred].append(rule)

	e = Emitter()
	open("pyco_out.cpp", "w").write(e.generate_cpp(query_rule, goal_graph))
	os.system("make pyco")
	print("#ok lets run this")
	sys.stdout.flush()
	os.system("valgrind ./pyco")

if __name__ == "__main__":
	query_from_files()





