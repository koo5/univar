/*so, err, writing of these _for_external files only works for a one-file test case, not if youd do kb filename, query filename..
*/




#include <stdio.h>
#include <sstream>
#include <tuple>
#include <iostream>
#include <queue>
#include <stack>
#include <set>
#include <stdexcept>

#include "univar.h"
#include "jsonld_tau.h"

#ifdef with_marpa
#include "marpa_tau.h"
#endif

#include <boost/algorithm/string/predicate.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>

#include "pstreams-0.8.1/pstream.h"


#ifdef debug_cli
#define CLI_TRACE(x) TRACE(x)
#else
#define CLI_TRACE(x)
#endif

int query_counter;

string current_file_name;

// to hold a kb/query string
string qdb_text;

enum Mode {COMMANDS, KB, QUERY, SHOULDBE, OLD, RUN};

string format = "";
string base = "";

bool irc = false;

int result_limit = 123;
std::set<string> silence;
bool in_silent_part = false;
std::ostream& dout = std::cout;
std::ostream& derr = std::cerr;
std::istream& din = std::cin;


bool nocolor = false;
bool fnamebase = true;//?

extern bool have_builtins;

std::map<string,bool*> _flags = {
		 {"nocolor",&nocolor}
		,{"deref",&deref}
		,{"irc",&irc}
		,{"shorten",&shorten}
		,{"base",&fnamebase}
		,{"builtins",&have_builtins}
};
typedef std::pair<int*, string> IOP;
std::map<string,IOP> int_flags = {
		  {"level",IOP(&level,"debug level")}
};

std::vector<string> extensions = {"jsonld", "natural3", "natq", "n3", "nq"};
std::vector<string> _formats = {
								#ifdef with_marpa
								"n3",
								#endif
								#ifndef NOPARSER
								"nq",
								#endif
								#ifdef JSON
								"jsonld"
								#endif
};


yprover *tauProver = 0;

std::vector<qdb> kbs;

bool done_anything = false;

results_t cppout_results;
results_t external_results;


class Input
;
std::stack<Input *> inputs;
#define INPUT (inputs.top())



class Input
{
public:
//Structure
	bool interactive = false;
	bool do_reparse = true;
	bool do_cppout = false;
	string external;
	bool do_query = true;
	bool do_test = true;
	std::string name;
	Mode mode = COMMANDS;
	int limit = 123;//this should be hierarchical tho
	

	virtual string pop() = 0;
	virtual string pop_long() = 0;
	virtual void take_back() = 0;
	virtual void readline()	{};
	virtual bool end() = 0;
	virtual bool done() = 0;

	Input()
	{
		if(inputs.size()) {
			//these should be inherited from parent input
			limit = INPUT->limit;
			do_cppout = INPUT->do_cppout;
			external = INPUT->external;
			do_query = INPUT->do_query;
			do_test = INPUT->do_test;
		}
	}
};

class ArgsInput : public Input
{
public:
	int argc;
	char **argv;
	int counter = 1;


	ArgsInput(int argc_, char**argv_)
	{
		argc = argc_;
		argv = argv_;
		name = "args";
	}


	bool end()
	{
		return counter == argc;
	}
	bool done()
	{
		return end();
	}
	string pop()
	{
		assert(!end());
		return argv[counter++];
	}
	string pop_long()
	{
		return pop();
	}
	void take_back()
	{
		counter--;
		assert(counter);
	}
};



class StreamInput : public Input
{
public:
	std::istream& stream;
	string line;
	size_t pos;
	std::stack<size_t> starts;

	void figure_out_interactivity()
	{
		//if its a file
		std::ifstream* s = dynamic_cast<std::ifstream*>(&stream);
		interactive = !s;
		//else its stdin
		if (!s) {
			//assert(stream == std::cin);//sometimes doesnt compile
			//but its not attached to a tty
			if (!isatty(fileno(stdin)) && !irc)
				interactive = false;
		}
	}

	StreamInput(string fn_, std::istream& is_) : stream(is_)
	{
		name = fn_;
		figure_out_interactivity();
	}
	bool done()
	{
		return stream.eof();
	}
	bool end()
	{
		bool r = pop_long() == "";
		take_back();
		return r;
	}

	void readline()
	{
		std::getline(stream, line);
		while(!starts.empty()) starts.pop();
		pos = 0;

		auto m = stream.rdbuf()->in_avail();
		//TRACE(dout << m << endl);
		do_reparse = interactive && m <= 0;
		/* got_more_to_read()? this isnt guaranteed to work.
		 * i would just use select here, like http://stackoverflow.com/a/6171237
		 * got any crossplatform idea?
		 */
	}
	string pop_x(char x)
	{

		while(line[pos] == ' ') pos++;
		size_t start = pos;
		while(line[pos] != x && line[pos] != '\n' && line[pos] != 0) pos++;
		size_t end = pos;
		string t = line.substr(start, end);
		starts.push(start);
		return t;
	}
	string pop()
	{
		return pop_x(' ');
	}
	string pop_long()
	{
		return pop_x(0);
	}
	void take_back()
	{
		assert(starts.size());
		pos = starts.top();
		starts.pop();
	}
};















void fresh_prover()
{
	if (tauProver)
		delete tauProver;
	dout << "constructing prover" << endl;
	tauProver = new yprover(merge_qdbs(kbs));
}


void set_mode(Mode m)
{
	dout << "#mode = ";
	switch(m) {
		case COMMANDS:
			dout << "commands";
			break;
		case KB:
			dout << "kb";
			break;
		case QUERY:
			dout << "query";
			break;
		case SHOULDBE:
			dout << "shouldbe";
			break;
		case OLD:
			dout << "old";
			break;
		case RUN:
			dout << "run";
			break;
	}
	dout << endl;
	INPUT->mode = m;
}

void help(){
	if(INPUT->end()){
		dout << "Help -- commands: kb, query, help, quit; use \"help <topic>\" for more detail." << endl;
		dout << "command 'kb': load a knowledge-base." << endl;
		dout << "command 'query': load a query and run." << endl;
		dout << "command 'help': Tau will help you solve all your problems." << endl;
		dout << "command 'quit': exit Tau back to terminal" << endl;
		dout << "\"fin.\" is part of the kb/query-loading, it denotes the end of your rule-base" << endl;
	}
	else{
		string help_arg = INPUT->pop();
		string help_str = "";
		if(help_arg == "kb"){
			help_str = "command 'kb': load a knowledge-base.";
		}
		else if(help_arg == "query"){
			help_str = "command 'query': load a query and run.";
		}
		else if(help_arg == "help"){
			help_str = "command 'help': Tau will help you solve all your problems.";
		}
		else if(help_arg == "quit") {
			help_str = "command 'quit': exit Tau back to terminal";
		}
		else if(help_arg == "fin"){
			help_str = "\"fin.\" is part of the kb/query-loading, it denotes the end of your rule-base";
		}else{
			dout << "No command \"" << help_arg << "\"." << endl;
			return;
		}
		dout << "Help -- " << help_str << endl;
	}
}


void switch_color(){
	if(nocolor){
                KNRM = KRED = KGRN = KYEL = KBLU = KMAG = KCYN = KWHT = "";
	}else{
		KNRM = "\x1B[0m";
		KRED = "\x1B[31m";
		KGRN = "\x1B[32m";
		KYEL = "\x1B[33m";
		KBLU = "\x1B[34m";
		KMAG = "\x1B[35m";
		KCYN = "\x1B[36m";
		KWHT = "\x1B[37m";
	}
}

bool _shouldbe(results_t &results, qdb &sb) {
	if (sb.first.empty() && sb.second.empty()) {
		return results.empty();
	}
	dout << "results.size()" << results.size() << endl;
	if(!results.size())
		return false;
	auto r = results.front();
	results.pop_front();
	return qdbs_equal(r, sb);
}



void test_result(bool x) {
	dout << INPUT->name << ":test:";
	if (x)
		dout << KGRN << "PASS" << KNRM << endl;
	else
		dout << KRED << "FAIL" << KNRM << endl;
}


void shouldbe(qdb &sb) {
	if (INPUT->do_query) 
		test_result(_shouldbe(tauProver->results, sb));
	if (INPUT->do_cppout) {
		bool r = _shouldbe(cppout_results, sb);
		dout << "cppout:";
		test_result(r);
	}
	if (!INPUT->external.empty()) {
		bool r = _shouldbe(external_results, sb);
		dout << "external:";
		test_result(r);
	}
}

void thatsall()
{
	test_result(tauProver->results.empty());
}

void clear_kb(){
	kbs.clear();
}


#ifndef NOPARSER
ParsingResult parse_nq(qdb &kb, qdb &query, std::istream &f)
{
	//We can maybe remove this class eventually and just
	//use functions? idk..
	nqparser parser;
        try {
                parser.parse(kb, f);
        } catch (std::exception& ex) {
                derr << "[nq]Error reading quads: " << ex.what() << endl;
                return FAIL;
        }
        try {
                parser.parse(query, f);
        } catch (std::exception& ex) {
                derr << "[nq]Error reading quads: " << ex.what() << endl;
                return FAIL;
        }
        return COMPLETE;
}
#endif



ParsingResult _parse(qdb &kb, qdb &query, std::istream &f, string fmt)
{
	CLI_TRACE(dout << "parse fmt: " << fmt << endl;)
#ifdef with_marpa
    if(fmt == "natural3" || fmt == "n3") {
		//dout << "Supported is a subset of n3 with our fin notation" << endl;
		return parse_natural3(kb, query, f, base);
	}
#endif
#ifndef NOPARSER
	if(fmt == "natq" || fmt == "nq" || fmt == "nquads")
		return parse_nq(kb, query, f);
#endif
#ifdef JSON
	if(fmt == "jsonld"){
		return parse_jsonld(kb, f);
	}
#endif
	return FAIL;
}

string fmt_from_ext(string fn){
	string fn_lc(fn);
	boost::algorithm::to_lower(fn_lc);

	for (auto x:extensions)
		if (boost::ends_with(fn_lc, x))
			return x;

	return "";
}

ParsingResult parse(qdb &kb, qdb &query, std::istream &f, string fn) {
	base = "file://"+fn;
	string fmt = format;
	if (fmt == "")
		fmt = fmt_from_ext(fn);
	if (fmt != "")
		return _parse(kb, query, f, fmt);
	else
	{
		ParsingResult best = FAIL;
		for (auto x : _formats) {
			ParsingResult r = _parse(kb, query, f, x);
			if (r > best)
			{
				if (r==COMPLETE)
					return r;
				best = r;
			}
		}
		return best;
	}
	return FAIL;
}


ParsingResult get_qdb(qdb &kb, string fname){
	std::ifstream is(fname);

	if (!is.is_open()) {
		dout << "failed to open file." << std::endl;
		return FAIL;
	}

	qdb dummy_query;

	auto r = parse(kb, dummy_query, is, fname);
	dout << "qdb graphs count:"<< kb.first.size() << std::endl;

	/*
	int nrules = 0;
	for ( pquad quad :*kb.first["@default"])
		nrules++;
	dout << "rules:" << nrules << std::endl;
	*/

	return r;
}

/*
int count_fins()
{
	int fins = 0;
	std::stringstream ss(qdb_text);
	do {
		string l;
		getline(ss, l);
		if(!ss.good())break;
		std::trim(l);
		if (l == "fin.") fins++;
	}
	return fins;
}
*/
int count_fins()
{
	int fins = 0;
	string line;
	stringstream ss(qdb_text);
	while (!ss.eof()) {
		getline(ss, line);
		if (startsWith(line, "fin") && *wstrim(line.c_str() + 3) == ".")
			fins++;
	}
	return fins;
}

bool dash_arg(string token, string pattern){
	return (token == pattern) || (token == "-" + pattern) || (token == "--" + pattern);
}

/*
void get_int(int &i, const string &tok)
{
	try
	{
		i = std::stoi(tok);
	}
	catch (std::exception& ex)
	{
		dout << "bad int, " << endl;
	}
}
*/





bool read_option(string s){
	if(s.length() < 2 || s.at(0) != '-' || s == "--")
		return false;
	
	while(s.at(0) == '-'){
		s = s.substr(1, s.length()-1);
	}

	string _option = s;

	
	for(string x : _formats){
		if(x == _option){
			format = x;
			dout << "input format:"<<format<<std::endl;
			return true;
		}
	}

	if (!INPUT->end()) {
		string token = INPUT->pop();
	
		if(_option == "silence") {
			silence.emplace(token);
			CLI_TRACE(dout << "silence:";
			for(auto x: silence)
				dout << x << " ";
			dout << endl;)
			return true;
		}


		for( auto x : _flags){
			CLI_TRACE(dout << _option << _option.size() << x.first << x.first.size() << std::endl;)
			if(x.first == _option){
				*x.second = std::stoi(token);
				if(x.first == "nocolor") switch_color();
				return true;
			}
		}


		for( auto x : int_flags){
			if(x.first == _option){
				*x.second.first = std::stoi(token);
				dout << x.second.second << ":" << *x.second.first << std::endl;
				return true;
			}
		}


#define input_option_int(x, y, z) \
		\
		if(_option == x){ \
			INPUT->y = std::stoi(token); \
			dout << z << ":" << INPUT->y << std::endl; \
			return true; \
		} 
#define input_option_string(x, y, z) \
		\
		if(_option == x){ \
			INPUT->y = token; \
			dout << z << ":" << INPUT->y << std::endl; \
			return true; \
		} 

		input_option_int("cppout", do_cppout, "cppout");
		input_option_string("external", external, "external");
		input_option_int("lambdas", do_query, "lambdas");
		input_option_int("test", do_test, "test");
		input_option_int("limit", limit, "results limit");

		INPUT->take_back();
	}

	return false;
}



void do_run(string fn)
{
	

	std::ifstream &is = *new std::ifstream(fn);
	if (!is.is_open()) {//weird behavior with directories somewhere around here
		dout << "[cli]failed to open \"" << fn << "\"." << std::endl;
	}
	else {
		dout << "[cli]loading \"" << fn << "\"." << std::endl;
		inputs.push(new StreamInput(fn, is));
	}
}
//err
void run()
{
	set_mode(RUN);
}

void do_query(qdb &q_in)
{
	dout << "query size: " << q_in.first.size() << std::endl;
	result_limit = INPUT->limit;
	tauProver->query(q_in);
	done_anything = true;
	query_counter += 1;
}


void cmd_query(){
	if(kbs.size() == 0){
		dout << "No kb; cannot query." << endl;
	}else{
		query_counter++;
		if(INPUT->end()){
			set_mode(QUERY);
		}else{
			if(!INPUT->end()){
				string fn = INPUT->pop_long();
				qdb q_in;
				ParsingResult r = get_qdb(q_in,fn);
				if (r != FAIL)
					do_query(q_in);
			}
		}
	}
}


void add_kb(string fn)
{
	qdb kb;
	ParsingResult r = get_qdb(kb,fn);
	if (r != FAIL)
		kbs.push_back(kb);
}


void cmd_kb(){
	if(INPUT->end()){
		clear_kb();
		set_mode(KB);
	}else{
		string token = INPUT->pop();
		if(dash_arg(token,"clear")){
			clear_kb();
			return;
		}
		/*else if(dash_arg(token,"set")){
			clear_kb();
		}*/
		else if(dash_arg(token,"add")){
			//dont clear,
			if (INPUT->end())
				throw std::runtime_error("add what?");
			else
				add_kb(INPUT->pop_long());
		}else{
			clear_kb();
			add_kb(token);
		}	
	}
}


//print the prompt string differently to
//specify current mode:
void displayPrompt(){
	if (INPUT->interactive) {
		string prompt;
		switch(INPUT->mode) {
			case OLD:
				prompt = "old";
				break;
			case COMMANDS:
				prompt = "tau";
				break;
			case KB:
				prompt = "kb";
				break;
			case RUN:
				prompt = "run";
				break;
			case QUERY:
				prompt = "query";
				break;
			case SHOULDBE:
				prompt = "shouldbe";
				break;
		}
		std::cout << prompt;
		if (format != "")
			std::cout << "["<<format<<"]";
		std::cout << "> ";

	}
}




bool try_to_parse_the_line__if_it_works__add_it_to_qdb_text() //:)
{
	string x = qdb_text + INPUT->pop_long() + "\n";

	if (!INPUT->do_reparse) {
		qdb_text = x;
	}
	else {
		qdb kb, query;
		std::stringstream ss(x);
		int pr = parse(kb, query, ss, "");
		dout << "parsing result:" << pr << std::endl;
		if (pr) {
			qdb_text = x;
		}
		else {
			dout << "[cli]that doesnt parse, try again" << std::endl;
			return false;
		}
	}
	return true;
}










void emplace_stdin()
{
	inputs.push(new StreamInput("stdin", std::cin));
}




void passthru(string s)
{
	std::string line;
	redi::ipstream m(s);
	while (getline(m.out(), line))
		dout << line << endl;
	m.close();
}



void qdb_to_nq(std::ostream &o, const qdb &db)
{
	for ( auto x : db.first )
	{
		auto graph = x.second;
		if (graph->size())
			o << *graph << std::endl;
	}
}

void write_file(string text, string fn)
{
	std::fstream out(text);
	out.open(fn, std::fstream::out);
	out << text;
	out.close();
}

void write_out_qdb_text_without_fins(string fn)
{
	//string without_fin = cut_off_fin(qdb_text);
	int fin_pos = qdb_text.length() - 5;
	string fin = qdb_text.substr(fin_pos);
	if (fin.compare(string("fin.\n")) != 0)
		throw std::runtime_error(fin.c_str());
	write_file(qdb_text.substr(0, fin_pos), fn);
}

int main ( int argc, char** argv)
{
  //This should probably go logically with other initialization stuff.
	//Initialize the prover strings dictionary with hard-coded nodes.
	dict.init();
	
	epout = new std::ofstream();
	epout->open("epdbg");
	


	//start by processing program arguments
	inputs.emplace(new ArgsInput(argc, argv));

	while (true) {

		displayPrompt();
		INPUT->readline();

		//maybe its time to go to the next input
		while (INPUT->done()) {
			auto popped = inputs.top();
			inputs.pop();
			/*if there werent any args, drop into repl*/
			if (dynamic_cast<ArgsInput*>(popped))
				if (!done_anything)
					emplace_stdin();
			if (!inputs.size())
				goto end;

			displayPrompt();
			INPUT->readline();
		}


		if (INPUT->mode == COMMANDS) {
			string token = INPUT->pop();
			if (startsWith(token, "#") || token == "")
				continue;
			else if (read_option(token))
				continue;
			else if (token == "help" || token == "halp" || token == "hilfe")
				help();
			else if (token == "kb")
				cmd_kb();
			else if (token == "query")
				cmd_query();
			else if (token == "shouldbe")
				set_mode(SHOULDBE);
			else if (token == "thatsall")
				thatsall();
			else if (token == "run")
				run();
			else if (token == "shouldbesteps") {
				//test_result(std::stoi(read_arg()) == tauProver->steps_);
			}
			else if (token == "shouldbeunifys") {
				//test_result(std::stoi(read_arg()) == tauProver->unifys_);
			}
			else if (token == "quit")
				break;
			else if (token == "-")
				emplace_stdin();
			else {
				INPUT->take_back();
				//maybe its old-style input
				if (try_to_parse_the_line__if_it_works__add_it_to_qdb_text())
					set_mode(OLD);
				else
					dout << "[cli]that doesnt parse, try again" << std::endl;
				continue;
			}
		}
		else if (INPUT->mode == KB || INPUT->mode == QUERY || INPUT->mode == SHOULDBE) {
			try_to_parse_the_line__if_it_works__add_it_to_qdb_text();
			int fins = count_fins();
			if (fins > 0) {

				qdb kb,kb2;

				std::stringstream ss(qdb_text);
				auto pr = parse(kb, kb2, ss, INPUT->name);

				if(pr == COMPLETE) {
					if (INPUT->mode == KB) {
						write_out_qdb_text_without_fins("kb_for_external_raw.n3");				
						kbs.push_back(kb);
						fresh_prover();
					}
					else if (INPUT->mode == QUERY) {
						if (INPUT->do_query)
							do_query(kb);
						if (INPUT->do_cppout) {
							cppout_results.clear();	
							tauProver->cppout(kb);
							passthru("sleep 1; astyle out.cpp; rm cppout out.o");

							stringstream omg;
							omg << "  || echo  \"test:cppout:make:" << KRED << "FAIL:" << KNRM;
							string fff=omg.str();
							stringstream errss;
							errss << "make -e cppout" << fff << INPUT->name << "\"";
							passthru(errss.str());

							if (INPUT->do_test)
							{

							stringstream cmdss;
							cmdss << "./cppout" << fff << INPUT->name << "\"";
							redi::ipstream p(cmdss.str());

							std::string line;
							while (getline(p.out(), line)) {
								dout << line << endl;
								if (startsWith(line, " RESULT ")) {
									string result = line.substr(line.find(":") + 1);
									qdb kb, kb2, cppout;
									std::stringstream ss(result);
									auto pr = parse(cppout, kb2, ss, "cppout output");
									cppout_results.push_back(cppout);
								}
							}
							p.close();
							}
						}
						if (!INPUT->external.empty()) {
							external_results.clear();		
							std::fstream out;
							out.open("query_for_external.nq", std::fstream::out);
							qdb_to_nq(out, kb);
							out.close();
							out.open("kb_for_external.nq", std::fstream::out);
							qdb_to_nq(out, merge_qdbs(kbs));
							out.close();
							write_out_qdb_text_without_fins("query_for_external_raw.n3");				

							if (INPUT->do_test)
							{

							stringstream cmdss;
							cmdss << INPUT->external;
							cmdss << "  --identification ";
							cmdss << current_file_name << "_" << query_counter;
							cmdss << "  --base ";
							cmdss << current_file_name;

							redi::ipstream p(cmdss.str());

							std::string line;
							while (getline(p.out(), line)) {
								dout << line << endl;
								if (startsWith(line, " RESULT ")) {
									dout << "result detected" << endl;
									string result = line.substr(line.find(":") + 1);
									qdb kb, kb2, external_output;
									std::stringstream ss(result);
									auto pr = parse(external_output, kb2, ss, current_file_name);
									external_results.push_back(external_output);
								}
							}
							p.close();
							if (!p.rdbuf()->exited()){
								dout << "process didnt exit?" << std::endl;
								test_result(false);
							}else
							if (p.rdbuf()->status()){
								dout << "non-zero exit code" << std::endl;
								test_result(false);
							}
							}
						}
						done_anything = true;
					}
					else if (INPUT->mode == SHOULDBE) {
						shouldbe(kb);
					}
				}
				else
					dout << "error" << endl;
				qdb_text = "";
				set_mode(COMMANDS);
			}
		}
		else if (INPUT->mode == RUN) {
			current_file_name = INPUT->pop_long();
			query_counter = 0;
			if (current_file_name == "-")
				emplace_stdin();
			else
				do_run(current_file_name);
		}
		else {
			assert(INPUT->mode == OLD);
			try_to_parse_the_line__if_it_works__add_it_to_qdb_text();
			int fins = count_fins();
			if (fins > 1) {
				kbs.clear();
				qdb kb,kb2;
				std::stringstream ss(qdb_text);
				auto pr = parse(kb, kb2, ss, INPUT->name);
				dout << "querying" << std::endl;
				kbs.push_back(kb);
				fresh_prover();
				do_query(kb2);
				qdb_text = "";
				set_mode(COMMANDS);
			}
		}
	}


	end:
	if (tauProver)
		delete tauProver;
}
