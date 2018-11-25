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
import pyin
from collections import defaultdict, OrderedDict
import memoized
import rdflib
import subprocess
from ordered_rdflib_store import OrderedStore

if sys.version_info.major == 3:
	unicode = str

trace= True

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
	bnodes = {}
	prologue = Lines()

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
		kind = "URI" if type(atom) == rdflib.URIRef else "STRING"
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
			r.append(Line('consts2nodeids_and_refcounts['+c+']=nodeid_and_refcount{'+code+',1};'))
			r.append(Statement('nodeids2consts.push_back('+c+')'))
			s.prologue.append(Statement('static const unsigned '+cpp_name+' = '+code))
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
		r = Module(
		[
			Lines([
				Statement("static ep_table "+x) for x in s.ep_tables]),

			Lines([s.pred(pred, rules) for pred,rules in list(preds.items()) + [[None, [goal]]]]),
			s.print_result(goal, goal_graph),
			s.unification()
		])
		return (str(s.get_prologue()) + '\n' +
			str(r) + '\n' +
			str(s.ep_tables_printer()) +
			'size_t bnode_origin_counter = '+str(s.bnode_origin_counter)+';')

	def unification(s):
		result = Lines([Line(
			"""
int unify(cpppred_state & __restrict__ state)
{
	#ifdef TRACE_PROOF
		state.num_substates = 0;
		state.status = ACTIVE;
	#endif
	Thing *x = state.incoming[0]; Thing *y = state.incoming[1];
	goto *(((char*)&&case0) + state.entry);
	case0:""")])
		if trace_proof_:
			result.append(Line("""state.set_comment("unify " + thing_to_string(x) + " with " + thing_to_string(y)); state.set_active(true);"""))
		result.append(Line("""
	ASSERT(x->type() != BOUND);ASSERT(y->type() != BOUND);
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
	if ((x->type() == BNODE) && (*x == *y))
	{
		switch (y->origin())
		{
			"""))
		s.state_index = 0
		outer_block = result
		for bnode_cpp_name, (rule, bnode_name) in s.bnodes.items():
			result.append(Line('case ' + bnode_cpp_name + ':'))
			states_len = '('+str(len(rule.head_vars)-1)+')'
			outer_block.append(Statement('state.states = grab_states'+states_len))
			if trace_proof_:
				outer_block.append(Statement('state.num_substates = '+states_len))
			block = outer_block
			for local_name in rule.head_vars:
				if local_name == bnode_name:
					continue
				local_idx = rule.locals_map[local_name]
				bnode_idx = rule.locals_map[bnode_name];
				offset = local_idx - bnode_idx
				block.append(Statement(s.substate()+'->entry = 0'))
				for i in range(2):
					ee = 'get_value(get_value(state.incoming['+str(i)+']) + '+str(offset)+')'
					block.append(Statement(s.substate()+'->incoming['+str(i)+'] = '+ee))
				block.append(Line('while (unify(*'+s.substate()+'))'))
				block = nest(block)
				s.state_index += 1
			block.append(s.do_yield())
			outer_block.append(Statement('release_states('+states_len+')'))
			if trace_proof_:
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

	def substate(s):
		return '(state.states+'+str(s.state_index)+')'

	def substituted_arg(s, r, arg):
		if type(arg) == rdflib.Literal:
			return Statement('cout << replaceAll(string('+cpp_string_literal('"""'+str(arg)+'"""') + '),"\\n", "\\\\n")')
		if type(arg) == rdflib.URIRef:
			return Statement('cout << "<' + cpp_string_literal_noquote(arg) +'> "')
		if type(arg) == rdflib.Variable:
			return Lines([
				Statement('v = get_value(state.locals+'+str(r.locals_map[arg])+')'),
				If('v->type() == CONST',
					If ('nodeids2consts[v->node_id()].type == URI',
						Statement('cout <<  "<" << nodeids2consts[v->node_id()].value << "> "'),
						Statement('cout << "\\"\\"\\""<< nodeids2consts[v->node_id()].value << "\\"\\"\\" "')
					),
					Statement('cout << "?' + str(arg) +' "'))
				])
		assert(False)


	def print_result(s, r, goal_graph):
		outer_block = b = Lines()
		b.append(Line('void print_result(cpppred_state &state)'))
		b = nest(b)
		b.append(Statement('(void)state;'))
		b.append(Statement('cout << " RESULT : "'))
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

	def pred(s, pred_name, rules):
		s._label = 0
		s.state_index = 0
		#max_body_len = max(len(r.body) for r in rules)
		#max_states_len = max(r.max_states_len for r in rules)
		return Collection([
			comment(common.shorten(pred_name) if pred_name else 'query'),
			Lines(
				[Statement("static Locals " + consts_of_rule(rule.debug_id) + s.things_literals(666, rule.consts)) for rule in rules]
			),
			Line(
				pred_func_declaration(('pred_'+cppize_identifier(pred_name)) if pred_name else 'query')
			),
			Block(
				[
					Statement('goto *(((char*)&&case0) + state.entry)'),
					s.label(),
					Lines([s.rule(rule) if type(rule) != Builtin else rule.build_in(s) for rule in rules]),
					Statement('return 0')
				]
			)
		])

	def rule(s, r):
		if len(r.existentials) > 1 or (len(r.existentials) == 1 and r.existentials[0] == r.head.args[0] and r.existentials[0] == r.head.args[1]):
			raise Exception("too many existentials in " + str(r) +" : " + str(r.existentials))
		outer_block = b = Lines()
		b.append(comment(r.__str__(shortener = common.shorten)))
		if len(r.locals_template):
			b.append(Statement("state.locals = grab_things(" + str(len(r.locals_template))  + ')'))
			for k,v in r.locals_map.items():
				b.append(Statement('state.locals['+str(v)+'] = ' +
					s.thing_literal(r, r.locals_template[v])))
		if r.max_states_len:
			b.append(Statement("state.states = grab_states(" + str(r.max_states_len) + ')'))
		if trace_proof_:
			b.append(Statement('state.num_substates = '+str(r.max_states_len)))
			for i in range(r.max_states_len):
				b.append(Statement('state.states['+str(i)+'].status = INACTIVE'))
		if len(r.existentials):
			pass
		if trace_proof_:
			b.append(Statement('state.set_comment('+cpp_string_literal(r.__str__(shortener = common.shorten))+')'))
			b.append(Statement('state.set_active(true)'))
		if r.head:
			b.append(s.head(r))
		else:
			b.append(s.body_triples_block(r))
		if trace_proof_:
			b.append(Statement('state.set_active(false)'))
		if r.max_states_len:
			b.append(Statement("release_states(" + str(r.max_states_len) + ')'))
			if trace_proof_:
				b.append(Statement('state.num_substates = 0'))
		if len(r.locals_template):
			b.append(Statement("release_things(" + str(len(r.locals_template))  + ')'))
		return outer_block

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
			if arg in r.existentials:
				b.append(Line("if (*("+arg_expr+") == "+s.thing_literal(r, r.locals_template[r.locals_map[arg]	])+")"))
				b = nest(b)
				if other_arg in r.locals_map:
					#print(r.locals_map, other_arg, arg)
					diff = r.locals_map[other_arg]-r.locals_map[arg]
					b.append(s.unify('state.incoming['+str(other_arg_idx)+']', ('get_value' if diff else '') + '('+str(diff)+'+get_value('+arg_expr+'))'))
				else:
					b.append(s.unify('state.incoming['+str(other_arg_idx)+']', '('+local_expr(other_arg, r)+')'))
				b = nest(b)
				b.append(s.do_yield())
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
			"""we know incoming's have been get_valued before the pred func was called"""
			b.append(Line("if (!find_ep(&ep"+str(r.debug_id)+", state))"))
			inner_block = b = nest(b)
			b.append(push_ep(r))
			if trace_proof_:
				outer_block.append(Line('else {state.status = EP;dump();state.status=ACTIVE;}'))
		for body_triple_index, triple in enumerate(r.body):
			if triple.pred in preds:
				b = s.nest_body_triple_block(r, b, body_triple_index, triple)
			else:
				dont_yield = True
				print("warning: "+str(triple.pred)+" unknown")
				break
		if not dont_yield:
			if do_ep:
				b.append(Lines([
					Statement("ASSERT(ep" +str(r.debug_id)+ ".size())"),
					Statement("ep" +str(r.debug_id)+ ".pop_back()")]))
			if trace_proof_:
				b.append(Statement('state.set_status(YIELD)'))
			b.append(s.do_yield())
			if trace_proof_:
				b.append(Statement('state.set_status(ACTIVE)'))
			if do_ep:
				b.append(push_ep(r))
				inner_block.append(Statement("ep" +str(r.debug_id)+ ".pop_back()"))
		outer_block.append(s.euler_step())

		return outer_block

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



class Builtin(object):
	last_debug_id = 0
	def __init__(s):
		s.debug_id = 'builtin'+str(Builtin.last_debug_id)
		Builtin.last_debug_id += 1
		s.consts = []
		s.pred = None
	def register(s, emitter):
		if s.pred == None:
			g = rdflib.Graph(store=OrderedStore())
			#g.bind("string_builtins", "http://loworbit.now.im/rdf#")
			g.parse(data=s.example, format='n3')
			_,s.pred,_ = list(g.triples((None,None,None)))[0]
		preds[s.pred].append(s)



def local_expr(name, rule, not_getval = False):
	if name in rule.locals_map:
		return ('get_value' if not not_getval else '') +  '(&state.locals[' + str(rule.locals_map[name]) + '])'
	elif name in rule.consts_map:
		return '&'+consts_of_rule(rule.debug_id) + '[' + str(rule.consts_map[name])+']'

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
	return Statement('ep'+str(rule.debug_id)+".push_back(&state)")


def nest(block):
	b = Block()
	block.append(b)
	return b

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
@click.option('--oneword', default=False, type=bool)
@click.option('--trace_ep_checks', default=False, type=bool)
@click.option('--trace_ep_tables', default=False, type=bool)
@click.option('--trace_proof', default=True, type=bool)
def query_from_files(kb, goal, identification, base, nolog, notrace, nodebug, novalgrind, oneword, trace_ep_checks, trace_ep_tables, trace_proof):
	global preds, query_rule, trace, oneword_, trace_ep_tables_, trace_proof_
	if notrace:
		trace_proof = False
		trace_ep_tables = False
	trace_proof_ = trace_proof
	trace_ep_tables_ = trace_ep_tables
	trace = not notrace
	preds = defaultdict(list)
	oneword_ = oneword
	pyin.kbdbg_file_name, pyin._rules_file_name, identification, base, this, outpath = pyin.set_up(identification, base)
	subprocess.call(['cp', '-r', 'pyco_visualization/html', outpath])
	subprocess.call(['cp', '-r', 'pyco_makefile', outpath+'Makefile'])
	pyin.nolog = nolog
	pyin.init_logging()
	common.log = pyin.log
	rules, query_rule, goal_graph = pyin.load(kb, goal, identification, base)
	for rule in rules:
		preds[rule.head.pred].append(rule)
	e = Emitter()
	create_builtins(e)
	if trace_ep_checks:
		e.prologue.append(Line('#define TRACE_EP_CHECKS'))
	if trace_ep_tables:
		e.prologue.append(Line('#define TRACE_EP_TABLES'))
	if trace_proof:
		e.prologue.append(Line('#define TRACE_PROOF'))
	open(outpath+"pyco_out.cpp", "w").write(e.generate_cpp(query_rule, goal_graph, outpath))
	try:
		subprocess.check_call(['make', ("pyco" if nodebug else "debug")], cwd = outpath)
	except subprocess.CalledProcessError:
		sys.exit(1)
	print("#ok lets run this")
	sys.stdout.flush()
	subprocess.call(["rm", outpath+"trace.js"])
	pyco_executable = outpath+'/pyco'
	if novalgrind:
		subprocess.check_call([pyco_executable], bufsize=1)#still not getting output until the end
	else:
		subprocess.check_call(['valgrind', pyco_executable])












def create_builtins(emitter):
	b = Builtin()
	b.doc = """(input)"x" is joined(y)."""
	b.example = """
	@prefix string_builtins: <http://loworbit.now.im/rdf/string_builtins#>.
	("x" "y") string_builtins:is_joined "xy"."""
	def build_in(s):
		if not(rdflib.RDF.first in preds and rdflib.RDF.rest in preds):
			s.prologue.append(Line("""
				size_t query_list(cpppred_state & __restrict__ state)
				{
					(void)state;
					return 0;
				}
		"""))
		else:
			s.prologue.append(Line("""
				size_t query_list(cpppred_state & __restrict__ state)
				{
					Thing *&rdf_list = state.incoming[0];
					ASSERT(rdf_list->type() != BOUND);
					Thing *&result_thing = state.incoming[1];
					vector<Thing*> *&result_vec = *((vector<Thing*>**)&result_thing);  
					const size_t first = 0;
					const size_t rest = 1; 
					goto *(((char*)&&case0) + state.entry);
					case0:
					#ifdef TRACE_PROOF
						state.num_substates = 0;
						state.status = ACTIVE;
					#endif
					//cerr << "i" << state.incoming[1] << endl;
					ASSERT(result_vec);
					//cerr << (result_vec) << ", " << result_vec->size() << endl;
					//ASSERT(result_vec->empty());
					state.states = grab_states(3);
					state.locals = grab_things(2);
					state.locals[first] = """+emitter.thing_literal(666,pyin.Var('first'))+""";
					state.locals[rest] = """+emitter.thing_literal(666,pyin.Var('rest'))+""";
					state.states[0].entry = 0;
					ASSERT(rdf_list->type() != BOUND);
					state.states[0].incoming[0] = rdf_list;
					state.states[0].incoming[1] = &state.locals[first];
					while ("""+'pred_'+cppize_identifier(rdflib.RDF.first)+"""(state.states[0]))
					{
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
								get_value(&state.locals[rest])->node_id() == consts2nodeids_and_refcounts[Constant{URI,"http://www.w3.org/1999/02/22-rdf-syntax-ns#nil"}].first)
							{
								yield(case1);
								case1:;
							}
							else
							{
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
					END;
				}
		"""))
		return Lines([Line("""
	state.states = grab_states(2);
	state.locals = grab_things(2);
	*((vector<Thing*>**)(&state.locals[0])) = new vector<Thing*>;
	{
		Thing *t = state.incoming[0];
		ASSERT (t->type() != BOUND);
		if (t->type() == UNBOUND)
		{
			cerr << "cant join this" << endl;
			goto is_joined_end;
		}
	}
	state.states[0].entry = 0;
	state.states[0].incoming[0] = state.incoming[0];
	state.states[0].incoming[1] = *((Thing**)(&state.locals[0]));
	while (query_list(state.states[0]))
	{
		{
			string result;
			for (Thing *t: **((vector<Thing*>**)(&state.locals[0])))
			{
				ASSERT (t->type() != BOUND);
				if (t->type() == UNBOUND)
					goto is_joined_end;
				else if (t->type() == CONST)
				{
					Constant c = nodeids2consts[t->node_id()];
					if (c.type == STRING)
						result += c.value;
					else
						goto is_joined_end;
				}
				else ASSERT(false);
			}
			state.locals[1] = Thing{CONST,push_const(Constant{STRING, result}) IF_TRACE(result)};
		}
		state.states[1].entry = 0;
		state.states[1].incoming[0] = state.incoming[1];
		state.states[1].incoming[1] = &state.locals[1];
		while (unify(state.states[1]))
		{
			"""), s.do_yield(), Line("""
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
	
	""")])
	b.build_in = build_in
	b.pred = rdflib.URIRef('http://loworbit.now.im/rdf/string_builtins#is_joined')
	b.register(emitter)

	b = Builtin()
	b.doc = """(input)"x" is_split(y)."""
	b.example = """
	@prefix string_builtins: <http://loworbit.now.im/rdf/string_builtins#>.
	("x" "y") string_builtins:is_split "xy"."""
	def build_in(s):
		ok = False
		for pred, rules in preds.items():
			for rule in rules:
				if type(rule) != Builtin:
					for i in rule.body:
						if i.pred == rdflib.URIRef('http://loworbit.now.im/rdf/string_builtins#is_split'):
							ok = True
		for i in query_rule.body:
			if i.pred == rdflib.URIRef('http://loworbit.now.im/rdf/string_builtins#is_split'):
				ok = True
		if not ok:
			return Lines()
		return Lines([Line("""
			{
			#ifdef TRACE_PROOF
				state.set_comment(thing_to_string(state.incoming[0]) + " is_split " + thing_to_string(state.incoming[1])); 
				state.num_substates = 0;
				state.set_active(true);
			#endif
			Thing *input = state.incoming[0];
			ThingType input_type = input->type();
			if (input_type != CONST)
				goto end_is_split0;
			Thing *output = state.incoming[1];
			ThingType output_type = output->type();
			if ((output_type != BNODE) && (output_type != UNBOUND))
				goto end_is_split0;
			string input_string;
			Constant c = nodeids2consts[input->node_id()];
			if (c.type == STRING)
				input_string = c.value;
			else
				goto end_is_split0;
			state.states = grab_states(1);
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
				const BnodeOrigin bn = r0bnbuiltins_aware_list;
				state.locals[1+i*2] = Thing{BNODE,bn IF_TRACE("bn"+to_string(i))};
				string s = input_string.substr(i,1);
				state.locals[2+i*2] = Thing{CONST, push_const(Constant{STRING, s}) IF_TRACE(s)};
			} 
		}
		state.states[0].entry = 0;
		state.states[0].incoming[0] = state.incoming[1];
		state.states[0].incoming[1] = &state.locals[1];
		while (unify(state.states[0]))
		{
			"""), s.do_yield(), Line("""
		}
		for (size_t i = 0; i < (locals_size-2)/2; i++)
			pop_const();
		release_things(locals_size);
		#undef locals_size_thing 
		release_states(1);
		end_is_split0:;
		#ifdef TRACE_PROOF
			state.set_active(false);
		#endif
	""")])
	b.build_in = build_in
	b.pred = rdflib.URIRef('http://loworbit.now.im/rdf/string_builtins#is_split')
	b.register(emitter)






	b = Builtin()
	b.doc = """dummy output "y"."""
	b.example = """
	@prefix tau_builtins: <http://loworbit.now.im/rdf/tau_builtins#>.
	:dummy tau_builtins:output "y" "xy"."""
	def build_in(s):
		return Lines([Line("""
			{
			{
			Thing *input = state.incoming[1];
			ThingType input_type = input->type();
			if (input_type == CONST)
			{
				string input_string;
				Constant c = nodeids2consts[input->node_id()];
				input_string = c.value;
				cerr << "OUTPUT : " << input_string << " [";
				for (char x: input_string)
					cerr << (int)x << ",";
				cerr << "]" << endl;
			}
			else
			{
				#ifdef TRACE
				cerr <<  "OUTPUT : " << thing_to_string_nogetval(input) << endl;
				#endif
			}
			}
			"""), s.do_yield(), Line("""
			//end_tau_output:;
			
			}
	""")])
	b.build_in = build_in
	b.pred = rdflib.URIRef('http://loworbit.now.im/rdf/tau_builtins#output')
	b.register(emitter)





if __name__ == "__main__":
	query_from_files()







	# 	#ifdef TRACE_PROOF
	# 		state.set_comment(thing_to_string(state.incoming[0]) + " is_split " + thing_to_string(state.incoming[1]));
	# 		state.num_substates = 0;
	# 		state.set_active(true);
	# 	#endif
	# 	Thing *input = state.incoming[0];
	# 	ThingType input_type = input->type();
	# 	if (input_type != CONST)
	# 		goto end_is_split0;
	# 	Thing *output = state.incoming[1];
	# 	ThingType output_type = output->type();
	# 	if ((output_type != BNODE) && (output_type != UNBOUND))
	# 		goto end_is_split0;
	# 	string input_string;
	# 	Constant c = nodeids2consts[input->node_id()];
	# 	if (c.type == STRING)
	# 		input_string = c.value;
	# 	else
	# 		goto end_is_split0;
	# 	state.states = grab_states(1);
	# 	#ifdef TRACE_PROOF
	# 		state.num_substates = 1;
	# 	#endif
	# 	size_t locals_size_int = /*locals len itself*/1+input_string.size()*2/*first,rest*/+1/*nil*/;
	# 	state.locals = grab_things(locals_size_int);
	# 	#define locals_size (*((size_t*)(&state.locals[0])))
	# 	locals_size = locals_size_int;
	#
	# 	state.locals[locals_size - 1] = Thing{CONST,push_const(rdf_nil) IF_TRACE("nil")};
	# 	for (size_t i = 0; i < input_string.size(); i++)
	# 	{
	# 		BnodeOrigin bn;
	# 		if (i == input_string.size() - 1)
	# 			bn = r0bnl0_0;
	# 		else
	# 			bn = r1bnub1bl5c3;
	# 		state.locals[1+i*2] = Thing{BNODE,bn IF_TRACE("bn"+to_string(i))};
	# 		string s = input_string.substr(i,1);
	# 		state.locals[2+i*2] = Thing{CONST, push_const(Constant{STRING, s}) IF_TRACE(s)};
	# 	}
	# }
	# 	state.states[0].entry = 0;
	# 	state.states[0].incoming[0] = state.incoming[1];
	# 	state.states[0].incoming[1] = &state.locals[1];
	# 	while (unify(state.states[0]))
	# 	{
	# 		"""), s.do_yield(), Line("""
	# 	}
	# 	for (size_t i = 0; i < (locals_size-2)/2; i++)
	# 		pop_const();
	# 	release_things(locals_size);
	# 	#undef locals_size_thing
	# 	release_states(1);
	# 	end_is_split0:;
	# 	#ifdef TRACE_PROOF
	# 		state.set_active(false);
	# 	#endif
