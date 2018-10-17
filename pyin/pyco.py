# -*- coding: utf-8 -*-

"""PYthon does the input, C++ is the Output"""

import cgen
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

def generate_cpp(input_rules, input_query):
	out('#include "pyco_static.cpp"')
	for pred,rules in preds.items():
		out(pred_func_declaration(pred_name)+';')
	for pred,rules in preds.items():
		do_pred(name, rules)


def consts_of_rule(rule_index):
	return "consts_of_rule_" + str(rule_index)
								 "
def thing_expression(storage, thing_index, rule_index):
	#if (storage == INCOMING):
	#	return "state.incoming["+str(incoming_index)+']';
	if (storage == LOCAL):
		return "(&state.locals["+str(thing_index)+"])";
	if (key == CONST):
		return "(&"_consts_of_rule(rule_index) + "[" + str(thing_index)+"])";

def do_pred(pred_name, rules):
	for rule in rules:
		rule.locals_map, rule.consts_map, rule.locals_template, rule.consts = make_locals(r.head, r.body, false)
	for i, rule in emunerate(rules):
		out("/*const*/static Locals " + consts_of_rule(i) + " = " << things_literals(rule.consts))
		if len(rule.body):
			out("static ep_t ep" + str(i))
	out(pred_func_declaration(pred_name))
	max_body_len = max([len(r.body) for r in rules])
	label = 1
	out ("case" +str(label) + ":")
	label += 1
	if(max_body_len)
		out("state.states.resize(" + str(max_states_len) + ");")
	for rule in rules:
		label = do_rule(rule, label)

def do_rule(rule,label):
	PUSH = ".push_back(thingthingpair(state.s, state.o));\n";
	has_body = len(rule.body) != 0;
	lm, cm, locals_template, consts = rule.locals_map, rule.consts_map, rule.locals_template, rule.consts
	if(len(locals_template)
		out("state.locals = " + things_literals(locals_template) + ";")
	function_block = cgen.Block()
	block = function_block
	if rule.head:
		head = rule.head
		head_args_len = len(head.args)
		head_arg_infos = (find_thing(rule.head.args[arg_i], lm, cm) for arg_i in range(head_args_len))
		head_arg_storages = (x[0] for x in head_arg_infos)
		head_arg_indexes = (x[1] for x in head_arg_infos)
		head_arg_types = get_type(fetch_thing(rule.head.args[i], locals_template, consts, lm, cm)) for i in range(head_args_len)
		local_param_s = param(hsk, hsi, name, i)
		local_param_o = param(hok, hoi, name, i)
		for arg_i in range(len(head.args)):
			new_block = cgen.Block()
			block.append(new_block)
			block = new_block
			block.append(cgen.Statement(
				"state.states[" + str(arg_i) + '] = unify(' +
				'state.incoming['+str(arg_id)+'], ',
				thing_expression(head_arg_storages[arg_id], rule_index)
			block.append(cgen.Line('while unify_coro(&state.states[' + str(arg_i) + ']))'))
	inner_block = block
	if (has_body):
		block.append(cgen.Line("if (!cppout_find_ep(&ep"+str(i)+", &state.incomings))"))
		new_inner_block = cgen.Block()
		inner_block.append(new_inner_block)
		inner_block = new_inner_block
		inner_block.append(cgen.Line("ep" +str(i)+ PUSH))
		inner_block.append(cgen.Statement("state.entry = " +str(label)))
		create_bnode_block(inner_block)


def emit_unification(block, a, b, state_index):
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
				emit_unification(inner_block, 'bnode['+get_local_index(arg)+']',





			for local in rule.locals:
				new_inner_block = cgen.Block()
				inner_block.append(new_inner_block)
				inner_block = new_inner_block
				inner_block.append(






		//if it's the query or a kb rule with non-empty body: (existing?)
		if(has_body) {
			size_t j = 0;
			for (pquad bi: *rule.body) {
				out << "//body item" << j << "\n";
				out << "entry" << j << " = 0;\n";

				stringstream ss;
				ss << "state.states[" << j << "]";
				string substate = ss.str();



				//set up the subject and object
				pos_t i1, i2; //positions
				nodeid s = dict[bi->subj];
				nodeid o = dict[bi->object];
				PredParam sk, ok;
				sk = find_thing(s, i1, lm, cm);
				ok = find_thing(o, i2, lm, cm);
				ThingType bist = get_type(fetch_thing(s, locals_template, consts, lm, cm));
				ThingType biot = get_type(fetch_thing(o, locals_template, consts, lm, cm));


				out << substate << ".s = " <<
					maybe_getval(bist, param(sk, i1, name, i)) << ";\n";
				out << substate << ".o = " <<
					maybe_getval(biot, param(ok, i2, name, i)) << ";\n";

				out << "do{\n";

				if (has(rules, dict[bi->pred]))
					out << "entry" << j << "=" << predname(dict[bi->pred]) << "(" << substate << ", entry" << j << ");\n";
				else
					out << "entry" << j << " = -1;\n";

				out << "if(" << "entry" << j << " == -1) break;\n";
				j++;
			}
		}

		if (name == "cppout_query") {
		//would be nice to also write out the head of the rule, and do this for all rules, not just query
			out << "{";



			if (rule.body->size() == 1)
			{


				pquad bi = (*rule.body).front();
				pos_t i1, i2;//s and o positions
				nodeid s = dict[bi->subj];
				nodeid o = dict[bi->object];
				PredParam sk, ok;
				sk = find_thing(s, i1, lm, cm);
				ok = find_thing(o, i2, lm, cm);
				out << "Thing * bisx, * biox;\n";
				out << "bisx = getValue(" << param(sk, i1, name, i) << ");\n";
				out << "biox = getValue(" << param(ok, i2, name, i) << ");\n";


					out << "if(prev_results.size() == 2){";
out << "	if (are_equal(prev_results[0], *bisx) && are_equal(prev_results[1], *biox) && (counter % 1024))goto skip;";
					out << "	prev_results[0] = *bisx;      prev_results[1] = *biox;}";
					out << "else {prev_results.push_back(*bisx);prev_results.push_back(*biox);}";
			}




			out << "if (!silent) dout << unifys << \" unifys \"  ;\n";
			out << "if (!silent) dout << \" RESULT \" << counter << \": \";\n";

			ASSERT(rule.body);

			for (pquad bi: *rule.body) {

				pos_t i1, i2;//s and o positions
				nodeid s = dict[bi->subj];
				nodeid o = dict[bi->object];
				PredParam sk, ok;
				sk = find_thing(s, i1, lm, cm);
				ok = find_thing(o, i2, lm, cm);
				out << "{Thing * bis, * bio;\n";
				out << "bis = getValue(" << param(sk, i1, name, i) << ");\n";
				out << "bio = getValue(" << param(ok, i2, name, i) << ");\n";

				out << "Thing n1; if (is_unbound(*bis)) {bis = &n1; n1 = create_node(" << ensure_cppdict(dict[bi->subj]) << ");};\n";
				out << "Thing n2; if (is_unbound(*bio)) {bio = &n2; n2 = create_node(" << ensure_cppdict(dict[bi->object]) << ");};\n";

				out << "if (!silent) dout << str(bis) << \" " << bi->pred->tostring() << " \" << str(bio) << \".\";};\n";

			}
			out << "if (!silent) dout << \"\\n\";}\n";

			out << "skip:;";


		}



		if (name == "cppout_query")
			out << "counter++;\n";


		if (rule.head && has_body) {
			out << "ASSERT(ep" << i << ".size());\n ep" << i << ".pop_back();\n\n";
		}


		/*mm keeping entry on stack for as long as the func is running
		is a good thing, (unless we start jumping into funcs and need to avoid
		any stack state), but we shouldnt save and restore entry's en masse
		around yield, but right after a pred func call returns.
		i think theres anyway not much to be gained from this except the
		top query function doesnt have to do the stores and loads at all
		..except maybe some memory traffic saving?*/
		if(has_body) {
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



