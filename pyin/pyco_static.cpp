#ifndef DEBUG
/*used at least by cassert, of the headers included below*/
#define NDEBUG
#endif


#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <cassert>
#include <iostream>
#include <fstream>
#include <sstream>
#include <ctime>
#include <chrono>
#include <unordered_map>


using namespace std;


#ifdef TRACE
#define IF_TRACE(x) ,x
#else
#define IF_TRACE(x)
#endif

#ifdef SECOND_CHANCE
#define IF_SECOND_CHANCE(x) ,x
#else
#define IF_SECOND_CHANCE(x)
#endif



#define ASSERT assert


/*im just allocating one block of hardcoded size for now*/
const size_t malloc_size = 1024ul*1024ul*480ul;
size_t block_size = malloc_size;
char *block; /*this is the start of the block inside which first_free_byte is*/
char *first_free_byte;


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










void print_ep_tables();

unsigned long long euler_steps_rate()
{
    chrono::steady_clock::time_point now = std::chrono::steady_clock::now();
    auto duration = chrono::duration_cast<std::chrono::seconds>(now - query_start_time).count();
    return duration ? (euler_steps / duration) : 0;
}

void print_euler_steps()
{
    cerr << euler_steps << " euler_steps, " << euler_steps_rate() << "/s." << endl;
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
    bool tracing_enabled = true;
    bool tracing_active = true;
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
        trace_write_raw("window.pyco = Object();window.pyco.frames = [];");//??
        //dump();
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
enum ConstantType {URI, STRING, INTEGER};
typedef pair<nodeid,size_t> nodeid_and_refcount;

struct Constant
{
    ConstantType type;
    string value;
    bool operator==(const Constant& b) const
    {
        return this->type == b.type && this->value == b.value;
    }
};

struct ConstantHash {
    size_t operator()(Constant c) const noexcept {
        return hash<ConstantType>()(c.type) ^ hash<string>()(c.value);
    }
};
/*silly duplication here, should be all merged into one better thought-out datastructure*/
#include <functional>

unordered_map<Constant,nodeid_and_refcount,ConstantHash> consts2nodeids_and_refcounts;
vector<Constant> nodeids2consts;
vector<nodeid> consts_stack; /*this is so coroutines can just call pop_const, without having to specify what to pop. That may be unnecessary*/





struct Thing;

#ifdef TRACE
string thing_to_string_nogetval(Thing* v);
#endif





enum ThingType {BOUND=0, UNBOUND=1, CONST=2, BNODE=3};
/*on a 64 bit system, we have 3 bits to store these, on a 32 bit system, two bits
reference? http://www.delorie.com/gnu/docs/glibc/libc_31.html
*/

typedef unsigned long BnodeOrigin; /*uniquely specifies rule and thing name*/




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
    bool _is_bnode_ungrounded;
    Thing* _bnode_bound_to;
    #ifdef TRACE
        char *_debug_name;
    #endif
    Thing (ThingType type IF_TRACE(char *debug_name)) : _type{type}
    {
        ASSERT(type == UNBOUND);
        #ifdef TRACE
            _debug_name = debug_name;
        #endif
        #ifdef DEBUG
            set_value((Thing*)0x666);
        #endif
    }
    Thing (ThingType type, unsigned long value IF_TRACE(char *debug_name)) : _type{type}
    {
        #ifdef TRACE
            _debug_name = debug_name;
        #endif
        set_value((Thing*)value);
        #ifdef DEBUG
        if (type == BNODE)
        #endif
        {
            _is_bnode_ungrounded = false;
            _bnode_bound_to = NULL;
        }
    }
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
    void make_bnode_ungrounded()
    {
        ASSERT(_type == BNODE);
        _is_bnode_ungrounded = true;
    }
    void set_bnode_bound_to(Thing *value)
    {
        ASSERT(_type == BNODE);
        #ifdef TRACE
        cerr << ((void*)this) << thing_to_string_nogetval(this) << " set_bnode_bound_to " << (void*)value << (value ? thing_to_string_nogetval(value) : "") << endl;
        #endif
        if (_bnode_bound_to)
        {
            ASSERT(value == NULL);
        }
        else
        {
            ASSERT(value != NULL);
            ASSERT(value->type() == BNODE);
        }
        _bnode_bound_to = value;
    }
#endif
};

Thing *get_value(Thing *x)
{
    #ifdef DEBUG
       size_t counter = 0;
    #endif
    while (x->type() == BOUND)
    {
        #ifdef DEBUG
            counter++;
            if (!(counter % 10000))
                cerr << "looks like a getvalue infiloop" << endl;
        #endif
        x = x->binding();
    }
    if (x->type() == BNODE && x->_bnode_bound_to)
        return get_value(x->_bnode_bound_to);
    return x;
}


void dump();
typedef pair<Thing*,Thing*> thingthingpair;
enum coro_status {INACTIVE, ACTIVE, EP, YIELD};
struct cpppred_state;



struct cpppred_state;
typedef vector<cpppred_state*> ep_table;

struct cpppred_state
{
    size_t entry;
    Thing *incoming[2];
    cpppred_state *states;
    Thing *locals;
    #ifdef SECOND_CHANCE
        vector<Thing*> *ep_lists[2];
    #endif
    #ifdef CACHE
       size_t cumulative_euler_steps;
    #endif
    #ifdef TRACE_PROOF
        size_t num_substates;
        coro_status status;
        string *comment;
        void set_comment(string x) {
            if (comment)
                *comment = x;
            else
                comment = new string(x);
        }
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
            comment = (string*)NULL;
            status = INACTIVE;
            #ifdef CACHE
                cumulative_euler_steps = 0;
            #endif
        }
        void destruct()
        {
            if (comment)
                delete comment;
        }
    #endif
};

cpppred_state *top_level_coro, *top_level_tracing_coro;















#ifdef TRACE
    string bnode_to_string(Thing* thing);
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
      {
        //cerr << "("<< ((void*)v) << "/" << ((void*)(first_free_byte - 1)) <<")" << endl;
        //cerr << v->_debug_name << endl;
        if (v->type() == UNBOUND)
            return string("?")+v->_debug_name;
        else if (v->type() == BNODE)
        {
            string r;
            if (v->_is_bnode_ungrounded)
                r = "(ungrounded)";
            r += bnode_to_string(v);
            if (v->_bnode_bound_to)
                r += "->" + thing_to_string_nogetval(v->_bnode_bound_to);
            return r;
        }
        else
        {
            ASSERT(v->type() == BOUND);
            return string("?")+v->_debug_name+"->"+thing_to_string(v);
        }
      }
    }

    string thing_to_string(Thing* thing)
    {
      return thing_to_string_nogetval(get_value(thing));
    }
#endif






#ifdef TRACE_EP_TABLES
    void print_ep_frame_arg(cpppred_state &f, size_t arg_i)
    {
        cerr << thing_to_string_nogetval(f.incoming[arg_i]);
        if (f.ep_lists[arg_i]->size())
        {
            cerr << " ( ";
            for (Thing *thing : (*(f.ep_lists[arg_i])))
            {
                cerr << thing_to_string_nogetval(thing) << " ";
            }
            cerr << ")";
        }
    }

    void print_ep_table(ep_table &t)
    {
        for (auto i: t)
        {
            print_ep_frame_arg(*i, 0);
            cerr << "   ";
            print_ep_frame_arg(*i, 1);
            cerr << endl;
        }
        cerr << endl;
    }
#endif

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
        if (!top_level_tracing_coro || !tracing_enabled || !tracing_active)
            return;
        trace_write_raw("window.pyco.frames.push(\"" + to_string(euler_steps) + ":<br><ul>");
        dump_state(0, *top_level_tracing_coro);
        trace_write_raw("</ul><br><br><br><br><br><br><br>\");");
        trace_flush();
        maybe_reopen_trace_file();
        //print_euler_steps();
    }
#endif


















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
    size_t *result = (size_t *)first_free_byte;
    size_t increase = count * sizeof(size_t);
    //cerr << "block="<<block<<", requested " << count << "words="<<count * sizeof(size_t)<<"bytes, increase="<<increase<<",first_free_byte before = " << first_free_byte<<", after="<<first_free_byte + increase << ", must realloc:"<< (first_free_byte+increase >= block + block_size)<<endl;
    first_free_byte += increase;
    while (first_free_byte >= block + block_size)
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

void release_bytes(size_t count)
{
    #ifdef DEBUG
        for (size_t i = 1; i <= count; i++)
            *(first_free_byte - i) = 0;
    #endif
    first_free_byte -= count;
}

void release_states (size_t count)
{
    #ifdef TRACE_PROOF
        for (size_t i = 0; i < count; i++)
            ((cpppred_state*)first_free_byte)[i].destruct();
    #endif
    release_bytes(count * sizeof(cpppred_state));
}

Thing *grab_things(size_t count)
{
    auto r = (Thing*) grab_words(count * sizeof(Thing) / sizeof(size_t));
    return r;
}

void release_things(size_t count)
{
    release_bytes(count * sizeof(Thing));
}


size_t query_list(cpppred_state & __restrict__ state);


vector<Thing*>* query_list_wrapper(Thing *x)
{
/*returns pointers to things, which could be invalid by the time this finishes...*/

    #ifdef TRACE_PROOF
        bool was_tracing_enabled = tracing_enabled;
        tracing_enabled = false;
    #endif
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
		have all the substates released*/
		//cerr << output << ", " << output->size() << endl;
	}
    if (result != output)
	    delete output;
	#undef output
	release_states(1);
	//cerr << "returning result " << result << " with size " << result->size() << endl;
	#ifdef TRACE_PROOF
	    tracing_enabled = was_tracing_enabled;
	#endif
	return result;
}


















bool is_bnode_productively_different(const cpppred_state &old, Thing *now)
{
    /*old.locals was allocated at the moment when the old frame was entered*/
    bool r = (void*)&old.locals[0] > (void*)now;
    #ifdef TRACE_EP_CHECKS
        cerr << thing_to_string_nogetval(now) << " was created " << (r ? "before" : "after") <<
        #ifdef TRACE_PROOF
            (old.comment ? (*old.comment) : "???")
        #else
            &old
        #endif
            << (r ? ", ok." : ", continuing ep check") << "" << endl;
    #endif
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

bool detect_ep(cpppred_state &old, cpppred_state &now IF_SECOND_CHANCE(vector<Thing*> *(&now_lists)[2]))
/* here we try to detect an ep by comparing a parent state to current one */
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
    #ifdef SECOND_CHANCE
    for (size_t term_arg_i = 0; term_arg_i < 2; term_arg_i++) //for subject and object
    {
        if (results[term_arg_i] == -1)
        {
            if (now.incoming[term_arg_i] == old.incoming[term_arg_i])
                continue;
            vector<Thing*> *lists[2];
            lists[0] = old.ep_lists[term_arg_i];
            if (now_lists[term_arg_i] == NULL)
                now_lists[term_arg_i] = query_list_wrapper(now.incoming[term_arg_i]);
            lists[1] = now_lists[term_arg_i];
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
                        /*cerr << "SECOND_CHANCE:" << thing_to_string_nogetval((*lists[0])[list_item_i]) <<
                        "(" << &((*lists[0])[list_item_i]) << ")" <<
                        ", " << thing_to_string_nogetval((*lists[1])[list_item_i]) <<
                         "(" << &((*lists[1])[list_item_i]) << ")"
                         << endl;*/
                    #endif
                    return false;
                    not_different:;
                }
            }
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
    bool r = false;
    #ifdef SECOND_CHANCE
        vector<Thing*> *now_lists[2] = {NULL, NULL};
    #endif
    for (cpppred_state *f: *table)
    {
        if (detect_ep(*f, now IF_SECOND_CHANCE(now_lists)))
        {
            r = true;
            goto end;
        }
    }
    end:
    #ifdef SECOND_CHANCE
        if (now_lists[0])
            delete now_lists[0];
        if (now_lists[1])
            delete now_lists[1];
    #endif
    return r;
}










static size_t query(cpppred_state & __restrict__ state);
void print_result(cpppred_state &state);
void initialize_consts();
bool result_is_grounded(cpppred_state &state);
bool find_ungrounded_bnode(Thing* v);



int main (int argc, char *argv[])
{
    (void )argc;
    (void )argv;
    ASSERT(consts2nodeids_and_refcounts.size() == nodeids2consts.size());
    block = (char*)malloc(block_size);
    if (block == 0)
    {
        cerr << "cant allocate ram" << endl;
        exit(1);
    }
    first_free_byte = block;
    initialize_consts();
    ASSERT(consts2nodeids_and_refcounts.size() == nodeids2consts.size());
    #ifdef TRACE_PROOF
        open_trace_file();
	#endif
    query_start_time = std::chrono::steady_clock::now();
    top_level_tracing_coro = top_level_coro = grab_states(1);
    top_level_coro->entry = 0;
    while(query(*top_level_coro)!=0)
    {
        print_result(*top_level_coro);
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
    ASSERT(consts2nodeids_and_refcounts.size() == nodeids2consts.size());
    auto it = consts2nodeids_and_refcounts.begin();
    nodeid id;
	if ((it = consts2nodeids_and_refcounts.find(c)) != consts2nodeids_and_refcounts.end())
	{
	    ASSERT (c.value == (it->first).value);
	    id = it->second.first;
	    //cerr << "const found: " << c.value << ", id:" << id <<endl;
	    size_t refcount = it->second.second;
        consts2nodeids_and_refcounts[c] = nodeid_and_refcount{id, refcount+1};
    }
    else
    {
        //cerr << "consts2nodeids_and_refcounts.size():" << consts2nodeids_and_refcounts.size();
        //cerr << "nodeids2consts.size():" << nodeids2consts.size();
        id = consts2nodeids_and_refcounts.size();
        //cerr << "const not found: " << c.value << ", new id:" << id <<endl;
        consts2nodeids_and_refcounts[c] = nodeid_and_refcount{id,1};
        nodeids2consts.push_back(c);
        //cerr << "added: " << nodeids2consts[id].value << endl;
    }
    consts_stack.push_back(id);
    ASSERT(consts2nodeids_and_refcounts.size() == nodeids2consts.size());
    return id;
}

void pop_const()
{
    ASSERT(consts2nodeids_and_refcounts.size() == nodeids2consts.size());
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
    ASSERT(consts2nodeids_and_refcounts.size() == nodeids2consts.size());
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




#ifdef CACHE
typedef cache unordered_map<
/*i think caching(memoization) is doable even with bnodes, and even reuse of half-finished rule states, but the complexity
quickly adds up..*/
#endif


