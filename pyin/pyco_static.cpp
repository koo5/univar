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
#include <map>


using namespace std;


#ifdef TRACE
#define IF_TRACE(x) ,x
#else
#define IF_TRACE(x)
#endif

#ifdef TRACE_PROOF
#define IF_TRACE_PROOF(x) ,x
#else
#define IF_TRACE_PROOF(x)
#endif

#ifdef SECOND_CHANCE
#define IF_SECOND_CHANCE(x) ,x
#else
#define IF_SECOND_CHANCE(x)
#endif






#define ASSERT assert


typedef long int RuleId;
typedef unsigned long nodeid;
enum ConstantType {URI, STRING, INTEGER};
typedef pair<nodeid,size_t> nodeid_and_refcount;







struct Thing;

#ifdef TRACE
string thing_to_string_nogetval(Thing* v, int depth);
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





#ifdef DEBUG
    #define INIT_DBG_DATA state.dbg_data = first_free_byte;
    #define CHECK_DBG_DATA  { \
        if (state.dbg_data != first_free_byte) \
        { \
            cerr << "state.dbg_data: " << state.dbg_data << endl<< "first_free_byte: " << (void*)first_free_byte << endl << "off by: " << first_free_byte  - ((char*)state.dbg_data) << endl; \
            ASSERT(state.dbg_data == first_free_byte); \
        } \
        }
#else
    #define INIT_DBG_DATA
    #define CHECK_DBG_DATA
#endif





string current_ep_comment;
typedef unsigned long euler_steps_t;
euler_steps_t euler_steps = 0;
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
    if (chrono::duration_cast<std::chrono::seconds>(now - last_ep_tables_printout).count() > 4)
    {
        last_ep_tables_printout = now;
        print_euler_steps();
    }
}




enum coro_status {INACTIVE, ACTIVE, EP, YIELD, BNODE_YIELD};
struct cpppred_state;
typedef vector<cpppred_state*> ep_table;
typedef size_t state_id;
state_id next_state_id = 10;




/*im just allocating one block of hardcoded size for now*/
const size_t malloc_size = 1024ul*1024ul*480ul;
size_t block_size = malloc_size;
char *block; /*this is the start of the block inside which first_free_byte is*/
char *first_free_byte;

void realloc();
size_t *grab_words(size_t count);
cpppred_state *grab_states(size_t count IF_TRACE_PROOF(cpppred_state *parent));
void release_bytes(size_t count);
void release_states(size_t count);
Thing *grab_things(size_t count);
void release_things(size_t count);




#ifdef TRACE_PROOF

    #define JSONCONS_NO_DEPRECATED
    #include <jsoncons/json.hpp>
    using jsoncons::json;

    void dump_tracing_step();
    void begin_tracing_step();
    void end_tracing_step();
    void proof_trace_add_op(json &js);
    void proof_trace_add_state(state_id id, state_id parent_id);
    void proof_trace_remove_state(state_id id);
    void proof_trace_set_comment(state_id id, const string &comment);
    void proof_trace_set_status(state_id id, coro_status status, bool with_introduction, state_id parent_id, RuleId rule_id, Thing* locals_address, string *comment);
    void proof_trace_emit_euler_steps();
    void proof_trace_emit_bind(Thing *t, Thing *t2);
    void proof_trace_emit_unbind(Thing *t);

    void dump();

    bool tracing_enabled = true;
    bool tracing_active = true;
    string trace_string;
    ofstream trace;
    size_t current_trace_file_id = 0;
    size_t written_bytes;

    void emit_rule_consts_location(RuleId rule, Thing *consts);
    void emit_thing_size();
    void trace_write_raw(string s);
    void open_trace_file();
    void trace_flush();
    void close_trace_file();
    void maybe_reopen_trace_file();

    void proof_trace_emit_rules_consts();
#endif















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
        #ifdef TRACE_PROOF
            proof_trace_emit_bind(this, v);
        #endif
    }
    void unbind()
    {
        _type = UNBOUND;
        #ifdef DEBUG
            set_value((Thing*)666);
        #endif
        #ifdef TRACE_PROOF
            proof_trace_emit_unbind(this);
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
        //cerr << ((void*)this) << thing_to_string_nogetval(this) << " set_bnode_bound_to " << (void*)value << (value ? thing_to_string_nogetval(value) : "") << endl;
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



typedef pair<Thing*,Thing*> thingthingpair;


struct cpppred_state
{
    size_t entry;
    Thing *incoming[2];
    cpppred_state *states;
    Thing *locals;
    #ifdef DEBUG
    	void* dbg_data;
	#endif
    #ifdef SECOND_CHANCE
        vector<Thing*> *ep_lists[2];
    #endif
    #ifdef CACHE
       size_t cumulative_euler_steps;
    #endif
    #ifdef TRACE_PROOF
        RuleId rule_id;
        bool was_introduced;
        state_id id, parent;
        size_t num_substates;
        coro_status status;
        string *comment;
        bool dont_trace;
        void set_comment(string x) {
            if (comment)
                *comment = x;
            else
                comment = new string(x);
            if (!dont_trace && tracing_enabled && tracing_active)
                if (was_introduced)
                    proof_trace_set_comment(id, *comment);
        }
        void set_active(bool a)
        {
            set_status(a ? ACTIVE : INACTIVE);
        }
        void set_status(coro_status s)
        {
            if (status == s) return;
            status = s;
            if (tracing_enabled && tracing_active && !dont_trace)
            {
                proof_trace_set_status(id, s, !was_introduced, parent, rule_id, locals, comment);
                was_introduced = true;
                dump_tracing_step();
            }
        }
        void construct(cpppred_state *parent_)
        {
            locals = 0;
            rule_id = -1;
            dont_trace = false;
            was_introduced = false;
            id = next_state_id++;
            if (parent_)
                parent = parent_->id;
            else
            {
                parent = 0;
                dont_trace = true;
            }
            if (parent_ && parent_->dont_trace)
                dont_trace = true;
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
    void grab_substates(size_t count)
    {
        states = grab_states(count IF_TRACE_PROOF(this));
    }
};

cpppred_state *top_level_coro, *top_level_tracing_coro;






struct SerializationTodoInfo{
    size_t id, indent;
};





void serialize_bnode(Thing* t, map<Thing*, SerializationTodoInfo> &todo, map<Thing*, size_t> &done, size_t &first_free_id, stringstream &result, size_t indent);



string serialize_literal_to_n3(string c)
{
    return "\"\"\"" +
        replaceAll(replaceAll(replaceAll(c,"\\", "\\\\"),"\n", "\\n"),"\"\"\"", "\\\"\\\"\\\"")
    + "\"\"\"";
}

#ifdef TRACE
    bool list_to_string(Thing *v, string &list_string);
    string bnode_to_string(Thing* thing, int depth);
    string thing_to_string(Thing* thing);
    string thing_to_string_nogetval(Thing* v, int depth = -1)
    {
      if (v->type() == CONST)
      {
        const Constant &c = nodeids2consts[v->node_id()];
        if (c.type == URI)
          return "<" + c.value + ">";
        else
          return serialize_literal_to_n3(c.value);
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
            /*its a bnode, not a rdf:nil, so it should have at least one item if its a list*/
            string list_string;
            if (list_to_string(v, list_string))
                r += list_string;
            else
                r += bnode_to_string(v, depth);
            if (v->_bnode_bound_to)
                r += "->" + thing_to_string_nogetval(v->_bnode_bound_to, depth);
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


    void serialize_thing2(Thing *v, map<Thing*, SerializationTodoInfo> &todo, map<Thing*, size_t> &done, size_t &first_free_id, stringstream &result, size_t depth)
    {
      v = get_value(v);
      if (v->type() == CONST)
      {
        const Constant &c = nodeids2consts[v->node_id()];
        if (c.type == URI)
          result << "<" << c.value << ">";
        else
          result << serialize_literal_to_n3(c.value);
      }
      else
      {
        if (v->type() == UNBOUND)
            result << "?" << v->_debug_name;
        else if (v->type() == BNODE)
        {
            size_t id;
            auto it = done.find(v);
            if (it != done.end())
                id = it->second;
            else
            {
                if (todo.find(v) == todo.end())
                {
                    id = first_free_id++;
                    todo[v] = SerializationTodoInfo{id, depth};
                }
                else
                    id = todo[v].id;
            }
            result << ":bn" << id;
        }
        else
            ASSERT(false);
      }
    }

    string serialize_thing(Thing* thing)
    {
        stringstream result;
        thing = get_value(thing);
        size_t first_free_id = 0;
        map<Thing*, SerializationTodoInfo> todo;
        map<Thing*, size_t> done;
        if (thing->type() != BNODE)
            serialize_thing2(thing, todo, done, first_free_id, result, 0);
        else
        {
            todo[thing] = SerializationTodoInfo{first_free_id++, 0};
            while(!todo.empty())
                serialize_bnode(todo.begin()->first, todo, done, first_free_id, result, todo.begin()->second.indent);
        }
        return result.str();
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

    #include "pyco_json_tracing.cpp"


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
            trace_write_raw("<li class=\\\"ep\\\">EP </li>" + jsonize_string(current_ep_comment));
        else if (state.status == YIELD)
            trace_write_raw("<li class=\\\"yield\\\">yield.</li>");
        else if (state.status == BNODE_YIELD)
            trace_write_raw("<li class=\\\"yield\\\">bnode yield.</li>");
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











size_t query_list(cpppred_state & __restrict__ state, bool *was_cut_off, int depth = -1);


vector<Thing*>* query_list_wrapper(Thing *x, int depth = -1)
{
    bool was_cut_off;
/*returns pointers to things, which could be invalid by the time this finishes, so get rid of this function. below is a version that makes a string of the results...
we can also deepcopy them, for ep check purposes...*/
    #ifdef DEBUG
        char* dbg_first_free_byte = first_free_byte;
    #endif
    #ifdef TRACE_PROOF
        bool was_tracing_enabled = tracing_enabled;
        tracing_enabled = false;
    #endif
    cpppred_state *state = grab_states(1 IF_TRACE_PROOF(NULL));
    state->entry = 0;
    state->incoming[0] = x;
    ASSERT(x->type() != BOUND);
    #define output (*((vector<Thing*>**)(&state->incoming[1])))
    vector<Thing*> *result = output = new vector<Thing*>;
    //cerr << output << ", " << output->size() << endl;
    while (query_list(*state, &was_cut_off, depth))
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
    #ifdef DEBUG
        ASSERT(dbg_first_free_byte == first_free_byte);
    #endif
	return result;
}




#ifdef TRACE
    bool list_to_string(Thing *v, string &list_string)
    {
        bool result = false;
        #ifdef DEBUG
            char* dbg_first_free_byte = first_free_byte;
        #endif
        #ifdef TRACE_PROOF
            bool was_tracing_enabled = tracing_enabled;
            tracing_enabled = false;
        #endif
        cpppred_state *state = grab_states(1 IF_TRACE_PROOF(NULL));
        state->entry = 0;
        ASSERT(v->type() != BOUND);
        state->incoming[0] = v;
        #define output (*((vector<Thing*>**)(&state->incoming[1])))
        output = new vector<Thing*>;
        bool was_cut_off = false;
        list_string += "(";
        size_t num_variants = 0;
        while (query_list(*state, &was_cut_off, 5))
        {
            if (++num_variants > 1)
                list_string += " /// ";
            if (output->size())
            {
                result = true;
                for(Thing *t:*output)
                {
                    list_string += thing_to_string(t) + " ";
                }
            }
            if (was_cut_off)
                list_string += "...";
            delete output;
            output = new vector<Thing*>;
        }
        list_string += ")";
        delete output;
        #undef output
        release_states(1);
        //cerr << "returning result " << result << " with size " << result->size() << endl;
        #ifdef TRACE_PROOF
            tracing_enabled = was_tracing_enabled;
        #endif
        #ifdef DEBUG
            ASSERT(dbg_first_free_byte == first_free_byte);
        #endif
        return result;
    }
#endif











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


#ifdef DEBUG_RULES
    struct BodyItemStats
    {
        int called_times=0, yielded_times=0;
    };
    typedef map<size_t, BodyItemStats> BodyItemsStats;
    struct RuleStats
    {
        int called_times=0;
        BodyItemsStats body_items_stats;
    };
    typedef map<size_t, RuleStats> RulesStats;

    RulesStats rules_stats;

    void print_rules_warnings()
    {
            for (auto kv: rules_stats)
            {
                size_t rule_id = kv.first;
                auto v = kv.second;
                if (v.called_times == 0)
                {
                    cerr << "rule " << rule_id << " was never called:" << endl;
                    //cerr << rule_original_head_string(rule_id) << endl;
                }
                else
                {
                    for (auto bi: v.body_items_stats)
                    {
                        if (bi.second.called_times == 0)
                        {
                            cerr << "rule " << rule_id << " bi " << bi.first << " never called" << endl;
                            break;
                        }
                    }
                    for (auto bi: v.body_items_stats)
                    {
                        if (bi.second.called_times != 0 && bi.second.yielded_times == 0)
                        {
                            cerr << "rule " << rule_id << " bi " << bi.first << " called " << bi.second.called_times << " times and always failed" << endl;
                            break;
                        }
                    }
                }
            }
    }
#endif





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
	#ifdef TRACE_PROOF
        proof_trace_emit_rules_consts();
	#endif
    query_start_time = std::chrono::steady_clock::now();
    top_level_tracing_coro = top_level_coro = grab_states(1 IF_TRACE_PROOF(NULL));
    #ifdef TRACE_PROOF
        top_level_coro->dont_trace = false;
    #endif
    top_level_coro->entry = 0;
    while(query(*top_level_coro)!=0)
    {
        print_result(*top_level_coro);
    }
    release_states(1);
    print_euler_steps();
    #ifdef DEBUG_RULES
        print_rules_warnings();
    #endif
    #ifdef TRACE_PROOF
        close_trace_file();
    #endif
    free(block);
}

#define yield(x) {state.entry = (char*)&&x - (char*)&&case0; return state.entry;}

int unify(cpppred_state & __restrict__ state);


#define END3 return 0;

#ifdef DEBUG
    #define END2 CHECK_DBG_DATA END3
#else
    #define END2 END3
#endif

#ifdef TRACE_PROOF
    #define END {state.set_active(false); END2}
#else
    #define END {END2}
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



#include "pyco_memory.cpp"


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




/*
bool is_arg_duplicate(Thing *now, *old)
{
    if (now->type() != old->type())
        return false;
    ThingType type = now->type();
    if (type == CONST)
        return (*now == *old);
    else if (type == BNODE)
    {
        if (*now != *old)
            return false;
        if (now->_is_bnode_ungrounded != old->_is_bnode_ungrounded)
            return false;
        for thing in other things in now:
            if (!is_arg_duplicate(get_value(now_thing), old_thing)
                return false;
    }
    else if (type == UNBOUND)
    {
        auto maybe_old = correspondences.find(now);
        if (maybe_old == correspondences.end())
             correspondences[now] = old;
        else
        {
            if (maybe_old->second != old)
                return false;
        }
    }
    else ASSERT(false);
    return true;
}

bool is_duplicate_yield(cpppred_state &state, size_t old_idx)
{
    now0 = state.incoming[0];
    now1 = state.incoming[1];

    old0 = state.yields_vector[old_idx].incoming[0];
    old1 = state.yields_vector[old_idx].incoming[1];

    if (!is_arg_duplicate(now0, old0) || !is_arg_duplicate(now1, old1))
        //yay, found a difference
        return false;

    state.yields_vector[old_idx].count += 1;
    return true;
}

clone_thing(Thing *x)
{
    x = get_value(x);
    if (x->type() == BNODE)
    {
        switch(x->origin())
        {
            case xxx:
                bnode = new Thing * size of bnode;
                y = bnode + bnode_thing_pos;
                for each var in bnode:
                    orig = get_value(x + var_offset);
                    &clone = *(y + var_offset);
                    if (orig in done):
                        clone = done[orig];
                    else
                        clone = clone_thing(orig);
        }
    }
    else if (x->type() == UNBOUND)
    {
        if (orig in done):
            clone = done[orig];
        else
            clone = clone_thing(orig);

    }


    (x->type() == CONST)


    Thing *y = new Thing{x->type(), x->value};
    if (x->type() == BNODE && x->_is_bnode_ungrounded)
        y->_is_bnode_ungrounded = true;

}





{
    Thing *t = new Thing{UNBOUND};
    c = clone_thing(t);
    ASSERT(c->type() == UNBOUND);





{?x x x. ?x y y} <= {}.
*/
