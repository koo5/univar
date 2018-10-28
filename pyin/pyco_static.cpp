#include <string>
#include <map>
#include <vector>
#include <cassert>

#define ASSERT assert

using namespace std;

typedef unsigned long nodeid;


enum ThingType {BOUND, UNBOUND, CONST, BOUND_BNODE, UNBOUND_BNODE};
/*on a 64 bit system, we have 3 bits to store these, on a 32 bit system, two bits*/

typedef unsigned BnodeOrigin;
typedef unsigned BnodeIndex;

//map<BnodeIndex,Locals> bnodes;


struct Thing;

typedef vector<Thing> Locals;

struct Bnode
{
    BnodeOrigin origin;
 };


struct Thing
{
    ThingType type;
    union
    {
        Thing *binding;
        nodeid string;
        Bnode bnode;
    };
};


typedef Thing ep_t[2];

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
int unify(cpppred_state & __restrict__ state)
{
    Thing *x = state.incoming[0];
    Thing *y = state.incoming[1];
    ASSERT(x->type != BOUND);
    ASSERT(y->type != BOUND);
    goto *(((char*)&&case0) + state.entry);
    case0:
    if (x == y)
    {
        //state.msg = "same things";
        state.entry = single_success;
        return state.entry;
    }
    else if (x->type() == UNBOUND)
    {
		x->bind(y);
        state.entry = unbind_x;
        return state.entry;
    }
    else if (y->type() == UNBOUND)
    {
		y->bind(x);
        state.entry = unbind_y;
        return state.entry;
    }
	elif y_is_var and x_is_var and val_x.is_a_bnode_from_original_rule == val_y.is_a_bnode_from_original_rule and val_x.is_from_name == val_y.is_from_name:
		return val_y.bind_to(val_x, yx)
	elif type(val_x) is Atom and type(val_y) is Atom:
		if val_x.value == val_y.value:
			return success("same consts", xy)
		else:
			return fail(nolog or ("different consts: %s %s" % (val_x.value, val_y.value)), xy)
	else:
		return fail(nolog or ("different things: %s %s" % (val_x, val_y)), xy)



}




