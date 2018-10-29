#include <string>
#include <map>
#include <tuple>
#include <vector>
#include <cassert>
#include <iostream>

#define ASSERT assert

using namespace std;

typedef unsigned long nodeid;


enum ThingType {BOUND, UNBOUND, CONST, BNODE};
/*on a 64 bit system, we have 3 bits to store these, on a 32 bit system, two bits*/

typedef unsigned BnodeOrigin;
typedef unsigned BnodeIndex;

//map<BnodeIndex,Locals> bnodes;


struct Thing;

typedef vector<Thing> Locals;

struct Thing
{
    ThingType type;
    union
    {
        Thing *binding;
        nodeid string_id;
        BnodeOrigin origin;
    };
    const bool operator==(const Thing& b)
    {
        return this->type == b.type && this->binding == b.binding;
    }
};

typedef pair<Thing,Thing> thingthingpair;
typedef thingthingpair ep_head;
typedef vector<ep_head> ep_table;
struct cpppred_state;
struct cpppred_state
{
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
    ASSERT(x->type != BOUND);ASSERT(y->type != BOUND);
    goto *(((char*)&&case0) + state.entry);
    case0:
    if (x == y)
        yield(single_success)
    Thing x_ = *x;
    Thing y_ = *y;
    if (x_.type == UNBOUND)
    {
		x_.binding = y;
        yield(unbind_x)
    }
    if (y_.type == UNBOUND)
    {
		y_.binding = x;
        yield(unbind_y)
    }
    if ((x_.type == CONST) && (x_ == y_))
        yield(end)
    unbind_x:
        x->binding = 0;
    single_success:
        return 0;
    unbind_y:
        y->binding = 0;
    end:
        return 0;
}


Thing *get_value(Thing *x)
{
    if (x->type == BOUND)
        return get_value(x->binding);
    return x;
}


bool find_ep(ep_table *table, ep_head incoming)
{//{BOUND, UNBOUND, CONST, BNODE};
    Thing a,b,x,y;
    x = incoming.first;
    y = incoming.second;
    ASSERT(x.type != BOUND);ASSERT(y.type != BOUND);
    for (const ep_head head: *table)
    {
        a = head.first;
        b = head.second;
        ASSERT(a.type != BOUND);ASSERT(b.type != BOUND);
        if ((a.type != x.type) || (b.type != y.type)) continue;
        if ((a.type != UNBOUND) && !(a == x)) continue;
        if ((b.type != UNBOUND) && !(b == y)) continue;
        return true;
    }
    return false;
}

int main (int argc, char *argv[])
{
    cpppred_state state;
    state.entry = 0;
    while(query(state)!=0)
    {
        print_result(state);
    }
}
