# -*- coding: utf-8 -*-

"""PYthon does the input, C++ does the Output"""

import cgen as c


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


def query(input_rules, input_query):
	out('#include "pyco_static.cpp"')
	for r in input_rules+input_query:
		"static " + r.kbdbg_name + "(cpppred_state & __restrict__ state);"
	for r in input_rules+input_query:
		void cppout_pred(string name, vector<Rule> rs)

def cppout_pred(name, rules):
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











/*can also use a much simpler version as in pyin for now, all the lists and consts stuff can go out*/


//think {?a x ?a. (?a) x b} => b x b
//locals: var (thats the ?a) | list header (size 1) | offset - 2 (pointing to the first var)  | nil
//consts:  b (node - a constant)
//a const in a list wont go into consts but stay in the list:
//{?a x ?a. (?a b) x b} => b x b
//locals: var (thats the ?a) | list header (size 2) | offset - 2 (pointing to the first var) | list bnode ("size" 1) | node b | nil
//consts: the node b


//Locals::Constructor
//Input: head, body
//To fill out: locals, consts, lm, cm
void make_locals(Locals &locals, Locals &consts, locals_map &lm, locals_map &cm, pquad head, pqlist body, bool head_goes_into_locals=true)
{
	FUN;

  //queue to load up our lists into.
	std::queue<toadd> lq;
  	//TRACE(dout << "head:" << format(head) << endl);

	/* Function definition region */
	//We make 3 function which we then apply later, so in reading this make_locals function,
	//treat this as if they're just some functions and skip past them until needed.




	//As long as there's still terms in lq, pop the 1st one off the list and
	auto expand_lists = [&lq, &locals, &lm]() {
		setproc("expand_lists");
		while (!lq.empty()) {
			//Pop the first node off of lq into ll.
			toadd ll = lq.front();
			lq.pop();

			//Grab the nodeid from the toadd.
			nodeid l = ll.first;

			//First item: bnode
			//2nd item: object related to that bnode by
			//rdffirst.
			//map<nodeid,nodeid> get_list(nodeid n)
			auto lst = get_list(l);

			//Make a thing
			Thing i0; // list size item, a sort of header / pascal string (array?) style thing
#ifdef KBDBG
			//Add the markup from the toadd to the thing.
			add_kbdbg_info(i0, ll.second);

			//What's this do
			unsigned long list_part = 0;
#endif
			//Why the size?

			//This will make the value of the Thing i0 the
			//number of items in the list, and put it in locals.
			//lm[l] = locals.size();
			make_this_list(i0, lst.size());
			locals.push_back(i0);
			lm[l] = locals.size()-1; // register us in the locals map

			//For each item in the list,
			for (auto list_item: lst) {
				nodeid bnode_id = list_item.first;
				nodeid li = list_item.second;
				TRACE(dout << "item..." << dict[bnode_id] << " : " << dict[li] << endl;)

#ifdef KBDBG

				Markup m = ll.second;
				//m.push_back(list_part++);
#endif
				//Create a Thing for the bnode of the item
				//and put it in locals.

				//we add bnodes that simulate rdf list structure
				Thing bnode = create_list_bnode(bnode_id);
				locals.push_back(bnode);


				//Create a Thing for the list item and put
				//it in locals.
				Thing t;
				if (li < 0) {
					TRACE(dout << "its a var" << endl);
					auto it = lm.find(li); //is it already in locals?
					if (it == lm.end()) { //no?
						MSG("create a fresh var")
						t = create_unbound();
						lm[li] = locals.size();
					}
					else { //yes? just point to it
					//hrmm
						make_this_offset(t, ofst(it->second, locals.size()));
					}
				}
				else { //its a node
					t = create_node(li);
					if (islist(li))
						#ifdef KBDBG
						lq.push(toadd(li, m));
						#else
						lq.push(toadd(li, {}));
						#endif
				}

#ifdef KBDBG
				add_kbdbg_info(t, m);
#endif
				locals.push_back(t);

			}

			//final nil
			Thing nil = create_node(rdfnil);
			locals.push_back(nil);

		}
	};

	//replace NODEs whose terms are lists with OFFSETs. expand_lists left them there.
	auto link_lists = [&locals, &lm]() {
		//For each Thing in locals:
		for (pos_t  i = 0; i < locals.size(); i++) {
			Thing &x = locals[i];
			if (is_node(x) && islist(get_node(x))) {
				make_this_offset(x, ofst(lm.at(get_node(x)), i));
			}
		}
	};


	//typedef map<nodeid, pos_t> locals_map;
	//typedef vector<Thing> Locals;

	//Why do we pass var to this when we pass xx to it and we could
	//just check x < 0
	//make a Thing out of our node (toadd) xx
	auto add_node = [](bool var, toadd xx, Locals &vec, locals_map &m) {
		setproc("add_node");

		//Make a blank Thing
		Thing t;

		//add the Markup from xx to t.
		add_kbdbg_info(t, xx.second);

		//Get the nodeid of our toadd
		nodeid x = xx.first;
//		TRACE(dout << "termid:" << x << " p:" << dict[x->p] << "(" << x->p << ")" << endl;)

		//Check to see if the termid is already in the map (locals/consts).
		//If it's not then add it.
		auto it = m.find(x);
		if (it == m.end()) {
			//This will give the position in vec that the Thing
			//will go, and m will map termid's to their position in
			//vec.
			m[x] = vec.size();

			//Create a Thing for this nodeid and push it to the back
			//of vec.
			//If it's a var it'll be unbound ofc. Bound variables
			//only happen during query.
			if(var)
				t = create_unbound();
			//If it's not a var it'll be a node, remember we're
			//not handling lists here.
			else
				t = create_node(x);

			//add the Markup from xx to t.
			//mm I think we did that already.
			//yea I think this is redundant.
			//we did it but for a different t
			//anyway, just dont worry about kbdbg
			add_kbdbg_info(t, xx.second);

			//Push the thing into our Locals vec.
			//We should have the equation:
			// t = vec[m[x]]
			vec.push_back(t);
		}
		//Are we normally not expecting the else condition?
//We only make offsets if KBDBG is defined?
//What are we doing if it's not KBDBG and the var's already in there?
//with kbdbg, every single occurence of a var in the rule has to have its
//own representation in locals, we cant just re-use the same position
#ifdef KBDBG
		else
		{
			//hrmm
			make_this_offset(t, ofst(it->second, vec.size()));
			//I think this would also be redundant.
			add_kbdbg_info(t, xx.second);
			vec.push_back(t);
		}
#endif
	};


	/* Execution region */

	//typedef vector<unsigned long> Markup;
	//typedef std::pair<nodeid, Markup> toadd;
	//Should call this nodes maybe?
	//We're going to put every node (subj/obj) used by the rule into this
	//vector.
	vector<toadd> terms;


	//Need to understand this kbdbg stuff

	//Store the value of the global before we modify it
	//unsigned long old_kbdbg_part = kbdbg_part;

	//Make a toadd for both the subject and object for each term in the
	//rule (both head & body), and push these into terms vector.
	//Increment kbdbg_part for each node added to terms, place this
	//value into a vector, and set that as the Markup for the toadd.
	//What's the Markup doing?
	if (head)
	{
		kbdbgp("head");
		kbdbgp("subject");
		terms.push_back(toadd(dict[head->subj], kbdbg_stack));
		kbdbgpop();
		kbdbgp("object");
		terms.push_back(toadd(dict[head->object], kbdbg_stack));
		kbdbgpop();
		kbdbgpop();
	}

	if(body)
	{

	kbdbgp("body");

	unsigned long i=0;
	for (pquad bi: *body)
	{
		kbdbgp("item",i++);
		kbdbgp("subject");
		terms.push_back(toadd(dict[bi->subj], kbdbg_stack));
		kbdbgpop();
		kbdbgp("object");
		terms.push_back(toadd(dict[bi->object], kbdbg_stack));
		kbdbgpop();
		kbdbgpop();
	}
	kbdbgpop();

	}

	TRACE(dout << "terms.size:" << terms.size() << endl);

	//For all our terms (toadds) in terms, if the term is not
	//a variable or a list, then "add_node(false, xx, locals, lm)".
	//If the term is a variable, then "add_node(true, xx, locals, lm)".
	//If it's a list, then push it to lq to be processed later.
	//std::pair<nodeid,Markup>



	for (toadd xx: terms)
	{
		nodeid x = xx.first;
		//If not a variable & not a list, then we'll make a 'constant' thing, i.e. add_node(false,...)
		//only says it's a list if it's in the head
		//no it definitely says its a list if its in @default
		//hmm
		if (x > 0 && !islist(x)) {

//islist() only tells us its a list if it's in the head?

//what's with consts & cm?
//not sure this whole KBDBG switch going on here

#ifndef KBDBG
			//force rule s and o into locals for now
		//If it's not a var, not a list, and is in the head, then
		//put it in locals. Why? //i guess just so i didnt have to complicate or make permutations of the rule lambda where it unifies the rule arguments against this
		//Why would we have !head? //for query top level
			if (head_goes_into_locals && head && (x == dict[head->subj] || x == dict[head->object]))
				add_node(false, xx, locals, lm);
		//If it's not a var, not a list, and is not in the head, then
		//put it in consts. Why?
			else
				add_node(false, xx, consts, cm);
#else
			//And why #ifdef KBDBG they both go into locals? simplicity
			add_node(false, xx, locals, lm);
#endif
		}
		//Is a variable, so we'll make a variable thing, i.e. add_node(true,...)
		else if (x < 0)
			add_node(true, xx, locals, lm);

		//Is a list, we'll push it to lq and save it for expand_lists() and link_lists()
		//only says it's a list if it's in the head
		else if (x > 0 && islist(x))
			lq.push(xx);
		else
			assert(false);
	}



	expand_lists();
	link_lists();



	TRACE(print_locals(locals, consts, lm, cm, head);)
}













http://www.cplusplus.com/reference/thread/thread/
