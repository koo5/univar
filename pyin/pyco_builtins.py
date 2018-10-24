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
		
		""")

