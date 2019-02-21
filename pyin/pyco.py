# -*- coding: utf-8 -*-

"""PYthon does the input, C++ is the Output
we use pyin for the Rule class to hold data, and for various bits of shared code

"""


from cgen import *
Lines = Collection #both Module and Collection are just a bunch of lines

def nest(block):
	b = Block()
	block.append(b)
	return b


import click
import sys
import common
import pyin
from collections import defaultdict, OrderedDict
import memoized


import rdflib
from rdflib.plugins.parsers import notation3
notation3.RDFSink.newList = common.newList


import subprocess
from ordered_rdflib_store import OrderedStore

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

	codes = OrderedDict()
	bnode_origin_counter = 0
	bnodes = {}
	prologue = Lines()
	epilogue = Lines()

	@memoized.memoized
	def add_bnode(s, rule, name):
		cpp_name = s.get_bnode_origin(rule.original_head_ref.id, str(name))
		s.bnodes[cpp_name] = rule, name
		return cpp_name

	@memoized.memoized
	def get_bnode_origin(s, orig_rule_id, name):
		global bnode_origin_counter
		assert(type(name) == str)
		r = 'r'+str(orig_rule_id)+'bn'+cppize_identifier(name)
		s.prologue.append(Statement('static const BnodeOrigin '+r+' = '+str(s.bnode_origin_counter)))
		s.bnode_origin_counter += 1
		return r

	def thing2code(s,atom):
		if atom in s.codes:
			return s.codes[atom][1]
		cpp_name = 'const_'
		if type(atom) == rdflib.URIRef:
			cpp_name += 'uri_'
		elif type(atom) == rdflib.Literal:
			cpp_name += 'lit_'
		else: assert False, atom
		cpp_name += cppize_identifier(str(atom))
		while s.find_code_by_cppname(cpp_name) is not None:
			cpp_name += "2"
		if type(atom) == rdflib.URIRef:
			kind = "URI"
		else:
			for atom2, (kind2,cpp_name2, code2) in s.codes.items():
				if kind2 != "URI":
					if str(atom2.value) == str(atom.value):
						#from IPython import embed; embed();
						raise Exception("not_implemented:"+str(atom2) + " in kb with " + str(atom))
			#from IPython import embed; embed();
			#if atom.datatype == rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer'):
			#	kind = "INTEGER"
			#else:
			kind = "STRING"
		code = str(len(s.codes))
		s.codes[atom] = kind,cpp_name, code
		return cpp_name

	def find_code_by_cppname(s, x):
		for k,(kind,cpp_name, code) in s.codes.items():
			if x==cpp_name:
				return k

	def consts_initialization(s):
		r = Lines()
		r.append(Line('void initialize_consts(){'))
		for atom, (kind,cpp_name, code) in s.codes.items():
			c = 'Constant{'+kind+','+cpp_string_literal(str(atom))+'}'
			r.append(Statement('consts2nodeids_and_refcounts['+c+']\n=nodeid_and_refcount{'+code+',1}'))
			r.append(Statement('nodeids2consts.push_back    ('+c+')'))
			r.append(Statement('ASSERT(consts2nodeids_and_refcounts.size() == nodeids2consts.size())'))
			s.prologue.append(Statement('static const unsigned '+cpp_name+' = '+code))
			if atom == rdflib.RDF.nil:
				s.prologue.append(Statement('static const unsigned nodeid_rdf_nil = '+code))
				r.append(Statement('(void)nodeid_rdf_nil'))#avoid "unused variable" warning
		r.append(Line('}'))
		return r

	def get_prologue(s):
		c = s.consts_initialization()
		return Lines([
			s.prologue, c
		])

	def ep_tables_printer(s):
		r = Lines()
		if not trace_ep_tables_: return r
		r.append(Line("void print_ep_tables(){"))
		for x in s.ep_tables:
			r.append(Statement('cerr << "'+x+':" << endl'))
			r.append(Statement('print_ep_table('+x+')'))
		r.append(Line("}"))
		return r

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
			v = ''
		elif type(thing) == pyin.Atom:
			t = 'CONST'
			v = ','+s.thing2code(thing.value)
		elif thing.is_bnode:
			t = 'BNODE'
			v = ','+s.add_bnode(r, thing.debug_name)
		result = 'Thing(' + t + v
		if trace:
			result += ',' + cpp_string_literal(thing.debug_name)
		return result + ')'

	def case_str(s):
		return "case" +str(s._label)

	def label(s):
		return Line(s.case_str() + ":;")

	def generate_cpp(s, goal, goal_graph, trace_output_path):
		if second_chance_:
			s.prologue.append(Line('#define SECOND_CHANCE'))
		if trace:
			s.prologue.append(Line('#define TRACE'))
			s.prologue.append(Line('#define trace_output_path "' + trace_output_path +'"'))
		s.prologue.append(Line('#include "../../pyin/pyco_static.cpp"'))
		all_rules = []
		for pred,rules in preds.items():
			for rule in rules:
				if type(rule) != Builtin:
					all_rules.append(rule)
		all_rules.append(goal)
		for rule in all_rules:
			rule.locals_map, rule.consts_map, rule.locals_template, rule.consts = make_locals(rule)
			rule.has_body = len(rule.body) != 0
			""" so, the cpppred_state struct has a vector of states,
			used for both head-unification and for calling other rules,
			so this is the number of generators that this rule will need at once, at most"""
			rule.max_states_len = (len(rule.head.args) if rule.head else 0) + len(rule.body)
			assert not rule.head or (len(rule.head.args) == 2)
			#gotcha; is args just the vars? no its args in the meaning of term with args
		s.ep_tables = ["ep" + str(rule.debug_id) for rule in all_rules if rule != goal]
		for pred_name in preds.keys():
			s.prologue.append(Statement(pred_func_declaration('pred_'+cppize_identifier(pred_name))+"__attribute__ ((unused))"))
		consts_done = set()
		consts = Lines()
		for rule in all_rules:
			if type(rule) == Builtin: continue
			i = rule.original_head
			if i in consts_done:
				continue
			consts_done.add(i)
			consts.append(
				Statement("static Locals " + consts_of_rule(i) + s.things_literals(666, rule.consts)))

		r = Module(
		[
			Lines([
				Statement("static ep_table "+x) for x in s.ep_tables]),
			consts,
			Lines([s.pred(pred, rules) for pred,rules in list(preds.items()) + [[None, [goal]]]]),
			s.print_result(goal, goal_graph),
			s.unification(),
			s.thing_groundedness_check(),
			s.result_groundedness_check(goal),
			(s.bnode_printer() if trace else Lines([])),
			(s.bnode_serializer() if trace else Lines([]))
		])
		import sys
		sys.setrecursionlimit(15000)

		return (str(s.get_prologue()) + '\n' +
			str(r) + '\n' +
			str(s.ep_tables_printer()) +
			str(s.epilogue))

	def unification(s):
		result = Lines([Line(
			"""
int unify(cpppred_state & __restrict__ state)
{
	#ifdef TRACE_PROOF
		state.num_substates = 0;
	#endif
	Thing *x = state.incoming[0]; Thing *y = state.incoming[1];
	goto *(((char*)&&case0) + state.entry);
	case0:
	INIT_DBG_DATA;
	#ifdef TRACE_UNIFICATION
		if(top_level_tracing_coro && tracing_enabled && tracing_active)
		{
			stringstream ss;
			ss << "unify " << (void*)x << thing_to_string_nogetval(x) << " with " << (void*)y << thing_to_string_nogetval(y);
			state.set_comment(ss.str());
			state.set_active(true);
		}
	#endif
	ASSERT(x->type() != BOUND);ASSERT(y->type() != BOUND);
	ASSERT(x->type() != BNODE || !x->_bnode_bound_to);
	ASSERT(y->type() != BNODE || !y->_bnode_bound_to);
	if (x == y)
		yield(single_success)
	if (x->type() == UNBOUND)
	{
		x->bind(y);
		yield(unbind_x)
	}
	if (y->type() == UNBOUND)
	{
		y->bind(x);
		yield(unbind_y)
	}
	if ((x->type() == CONST) && (*x == *y))
		yield(single_success)
	if ((x->type() == BNODE) && (*x == *y)) //same origin
	{
		ASSERT(!x->_bnode_bound_to);
		ASSERT(!y->_bnode_bound_to);
		switch (y->origin())
		{
			""")])
		s.state_index = 0
		outer_block = result
		for bnode_cpp_name, (rule, bnode_name) in s.bnodes.items():
			result.append(Line('case ' + bnode_cpp_name + ':'))
			result.append(Line("""if (y->_is_bnode_ungrounded)
			{
				Thing *swap_temp = x;
				x = y;
				y = swap_temp;
			}
			"""))
			states_len = '('+str(len(rule.head_vars)-1)+')'
			outer_block.append(Statement('state.grab_substates('+states_len+')'))
			if trace_unification_:
				outer_block.append(Statement('state.num_substates = '+states_len))
			block = outer_block
			for local_name in rule.head_vars:
				if local_name == bnode_name:
					continue
				local_idx = rule.locals_map[local_name]
				bnode_idx = rule.locals_map[bnode_name];
				offset = local_idx - bnode_idx
				block.append(Statement(s.substate()+'->entry = 0'))
				block.append(Statement(
					s.substate()+'->incoming[0] = get_value(get_value(x) + '+str(offset)+')'))
				block.append(Statement(
					s.substate()+'->incoming[1] = get_value(get_value(y) + '+str(offset)+')'))
				block.append(Line('while (unify(*'+s.substate()+'))'))
				block = nest(block)
				s.state_index += 1
			block.append(Statement('x->set_bnode_bound_to(y)'))
			block.append(s.do_yield())
			block.append(Line("""if (y->_is_bnode_ungrounded)
			{
				Thing *swap_temp = x;
				x = y;
				y = swap_temp;
			}
			"""))
			block.append(Statement('x->set_bnode_bound_to(NULL)'))
			outer_block.append(Statement('release_states('+states_len+')'))
			if trace_unification_:
				outer_block.append(Statement('state.num_substates = 0'))
			outer_block.append(Statement('break'))
			s.state_index = 0
		result.append(Line("""
			default:
			ASSERT(false);
		}"""))
		if trace_proof_:
			result.append(Statement('state.num_substates = 0'))
		result.append(Line("""
		#ifdef TRACE_PROOF
		state.set_active(false);
		#endif
	}
	single_success:
	END;
	unbind_x:
	x->unbind();
	END;
	unbind_y:
	y->unbind();
	END;
}"""))
		return result

	def thing_groundedness_check(s):
		result = Lines([Line(
			"""
bool find_ungrounded_bnode(Thing* v)
{
    v = get_value(v);
    if (v->type() != BNODE)
        return false;
    if(v->_is_bnode_ungrounded)
        return true;
    else switch(v->origin())
	{
""")])
		for bnode_cpp_name, (rule, bnode_name) in s.bnodes.items():
			result.append(Line('case ' + bnode_cpp_name + ':'))
			for local_name in rule.head_vars:
				if local_name == bnode_name:
					continue
				local_idx = rule.locals_map[local_name]
				bnode_idx = rule.locals_map[bnode_name];
				offset = local_idx - bnode_idx
				result.append(If('find_ungrounded_bnode(v + '+str(offset)+')',
								 Statement('return true')))
			result.append(Statement('break;'))
		result.append(Line(
"""
		default:
		ASSERT(false);
	}
	return false;
}
"""))
		return result

	def result_groundedness_check(s, query):
		result = Lines([Line("""
bool result_is_grounded(cpppred_state &state)
{
	""")])
		if len(query.locals_map) == 0:
			result.append(Statement('(void)state'))
		done = []
		assert len(query.body)
		for triple in query.body:
			assert len(triple.args)
			for arg_idx in range(len(triple.args)):
				arg = triple.args[arg_idx]
				if arg not in query.locals_map: continue
				if arg in done:	continue
				done.append(arg)
				it = local_expr(arg, query)
				result.append(If('find_ungrounded_bnode('+it+')',
					Block([
						Line("""
						#ifdef TRACE
						cerr << "#ungrounded """ + str(arg) + """:" << thing_to_string("""+it +""") << endl;
						#endif
						"""),
						Statement('return false')])))
		result.append(Line(
	"""
	return true;	
}	
	"""))
		return result





	def bnode_serializer(s):
		result = Lines([Line(
			"""
void serialize_bnode(Thing* t, map<Thing*, size_t> &todo, map<Thing*, size_t> &done, size_t &first_free_id, stringstream &result)
{
	(void)first_free_id;
	(void)result;

	size_t id = todo[t];
	done[t] = id;
	todo.erase(t);
	
	switch (t->origin())
	{
""")])
		def do_arg(arg):
			if arg in rule.locals_map:
				t = locals+'+'+str(rule.locals_map[arg])
			else:
				t = local_expr(arg, rule)
			result.append(Statement(
				'serialize_thing2('+t+', todo, done, first_free_id, result)'))
		for bnode_cpp_name, (rule, bnode_name) in s.bnodes.items():
			result.append(Line('case ' + bnode_cpp_name + ':'))
			for triple, is_last in common.tell_if_is_last_element(rule.original_head_triples):
				bnode_idx = rule.locals_map[bnode_name]
				locals = 't - '+str(bnode_idx)
				do_arg(triple.args[0])
				result.append(Statement('result << " <' + cpp_string_literal_noquote(triple.pred) + '> "'))
				do_arg(triple.args[1])
				result.append(Statement('result << ". " << endl'))
			result.append(Statement('break'))
		result.append(Line("""
	}
}
"""))
		return result



	def bnode_printer(s):
		result = Lines([Line(
			"""
string bnode_to_string2(set<Thing*> &processing, Thing* thing)
{
	processing.insert(thing);
	stringstream result;
	result << endl;
	//result << "(" << processing.size() << ")";
	for (size_t i = 0; i < processing.size(); i++)
		result << "  ";
	result << "[";
	//cerr << "bnode_to_string2: "<< thing << " " << &processing << " "  << processing.size()<< endl;
	switch (thing->origin())
	{
""")])
		def do_arg(arg):
			result.append(s.substituted_arg2('result', locals, rule, arg, arg!=bnode_name))
		for bnode_cpp_name, (rule, bnode_name) in s.bnodes.items():
			result.append(Line('case ' + bnode_cpp_name + ':'))
			for triple, is_last in common.tell_if_is_last_element(rule.original_head_triples):
				bnode_idx = rule.locals_map[bnode_name]
				locals = 'thing - '+str(bnode_idx)
				do_arg(triple.args[0])

				#shorten = cpp_string_literal_noquote()
				shorten = common.shorten

				result.append(Statement('result << " <' + shorten(triple.pred) + '> "'))
				do_arg(triple.args[1])
				if not is_last: result.append(Statement('result << ". "'))
			result.append(Statement('break'))
			#from IPython import embed; embed();exit()
		result.append(Line('}; result << "]"; processing.erase(thing);'))
		#result.append(Line('cerr << "bnode_to_string2: "<< thing << " " << &processing << " "  << processing.size()<< endl;'))
		result.append(Line('return result.str();}'))
		result.append(Line("""
		string bnode_to_string(Thing* thing)
		{
			set<Thing*> processing;
			return bnode_to_string2(processing, thing);
		}
		"""))
		return result

	def substituted_literal(s, outstream, arg):
		q = cpp_string_literal('"""')
		return Statement(outstream+' << '+q+
			 '<<serialize_literal_to_n3('+cpp_string_literal(str(arg))+')<<'+q)

	def substituted_uriref(s, outstream, arg):
		if type(arg) == rdflib.URIRef:
			return Statement(outstream+' << "<' + cpp_string_literal_noquote(arg) +'> "')

	def substituted_arg2(s, outstream, locals, r, arg, do_bnodes):
		if type(arg) == rdflib.Literal:
			return s.substituted_literal(outstream, arg)
		if type(arg) == rdflib.URIRef:
			return s.substituted_uriref(outstream, arg)
		if type(arg) == rdflib.Variable:
			return Block([
				Statement('Thing *v = get_value('+locals+'+'+str(r.locals_map[arg])+')'),
				If('v->type() == CONST',
					If ('nodeids2consts[v->node_id()].type == URI',
						Statement(outstream+' <<  "<" << nodeids2consts[v->node_id()].value << "> "'),
						Statement(outstream+' << "\\"\\"\\""<< replaceAll(nodeids2consts[v->node_id()].value,"\\n", "\\\\n") << "\\"\\"\\" "')
					),
				   (If ('v->type() == BNODE',
						If ('processing.find(v) != processing.end()',
							Statement(outstream+' << "LOOPSIE"'),
							Statement(outstream+' << bnode_to_string2(processing, v)')),
						Statement(outstream+' << "?' + str(arg) +'"'))
				   if do_bnodes else
				   		Statement(outstream+' << "?' + str(arg) +'"'))
				)
				])
		assert(False)

	def substituted_arg(s, r, arg):
		if type(arg) == rdflib.Literal:
			return s.substituted_literal('cout', arg)
		if type(arg) == rdflib.URIRef:
			return s.substituted_uriref('cout', arg)
		if type(arg) == rdflib.Variable:
			return Lines([
				Statement('v = get_value(state.locals+'+str(r.locals_map[arg])+')'),
				If('v->type() == CONST',
					If ('nodeids2consts[v->node_id()].type == URI',
						Statement('cout <<  "<" << nodeids2consts[v->node_id()].value << "> "'),
						Statement('cout << "\\"\\"\\""<< replaceAll(nodeids2consts[v->node_id()].value,"\\n", "\\\\n") << "\\"\\"\\" "')
					),
					Statement('cout << "?' + str(arg) +' "'))
				])
		assert(False)

	def print_result(s, r, goal_graph):
		outer_block = b = Lines()
		b.append(Line('void print_result(cpppred_state &state)'))
		b = nest(b)
		b.append(Statement('(void)state;'))
		b.append(Statement('print_euler_steps()'))
		b.append(Statement('cout << " RESULT : "'))
		b.append(Statement('cerr << " (RESULT) "'))
		b.append(Statement('Thing *v;(void)v'))
		gg = goal_graph[:]
		#gg.reverse()
		for term in gg:
			b.append(s.substituted_arg(r, term.args[0]))
			b.append(Statement('cout << "<' + str(term.pred) + '> "'))
			b.append(s.substituted_arg(r, term.args[1]))
			b.append(Statement('cout << ". "'))
		b.append(Statement('cout << endl'))
		b.append(Statement('cout << endl << flush'))
		return outer_block

	def substate(s):
		return '(state.states+'+str(s.state_index)+')'

	def pred(s, pred_name, rules):
		s._label = 0
		s.state_index = 0
		#max_body_len = max(len(r.body) for r in rules)
		#max_states_len = max(r.max_states_len for r in rules)
		result = Collection([
			comment(common.shorten(pred_name) if pred_name else 'query'),
			Line(
				pred_func_declaration(('pred_'+cppize_identifier(pred_name)) if pred_name else 'query')
			)])
		b = nest(result)
		b.append(Statement('goto *(((char*)&&case0) + state.entry)'))
		b.append(s.label())
		if trace_proof_:
			b.append(If('(top_level_tracing_coro == NULL) && tracing_enabled', Statement('top_level_tracing_coro = &state')))
		if prune_duplicate_results_:
			b.append(Statement('state.results = new results_vector'))
		b.append(Lines([s.rule(rule) if type(rule) != Builtin else rule.build_in(rule) for rule in rules]))
		if prune_duplicate_results_:
			b.append(Statement('delete state.results'))
		b.append(Statement('return 0'))
		return result

	def rule(s, r):
		if len(r.existentials) > 1 or (len(r.existentials) == 1 and r.existentials[0] == r.head.args[0] and r.existentials[0] == r.head.args[1]):
			raise Exception("too many existentials in " + str(r) +"\nexistentials: " + str(r.existentials))
		b = Lines()
		b.append(comment(r.__str__()))#shortener = common.shorten)))
		b.append(Statement('INIT_DBG_DATA'))
		b.append(Statement('ASSERT(consts2nodeids_and_refcounts.size() == nodeids2consts.size())'))
		if len(r.locals_template):
			b.append(Statement("state.locals = grab_things(" + str(len(r.locals_template))  + ')'))
			for k,v in r.locals_map.items():
				b.append(Statement('state.locals['+str(v)+'] = ' +
					s.thing_literal(r, r.locals_template[v])))
		if r.max_states_len:
			b.append(Statement("state.grab_substates(" + str(r.max_states_len) + ')'))
		if trace_proof_:
			b.append(Statement('state.num_substates = '+str(r.max_states_len)))
			#for i in range(r.max_states_len):
			#	b.append(Statement('state.states['+str(i)+'].status = INACTIVE'))
		if len(r.existentials):
			pass
		if trace_proof_:
			b.append(
				If("top_level_tracing_coro && tracing_enabled && tracing_active",
					Statement('state.set_comment('+cpp_string_literal(r.__str__(shortener = common.shorten))+')')))
			b.append(Statement('state.set_active(true)'))
			#b.append(Statement('proof_trace_add_state(state)'))
		if r.head:
			b.append(Statement('ASSERT(state.incoming[0]->type() != BOUND)'))
			b.append(Statement('ASSERT(state.incoming[1]->type() != BOUND)'))
			b.append(s.head(r))
		else:
			b.append(s.body_triples_block(r))
		if trace_proof_:
			b.append(Statement('state.set_active(false)'))
		if r.max_states_len:
			b.append(Statement("release_states(" + str(r.max_states_len) + ')'))
			if trace_proof_:
				b.append(Statement('state.num_substates = 0'))
				#b.append(Statement('proof_trace_remove_state(state)'))
		if len(r.locals_template):
			b.append(Statement("release_things(" + str(len(r.locals_template))  + ')'))
		b.append(Statement('CHECK_DBG_DATA'))
		return b

	def head(s, r):
		outer_block = b = Lines()
		todo = []
		for arg_i, arg in enumerate(r.head.args):
			if arg in r.existentials:
				dont = False
				for (xxxarg_i, xxxarg) in todo:
					if xxxarg == arg:
						dont = True
				if not dont:
					todo.append((arg_i, arg))
		for arg_i, arg in enumerate(r.head.args):
			if arg not in r.existentials:
				todo.append((arg_i, arg))
		s.state_index = 0
		if len(todo) == 1:
			todo = todo * 2
		for pos_i, (arg_i, arg) in enumerate(todo):
			other_arg_idx, other_arg = todo[0 if (pos_i == 1) else 1]
			arg_expr = 'state.incoming['+str(arg_i)+']'
			other_arg_expr = 'state.incoming['+str(other_arg_idx)+']'


			"""here we check if one of the incoming arguments is bnode already produced by this rule.
			in that case, we simply bind the other argument to the appropriate local of the producing 
			rule and yield. This should be just a (big) optimization, only the number of yields might 
			differ. 
			We could as well rely on bnode unification and let the body run its course. 
			Todo add a command line switch to test this on and off"""
			if arg in r.existentials:
				b.append(Line("if (*"+arg_expr+" == "+s.thing_literal(r, r.locals_template[r.locals_map[arg]	])+")"))
				b = nest(b)
				if other_arg in r.locals_map:
					#print(r.locals_map, other_arg, arg)
					diff = r.locals_map[other_arg]-r.locals_map[arg]
					b.append(s.unify('state.incoming['+str(other_arg_idx)+']',  ('get_value' if diff else '') + '('+str(diff)+'+'+arg_expr+')'))
				else:
					b.append(s.unify('state.incoming['+str(other_arg_idx)+']', '('+local_expr(other_arg, r)+')'))
				b = nest(b)
				if trace_proof_:
					b.append(Statement('state.set_status(BNODE_YIELD)'))
				b.append(s.do_yield())
				if trace_proof_:
					b.append(Statement('state.set_status(ACTIVE)'))
				outer_block.append(Line('else'))
				b = outer_block



		b = nest(outer_block)
		s.state_index = 0
		is_first_arg = True
		for arg_i, arg in enumerate(r.head.args):
			b.append(comment(arg))
			ua1 = '(state.incoming['+str(arg_i)+'])'
			ua2 = '('+local_expr(arg, r, not_getval=is_first_arg)+')'
			if is_first_arg:
				b.append(Statement('ASSERT('+ua1+'->type() != BOUND)'))
				b.append(Statement('ASSERT('+ua2+'->type() != BOUND)'))
			b.append(s.unify(('get_value' if not is_first_arg else '') + ua1, ua2))
			b = nest(b)
			is_first_arg = False
		b.append(s.body_triples_block(r))
		return outer_block

	def unify(s, a, b):
		r = Lines([
			Statement("state.states[" + str(s.state_index) + '].entry = 0'),
			Statement("state.states[" + str(s.state_index) + '].incoming[0] = ('+a+')'),
			Statement("state.states[" + str(s.state_index) + '].incoming[1] = ('+b+')'),
			Line('while(unify(*(state.states + ' + str(s.state_index) + ')))')])
		s.state_index += 1
		return r

	def body_triples_block(s, r):
		dont_yield = False
		do_ep = (r.head and r.has_body)
		outer_block = b = Lines()
		if do_ep:
			#we know incoming's have been get_valued before the pred func was called
			b.append(Line("if (!find_ep(&ep"+str(r.debug_id)+", state))"))
			inner_block = b = nest(b)
			if second_chance_:
				for arg_i in (0,1):
					b.append(Statement('state.ep_lists[{0}] = query_list_wrapper(get_value(state.incoming[{0}]))'.format(arg_i)))
			b.append(push_ep(r))
		for body_triple_index, triple in enumerate(r.body):
			if triple.pred in preds:
				b = s.nest_body_triple_block(r, b, body_triple_index, triple)
			else:
				dont_yield = True
				print("warning: "+str(triple.pred)+" unknown in " + str(r))
				break
		if not dont_yield:
			if do_ep:
				b.append(Lines([
					Statement("ASSERT(ep" +str(r.debug_id)+ ".size())"),
					Statement("ep" +str(r.debug_id)+ ".pop_back()")]))
			if r.head == None:
				b.append(Line('if (!result_is_grounded(state))cerr << "#ungrounded result." << endl; else'))
			b.append(s.yield_block())
			if do_ep:
				b.append(push_ep(r))
		if do_ep:
			inner_block.append(Statement("ep" +str(r.debug_id)+ ".pop_back()"))
			if second_chance_:
				inner_block.append(Statement('delete state.ep_lists[0]'))
				inner_block.append(Statement('delete state.ep_lists[1]'))
		if do_ep:
			outer_block.append(Line('else'))
			bbb = nest(outer_block)
			done = []
			for arg in r.head.args:
				if arg in r.existentials and arg not in done:
					bbb.append(Block([
						Statement(local_expr(arg, r) + '->make_bnode_ungrounded()')
				]))
				done.append(arg)
			if len(r.existentials):
				if trace_proof_:
					bbb.append(Statement('state.set_status(EP)'))
				bbb.append(s.do_yield())
				if trace_proof_:
					bbb.append(Statement('state.set_status(ACTIVE)'))
		outer_block.append(s.euler_step())
		return outer_block

	def yield_block(s):
		b = Block()
		if trace_proof_:
			b.append(Statement('state.set_status(YIELD)'))
		b.append(s.do_yield())
		if trace_proof_:
			b.append(Statement('state.set_status(ACTIVE)'))
		return b

	def do_yield(s):
		return Lines([
			s.set_entry(),
			Statement('return state.entry'),
			s.label()
		])

	def set_entry(s):
		s._label += 1
		r = Statement('state.entry = ((char*)&&case' + str(s._label) + ') - ((char*)&&case0)')
		return r

	def euler_step(s):
		if trace:
			return Statement('if (!(euler_steps++ & 0b111                  ))maybe_print_euler_steps()')
		else:
			return Statement('if (!(euler_steps++ & 0b111111111111111111111))maybe_print_euler_steps()')

	def nest_body_triple_block(s, r, b, body_triple_index, triple):
		b.append(comment(triple.str(common.shorten)))
		substate = "state.states["+str(s.state_index)+"]"
		for arg_idx in range(len(triple.args)):
			arg = triple.args[arg_idx]
			b.append(Statement(
				substate + ".incoming["+str(arg_idx)+"]="+local_expr(arg, r)))
		b.append(Statement(substate + ".entry = 0"))
		b.append(s.euler_step())
		b.append(Line('while(pred_'+cppize_identifier(triple.pred) +'('+ substate+')'+'!=0)'))
		b = nest(b)
		s.state_index += 1
		return b


def local_expr(name, rule, not_getval = False):
	if name in rule.locals_map:
		return ('get_value' if not not_getval else '') +  '(&state.locals[' + str(rule.locals_map[name]) + '])'
	elif name in rule.consts_map:
		return '&'+consts_of_rule(rule.original_head) + '[' + str(rule.consts_map[name])+']'

def cppize_identifier(i: str) -> str:
	return common.fix_up_identification((i))

#String -> String
def pred_func_declaration(pred_name):
	pred_name = cppize_identifier(pred_name)
	return "static size_t " + pred_name + "(cpppred_state & __restrict__ state)"

def consts_of_rule(original_head_id):
	return "consts_of_rule_" + str(original_head_id)

def push_ep(rule):
	return Statement('ep'+str(rule.debug_id)+
					 ".push_back(&state)"
		)

def cpp_string_literal(s):
	return '"'+cpp_string_literal_noquote(s)+'"'

def cpp_string_literal_noquote(s):
	s = str(s)
	result = ''
	for c in s:
		if not (32 <= ord(c) < 127) or c in ('\\', '"', 10):
			result += '\\%03o' % ord(c)
		else:
			result += c
	return result

def comment(s):
	s.replace('*', 'xXx')
	return Comment(s)


@click.command()
@click.argument('kb', type=click.File('rb'))
@click.argument('goal', type=click.File('rb'))
@click.option('--identification', default="unknown")
@click.option('--base', default="")
@click.option('--nolog', default=False, type=bool)
@click.option('--notrace', default=False, type=bool)
@click.option('--nodebug', default=False, type=bool)
@click.option('--novalgrind', default=False, type=bool)
@click.option('--profile', default=False, type=bool)
@click.option('--profile2', default=False, type=bool)
@click.option('--oneword', default='auto', type=click.Choice(['true','false','auto']))
@click.option('--trace_ep_checks', default=False, type=bool)
@click.option('--trace_ep_tables', default=False, type=bool)
@click.option('--trace_proof', default=True, type=bool)
@click.option('--trace_unification', default=False, type=bool)
@click.option('--second_chance', default=True, type=bool)
@click.option('--prune_duplicate_results', default=False, type=bool)
def query_from_files(kb, goal, identification, base, nolog, notrace, nodebug, novalgrind, profile, profile2, oneword, trace_ep_checks, trace_ep_tables, trace_proof, trace_unification, second_chance, prune_duplicate_results):
	global preds, query_rule, trace, trace_ep_tables_, trace_proof_, trace_unification_, second_chance_, prune_duplicate_results_
	prune_duplicate_results_ = prune_duplicate_results
	trace_unification_ = trace_unification
	second_chance_ = second_chance
	if notrace:
		trace_proof = False
		trace_ep_tables = False
		trace_unification_ = False
	trace_proof_ = trace_proof
	trace_ep_tables_ = trace_ep_tables
	trace = not notrace
	preds = defaultdict(list)
	pyin.kbdbg_file_name, pyin._rules_file_name, identification, base, this, outpath = pyin.set_up(identification, base)
	subprocess.call(['ln', '-s', '../../pyco_visualization/html', outpath])
	subprocess.call(['cp', '-r', 'pyco_makefile', outpath+'Makefile'])
	pyin.nolog = nolog
	pyin.init_logging()
	common.log = pyin.log
	rules, query_rule, goal_graph = pyin.load(kb, goal, identification, base)
	for rule in rules:
		pred = rule.head.pred
		use = False
		for rule2 in rules + [query_rule]:
			for bi in rule2.body:
				if bi.pred == pred:
					use = True
		if use:
			preds[pred].append(rule)
	e = Emitter()
	create_builtins(e)
	if oneword == 'auto':
		oneword = not trace
	elif oneword == 'true':
		oneword = True
	else:
		oneword = False
	if oneword:
		e.prologue.append(Line('#define ONEWORD'))
	if trace_ep_checks:
		e.prologue.append(Line('#define TRACE_EP_CHECKS'))
	if trace_ep_tables:
		e.prologue.append(Line('#define TRACE_EP_TABLES'))
	if trace_proof:
		e.prologue.append(Line('#define TRACE_PROOF'))
	if trace_unification:
		e.prologue.append(Line('#define TRACE_UNIFICATION'))
	open(outpath+"pyco_out.cpp", "w").write(e.generate_cpp(query_rule, goal_graph, outpath))
	try:
		subprocess.check_call(['make', ("profile" if profile else ("pyco" if nodebug else "debug"))], cwd = outpath)
	except subprocess.CalledProcessError:
		sys.exit(1)
	subprocess.call(["rm", outpath+"trace.js"])
	print("#ok lets run this")
	sys.stdout.flush()
	pyco_executable = outpath+'/pyco'

	import os
	def exit_gracefully(signum, frame):
		exit_gracefully2()
	def exit_gracefully2():
		print('exit_gracefully..')
		#os.system('killall pyco;sleep 1;')
	import atexit
	atexit.register(exit_gracefully2)
	import signal
	signal.signal(signal.SIGINT, exit_gracefully)
	signal.signal(signal.SIGTERM, exit_gracefully)

	if profile:
		subprocess.check_call(('time valgrind --tool=callgrind --dump-instr=yes --dump-line=yes --simulate-cache=yes --collect-jumps=yes --collect-systime=yes  --collect-bus=yes  --branch-sim=yes --cache-sim=yes'.split())+ [pyco_executable])
	elif profile2:
		subprocess.check_call(['time'] + 'sudo perf record -g --call-graph dwarf -o perf.data'.split() + [pyco_executable])
	elif novalgrind:
		subprocess.check_call(['time', pyco_executable], bufsize=1)#still not getting output until the end
	else:
		subprocess.check_call(['time', 'valgrind', '--main-stacksize=128000000', '--vgdb-error=1', pyco_executable])




class Builtin(object):
	last_debug_id = 0
	def __init__(s):
		s.debug_id = 'builtin'+str(Builtin.last_debug_id)
		Builtin.last_debug_id += 1
		s.consts = []
		s.pred = None
	def register(s, emitter):
		if s.pred == None:
			#this didnt work for some reason, so its not used
			g = rdflib.Graph(store=OrderedStore())
			#g.bind("string_builtins", "http://loworbit.now.im/rdf#")
			g.parse(data=s.example, format='n3')
			_,s.pred,_ = list(g.triples((None,None,None)))[0]
		preds[s.pred].append(s)


def is_pred_used(pred):
	for _, rules in list(preds.items()) + [(None,[query_rule])]:
		for rule in rules:
			if type(rule) != Builtin:
				for i in rule.body:
					if i.pred == pred:
						return True


def create_builtins(emitter):
	b = Builtin()
	b.doc = """ generalizes is_joined and is_split"""
	b.example = """
	@prefix string_builtins: <http://loworbit.now.im/rdf/string_builtins#>.
	"xy" string_builtins:strXlst ("x" "y") ."""
	def build_in(builtin):
		if not 'r1bnbuiltins_aware_list' in emitter.bnodes:
			emitter.prologue.append(Line("""
size_t query_list(cpppred_state & __restrict__ state)
{
	(void)state;
	return 0;
}
		"""))
			return Lines()
		else:
			emitter.epilogue.append(Line("""
size_t query_list(cpppred_state & __restrict__ state)
{
	const size_t first = 0;
	const size_t rest = 1; 
	Thing *&rdf_list = state.incoming[0];
	ASSERT(rdf_list->type() != BOUND);
	Thing *&result_thing = state.incoming[1];
	vector<Thing*> *&result_vec = *((vector<Thing*>**)&result_thing);  

	goto *(((char*)&&case0) + state.entry);
	case0:
	INIT_DBG_DATA

	if (rdf_list->type() == CONST && rdf_list->node_id() == nodeid_rdf_nil)
	{
		yield(case_nil);
		case_nil:;
	}
	else
	{	
		if (!(*rdf_list == Thing{BNODE, r1bnbuiltins_aware_list IF_TRACE("whatever")}))
		{
			CHECK_DBG_DATA
			return 0;
		}
		/*if (find_ungrounded_bnode(rdf_list))
		{
			CHECK_DBG_DATA
			return 0;
		}*/
		#ifdef TRACE_PROOF
			state.num_substates = 0;
			state.set_status(ACTIVE);
			//proof_trace_add_state(state);/*finish me*/
		#endif
		//cerr << "i" << state.incoming[1] << endl;
		ASSERT(result_vec);
		//cerr << (result_vec) << ", " << result_vec->size() << endl;
		//ASSERT(result_vec->empty());
		state.grab_substates(3);
		state.locals = grab_things(2);
		state.locals[first] = """+emitter.thing_literal(666,pyin.Var('first'))+""";
		state.locals[rest] = """+emitter.thing_literal(666,pyin.Var('rest'))+""";
		state.states[0].entry = 0;
		ASSERT(rdf_list->type() != BOUND);
		state.states[0].incoming[0] = rdf_list;
		state.states[0].incoming[1] = &state.locals[first];
		while ("""+'pred_'+cppize_identifier(rdflib.RDF.first)+"""(state.states[0]))
		{
			/*if (find_ungrounded_bnode(&state.locals[first]))
				continue;*/
			//cerr << thing_to_string_nogetval(get_value(&state.locals[first])) << endl;
			ASSERT(state.locals[first].type() == BOUND);
			result_vec->push_back(state.locals[first].binding());
			state.states[1].entry = 0;
			ASSERT(rdf_list->type() != BOUND);
			state.states[1].incoming[0] = rdf_list;
			state.states[1].incoming[1] = &state.locals[rest];
			while ("""+'pred_'+cppize_identifier(rdflib.RDF.rest)+"""(state.states[1]))
			{
				if (get_value(&state.locals[rest])->type() == CONST and 
					get_value(&state.locals[rest])->node_id() == nodeid_rdf_nil)
				{
					yield(case1);
					case1:;
				}
				else
				{
					/*if (find_ungrounded_bnode(&state.locals[rest]))
						continue;*/
					state.states[2].entry = 0;
					state.states[2].incoming[0] = get_value(&state.locals[rest]);
					state.states[2].incoming[1] = result_thing;
					while(query_list(state.states[2]))
					{
						yield(case2);
						case2:;
					}
				}
			}
		}
		release_things(2);
		release_states(3);
	}
	END;
}
			"""))
			if not is_pred_used(builtin.pred):
				return Lines()
			return Lines([Line("""
			{
				INIT_DBG_DATA
				#ifdef TRACE
				{
					/*
					string comment = thing_to_string(state.incoming[0]) + " strXlst " + thing_to_string(state.incoming[1]);
					cerr << comment << endl;
					*/				
					#ifdef TRACE_PROOF
						if (top_level_tracing_coro && tracing_enabled && tracing_active)
						{
							string comment = thing_to_string(state.incoming[0]) + " strXlst " + thing_to_string(state.incoming[1]);
							state.set_comment(comment); 
							state.num_substates = 0;
							state.set_active(true);
						}
					#endif
				}
				#endif
				#define str state.incoming[0]
				ASSERT (str->type() != BOUND);
				#define lst state.incoming[1]
				ASSERT (lst->type() != BOUND);
				if(str->type() == CONST)
				{
					{
						if ((lst->type() != BNODE) && (lst->type() != UNBOUND))
							goto end_str2list;
						Constant input_const = nodeids2consts[str->node_id()];
						string input_string = input_const.value;
	
						state.grab_substates(1);
						#ifdef TRACE_PROOF
							state.num_substates = 1;
						#endif
						size_t locals_size_int = /*locals len itself*/1+input_string.size()*2/*first,rest*/+1/*nil*/;
						state.locals = grab_things(locals_size_int);
						#define locals_size (*((size_t*)(&state.locals[0])))
						locals_size = locals_size_int;
						state.locals[locals_size - 1] = Thing{CONST,push_const(rdf_nil) IF_TRACE("nil")};	
						for (size_t i = 0; i < input_string.size(); i++)
						{
							const BnodeOrigin bn = r1bnbuiltins_aware_list;
							state.locals[1+i*2] = Thing{BNODE,bn IF_TRACE("bn")};//+to_string(i)
							string s = input_string.substr(i,1);
							state.locals[2+i*2] = Thing{CONST, push_const(Constant{STRING, s}) IF_TRACE("some substring")};//IF_TRACE(s)};
						}
					} 
					state.states[0].entry = 0;
					state.states[0].incoming[0] = state.incoming[1];
					state.states[0].incoming[1] = &state.locals[1];
					while (unify(state.states[0]))
					{
						"""), emitter.do_yield(), Line("""
					}
					for (size_t i = 0; i < (locals_size-2)/2; i++)
						pop_const();
					release_things(locals_size);
					#undef locals_size_thing 
					release_states(1);
 				}
				else if ((lst->type() == BNODE) || (lst->type() == CONST && lst->node_id() == nodeid_rdf_nil))
				{
					state.grab_substates(2);
					state.locals = grab_things(2);
					*((vector<Thing*>**)(&state.locals[0])) = new vector<Thing*>;
					state.states[0].entry = 0;
					state.states[0].incoming[0] = lst;
					state.states[0].incoming[1] = *((Thing**)(&state.locals[0]));
					while (query_list(state.states[0]))
					{
						{
							string result;
							for (Thing *t: **((vector<Thing*>**)(&state.locals[0])))
							{
								ASSERT (t->type() != BOUND);
								if (t->type() == CONST)
								{
									/*cerr << "adding " << t->node_id() << endl;
									cerr << "thats " << nodeids2consts[t->node_id()].value << endl;
									*/
									Constant c = nodeids2consts[t->node_id()];
									result += c.value;
								}
								else
								{
									while (query_list(state.states[0]))
									{
									};
									goto is_joined_end;
								}
							}
							{
								//cerr << "consts2nodeids_and_refcounts.size():" << consts2nodeids_and_refcounts.size() << endl;
								nodeid ndid = push_const(Constant{STRING, result});
								//cerr << "ndid:" << ndid << endl;
								state.locals[1] = Thing{CONST,ndid IF_TRACE("strXlst result")};//IF_TRACE(result)
								//cerr << "ndid." << state.locals[1].node_id() << endl;
								//cerr << "thats " << nodeids2consts[state.locals[1].node_id()].value << endl;
							}
						}
						state.states[1].entry = 0;
						state.states[1].incoming[0] = str;
						state.states[1].incoming[1] = &state.locals[1];
						while (unify(state.states[1]))
						{
							{
								/*
								Thing * str2 = get_value(str);
								cerr << "unified0: " << str2 << endl;
								cerr << "unified1: " << str2->node_id() << endl;
								cerr << "unified0: " << nodeids2consts[str2->node_id()].value << endl;
								*/
							}
							"""), emitter.do_yield(), Line("""
						}
						pop_const();
						delete *((vector<Thing*>**)(&state.locals[0]));
						*((vector<Thing*>**)(&state.locals[0])) = new vector<Thing*>;
						state.states[0].incoming[1] = *((Thing**)(&state.locals[0]));
					}
					is_joined_end:
					delete *((vector<Thing*>**)(&state.locals[0]));
					release_things(2);
					release_states(2);
				}
				end_str2list:;
				#ifdef TRACE_PROOF
					state.set_active(false);
				#endif
				#undef str
				#undef lst
				CHECK_DBG_DATA
			}
			""")])
	b.build_in = build_in
	b.pred = rdflib.URIRef('http://loworbit.now.im/rdf/string_builtins#strXlst')
	b.register(emitter)


	b = Builtin()
	b.doc = """dummy output "y"."""
	b.example = """
	@prefix tau_builtins: <http://loworbit.now.im/rdf/tau_builtins#>.
	:dummy tau_builtins:output "y" "xy"."""
	def build_in(builtin):
		return Lines([Line("""
			{
			INIT_DBG_DATA
			{
			Thing *tag = get_value(state.incoming[0]);
			//cerr << "xxx" << nodeids2consts[tag->node_id()].value << endl;
			if (tag->type() == CONST && nodeids2consts[tag->node_id()].value == "file://dummy")
			{
				Thing *input = state.incoming[1];
				ThingType input_type = input->type();
				stringstream output;
				if (input_type == CONST)
				{
					string input_string;
					Constant c = nodeids2consts[input->node_id()];
					input_string = c.value;
					output << "(" << (size_t*)first_free_byte << ") OUTPUT : " << input_string;
					/*output << " [";
					for (char x: input_string)
						output << (int)x << ",";
					output << "]";*/
				}
				else
				{
					output << "OUTPUT : ?";
					#ifdef TRACE
						output <<  " - " << thing_to_string_nogetval(input);
					#endif
				}
				cerr << output.str() << endl;
			}
			#ifdef TRACE_PROOF
				if (top_level_tracing_coro && tracing_enabled && tracing_active)
				{
					//state.set_comment(output.str()); 
					state.num_substates = 0;
					state.set_active(true);
				}
			#endif
			}
			"""), emitter.do_yield(), Line("""
			#ifdef TRACE_PROOF
				state.set_active(false);
			#endif
			CHECK_DBG_DATA
			}
	""")])
	b.build_in = build_in
	b.pred = rdflib.URIRef('http://loworbit.now.im/rdf/tau_builtins#output')
	b.register(emitter)



	b = Builtin()
	b.doc = """dummy serialize_thing "y"."""
	b.example = """
	@prefix tau_builtins: <http://loworbit.now.im/rdf/tau_builtins#>.
	:dummy tau_builtins:serialize_thing [ :x "y"; :xy "xy"]."""
	def build_in(builtin):
		return Lines([Line("""
			{
			{
			stringstream output;
			{
				output << "SERIALIZE : " << endl;
				#ifdef TRACE
					Thing *input = state.incoming[1];
					output << serialize_thing(input);
				#endif
			}
			cerr << output.str() << endl;
			#ifdef TRACE_PROOF
				if (top_level_tracing_coro && tracing_enabled && tracing_active)
				{
					//state.set_comment(output.str());//nope, gotta push_const 
					state.num_substates = 0;
					state.set_active(true);
				}
			#endif
			}
			"""), emitter.do_yield(), Line("""
			#ifdef TRACE_PROOF
				state.set_active(false);
			#endif
			}
	""")])
	b.build_in = build_in
	b.pred = rdflib.URIRef('http://loworbit.now.im/rdf/tau_builtins#serialize_thing')
	b.register(emitter)



	b = Builtin()
	b.doc = """dummy toggle_tracing dummy.
	stops tracing, or re-starts tracing from next rule. The emitted prooof tree will have that rule as root.
	"""
	b.example = """
	@prefix tau_builtins: <http://loworbit.now.im/rdf/tau_builtins#>."""
	def build_in(builtin):
		return Lines([Line("""
			{
			#ifdef TRACE_PROOF
				tracing_enabled = !tracing_enabled;
				top_level_tracing_coro = NULL;				
			#endif
			"""), emitter.do_yield(), Line("""
			#ifdef TRACE_PROOF
				tracing_enabled = !tracing_enabled;		
				top_level_tracing_coro = NULL;				
			#endif

			}
			""")])
	b.build_in = build_in
	b.pred = rdflib.URIRef('http://loworbit.now.im/rdf/tau_builtins#toggle_tracing')
	b.register(emitter)


	b = Builtin()
	b.doc = """dummy toggle_tracing_active dummy.
	does not change the root of the proof tree, just deactivates tracing beyond this rule, until the next invocation or backtrack
	"""
	b.example = """
	@prefix tau_builtins: <http://loworbit.now.im/rdf/tau_builtins#>."""
	def build_in(builtin):
		return Lines([Line("""
			{
			#ifdef TRACE_PROOF
				tracing_active = !tracing_active;		
			#endif
			"""), emitter.do_yield(), Line("""
			#ifdef TRACE_PROOF
				tracing_active = !tracing_active;				
			#endif
			}
			""")])
	b.build_in = build_in
	b.pred = rdflib.URIRef('http://loworbit.now.im/rdf/tau_builtins#toggle_tracing_active')
	b.register(emitter)


	b = Builtin()
	b.example = """
	@prefix tau_builtins: <http://loworbit.now.im/rdf/string_builtins#>.
	"x" const_is_not_equal_to_const "y"."""
	def build_in(builtin):
		return Lines([Line("""
			{
				#define i0 state.incoming[0]
				#define i1 state.incoming[1]
				if (i0->type() != CONST || i1->type() != CONST)
					goto const_is_not_equal_to_const_end;
				if (nodeids2consts[i0->node_id()].value == nodeids2consts[i1->node_id()].value)
					goto const_is_not_equal_to_const_end;
			"""), emitter.do_yield(), Line("""
				const_is_not_equal_to_const_end:;
				#undef i0
				#undef i1
			}
			""")])
	b.build_in = build_in
	b.pred = rdflib.URIRef('http://loworbit.now.im/rdf/string_builtins#const_is_not_equal_to_const')
	b.register(emitter)


	#this one is bad, maybe does_not_unify?
	b = Builtin()
	b.example = """
	@prefix tau_builtins: <http://loworbit.now.im/rdf/tau_builtins#>.
	"x" things_are_different "y"."""
	def build_in(builtin):
		return Lines([Line("""
			{
				#define i0 state.incoming[0]
				#define i1 state.incoming[1]
				if (i0 != i1)
				{
			"""), emitter.do_yield(), Line("""
				}
				#undef i0
				#undef i1
			}
			""")])
	b.build_in = build_in
	b.pred = rdflib.URIRef('http://loworbit.now.im/rdf/tau_builtins#things_are_different')
	b.register(emitter)





	b = Builtin()
	b.example = """
	@prefix string_builtins: <http://loworbit.now.im/rdf/string_builtins#>.
	?what string_builtins:any_char_except "xy" ."""
	def build_in(builtin):
		if not is_pred_used(builtin.pred):
			return Lines()
		else:
			return Lines([Line("""
			{
				INIT_DBG_DATA
				#ifdef TRACE_PROOF
				{
					if (top_level_tracing_coro && tracing_enabled && tracing_active)
					{
						string comment = thing_to_string(state.incoming[0]) + " any_char_except " + thing_to_string(state.incoming[1]);
						//cerr << comment;				
						state.set_comment(comment); 
						state.num_substates = 0;
						state.set_active(true);
					}
				}
				#endif

				ASSERT (state.incoming[0]->type() != BOUND);
				ASSERT (state.incoming[1]->type() != BOUND);

				#define character  state.incoming[0]
				#define exceptions state.incoming[1]
				
				if (exceptions->type() != CONST)
					goto fail_any_char_except;
				
				if(character->type() == CONST)
				{
					{
						string character_string = nodeids2consts[character->node_id()].value;
						if (character_string.size() != 1)
							goto fail_any_char_except;					
						
						string exceptions_string = nodeids2consts[exceptions->node_id()].value;
						{
							char ch = character_string[0];
							for (size_t exceptions_pos = 0; exceptions_pos < exceptions_string.size(); exceptions_pos++)
								if (exceptions_string[exceptions_pos] == ch)
									goto fail_any_char_except;
						}							  
					}
					"""), emitter.do_yield(), Line("""
				}
				else if(character->type() == UNBOUND)
				{
					state.grab_substates(1);
					state.locals = grab_things(2);
					#define ch (*((char*)(&state.locals[0])))
					#define ch_thing state.locals[1]
					state.states[0].incoming[0] = character;
					state.states[0].incoming[1] = &state.locals[0];
					for (ch = 1; ch < 127; ch++)
					{
						{
							string exceptions_string = nodeids2consts[exceptions->node_id()].value;
							for (size_t exceptions_pos = 0; exceptions_pos < exceptions_string.size(); exceptions_pos++)
								if (exceptions_string[exceptions_pos] == ch)
									goto any_char_except__next_char;
							string ch_string(1, ch);
					 		ch_thing = Thing{CONST,push_const(Constant{STRING, ch_string}) IF_TRACE("ch_string")};//IF_TRACE(ch_string)};
					 	}
						state.states[0].entry = 0;
						while (unify(state.states[0]))
						{
							"""), emitter.do_yield(), Line("""
						}
						pop_const();
						any_char_except__next_char:;
					}
					release_things(2);
					release_states(1);
				}

				fail_any_char_except:;

				#ifdef TRACE_PROOF
					state.set_active(false);
				#endif
				#undef ch
				#undef ch_thing
				#undef exceptions
				#undef character
				CHECK_DBG_DATA	
			}
			""")])
	b.build_in = build_in
	b.pred = rdflib.URIRef('http://loworbit.now.im/rdf/string_builtins#any_char_except')
	b.register(emitter)




if __name__ == "__main__":
	query_from_files()


