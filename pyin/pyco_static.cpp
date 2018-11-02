#include <string>
#include <map>
#include <tuple>
#include <vector>
#include <cassert>
#include <iostream>

#define ASSERT assert

using namespace std;

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

    //just bitwise comparison, not recursive check of equality of bindings

    bool operator==(const Thing& b) const
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
};


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
#define yield(x) {state.entry = (char*)&&x - (char*)&&case0; return state.entry;}

int unify(cpppred_state & __restrict__ state)
{
    Thing *x = state.incoming[0];
    Thing *y = state.incoming[1];
    goto *(((char*)&&case0) + state.entry);
    case0:
    ASSERT(x->type != BOUND);ASSERT(y->type != BOUND);
    if (x == y)
        yield(single_success)
    if (x->type == UNBOUND)
    {
        x->bind(y);
        yield(unbind_x)
    }
    if (y->type == UNBOUND)
    {
        y->bind(x);
        yield(unbind_y)
    }
    if ((x->type == CONST) && (*x == *y))
        yield(single_success)
    //two bnodes fail
    single_success:
	return 0;
    unbind_x:
    x->unbind();
    return 0;
    unbind_y:
    y->unbind();
    return 0;
}


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
    cpppred_state state;
    state.entry = 0;
    while(query(state)!=0)
    {
        print_result(state);
    }
}
