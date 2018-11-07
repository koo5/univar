#include <string>
#include <map>
#include <tuple>
#include <vector>
#include <cassert>
#include <iostream>
#include <fstream>

using namespace std;

ofstream trace;
string trace_string;

#define ASSERT assert


typedef unsigned long nodeid;

enum ConstantType {URI, STRING};

typedef pair<ConstantType,string> Constant;

extern vector<Constant> strings;

enum ThingType {BOUND, UNBOUND, CONST, BNODE};
/*on a 64 bit system, we have 3 bits to store these, on a 32 bit system, two bits

reference?
*/

typedef unsigned long BnodeOrigin;
typedef unsigned BnodeIndex;

//map<BnodeIndex,Locals> bnodes;


struct Thing;

typedef vector<Thing> Locals;

static_assert(sizeof(Thing*) == sizeof(nodeid), "damn");
static_assert(sizeof(Thing*) == sizeof(BnodeOrigin), "damn");


struct Thing
{
    ThingType type;
    union
    {
        Thing *binding;
        nodeid string_id;
        BnodeOrigin origin;
    };
    #ifdef TRACE
        string debug_name;
    #endif

    bool operator==(const Thing& b) const
    //just bitwise comparison, not recursive check of equality of bindings
    {
        return this->type == b.type && this->binding == b.binding;
    }
    void set_value(Thing* v)
    {
        binding = v;
        assert (v != (Thing* )0x31);
    }
    void bind(Thing* v)
    {
        type = BOUND;
        set_value(v);
    }
    void unbind()
    {
        type = UNBOUND;
         set_value((Thing*)666);
    }
};

map<Thing*,unsigned long> bnode_to_id;
unsigned long bnode_counter = 0;

Thing *get_value(Thing *x)
{
    if (x->type == BOUND)
        return get_value(x->binding);
    return x;
}

void dump();

typedef pair<Thing*,Thing*> thingthingpair;
//ep_head is an array/pair of 2 Things
typedef thingthingpair ep_head;
typedef vector<ep_head> ep_table;
struct cpppred_state;
struct cpppred_state
{
    size_t entry;
    Locals locals;
    Thing *incoming[2];
    vector<cpppred_state> states;
    #ifdef TRACE
        bool active = false;
        string comment;
        void set_comment(string x) {comment = x;};
        void set_active(bool a)
        {
            active = a;
            dump();
        }
    #endif
};

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

#ifdef TRACE
void trace_flush()
{
    trace << trace_string;
    trace_string.clear();
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

void dump_state(int indent, cpppred_state *state)
{
    if (!state->active)
        return;
    //for (int i = 0; i < indent; i++)
    //    trace_write("\t");

    trace_write_raw("<li>");
    trace_write(state->comment);
    trace_write_raw("</li>");
    indent += 2;
    trace_write_raw("<ul>");
    for (auto substate: state->states)
    {
        if (!substate.active) break;
        dump_state(indent, &substate);
    }
    trace_write_raw("</ul>");
}

void dump()
{
    trace_write_raw("window.pyco.frames.push(\"<ul>");
        dump_state(0, query_state);
    trace_write_raw("</ul><br><br><br><br><br><br><br>\");\n");
    trace_flush();
}

string thing_to_string(Thing* thing);
string thing_to_string_nogetval(Thing* v)
{
  if (v->type == CONST)
    if (strings[v->string_id].first == URI)
      return "<" + strings[v->string_id].second + ">";
    else
      return "\"" + strings[v->string_id].second + "\"";
  else
    if (v->type == UNBOUND)
        return "?"+v->debug_name;
    else if (v->type == BNODE)
        return "["+v->debug_name+"]";
    else
        return "?"+v->debug_name+"->"+thing_to_string(v);

}

string thing_to_string(Thing* thing)
{
  return thing_to_string_nogetval(get_value(thing));
}


#endif
/*
unsigned push_string(string);
	pop_string(string);

	vector<string> strings;

	add_string(string)
	{
		if ((it = string2codes.find(string)) != string2codes.end())
			return *it;
		string2codes[string] =

	}
*/

/*
remember to getvalue as needed before.

later, for optimalization, we dont need to call this function in every case.
the pred function knows when its unifying two constants, for example,
and can trivially yield/continue on.
*/

bool is_bnode_productively_different(Thing *old, Thing *now)
{
    return (bnode_to_id[now] < bnode_to_id[old]);
}

bool is_arg_productively_different(Thing *old, Thing *now)
{
    if (now->type == BOUND || now->type == UNBOUND)
    {
        if (old->type == BOUND || old->type == UNBOUND)
            return false;
        if (old->type == CONST || old->type == BNODE)
            return true;
    }
    if (now->type == CONST)
    {
        if (old->type == BOUND || old->type == UNBOUND || old->type == BNODE)
            return true;
        ASSERT(old->type == CONST);
            return !(*old == *now);
    }
    if (now->type == BNODE)
    {
        if (old->type == BOUND || old->type == UNBOUND || old->type == CONST)
            return true;
        ASSERT(old->type == BNODE);
            return false;
    }
    ASSERT(false);
}

bool detect_ep(const ep_head head, const ep_head incoming)
{
#ifdef TRACE
        cerr << thing_to_string_nogetval(head.first) << " vs " << thing_to_string_nogetval(incoming.first) << " and " <<
        thing_to_string_nogetval(head.second) << " vs " << thing_to_string_nogetval(incoming.second) << endl;
#endif
        if (is_arg_productively_different(head.first, incoming.first) ||
            is_arg_productively_different(head.second, incoming.second))
            return false;
        if (head.first->type == BNODE && incoming.first->type == BNODE)
            if (is_bnode_productively_different(head.first, incoming.first))
                return false;
        if (head.second->type == BNODE && incoming.second->type == BNODE)
            if (is_bnode_productively_different(head.second, incoming.second))
                return false;
        return true;
}

bool find_ep(ep_table *table, ep_head incoming)
{
    for (const ep_head head: *table)
    {
        if (detect_ep(head, incoming))
            return true;
    }
    return false;
}


static size_t query(cpppred_state & __restrict__ state);
void print_result(cpppred_state &state);

int main (int argc, char *argv[])
{
	(void )argc;
	(void )argv;
    #ifdef TRACE
	trace.open("pyco_visualization/trace.js");
	trace_write_raw("window.pyco = Object();window.pyco.frames = [];\n");
	#endif
    cpppred_state state;
    query_state = &state;
    state.entry = 0;
    while(query(state)!=0)
    {
        print_result(state);
    }
    #ifdef TRACE
    trace_flush();
    trace.close();
    #endif
}

#define yield(x) {state.entry = (char*)&&x - (char*)&&case0; return state.entry;}

int unify(cpppred_state & __restrict__ state);


#ifdef TRACE
#define END {state.set_active(false); return 0;}
#else
#define END {return 0;}
#endif




