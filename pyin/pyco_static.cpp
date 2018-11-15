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



#define IF_TRACE(x) \
	#ifdef TRACE \
		x \
	#endif





using namespace std;

unsigned long euler_steps = 0;
chrono::steady_clock::time_point last_ep_tables_printout = chrono::steady_clock::time_point::min();

void print_ep_tables();

void print_euler_steps()
{
    cerr << euler_steps << " euler_steps." << endl;
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


ofstream trace;
string trace_string;

#define ASSERT assert












typedef unsigned long nodeid;

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
struct cpppred_state
{
    size_t entry;
    Thing *incoming[2];
    cpppred_state *states;
    Thing *locals;
    #ifdef TRACE_PROOF
        size_t num_substates;
        coro_status status = INACTIVE;
        string *comment;
        void set_comment(string x) {*comment = x;}
        void set_active(bool a)
        {
            status = a ? ACTIVE : INACTIVE;
            dump();
        }
        void construct()
        {
            comment = new string;
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
void trace_flush()
{
    trace << trace_string;
    trace_string.clear();
    trace.close();
	trace.open(trace_output_path"/trace.js", ios_base::app);
}

void trace_write_raw(string s)
{
    trace_string += s;
}

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
        trace_write(*state.comment);
    trace_write_raw("</li>");
    indent += 2;
    trace_write_raw("<ul>");
    for (size_t i = 0; i < state.num_substates; i++)
    {
        dump_state(indent,*(state.states+i));
    }
    if (state.status == EP)
        trace_write_raw("<li>EP</li>");
    trace_write_raw("</ul>");
}

void dump()
{
    trace_write_raw("window.pyco.frames.push(\"<ul>");
        dump_state(0, *query_state);
    trace_write_raw("</ul><br><br><br><br><br><br><br>\");\n");
    trace_flush();
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
      return "\"" + c.value + "\"";
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

/*
remember to get_value as needed before.
later, for optimalization, we dont need to call get_value in every case.
the pred function knows when its unifying two constants, for example,
and can trivially yield/continue on.
*/

bool is_bnode_productively_different(const cpppred_state &old, cpppred_state &now, size_t idx)
{
    /*told.locals was allocated at the moement when the old frame was entered*/
    bool r = (void*)now.incoming[idx] < (void*)&old.locals[0];
    if (r)
    {
       #ifdef TRACE_EP_CHECKS
            cerr << thing_to_string_nogetval(now.incoming[idx]) << " was created before " << *old.comment << endl;
        #endif
    }
    else
    {
        #ifdef TRACE_EP_CHECKS
            cerr << thing_to_string_nogetval(now.incoming[idx]) << " was created after " << *old.comment << endl;
        #endif
    }
    if (now.incoming[idx] == old.incoming[idx])
    {
        #ifdef TRACE_EP_CHECKS
            cerr << "but these are the same bnodes" << endl;
        #endif
        return false;
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
            return true;
    }
    else if (now->type() == CONST)
    {
        if (old->type() == BOUND || old->type() == UNBOUND || old->type() == BNODE)
            return true;
        else {
             ASSERT(old->type() == CONST);
             return !(*old == *now);
        }
    }
    else if (now->type() == BNODE)
    {
        if (old->type() == BNODE)
            return -1;
        else {
            return true;
        }
    }
    else { ASSERT(false);  }
    return false;
}

bool detect_ep(const cpppred_state &old, cpppred_state &now)
{
    #ifdef TRACE_EP_CHECKS
    cerr << thing_to_string_nogetval(old.incoming[0]) << " vs " << thing_to_string_nogetval(now.incoming[0]) << " and " <<
        thing_to_string_nogetval(old.incoming[1]) << " vs " << thing_to_string_nogetval(now.incoming[1]) << endl;
    #endif
    int results[2];
    for (size_t i = 0; i < 2; i++)
    {
        results[i] = is_arg_productively_different(old.incoming[i], now.incoming[i]);
        if (results[i] == 1)
        {
            #ifdef TRACE_EP_CHECKS
                cerr << i << " is different." << endl;
            #endif
            return false;
        }
    }
    for (size_t i = 0; i < 2; i++)
    {
        if (results[i] == -1 && is_bnode_productively_different(old, now, i))
        {
            #ifdef TRACE_EP_CHECKS
                cerr << i << " is different bnode." << endl;
            #endif
            return false;
        }
    }
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





const size_t malloc_size = 1024ul*1024ul*48ul;
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
	trace.open(trace_output_path"/trace.js");
	trace_write_raw("window.pyco = Object();window.pyco.frames = [];\n");
	#endif
    query_state = grab_states(1);
    query_state->entry = 0;
    while(query(*query_state)!=0)
    {
        print_result(*query_state);
    }
    release_states(1);
    print_euler_steps();
    #ifdef TRACE_PROOF
    trace_flush();
    trace.close();
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
	if ((it = consts2nodeids_and_refcounts.find(c)) != consts2nodeids_and_refcounts.end())
	{
	    nodeid id = it->second.first;
	    size_t refcount = it->second.second;
        consts2nodeids_and_refcounts[c] = nodeid_and_refcount{id, refcount+1};
		return id;
    }
    nodeid id = consts2nodeids_and_refcounts.size();
    consts2nodeids_and_refcounts[c] = nodeid_and_refcount{id,1};
    nodeids2consts.push_back(c);
    return id;
}

void pop_const()
{
    Constant c = nodeids2consts.back();
    auto it = consts2nodeids_and_refcounts[c];
    nodeid id = it.first;
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
