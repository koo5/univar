# -*- coding: utf-8 -*-

"""PYthon does the input, C++ is the Output"""

from cgen import *
Lines = Collection

from weakref import ref as weakref
from rdflib import URIRef
import rdflib
import sys
import os
import logging
try:
	from urllib.parse import quote_plus
except ImportError:
	from urllib import quote_plus
from collections import defaultdict, OrderedDict
from common import shorten#, traverse, join_generators
from time import sleep
from common import pyin_prefixes as prefixes

nolog = False
kbdbg_prefix = URIRef('http://kbd.bg/#')
log, kbdbg_text = 666,666
pool = None
futures = []

if sys.version_info.major == 3:
	unicode = str

def pred_func_declaration(pred_name):
	return "static " + pred_name + "(cpppred_state & __restrict__ state)"

def consts_of_rule(rule_index):
	return "consts_of_rule_" + str(rule_index)

def thing_expression(storage, thing_index, rule_index):
	#if (storage == INCOMING):
	#	return "state.incoming["+str(incoming_index)+']';
	if (storage == LOCAL):
		return "(&state.locals["+str(thing_index)+"])";
	if (key == CONST):
		return "(&"_consts_of_rule(rule_index) + "[" + str(thing_index)+"])";


class Emitter(object):
	@staticmethod
	def push_ep(rule):
		return Statement('ep'+str(rule.debug_id)+".push_back(thingthingpair(state.incoming[0], state.incoming[1]))")

	def label(s):
		s.label += 1
		return Line("case" +str(s.label) + ":")



	def generate_cpp(input_rules, input_query):
		for pred,rules in preds.items():
			for rule in rules:
				rule.locals_map, rule.consts_map, rule.locals_template, rule.consts = make_locals(rule)
				rule.has_body = len(rule.body) != 0

		print(Module([
			Line('#include "pyco_static.cpp"'),
			Lines(Statement("static ep_t ep" + str(i)) for rule in rules),
			Lines([Statement(pred_func_declaration(pred_name))) for pred_name in preds.keys()]),
			Lines([s.pred(pred, rules) for pred,rules in preds.items()])
		]))

	def pred(s, pred_name, rules):
		s.label = -1
		max_body_len = max(len(r.body) for r in rules)
		max_states_len = max(r.max_states_len for r in rules)
		return Collection(
			Lines([Statement("/*const*/static Locals " + consts_of_rule(rule.debug_id) + " = " + things_literals(rule.consts)) for rule in rules]),
			Line(pred_func_declaration(pred_name)),
			Block(
				Statement('goto case'+str(state.entry),
				s.label(),
				Statement("state.states.resize(" + str(max_states_len) + ")") if max_states_len else Line()
				Lines(s.rule(rule) for rule in rules))
		)

	def rule0(r):
		return Lines([
			Statement("state.locals = " + things_literals(r.locals_template)) if len(r.locals_template) else Line(),
			s.rule1(r)
			])

	def rule1(s, r):
		b = Block()
		if r.head:
			r.head_args_len = len(head.args)
			head_arg_infos = (find_thing(rule.head.args[arg_i], lm, cm) for arg_i in range(head_args_len))
			r.head_arg_storages = (x[0] for x in head_arg_infos)
			r.head_arg_indexes = (x[1] for x in head_arg_infos)
			r.head_arg_types = get_type(fetch_thing(rule.head.args[i], locals_template, consts, lm, cm)) for i in range(head_args_len)
			local_param_s = param(hsk, hsi, name, i)
			local_param_o = param(hok, hoi, name, i)
			for arg_i in range(len(head.args)):
				b.append(unify(
					'state.incoming['+str(arg_i)+'], ',
					thing_expression(head_arg_storages[arg_i], rule.debug_id)))
				b = nest(b)
		if (has_body):
			b.append(Line("if (!cppout_find_ep(&ep"+str(i)+", &state.incomings))"))
			b = nest(b)
			b.append(push_ep(r))
			create_bnode_block(inner_block)


def unify(block, a, b, state_index):
	block.append(cgen.Statement(
		"state.states[" + str(state_index) + '] = unify(' + a + ',' + b + ')'))
	block.append(cgen.Line('while unify_coro(&state.states[' + str(state_index) + ']))'))


def create_bnode_block(inner_block):
	for arg in head.args:
		if arg in rule.existentials:
			local = find_local(arg)
			inner_block.append(cgen.Statement(
				'Thing vv = get_value('+local+')')
			inner_block.append(cgen.Line(
				'if ((vv != v) && (vv.type() == BNODE) && (vv.origin == '+get_origin(rule,arg)+'))')
			inner_block = nest(inner_block)
			inner_block.append(cgen.Statement("Locals *bnode = vv.locals"))
			for local in locals:
				emit_unification(inner_block, 'bnode['+get_local_index(arg)+']',)
				inner_block = nest(inner_block)


def do_label(s):
	s.block.append(cgen.Statement('entry'))

def do_body(rule, block):
	for triple_index, triple in enumerate(rule.body):
		inner_block.append(cgen.Statement('//body item ' +str(j)+)
		substate_expr = "state.states[" +str(j) + "]"

		pos_t i1, i2; //positions
		nodeid s = dict[bi->subj];
		nodeid o = dict[bi->object];
		PredParam sk, ok;
		sk = find_thing(s, i1, lm, cm);
		ok = find_thing(o, i2, lm, cm);
		ThingType bist = get_type(fetch_thing(s, locals_template, consts, lm, cm));
		ThingType biot = get_type(fetch_thing(o, locals_template, consts, lm, cm));

		for arg_idx in range(len(triple.args)):
			s.statement(substate + ".incoming["+str(arg_idx)+"] = " +
				maybe_getval(bist, param(sk, i1, name, i)) << ";\n";

		out << "do{\n";

				if (has(rules, dict[bi->pred]))
					out << "entry" << j << "=" << predname(dict[bi->pred]) << "(" << substate << ", entry" << j << ");\n";
				else
					out << "entry" << j << " = -1;\n";

				out << "if(" << "entry" << j << " == -1) break;\n";
				j++;
			}
		}

		if (rule.head and has_body):
			s.statement("ASSERT(ep" +str(rule_index)+ ".size());ep" +str(rule_index)+ ".pop_back()")
		if(has_body):
			size_t j = 0;
			for (pquad bi: *rule.body) {
				stringstream ss;
				ss << "state.states[" << j << "]";
				string substate = ss.str();
				out << substate << ".entry = " << "entry" << j++ << ";\n";
			}
		}


		out << "return entry;\n";
		out << "case " << label++ << ":;\n";


		if(has_body) {
			size_t j = 0;
			for (pquad bi: *rule.body) {
				stringstream ss;
				ss << "state.states[" << j << "]";
				string substate = ss.str();
				out << "entry" << j++ << " = " << substate << ".entry;\n";
			}
		}


		if (rule.head && has_body) {
			out << "ep" << i << PUSH;
		}

		if(rule.body)
			for (pos_t closing = 0; closing < rule.body->size(); closing++)
				out << "}while(true);\n";

		if (rule.head && has_body)
			out << "ASSERT(ep" << i << ".size());\nep" << i << ".pop_back();\n}\n";

		if (rule.head) {
			if (hot == NODE)
				out << "unbind_from_const(state.o);\n";
			else if (hot == UNBOUND)
				out << "unbind_from_var(state.ou.magic, state.o, " << param(hok, hoi, name, i) << ");\n";
			else
				out << "state.ou.c();//unbind\n";
			out << "}\n";
			if (hst == NODE)
				out << "unbind_from_const(state.s);\n";
			else if (hst == UNBOUND)
				out << "unbind_from_var(state.su.magic, state.s, " << param(hsk, hsi, name, i) << ");\n";
			else
				out << "state.su.c();//unbind\n";
			out << "}\n";
		}
		i++;
	}
	out << "}return -1;}\n\n";
}









if do_builtins:
	add_builtins()







#http://www.cplusplus.com/reference/thread/thread/
#smil svg or different animations


def add_builtins():
	global builtins
	builtins = []

	out.write(
"""
//#include <string>
""")

	_builtins = (
	(
"""
(input)"x" is a substring of (input)"xyx" spanning from position (input)0 to position (input)0.
""",
"""
"x" string_builtins:is_a_substring_of ("xyx" 0 0).
""",
"""
Thing result_thing;
""",
"""
o_list = get_list_items_values(o);
hay = o_list[0].const_value();
state.result_thing = new_const_thing(str.substr (o_list[1],o_list[2]));
while (unify(state.args[0], state.result_thing))
	yield;
"""
	),)

	for doc,example,state,code in _builtins:
		g = rdflib.Graph(store=OrderedStore())
		g.bind("string_builtins", "file://autonomic.net")
		g.parse(example)
		_,predicate,_ = list(g.triples((None,None,None)))[0]
		cpp_name = predicate.replace(':','__')
		builtins[predicate] = cpp_name
		out.write("""
		void {cpp_name}(coro_state *state_ptr)
		{{
			coro_state &state = *state_ptr;
			Thing s;
			Thing o;
			
			goto state.entry;
			l0:
				s = get_value(state.args[0]);
				o = get_value(state.args[1]);
				
				
				
			{body}
		
		
		}}	
		
		"""



string maybe_getval(ThingType t, string what)
{
	stringstream ss;
	bool yes = (t != NODE);
	if (yes)
		ss << "getValue_nooffset(";
	ss << what;
	if (yes)
		ss << ")";
	return ss.str();
}





