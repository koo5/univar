#ifndef NOPARSER
#include <string>
#include <iostream>
#include <set>
#include <stdexcept>
#include "rdf.h"
#include <boost/algorithm/string.hpp>
#include "jsonld.h"
#include "misc.h"
using namespace boost::algorithm;


nqparser::nqparser() : t(new char[4096/*wat*/*/*da*/4096]) {/*fuck*/}
nqparser::~nqparser() { delete[] t; }


/*
iswspace: 
    space 		0x20, ' '
    form feed 		0x0c, '\f'
    line feed 		0x0a, '\n'
    carriage return 	0x0d, '\r'
    horizontal tab 	0x09, '\t'
    vertical tab 	0x0b, '\v' 
*/

//should be 'nqparser::readcontext'
//ws*,{~'{'},return
//ws*,'{',ws*,'}',return
//ws*,'{',ws*,{~'}'}, << (*this)(s,*r) >>
pnode nqparser::readcurly(qdb& kb) {
	setproc("readcurly");
	//Skip any white-space at the beginning of the line:
	while (iswspace(*s)) ++s;

	//If the next char is not '{' then this is not a syntactically
	//correct context, return "(pnode)0".
	if (*s != '{') return (pnode)0;
	++s;

	//Skip any white-space at the beginning of the context:
	while (iswspace(*s)) ++s;

	//**needs comments**
	//Create a unique blank-node ID for this context
	auto r = gen_bnode_id();

	//If the next character is '}' then move the string-pointer past '}',
	//make a bnode for r, and return this.
	if (*s == '}') { ++s; return mkbnode(r); }

	//This needs to be fixed
	//This says that any string that the parser would accept as valid syntax
	//can be placed inside a curly, and this new string will also be accepted
	//as valid syntax.
	
	_parse(kb, *r);

	return mkbnode(r);
}


// {~'('}, return
// '(',ws*,')',return

//(ws*,{~')'},readany_success,ws*,(('.',ws*)|{~('.' | '}'}),{~')'})* as X

// '(',ws*,{~')'},X,ws*,')',break,ws*
// '(',ws*,{~')'},X,ws*,{~')'},readany_error,error

// '(',ws*,{~')'},X,ws*,{~')'},readany_success,ws*,{'}'},error
// '(',ws*,{~')'},X,ws*,{~')'},readany_success,ws*,(('.',ws*)|{~('.' | '}'}),{')'},ws*

pnode nqparser::readlist(qdb& kb) {
	setproc("readlist");

	//We don't skip over any white-space here?

	//If the first character is not '(', then we assume it's not
	//a list and return "(pnode)0".
	if (*s != '(') return (pnode)0;
	++s;

	//**needs comments**
	int lpos = 0;
	listid();
	const string head = list_bnode_name(lpos);

	pnode pn;

	//Skip over any white-space
	while (iswspace(*s)) ++s;

	//If the next character is ')' then I guess we have
	//an empty list and we return RDF_NIL.
	if (*s == ')') {
		 ++s;
		return mkiri(RDF_NIL); 
	}

	do {
		//Skip over any white-space
		while (iswspace(*s)) ++s;

		//If the next character is ')' then we've reached the end
		//of the list, break.
		if (*s == ')') {
			break;
		}

		//Here's why we can't have contexts in lists right now:
		//readany() does not read contexts. If we had a context there
		//then i think it would try to read it as an IRI and fail.
		//Attempt to readany(true) into pn. If we fail, throw an error.
		if (!(pn = readany(kb, true)))
			//or literal apparently?
			throw std::runtime_error(string("expected iri or bnode or list in list: ") + string(s,0,48));
		
		//**needs comments**
		pnode cons = mkbnode(pstr(list_bnode_name(lpos)));

		//**needs comments**
		lists.emplace_back(cons, mkiri(RDF_FIRST), pn);//then we create first triple?

		//**needs comments**
		kb.second[head].push_back(pn);
		//qlists[head].push_back(pn);//and into qdb.second i presume we add the item too

		++lpos;

		//Skip over any white-space.
		while (iswspace(*s)) ++s;

		//**needs comments**
		if (*s == ')') lists.emplace_back(cons, mkiri(RDF_REST), mkiri(RDF_NIL));//end

		else lists.emplace_back(cons, mkiri(RDF_REST), mkbnode(pstr(list_bnode_name(lpos))));

		//**needs comments**
		//If the next character is '.', then read that and skip over any white-space
		//following it.
		if (*s == '.'){
			s++;
			while (iswspace(*s++));
		}

		//If the next character is '}', then throw a run-time error.
		//**needs comments**
		if (*s == '}') throw std::runtime_error(string("expected { inside list: ") + string(s,0,48));

	}
	//Can we encounter an infinite loop here? Let's find out.
	while (*s != ')');//id be more worried about this endless loop :)
		

	//Skip over any white-space.
	do { ++s; } while (iswspace(*s));

	return mkbnode(pstr(head));
}



//(iswspace | ',' | ';' | '.' | '}' | '{' | ')') as special

//iswspace*, 0, error
//iswspace*, {!0}, '<',!('>')*,'>', return
//iswspace*, {!0}, {!'<'}, "=>", return
//iswspace*, {!0}, {!'<'}, !{"=>"}, (~special)*, {"true"}, return
//iswspace*, ..., (~special)*, {~("true")}, {"false"}, return
//iswspace*, ..., (~special)*, {~("true" | "false")}, {atoi}, return
//iswspace*, ..., (~special)*, {~("true" | "false" | atoi)}, {atof}, return
//iswspace*, ..., (~special)*, {~("true" | "false" | atoi | atof)}...other tokenization,
//		**the string-pointer has already advanced as far as it will go in
//		**readiri(), the rest is tokenization.
pnode nqparser::readiri() {
	setproc("readiri");
	//Skip any white-space at the beginning of the line:
	while (iswspace(*s)) ++s;


	//If *s==0 then fail. I.e. our char pointer has nothing to point to.
	if (*s == 0)
		throw std::runtime_error("iri expected");


	//If our next char is '<', then we're expecting an IRI
	if (*s == '<') {
		while (*++s != '>')
		//until bracket, copy s to t
		//*note: increments 'pos' *after* storing '*s'.
		//**therefore "t[pos] = 0;" is not overwriting anything
			t[pos++] = *s;
		//append a null
		t[pos] = 0; 
		pos = 0;
		//Move pointer past the '>'.
		++s;
		return mkiri(wstrim(t));
	}

	
	//"@prefix: =>" ?
	//If the next two chars are '=>', then this is an implication.
	else if (*s == '=' && *(s+1) == '>')
	{ 
		++++s; return mkiri(pimplication); 
	}
	

	//Okay so we didn't hit a '<' bracket, and we didn't get an implication, so
	//copy whatever else we've got from s into t until we hit either white-space or
	//one of these special chars: ",;.}{)". What about "("?	
	while (!iswspace(*s) && *s != ',' && *s != ';' && *s != '.' && *s != '}' && *s != '{' && *s != ')') t[pos++] = *s++;
	t[pos] = 0; pos = 0;
	pstring iri = wstrim(t);


	//Check if the string you found represents one of these literal values:
	//Why literals when we're doing readiri?
	if (lower(*iri) == "true")
		return mkliteral(pstr("true"), XSD_BOOLEAN, 0);
	if (lower(*iri) == "false")
		return mkliteral(pstr("false"), XSD_BOOLEAN, 0);
	if (std::atoi(ws(*iri).c_str()))
		return mkliteral(iri, XSD_INTEGER, 0);
	if (std::atof(ws(*iri).c_str()))
		return mkliteral(iri, XSD_DOUBLE, 0);
	//??if (*iri == "0") return mkliteral(iri, XSD_INTEGER, 0);


	//So we didn't determine it to be a literal. Check if the string contains ':',
	//implying that the substring coming before ':' is a prefix.
	auto i = iri->find(':');
	
	//If we didn't find ':' then we'll have that "i == string::npos", and so
	//return mkiri() of the whole string.
	if (i == string::npos) return mkiri(iri);

	//Otherwise we did find ':', so we assume that the the substring coming before
	//this represents a prefix, and we'll copy this into 'p'.
	string p = iri->substr(0, ++i);

//	TRACE(dout<<"extracted prefix \"" << p <<'\"'<< endl);

	//Now check if that prefix is contained in nqparser::prefixes.
	auto it = prefixes.find(p);
	if (it != prefixes.end()) {
		//If it is, then prepend the value in nqparser::prefixes to the
		//the remainder of the string after ':', and take this as the value
		//for 'iri'.
//		TRACE(dout<<"prefix: " << p << " subst: " << *it->second->value<<endl);
		iri = pstr(*it->second->value + iri->substr(i));
	}

	//Make the iri and return it.
	return mkiri(iri);
}




//(iswspace | ',' | ';' | '.' | '}' | '{' | ')') as special.

//iswspace*, {~("_:")}, return
//iswspace*, "_:",(~special)*, return.
pnode nqparser::readbnode() {
	setproc("readbnode");

	//Skip any white-space at the beginning of the line:
	while (iswspace(*s)) ++s;

	//If the next two characters are not exactly "_:" then apparently it is not
	//a syntactically correct blank node, and we return "pnode(0)".
	if (*s != '_' || *(s+1) != ':') return pnode(0);
	//We don't need to advance s here because that will be taken care of in the while
	//loop. We can see that neither '_' nor ':' are any of the characters triggering
	//false in that conditional.

	//Copy characters from s into t until reaching either a whitespace character
	//or one of the special characters ",;.}{)".
	while (!iswspace(*s) && *s != ',' && *s != ';' && *s != '.' && *s != '}' && *s != '{' && *s != ')') t[pos++] = *s++;

	//Append a null character to t and set pos back to 0.
	t[pos] = 0; pos = 0;

	//Make a blank node from the bnode identifier string parsed into t, and return
	//this node.
	return mkbnode(wstrim(t));
}





//iswspace*, <!('@')>, return
//iswspace*, '@', <!("@prefix ")>, error
//iswspace*, "@prefix ", (~(':'|0|'\n'))*,(0|\n),error
//iswspace*, "@prefix ", (~(':'|0|'\n'))*, ':',(0|\n),error
//iswspace*, "@prefix ", (~(':'|0|'\n'))*, ':',~(0|\n), readiri()_error, error
//iswspace*, "@prefix ", (~(':'|0|'\n'))*, ':',~(0|\n), readiri()_success,(~('.'|'\n'|0))*,('.'|'\n'|0).
void nqparser::readprefix() {
	setproc("readprefix");

	//Skip any white-space at the beginning of the line:
	while (iswspace(*s)) ++s;

	//If the next char is not '@'. Then it's not a '@prefix' tag, so return.
	if (*s != '@') return;

	//Otherwise, check to see if the next 8 characters match "@prefix ". If
	//not, then the appearance of '@' is apparently syntactically incorrect
	//because we're throwing an error about it.
	if (memcmp(s, "@prefix ", 8*sizeof(*s)))
			throw std::runtime_error(string("\"@prefix \" expected: ") + string(s,0,48));

	//We didn't throw a run-time error, so the 8 characters must have matched "@prefix ".
	//Advance the string-pointer by 8, i.e. past the "@prefix ".
	s += 8;


	//Copy the string from s into t until reaching ":".
	//what about white-space		
	while (*s != ':' && *s!= 0 && *s!='\n') t[pos++] = *s++;
	if (!(*s!= 0 && *s!='\n'))
		throw std::runtime_error("hm");
	
	//Advance past the ':'
	t[pos++] = *s++;
	t[pos] = 0; pos = 0;
	
        if (!(*s!= 0 && *s!='\n'))
                throw std::runtime_error("hm");

	//Trim the resulting string
	pstring tt = wstrim(t);
	TRACE(dout<<"reading prefix: \"" << *tt<<'\"' << endl);

	//Expecting the next token to represent an IRI, so readiri and add it
	//to prefixes at key *tt.
	prefixes[*tt] = readiri();

	//Now that we've read the prefix, we're expecting to find a '.', so
	//just move our string-pointer past the '.'.
	while (*s != '.' && *s != '\n' && *s != 0) ++s;
	++s;
}




//(iswspace | '?' | ',' | ';' | '.' | '}' | '{' | ')') as special.
//(iswspace | ',' | ';' | '.' | '}' | '{' | ')') as special2.

//iswspace*, {~'?'},return
//iswspace*, '?', (~special)*,{'?'},error
//iswspace*, '?', (~special)*,{special2},return.
pnode nqparser::readvar() {
	setproc("readvar");
	//Skip any white-space at the beginning of the line:
	while (iswspace(*s)) ++s;

	//If the next character is not '?', then apparently it's not
	//a syntactically correct variable, so we return "pnode(0)"
	if (*s != '?') return pnode(0);
	s++; 

	//Copy characters from s into t until reaching either a whitespace character
	//or one of the special characters ",;.}{)".
	while (!iswspace(*s) && *s != '?' && *s != ',' && *s != ';' && *s != '.' && *s != '}' && *s != '{' && *s != ')') t[pos++] = *s++;
	if(*s == '?') throw std::runtime_error(string("bad variable name") + string(s,0,48));

	t[pos] = 0; pos = 0;

	//Make an IRI node for the var identifier string that we parsed into t, and return it.
	return mkiri(wstrim(t));
}



//(!iswspace | ',' | ';' | '.' | '}' | '{' | ')') as special

//iswspace*, {~'\"'}, return
//iswspace*, '\"',((~('\\' | '\"')) | ('\\', $))*, '\"',"^^",'<',(~'>')*,'>'
//iswspace*, '\"',((~('\\' | '\"')) | ('\\', $))*, '\"','@',(~iswspace)*
//iswspace*, '\"',((~('\\' | '\"')) | ('\\', $))*, '\"',~(special | "^^" | '@'), error
pnode nqparser::readlit() {
	setproc("readlit");

	//Skip any white-space at the beginning of the line:
	while (iswspace(*s)) ++s;

	//If the next char found is not a '\"', then it's apparently not a syntactically
	//correct literal, because we're returning 'pnode(0)'
	if (*s != '\"') return pnode(0);

	//Move the string ponter past the '\"'.
	++s;

	//Does this miss the string "\"\"" ?
	//Copy characters from s into t until you reach a '\"' that isn't preceded
	//by a '\\'. (Because \" is a literal quote character and not one of the
	//quotes delimiting the literal value).

	//do { t[pos++] = *s++; } while (!(*(s-1) != '\\' && *s == '\"'));

	while (!(*(s-1) != '\\' && *s == '\"')) t[pos++] = *s++;
	//Move the string-pointer past the '\"'.
	++s;

	string dt, lang;


//what loop?

	//As long as the next character is not whitespace and not one of the special
	//characters ",;.}{)" then:
	if (!iswspace(*s) && *s != ',' && *s != ';' && *s != '.' && *s != '}' && *s != '{' && *s != ')') {
		//If the next two characters are "^^", then:
		if (*s == '^' && *++s == '^') {
			//Check if the next character is '<', and if so then
			//copy characters from s into dt until reaching a '>' character.
			//Then move the string-pointer past the '>' and break from
			//the loop.
			if (*++s == '<')  {
				++s;
				while (*s != '>') dt += *s++;
				++s;
				//break;
			}
		//Otherwise, if the next character is '@', then copy characters
		//from s into lang until reaching a whitespace character. Then break
		//from the loop.
		} else if (*s == '@') {
			while (!iswspace(*s)) lang += *s++;
			//break;
		}

		//Otherwise we didn't receive either a langtag or an iri, so throw an error:
		else throw std::runtime_error(string("expected langtag or iri:") + string(s,0,48));
	}
	//Append a null character to t and set pos back to 0.
	t[pos] = 0; pos = 0;

	//Copy t into t1 and replace all occurrences of "\\\\" with "\\".
	string t1 = t;
	boost::replace_all(t1, "\\\\", "\\");
	//eww, this isnt how you unescape stuff

	//Make a literal node from the value, the IRI and the langtag, and return this node.
	return mkliteral(wstrim(t1), pstrtrim(dt), pstrtrim(lang));
}


pnode nqparser::readany(qdb& kb, bool lit){
	pnode pn;
	//Attempt to read a prefix tag.
	readprefix();

	//Try to read the next token using: readbnode(), readvar(), readlit(), readlist(), readcurly(),
	//and readiri(). If it fails, return "(pnode)0". Otherwise, return the node received into pn.
	if (!(pn = readbnode()) && !(pn = readvar()) && (!lit || !(pn = readlit())) && !(pn = readlist(kb)) && !(pn = readcurly(kb)) && !(pn = readiri()) )
		return (pnode)0;
	return pn;
}


void nqparser::preprocess(std::istream& is, std::stringstream& ss){
        string s; //get lines from is into s.

        //Make a function out of this
        //Iterate over lines coming from is, placing them into s, and
	//accumulating these strings into ss.
        while (getline(is, s)) {
                //dout << "line:\"" << s << "\"" << std::endl;

                //Trim white-space on the line.
                //(in what specific manner?)
                trim(s);

                //If it's an empty line or a comment then continue.
                if (!s.size() || s[0] == '#') continue;

                //Check to see if the line is "fin." or some variation where
                //white-space separates "fin" from "." (...?), and if so
                //break.
                if (startsWith(s, "fin") && *wstrim(s.c_str() + 3) == "."){
                        break;
                }
		//dout << s << endl;
                //Otherwise, add this line into ss. 
                //(more trailing white-space).
                ss << ' ' << s<< ' ';

	}
}


void nqparser::parse(qdb& kb, std::istream& is){
	std::stringstream ss;
	preprocess(is,ss);
	string x = ss.str();//weird
	s = x.c_str();
	_parse(kb, "@default");
}

void nqparser::_parse(qdb& kb, string ctx){
	std::list<std::pair<pnode, plist>> preds;

	string graph;
	pnode subject, pn;
	pos = 0;

	//Get a reverse_iterator pointing to the last element in preds into pos1.
	auto pos1 = preds.rbegin();

	if (s){
	while(*s) {
		//This is expecting to read a subject node immediately by using readany(false).
		//Try to read any node except a literal into subject. RDF subjects can only
		//be IRIs or blank-nodes. If we fail to read a node, then throw an error.
		if (!(subject = readany(kb, false)))
			throw std::runtime_error(string("expected iri or bnode subject:") + string(s,0,48));

		//This is expecting to be looping over the predicate-object pairs given for this subject,
		//separated by ';' i.e. like "subject pred1 obj1; pred2 obj2;" or
		// "subject pred1 obj1a, obj1b, obj1c; pred2 obj2a, obj2b, obj2c." etc.
		//This loop is over the preds, i.e. "subject pred1 ...; pred2 ...; ...."
		//and you'll see in the do-condition that reading ';' is what iterates the loop.
		do {
			while (iswspace(*s) || *s == ';') ++s;

			//On the first time around this might just be subject-nothing-nothing	
			//If we reach either the end, a '.', or a '}', then break.
			if (!*s || *s == '.' || *s == '}') break;
	
			//readcurly() here?
			//Otherwise, try to readiri() and then try to readcurly().
			if ((pn = readiri()) || (pn = readcurly(kb))) {
				//If one of them succeeds, we'll have a node in 'pn', and we'll
				//stick this node along with an empty list on the back of preds.
				//This list will hold all the object nodes captured in the
				//following do-loop.
				preds.emplace_back(pn, plist());

				//Set pos1 to the back of the list
				pos1 = preds.rbegin();
			}
			//If both readiri() and readcurly() fail, then throw an error.
			else throw std::runtime_error(string("expected iri predicate:") + string(s,0,48));

			//This loop is over the objects for each predicate, and you can see
			//in the do-condition that it iterates on ending up at a ','.
			do {
				//Skip the following characters until reading something besides
				//whitespace and ','.
				while (iswspace(*s) || *s == ',') ++s;
				
				//*On the first time around this would be subject-predicate-nothing
				//If that character is '.' or '}' then break.
				if (*s == '.' || *s == '}') break;

				//Otherwise, it's some other character, try to read a node
				//into 'pn' using readany(true). (Can be either IRI, blank node,
				//or literal).
				if ((pn = readany(kb, true))) {
					//If we successfully read a node, then we place it on
					//the back of the plist() we made for our predicate.
					pos1->second.push_back(pn);
				}

				//If we can't read a node using readany(true), then throw an error.
				else throw std::runtime_error(string("expected iri or bnode or literal object:") + string(s,0,48));
				//Skip any more white-space following this.
				while (iswspace(*s)) ++s;

			//If the next character is ',', then repeat.
			//i.e. expecting to capture another object.
			} while (*s == ',');

			//Okay, we did that do-sequence and finally exited because when we
			//checked the conditional, the character was something other than ','.
			//Skip any more white-space following this.
			while (iswspace(*s)) ++s;

		//If the next character is ';', then repeat.
		//i.e. expecting to capture another predicate and object list.
		} while (*s == ';');

		//Okay, we did that do-sequence and finally exited because when we checked
		//the conditional, the character was something other than ';'. Check to see
		//if the next character is either '.' or '}' or if we hit the end of the file.

		if (*s != '.' && *s != '}' && *s) {

			//We did not get any of those, and so we'll try to read either a blank node
			//or an IRI node into pn. We're attempting to read a context label. If that 
			//fails, we throw an error, otherwise we copy the value of this node into 'graph'.
			if (!(pn = readbnode()) && !(pn = readiri()))
				throw std::runtime_error(string("expected iri or bnode graph:") + string(s,0,48));

			graph = *pn->value;
		} else
			//The next character was either '.' or '}', and so we copy the
			//value of 'ctx' into 'graph'.
			graph = ctx;

		if (kb.first.find(graph) == kb.first.end()) kb.first[graph] = make_shared<qlist>();
		for (auto d : lists){
			quad dquad = quad(std::get<0>(d), std::get<1>(d), std::get<2>(d), graph);
			kb.first[graph]->push_back(make_shared<quad>(dquad));
		}
				//r.emplace_back(std::get<0>(d), std::get<1>(d), std::get<2>(d), graph);

		for (auto x : preds){
			for (pnode object : x.second){
				quad xquad = quad(subject, x.first, object, graph);
				kb.first[graph]->push_back(make_shared<quad>(xquad));
			}
		}
				//r.emplace_back(subject, x.first, object, graph);
		lists.clear();
		preds.clear();

		
		//Skip all following white-space, the character '.' if it's there, and 
		//then skip all white-space following that.
		while (iswspace(*s)) ++s;

		if(*s == '.') ++s; 
//what about white-space between the '.' how many are you expecting? well, not sure if this parser is attempting to follow any spec, but personally im not expecting more than one
		//according to this as many as i want
		while (iswspace(*s)) ++s;

		//Okay we're past the white-space and the '.', 
		//return here?
		if (*s == '}') { ++s; /*rr = { r, qlists };*/ }
		if (*s == ')') throw std::runtime_error(string("expected ) outside list: ") + string(s,0,48));
	}
	}
}
#endif
