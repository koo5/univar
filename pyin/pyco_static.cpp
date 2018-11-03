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

void dump();

typedef pair<Thing,Thing> thingthingpair;
//ep_head is an array/pair of 2 Things
typedef thingthingpair ep_head;
typedef vector<ep_head> ep_table;
struct cpppred_state;
struct cpppred_state
{
    ep_head ep;
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
    for (int i = 0; i < indent; i++)
        trace_write("\t");
    trace_write(state->comment);
    trace_write_raw("<br>\\n");
    indent += 2;
    for (auto substate: state->states)
    {
        if (!substate.active) break;
        dump_state(indent, &substate);
    }
}

void dump()
{
    trace_write_raw("window.pyco.frames.push(\"");
        dump_state(0, query_state);
    for (int i = 0; i < 10; i++) //force scrollbar to always appear so it doesnt blink in and out and cause reflows
        trace_write_raw("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>");
    trace_write_raw("\");\n");
    trace_flush();
}


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

Thing *get_value(Thing *x)
{
    if (x->type == BOUND)
        return get_value(x->binding);
    return x;
}


bool find_ep(ep_table *table, ep_head incoming)
{
    Thing a,b,x,y;
    x = incoming.first;
    y = incoming.second;
    ASSERT(x.type != BOUND);ASSERT(y.type != BOUND);
    for (const ep_head head: *table)
    {
        a = head.first;
        b = head.second;
        ASSERT(a.type != BOUND);ASSERT(b.type != BOUND);
        if ((a == x) && (b == y)) return true;
    }
    return false;
}

static size_t query(cpppred_state & __restrict__ state);
void print_result(cpppred_state &state);

int main (int argc, char *argv[])
{
	(void )argc;
	(void )argv;
	trace.open("pyco_visualization/trace.js");
	trace_write_raw("window.pyco = Object();window.pyco.frames = [];\n");
    cpppred_state state;
    query_state = &state;
    state.entry = 0;
    while(query(state)!=0)
    {
        print_result(state);
    }
    trace.close();
}

#define yield(x) {state.entry = (char*)&&x - (char*)&&case0; return state.entry;}

int unify(cpppred_state & __restrict__ state);

#define END {state.set_active(false);return 0;}
extern vector<Constant> strings;

string thing_to_string(Thing* thing)
{
  Thing *v = get_value(thing);
  if (v->type == CONST)
    if (strings[v->string_id].first == URI)
      return "<" + strings[v->string_id].second + ">";
    else
      return "\"" + strings[v->string_id].second + "\"";
  else
    return thing->debug_name;
}
