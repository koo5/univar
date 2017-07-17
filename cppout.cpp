#ifdef CPPOUT
#define CPPOUT2
#ifdef CPPOUT3

/*todo:

???
unify bm?
s and o re-fetching
???


 unify is still a bitch, could we use a switch?
 (on some aggregate value computed/masked from the two things


  * http://stackoverflow.com/questions/8019849/labels-as-values-vs-switch-statement
	: avoid the range check of 'entry' inherent in the switch(entry) statement

  * reuse one consts array throughout the pred func


oneword2:
<maybekoo2> so, preallocator thread can pre-resolve all offsets into variables
<maybekoo2> unbound shouldnt be identified by all zeroes but something like xxx01
<maybekoo2> so, not the same typebits pattern as bound
<maybekoo2> so, getValue only has to do one cmp instead of 3
getValue:
 00 = bound at runtime, at compile/alloc time also offset. its *the* pointer, no masking needed
unify:
 01 = unbound
 10 = node
(???)
 11 = list bnode(containing only remaining list size)


*/

struct Query;
struct Search;
{


}

static Thing *cppout_getValue (Thing *_x)
{
       ASSERT(_x);

       Thing x = *_x;

       // return the value of it's value.
       if (is_bound(x)) {
               //get the pointer
               Thing * thing = get_thing(x);
               ASSERT(thing);
               //and recurse
               return getValue(thing);
       }

       else
               return _x;
}
               
       

typedef cppout3Thing void*;
static Thing *get_value (cppout3Thing x) __attribute__ ((pure));
static Thing *get_value (cppout3Thing x)
{
    /*reorder this based on usage statistics*/
    auto y = x & 0b11;
	if(y)
		return x;
	else
	{
		auto y = *x;
		return cppout3getValue(y);
	}
}

bool would_unify(const Thing *old_, const Thing *now_)
{
	FUN;

	const Thing old = *old_;
	const Thing now = *now_;

	ASSERT(!is_bound(now));

	if(is_var(old) && is_var(now))
		return true;
	else if (is_node(old))
		return are_equal(old, now);
	else if (types_differ(old, now)) // in oneword mode doesnt differentiate between bound and unbound!
		return false;
	ASSERT(false);
}

bool cppout_find_ep(const ep_t *ep, const Thing *s, const Thing *o)
{
	FUN;

	ASSERT(!is_bound(*s));
	ASSERT(!is_bound(*o));

	EPDBG(endl << endl << ep->size() << " ep items." << endl);

	for (auto i: *ep)
	{
		auto os = i.first;
		auto oo = i.second;
//		ASSERT(!is_offset(*os));
//		ASSERT(!is_offset(*oo));
		//what about !is_bound

		//TRACE(dout << endl << " epitem " << str(os) << "    VS     " << str(s) << endl << str(oo) << "    VS    " << str(o) << endl;)
		EPDBG(endl << " epcheck " << str(os) << "    VS     " << str(s) << endl << " epcheck " << str(oo) << "    VS    " << str(o) << endl;)

//reorder
		if (!would_unify(os,s) || !would_unify(oo,o))
		    continue;
		return true;
	}
	return false;
}


#endif
#ifdef CPPOUT2


/*may want to reorder this based on usage statistics*/



bool cppout_would_unify(const Thing *old_, const Thing *now_)
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




bool cppout_find_ep(const ep_t *ep, const Thing *s, const Thing *o)
{
	FUN;

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
	if (key == LOCAL)
		ss << "(&state.locals[" << thing_index << "])";
	else if (key == CONST)
		ss << "(&consts_" << predname << "_" << rule_index << "[" << thing_index << "])";
	else assert(false);
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
		out << "static const Locals consts_" << name << "_" << i << " = " << things_literals(consts) << ";\n";
	}
}


char unify_with_var(Thing * a, Thing * b)
{
    ASSERT(is_unbound(*b));
    
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
			out << "static int counter = 0;\n";



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
			//out << "if (!(counter & 0b11111111111))";
			out << "{";
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
				out << "bis = cppout_getValue(" << param(sk, i1, name, i) << ");\n";
				out << "bio = cppout_getValue(" << param(ok, i2, name, i) << ");\n";

				out << "Thing n1; if (is_unbound(*bis)) {bis = &n1; n1 = create_node(" << ensure_cppdict(dict[bi->subj]) << ");};\n";
				out << "Thing n2; if (is_unbound(*bio)) {bio = &n2; n2 = create_node(" << ensure_cppdict(dict[bi->object]) << ");};\n";

				out << "if (!silent) dout << str(bis) << \" " << bi->pred->tostring() << " \" << str(bio) << \".\";};\n";
			}
			out << "if (!silent) dout << \"\\n\";}\n";
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

/*




In [4]: #pred1906 size

In [5]: (0x43bf9d - 0x43bc00)/8
Out[5]: 115.625




unify_with_const etc asserts !bound, what if we got s and o both pointing to the same unbound var, 
then bound it?

otoh, we can drop the unbinds and binds of the outer param (s) that happen between yields in a fact pred
so, unify_with_const(orig_s, state.s, const), decides based on orig_ but acts on state

also, the eventual unbind at the end can be just an assignment of the old value

facts, table or not to table
unrolling - only fact runs?

btw, for forward compatibility you may not *use* a pointer with arbitrary information in high bits, but 


*/



#else

void yprover::cppout(qdb &goal)
{
	FUN;
	(void)goal;
	dout << "not compiled with -DCPPOUT." << endl;
	

}

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