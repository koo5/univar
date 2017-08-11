#ifdef CPPOUT
#define CPPOUT2
#ifdef CPPOUT2




/* not used but would be nice, but if something returns a const pointer, 
structures and functions that accept it have to declare the constness too
havent thought too far about it, if theres any speed improvement to be gained,
this would i think require generating quite a bit of permutations of other functions

the motivating case is: rule consts array cant be declared const now
gcc doesnt even know to avoid a call to getValue on a const.

const static Thing *const_getValue (const Thing *_x)

	ASSERT(_x);

	const Thing x = *_x;

	//Is a bound variable, return the value of it's value.
	if (is_bound(x)) {
		//get the pointer
		Thing * thing = get_thing(x);
		ASSERT(thing);
		//and recurse
		return const_getValue(thing);
	}

	//Need to understand this whole offset thing better
	else if (is_offset(x))
	{
		//Thing of type offset is used for the 2nd or later occurrence
		// of a local variable in a
		//rule; it will store a value offset of type offset_t. 

		////This is the offset from the pointer to the Thing representing 
		////this instance of a local variable to the pointer to it's 
		////"representative", which will be labeled either bound or 
		////unbound.
		
		//its an offset from the address of the offset to where the 
		//value is
		
		//get the number
		const offset_t offset = get_offset(x);
		//add it to the current address
		const Thing * z = _x + offset;
		
		
		//Why do we bind here? We already have _x as offset to z
		//this is an attempt at optimization so that the second time
		//we look at this, it will be a variable, which should be 
		//followed faster than the offset
		//make_this_bound(_x, z);
		
		//and recurse
		return const_getValue(z);
	}
	//Is either an unbound variable or a value.
	else
		return _x;
}

getValue makes quite a bit of difference, its a big part of what a rule does
also, is_bound translates to two cmps, 
see work on oneword2
alternatively, scheme A can be faster*/


static Thing *getValue_nooffset (Thing *_x)
{

	ASSERT(_x);

	Thing x = *_x;

	if (is_bound(x)) {
		#ifdef getValue_profile
		getValue_BOUNDS++;
		#endif
		//get the pointer
		Thing * thing = get_thing(x);
		ASSERT(thing);
		//and recurse
		return getValue_nooffset(thing);
	}
	else //if (!is_offset(x))
	{	//Is either an unbound variable or a value.
		#ifdef getValue_profile
		getValue_OTHERS++;
		#endif
		return _x;
	}/*
	else
	{	
		ASSERT(is_offset(x));
		#ifdef getValue_profile
		getValue_OFFSETS++;
		#endif
		//Thing of type offset is used for the 2nd or later occurrence
		// of a local variable in a
		//rule; it will store a value offset of type offset_t. 

		////This is the offset from the pointer to the Thing representing 
		////this instance of a local variable to the pointer to it's 
		////"representative", which will be labeled either bound or 
		////unbound.
		
		//its an offset from the address of the offset to where the 
		//value is
		
		//get the number
		const offset_t offset = get_offset(x);
		//add it to the current address
		Thing * z = _x + offset;
		
		
		//Why do we bind here? We already have _x as offset to z
		//this is an attempt at optimization so that the second time
		//we look at this, it will be a variable, which should be 
		//followed faster than the offset
		make_this_bound(_x, z);
		
		//and recurse
		return getValue_nooffset(z);
	}*/
}
//^^ several percent speed improvement on adder
//we can resolve offsets in alloc thread




bool cppout_would_unify(const Thing *old_, Thing *now_)
{
	FUN;
	const Thing old = *old_;
	const Thing now = *now_;
	 
	ASSERT(!is_offset(old));
	ASSERT(!is_offset(now));
	ASSERT(!is_bound(now));
	
	if(is_var(old) && is_var(now))
		return true;
	else if (is_node(old))
		return are_equal(old, now);
	else if (is_list(old)) {
		assert(false);
	}
	if ((is_list_bnode(*old_) || is_nil(old_)) && (is_list_bnode(*now_) || is_nil(now_))) {
		assert(false);
	}
	else if (types_differ(old, now)) // in oneword mode doesnt differentiate between bound and unbound!
		return false;
	assert(false);
}




bool cppout_find_ep(const ep_t *ep, Thing *s, Thing *o)
{
	FUN;
	s = getValue(s);
	o = getValue(o);

	ASSERT(!is_offset(*s));
	ASSERT(!is_offset(*o));
	ASSERT(!is_bound(*s));
	ASSERT(!is_bound(*o));

	EPDBG(endl << endl << ep->size() << " ep items." << endl);

	for (auto i: *ep)
	{
		auto os = i.first;
		auto oo = i.second;
		ASSERT(!is_offset(*os));
		ASSERT(!is_offset(*oo));
		//what about !is_bound
		
		//TRACE(dout << endl << " epitem " << str(os) << "    VS     " << str(s) << endl << str(oo) << "    VS    " << str(o) << endl;)
		EPDBG(endl << " epcheck " << str(os) << "    VS     " << str(s) << endl << " epcheck " << str(oo) << "    VS    " << str(o) << endl;)

		if (!cppout_would_unify(os,s) || !cppout_would_unify(oo,o))
		    continue;
		return true;
	}
	return false;
}




fstream out;

string predname(nodeid x)
{
	stringstream ss;
	ss << "cpppred" << x;
	return ss.str();
}


string param(PredParam key, pos_t thing_index, string predname, pos_t rule_index)
{
	stringstream ss;
	if (key == HEAD_S)
	ss << "s";
	if (key == HEAD_O)
	ss << "o";
	if (key == LOCAL)
	ss << "(&state.locals[" << thing_index << "])";
	if (key == CONST)
	ss << "(&consts_" << predname << "_" << rule_index << "[" << thing_index << "])";
	return ss.str();
}

nodeid ensure_cppdict(nodeid node)
{
//	dout << node << endl;
	cppdict[node] = *dict[node].value;
	return node;
}


string things_literals(const Locals &things)
{
	stringstream ss;
	ss << "{";
	pos_t i = 0;
	for (Thing t: things) 
	{
		if (i++ != 0) ss << ", ";

		if (is_node(t))
			ensure_cppdict(get_node(t));

		#ifndef oneword
		if (is_unbound(t))
			t.node = 0;
		ss << "Thing(" << ThingTypeNames.at(t.type) << ", " << t.node << ")";
		#else
		ss << "(Thing)" << t;
		#endif

	}
	ss << "}";
	return ss.str();
}







void cppout_consts(string name, vector<Rule> rs)
{
	for (pos_t i = 0; i < rs.size(); i++) {
		auto &r = rs[i];
		locals_map lm, cm;
		Locals locals_template;
		Locals consts;
		make_locals(locals_template, consts, lm, cm, r.head, r.body, false);
		out << "static Locals consts_" << name << "_" << i << " = " << things_literals(consts) << ";\n";
	}
}


char unify_with_var(Thing * a, Thing * b)
{
    ASSERT(is_unbound(*b));
    unifys++;
    if (!are_equal(*a, *b))
    {
        if (is_unbound(*a))
        {
	    make_this_bound(a, b);
	    return (0b101);
        }
        make_this_bound(b, a);
        return (0b011);
    }
    return (0b001);
}

void unbind_from_var(char magic, Thing * __restrict__ a, Thing * __restrict__ b)
{
    if (magic & 0b100)
	make_this_unbound(a);
    if (magic & 0b010)
	make_this_unbound(b);
}


bool unify_with_const(Thing * a, Thing * b)
{
    ASSERT(!is_bound(*a));
unifys++;
    if (are_equal(*a, *b))
	return true;
    if (is_unbound(*a))
    {
	make_this_bound(a, b);
	return true;
    }
    return false;
}

	
void unbind_from_const(Thing *x)
{
        ASSERT(!is_unbound(*x));
	if (is_var(*x))
		make_this_unbound(x);
}

string preddect(string name)
{
	stringstream ss;
	ss << "static int " << name << "(cpppred_state & __restrict__ state, int entry)";
	return ss.str();
}


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
	

void cppout_pred(string name, vector<Rule> rs)
{
	cppout_consts(name, rs);

	out << "\n" << preddect(name);
	out << "{\n";
	for (pos_t i = 0; i < rs.size(); i++) {
		if (rs[i].head && rs[i].body && rs[i].body->size())
			out << "static ep_t ep" << i << ";\n";
	}

	size_t max_body_len = 0;
	for (auto rule:rs) {
		if (rule.body && max_body_len < rule.body->size())
			max_body_len = rule.body->size();
	}
	
	for (size_t j = 0; j < max_body_len; j++)
		out << "int entry" << j << ";\n";


	if (name == "cppout_query")
	{
		out << "static int counter = 0;\n";
		out << "static vector<Thing> prev_results;";
	}



	out << "char uuus;(void)uuus;\n";
	out << "char uuuo;(void)uuuo;\n";

	int label = 0;

	out << "switch(entry){\n";

	//case 0:
	out << "case "<< label++ << ":\n";

	if(max_body_len)
		out << "state.states.resize(" << max_body_len << ");\n";



	const string PUSH = ".push_back(thingthingpair(state.s, state.o));\n";


	int i = 0;
	//loop over all kb rules for the pred
	for (Rule rule:rs)
	{
		bool has_body = rule.body && rule.body->size();

		out << "//rule " << i << ":\n";
		//out << "// "<<<<":\n";
		//out << "case " << label << ":\n";


		locals_map lm, cm;
		Locals locals_template;
		Locals consts;
		make_locals(locals_template, consts, lm, cm, rule.head, rule.body, false);

		if(locals_template.size())
			out << "state.locals = " << things_literals(locals_template) << ";\n";

		//if it's a kb rule and not the query then we'll
		//make join'd unify-coros for the subject & object of the head
		
		PredParam hsk, hok; //key
		ThingType hst, hot; //type
		pos_t hsi, hoi;     //index
		
		if (rule.head) {

			hsk = find_thing(dict[rule.head->subj], hsi, lm, cm);//sets hs
			hok = find_thing(dict[rule.head->object], hoi, lm, cm);
			hst = get_type(fetch_thing(dict[rule.head->subj  ], locals_template, consts, lm, cm));
			hot = get_type(fetch_thing(dict[rule.head->object], locals_template, consts, lm, cm));
			
			if (hst == NODE)
				out << "if (unify_with_const(state.s, " << param(hsk, hsi, name, i) << ")){\n";
			else if (hst == UNBOUND)
			{
				out << "uuus = unify_with_var(state.s, " << param(hsk, hsi, name, i) << ");\n";
				out << "if (uuus & 1){ state.su.magic = uuus;\n";
			}
			else
			{
				out << "state.su.c = unify(state.s, " << param(hsk, hsi, name, i) << ");\n";
				out << "if(state.su.c()){\n";
			}

			if (hot == NODE)
				out << "if (unify_with_const(state.o, " << param(hok, hoi, name, i) << ")){\n";
			else if (hot == UNBOUND)
			{
				out << "uuuo = unify_with_var(state.o, " << param(hok, hoi, name, i) << ");\n";
				out << "if (uuuo & 1){ state.ou.magic = uuuo;\n";
			}
			else
			{
				out << "state.ou.c = unify(state.o, " << param(hok, hoi, name, i) << ");\n";
				out << "if(state.ou.c()){\n";
			}
		}
		//if it's a kb rule (not the query) with non-empty body, then after the suc/ouc coros succeed, we'll check to see if there's an ep-hit
		if (rule.head && has_body) {
			out << "if (!cppout_find_ep(&ep" << i << ", state.s, state.o)){\n";
			out << "ep" << i << PUSH;
		}

		out << "entry = " << label << ";\n";


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


			
			
			out << "if (!silent) dout << unifys << \" unifys\\n\"  ;\n";
			out << "if (!silent) dout << \"RESULT \" << counter << \": \";\n";

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









void yprover::cppout(qdb &goal)
{
	FUN;

	cppdict.clear();
	out.open("out.cpp", fstream::out);

	out << "#include \"globals.cpp\"\n";
	out << "#include \"univar.cpp\"\n";
	out << "union unbinder{coro c; char magic; unbinder(){} unbinder(const unbinder&u){(void)u;} ~unbinder(){}};\n";
	out << "struct cpppred_state;\n";
	out << "struct cpppred_state {\n"
		"int entry=0;\n"
		"vector<Thing> locals;\n"
		"unbinder su,ou;\n"
		"Thing *s, *o;\n"
		"vector<cpppred_state> states;\n};\n"
				   ""
				   "bool silent = false;"
				   ;

	auto unroll = 0;


	out << "/* forward declarations */\n";
	for(auto x: rules) {
		out << preddect(predname(x.first)) << ";\n";
	}


	out << "/* pred function definitions */\n";
	for(auto x: rules) {
		cppout_pred(predname(x.first), x.second);
	}


	auto qit = goal.first.find("@default");
	if (qit == goal.first.end())
		return;

	lists_rules = add_ruleses(rules, quads2rules(goal));
	collect_lists();

	//query is baked in for now
	cppout_pred  ("cppout_query", {Rule(0, qit->second)});



	out << "void cppdict_init(){\n";
	for (auto x:cppdict)
		out << "cppdict[" << x.first << "] = \"" << x.second << "\";\n";
	out << "}\n";


	out << "#include \"cppmain.cpp\"\n" << endl;
	out.close();

}

#endif
#endif

/*
/allocator thread - facebook folly
https://github.com/google/dtask
http://stackoverflow.com/a/31688096
when we support multi-arg preds, can we use something like
x first_6 a b c d e f
x rest nil
in place of internalized lists, for comparable speed?


http://www.oldskool.org/pc/lz4_8088


*/