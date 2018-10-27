#include <string>
#include <map>
#include <vector>

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
    Locals *locals;
    Thing *binding;
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
    Thing incoming[2];
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
