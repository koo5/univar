#ifndef DEBUG
#define NDEBUG
#endif

#include <string>
#include <unordered_map>
#include <tuple>
#include <vector>
#include <cassert>
#include <iostream>
#include <fstream>
#include <ctime>
#include <chrono>

using namespace std;

#ifdef TRACE
#define IF_TRACE(x) ,x
#else
#define IF_TRACE(x)
#endif
#define ASSERT assert

extern size_t bnode_origin_counter;
string current_ep_comment;
unsigned long euler_steps = 0;
chrono::steady_clock::time_point last_ep_tables_printout = chrono::steady_clock::time_point::min();

chrono::steady_clock::time_point query_start_time;

string replaceAll(std::string str, const std::string& from, const std::string& to) {
    if(from.empty())
        return str;
    size_t start_pos = 0;
    while((start_pos = str.find(from, start_pos)) != std::string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length(); // In case 'to' contains 'from', like replacing 'x' with 'yx'
    }
    return str;
}

string jsonize_string(string str)
{
    return replaceAll(str, "\n", "<br>");
}

void print_ep_tables();

void print_euler_steps()
{
    chrono::steady_clock::time_point now = std::chrono::steady_clock::now();
    auto duration = chrono::duration_cast<std::chrono::seconds>(now - query_start_time).count();
    unsigned long long rate = duration ? (euler_steps / duration) : 0;
    cerr << euler_steps << " euler_steps, " << rate << "/s." << endl;
    #ifdef TRACE_EP_TABLES
        print_ep_tables();
    #endif
}

void maybe_print_euler_steps()
{
    chrono::steady_clock::time_point now = std::chrono::steady_clock::now();
    if (chrono::duration_cast<std::chrono::seconds>(now - last_ep_tables_printout).count())
    {
        last_ep_tables_printout = now;
        print_euler_steps();
    }
}


#ifdef TRACE_PROOF

string trace_string;
ofstream trace;
size_t current_trace_file_id = 0;
size_t written_bytes;

void trace_write_raw(string s)
{
    trace_string += s;
}

void open_trace_file()
{
    written_bytes = 0;
	trace.open(trace_output_path"/trace" + to_string(current_trace_file_id) + ".js");
	trace_write_raw("window.pyco = Object();window.pyco.frames = [];");
}

void trace_flush()
{
    written_bytes += trace_string.size();
    trace << trace_string << endl;
    trace_string.clear();
    /*trace.close();
	trace.open(trace_output_path"/trace.js", ios_base::app);*/
}

void close_trace_file()
{
	trace_flush();
    trace.close();
}

void maybe_reopen_trace_file()
{
    if (written_bytes / (1024*1024*100))
    {
        close_trace_file();
        current_trace_file_id++;
        open_trace_file();
    }
}

#endif







typedef unsigned long nodeid;


vector<nodeid> consts_stack;

enum ConstantType {URI, STRING};

struct Constant
{
    ConstantType type;
    string value;
    bool operator==(const Constant& b) const
    {
        return this->type == b.type && this->value == b.value;
    }
};

typedef pair<nodeid,size_t> nodeid_and_refcount;

struct ConstantHash {
    size_t operator()(Constant c) const noexcept {
        return hash<ConstantType>()(c.type) ^ hash<string>()(c.value);
    }
};

unordered_map<Constant,nodeid_and_refcount,ConstantHash> consts2nodeids_and_refcounts;
vector<Constant> nodeids2consts;

enum ThingType {BOUND=0, UNBOUND=1, CONST=2, BNODE=3};
/*on a 64 bit system, we have 3 bits to store these, on a 32 bit system, two bits
reference? http://www.delorie.com/gnu/docs/glibc/libc_31.html
*/

typedef unsigned long BnodeOrigin;
typedef unsigned BnodeIndex;


struct Thing;

typedef vector<Thing> Locals;

static_assert(sizeof(Thing*) == sizeof(nodeid), "damn");
static_assert(sizeof(Thing*) == sizeof(BnodeOrigin), "damn");
static_assert(sizeof(Thing*) == sizeof(unsigned long), "damn");
static_assert(sizeof(Thing*) == sizeof(size_t), "damn");

struct Thing
{
#ifdef ONEWORD
    unsigned long value;
    Thing *binding() {return (Thing *)value;};
    unsigned long ulong {return value & ~type_mask;};
    nodeid node_id() {return ulong();};
    BnodeOrigin origin {return ulong();};
    void bind(Thing* v) {value = v;}
    void unbind() {value = UNBOUND;}
    ThingType type() {return (ThingType)(value &type_mask);};
#else
    ThingType _type;
    union
    {
        Thing *_binding;
        nodeid _node_id;
        BnodeOrigin _origin;
    };
    #ifdef TRACE
        string *_debug_name;
        void construct()
        {
            _debug_name = new string;
        }
        void destruct()
        {
            delete _debug_name;
        }
    #endif
    Thing (ThingType type
    #ifdef TRACE
    ,string debug_name
    #endif
    ) : _type{type}
    {
        ASSERT(type == UNBOUND);
        #ifdef TRACE
        construct();
        *_debug_name = debug_name;
        #endif
        #ifdef DEBUG
        set_value((Thing*)666);
        #endif
    }
    Thing (ThingType type, unsigned long value
    #ifdef TRACE
    ,string debug_name
    #endif
    ) : _type{type}
    {
        #ifdef TRACE
        construct();
        *_debug_name = debug_name;
        #endif
        set_value((Thing*)value);
    }
    /*
    ~Thing()
    {
        destruct();
    }
    */
    bool operator==(const Thing& b) const
    {    //just bitwise comparison, not recursive check of equality of bindings
        return this->_type == b._type && this->_binding == b._binding;
    }
    ThingType type()
    {
        return _type;
    }
    Thing* binding()
    {
        return _binding;
    }
    BnodeOrigin origin()
    {
        return _origin;
    }
    nodeid node_id()
    {
        return (nodeid)(_node_id);
    };
    void set_value(Thing* v)
    {
        _binding = v;
    }
    void bind(Thing* v)
    {
        _type = BOUND;
        set_value(v);
    }
    void unbind()
    {
        _type = UNBOUND;
        #ifdef DEBUG
        set_value((Thing*)666);
        #endif
    }
#endif
};

Thing *get_value(Thing *x)
{
    while (x->type() == BOUND)
        x = get_value(x->binding());
    return x;
}

void dump();
typedef pair<Thing*,Thing*> thingthingpair;
enum coro_status {INACTIVE, ACTIVE, EP, YIELD};
struct cpppred_state;



#ifdef CACHE
typedef cache unordered_map<

#endif


struct cpppred_state
{
    size_t entry;
    Thing *incoming[2];
    cpppred_state *states;
    Thing *locals;
    #ifdef CACHE
    size_t cumulative_euler_steps;
    #endif
    #ifdef TRACE_PROOF
        size_t num_substates;
        coro_status status;
        string *comment;
        void set_comment(string x) {*comment = x;}
        void set_active(bool a)
        {
            status = a ? ACTIVE : INACTIVE;
            dump();
        }
        void set_status(coro_status s)
        {
            status = s;
            dump();
        }
        void construct()
        {
            comment = new string;
            status = INACTIVE;
            #ifdef CACHE
            cumulative_euler_steps = 0;
            #endif
        }
        void destruct()
        {
            delete comment;
        }
    #endif
};

string thing_to_string_nogetval(Thing* v);

typedef vector<cpppred_state*> ep_table;

#ifdef TRACE_EP_TABLES
void print_ep_table(ep_table &t)
{
    for (auto i: t)
    {
        cerr << thing_to_string_nogetval(i->incoming[0]) << "   " << thing_to_string_nogetval(i->incoming[1]) << endl;
    }
    cerr << endl;
}
#endif

cpppred_state *query_state;

void escape_trace(string& data) {
    string buffer;
    buffer.reserve(data.size());
    for(size_t pos = 0; pos != data.size(); ++pos) {
        switch(data[pos]) {
            case '\t': buffer.append("&nbsp;&nbsp;");break;
            case '&':  buffer.append("&amp;");       break;
            case '\"': buffer.append("&quot;");      break;
            case '\'': buffer.append("&apos;");      break;
            case '<':  buffer.append("&lt;");        break;
            case '>':  buffer.append("&gt;");        break;
            default:   buffer.append(&data[pos], 1); break;
        }
    }
    data.swap(buffer);
}

#ifdef TRACE_PROOF

void trace_write(string s)
{
    escape_trace(s);
    trace_write_raw(s);
}

void dump_state(int indent, const cpppred_state &state)
{
    if (state.status == INACTIVE)
        return;
    trace_write_raw("<li>");
    if (state.comment)
        trace_write(jsonize_string(*state.comment));
    trace_write_raw("</li>");
    indent += 2;
    trace_write_raw("<ul>");
    for (size_t i = 0; i < state.num_substates; i++)
    {
        dump_state(indent,*(state.states+i));
    }
    if (state.status == EP)
        trace_write_raw("<li class=\\\"ep\\\">EP</li>" + jsonize_string(current_ep_comment));
    else if (state.status == YIELD)
        trace_write_raw("<li class=\\\"yield\\\">yield.</li>");
    trace_write_raw("</ul>");
}

void dump()
{
    trace_write_raw("window.pyco.frames.push(\"" + to_string(euler_steps) + ":<br><ul>");
        dump_state(0, *query_state);
    trace_write_raw("</ul><br><br><br><br><br><br><br>\");");
    trace_flush();
    maybe_reopen_trace_file();
    //print_euler_steps();
}
#endif

#ifdef TRACE
string thing_to_string(Thing* thing);
string thing_to_string_nogetval(Thing* v)
{
  if (v->type() == CONST)
  {
    const Constant &c = nodeids2consts[v->node_id()];
    if (c.type == URI)
      return "<" + c.value + ">";
    else
      return "\"\"\"" + c.value + "\"\"\"";
  }
  else
    if (v->type() == UNBOUND)
        return "?"+*v->_debug_name;
    else if (v->type() == BNODE)
        return "["+*v->_debug_name+"]";
    else
        return "?"+*v->_debug_name+"->"+thing_to_string(v);
}

string thing_to_string(Thing* thing)
{
  return thing_to_string_nogetval(get_value(thing));
}

#endif












const size_t malloc_size = 1024ul*1024ul*480ul;
size_t block_size = malloc_size;
char *block;
char *free_space;


void realloc()
{
        block_size += malloc_size;
        if (realloc(block, block_size) != block)
        {
            cerr << "cant expand memory" << endl;
            exit(1);
        }
}

size_t *grab_words(size_t count)
{
    size_t *result = (size_t *)free_space;
    size_t increase = count * sizeof(size_t);
    //cerr << "block="<<block<<", requested " << count << "words="<<count * sizeof(size_t)<<"bytes, increase="<<increase<<",free_space before = " << free_space<<", after="<<free_space + increase << ", must realloc:"<< (free_space+increase >= block + block_size)<<endl;
    free_space += increase;
    while (free_space >= block + block_size)
        realloc();
    return result;
}

cpppred_state *grab_states(size_t count)
{
    auto r = (cpppred_state*) grab_words(count * sizeof(cpppred_state) / sizeof(size_t));
    #ifdef TRACE_PROOF
        for (size_t i = 0; i < count; i++)
            r[i].construct();
    #endif
    return r;
}

void release_states (size_t count)
{
    free_space -= count * sizeof(cpppred_state);
    #ifdef TRACE_PROOF
        for (size_t i = 0; i < count; i++)
            ((cpppred_state*)free_space)[i].destruct();
    #endif
}

Thing *grab_things(size_t count)
{
    auto r = (Thing*) grab_words(count * sizeof(Thing) / sizeof(size_t));
    #ifdef TRACE
        for (size_t i = 0; i < count; i++)
            r[i].construct();
    #endif
    return r;
}

void release_things (size_t count)
{
    free_space -= count * sizeof(Thing);
    #ifdef TRACE
        for (size_t i = 0; i < count; i++)
            ((Thing*)free_space)[i].destruct();
    #endif
}









size_t query_list(cpppred_state & __restrict__ state);


vector<Thing*>* query_list_wrapper(Thing *x)
/*
this only returns pointers to things, which could be invalid by the time this returns...
*/
{
    cpppred_state *state = grab_states(1);
    state->entry = 0;
    state->incoming[0] = x;
    ASSERT(x->type() != BOUND);
    #define output (*((vector<Thing*>**)(&state->incoming[1])))
    vector<Thing*> *result = output = new vector<Thing*>;
    //cerr << output << ", " << output->size() << endl;
    while (query_list(*state))
    {
		if (result != output)
		    delete output;
		output = new vector<Thing*>;
		/*we're only interested in the first result, but
		we gotta keep calling query_list until it comes to it's natural end, thats the easiest way to
		have all its substates released*/
		//cerr << output << ", " << output->size() << endl;
	}
    if (result != output)
	    delete output;
	#undef output
	release_states(1);
	//cerr << "returning result " << result << " with size " << result->size() << endl;
	return result;
}


bool is_bnode_productively_different(const cpppred_state &old, Thing *now)
{
    /*old.locals was allocated at the moment when the old frame was entered*/
    bool r = (void*)&old.locals[0] > (void*)now;
    if (r)
    {
       #ifdef TRACE_EP_CHECKS
            cerr << thing_to_string_nogetval(now) << " was created before " << *old.comment << ", ok." << endl;
       #endif
    }
    else
    {
        #ifdef TRACE_EP_CHECKS
            cerr << thing_to_string_nogetval(now) << " was created after " << *old.comment << endl;
        #endif
    }
    return r;
}

int is_arg_productively_different(Thing *old, Thing *now)
{
    if (now->type() == BOUND || now->type() == UNBOUND)
    {
        if (old->type() == BOUND || old->type() == UNBOUND)
            return false;
        else if (old->type() == CONST || old->type() == BNODE)
            goto yes;
    }
    else if (now->type() == CONST)
    {
        if (old->type() == BOUND || old->type() == UNBOUND || old->type() == BNODE)
            goto yes;
        else
        {
             ASSERT(old->type() == CONST);
             if (*old == *now)
                return false;
             goto yes;
        }
    }
    else if (now->type() == BNODE)
    {
        if (old->type() == BNODE)
            return -1;
        else {
            goto yes;
        }
    }
    else { ASSERT(false);  }
    return false;
    yes:
    #ifdef TRACE_EP_CHECKS
        cerr << thing_to_string_nogetval(now) << " is different." << endl;
    #endif
    return true;
}

bool detect_ep(const cpppred_state &old, cpppred_state &now)
{
    #ifdef TRACE_EP_CHECKS
        current_ep_comment = thing_to_string_nogetval(old.incoming[0]) + " vs " + thing_to_string_nogetval(now.incoming[0]) +
        " and " +            thing_to_string_nogetval(old.incoming[1]) + " vs " + thing_to_string_nogetval(now.incoming[1]);
        cerr << current_ep_comment << endl;
    #endif
    int results[2];
    for (size_t i = 0; i < 2; i++)
    {
        results[i] = is_arg_productively_different(old.incoming[i], now.incoming[i]);
        if (results[i] == 1)
            return false;
    }
    for (size_t i = 0; i < 2; i++)
    {
        if (results[i] == -1)
        {
            if (now.incoming[i] == old.incoming[i])
            {
                #ifdef TRACE_EP_CHECKS
                    cerr << "these are the same bnodes" << endl;
                #endif
            }
            else if (is_bnode_productively_different(old, now.incoming[i]))
                return false;
        }
    }
    #define SECOND_CHANCE
    #ifdef SECOND_CHANCE
    for (size_t term_arg_i = 0; term_arg_i < 2; term_arg_i++) //for subject and object
    {
        if (results[term_arg_i] == -1)
        {
            if (now.incoming[term_arg_i] == old.incoming[term_arg_i])
                continue;
            vector<Thing*> *lists[2];
            lists[0] = query_list_wrapper(old.incoming[term_arg_i]);
            lists[1] = query_list_wrapper(now.incoming[term_arg_i]);
            //cerr << "lists[0]" << lists[0] << endl;
            //cerr << "lists[1]" << lists[1] << endl;
            //cerr << "lists[0]s" << lists[0]->size() << endl;
            //cerr << "lists[1]s" << lists[1]->size() << endl;
            if (lists[0]->size() == lists[1]->size())
            {
                for (size_t list_item_i = 0; list_item_i < lists[0]->size(); list_item_i++)
                {
                    switch(is_arg_productively_different((*lists[0])[list_item_i], (*lists[1])[list_item_i]))
                    {
                    case 1:
                        #ifdef TRACE_EP_CHECKS
                            cerr << "args are productively different" << endl;
                        #endif
                        goto falsies;
                    case -1:
            //cerr << "xlists[0][list_item_i]" << lists[0][list_item_i] << endl;
            //cerr << "xlists[1][list_item_i]" << lists[1][list_item_i] << endl;
                        if ((*lists[0])[list_item_i] == (*lists[1])[list_item_i])
                        {
                            #ifdef TRACE_EP_CHECKS
                                cerr << "these are the same bnodes" << endl;
                            #endif
                        }
                        else if (is_bnode_productively_different(old, (*lists[1])[list_item_i]))
                        {
                            #ifdef TRACE_EP_CHECKS
                                cerr << "bnodes are productively different" << endl;
                            #endif
                            goto falsies;
                        }
                    default:;
                    }
                    goto not_different;
                    falsies:;
                    #ifdef TRACE
                        cerr << "SECOND_CHANCE:" << thing_to_string_nogetval((*lists[0])[list_item_i]) <<
                        "(" << &((*lists[0])[list_item_i]) << ")" <<
                        ", " << thing_to_string_nogetval((*lists[1])[list_item_i]) <<
                         "(" << &((*lists[1])[list_item_i]) << ")"
                         << endl;
                    #endif
                    delete lists[0];
                    delete lists[1];
                    return false;
                    not_different:;
                }
            }
            delete lists[0];
            delete lists[1];
        }
    }
    #endif
    #ifdef TRACE_EP_CHECKS
        cerr << "EP." << endl;
    #endif
    return true;
}



bool find_ep(ep_table *table, cpppred_state &now)
{
    for (const cpppred_state *old: *table)
    {
        if (detect_ep(*old, now))
            return true;
    }
    return false;
}










static size_t query(cpppred_state & __restrict__ state);
void print_result(cpppred_state &state);
void initialize_consts();

int main (int argc, char *argv[])
{
    (void )argc;
    (void )argv;
    block = (char*)malloc(block_size);
    if (block == 0)
        exit(1);
    free_space = block;
    initialize_consts();
    #ifdef TRACE_PROOF
    open_trace_file();
	#endif
    query_start_time = std::chrono::steady_clock::now();
    query_state = grab_states(1);
    query_state->entry = 0;
    while(query(*query_state)!=0)
    {
        print_result(*query_state);
    }
    release_states(1);
    print_euler_steps();
    #ifdef TRACE_PROOF
    close_trace_file();
    #endif
    free(block);
}

#define yield(x) {state.entry = (char*)&&x - (char*)&&case0; return state.entry;}

int unify(cpppred_state & __restrict__ state);


#ifdef TRACE_PROOF
#define END {state.set_active(false); return 0;}
#else
#define END {return 0;}
#endif


nodeid push_const(Constant c)
{
    auto it = consts2nodeids_and_refcounts.begin();
    nodeid id;
	if ((it = consts2nodeids_and_refcounts.find(c)) != consts2nodeids_and_refcounts.end())
	{
	    id = it->second.first;
	    size_t refcount = it->second.second;
        consts2nodeids_and_refcounts[c] = nodeid_and_refcount{id, refcount+1};
    }
    else
    {
        id = consts2nodeids_and_refcounts.size();
        consts2nodeids_and_refcounts[c] = nodeid_and_refcount{id,1};
        nodeids2consts.push_back(c);
    }
    consts_stack.push_back(id);
    return id;
}

void pop_const()
{
    nodeid id = consts_stack.back();
    consts_stack.pop_back();
    Constant c = nodeids2consts[id];
    auto it = consts2nodeids_and_refcounts[c];
    size_t refcount = it.second - 1;
    if(refcount)
        consts2nodeids_and_refcounts[c] = nodeid_and_refcount{id, refcount};
    else
    {
        consts2nodeids_and_refcounts.erase(c);
        nodeids2consts.pop_back();
    }
}

Constant rdf_nil = Constant{URI,"http://www.w3.org/1999/02/22-rdf-syntax-ns#nil"};
Constant rdf_first = Constant{URI,"http://www.w3.org/1999/02/22-rdf-syntax-ns#first"};
Constant rdf_rest = Constant{URI,"http://www.w3.org/1999/02/22-rdf-syntax-ns#rest"};



/*
remember to get_value as needed before.
later, for optimalization, we dont need to call get_value in every case.
the pred function knows when its unifying two constants, for example,
and can trivially yield/continue on.
*/
