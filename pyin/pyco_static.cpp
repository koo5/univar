#include <string>

using namespace std;

typedef unsigned long nodeid;
nodeid last_nodeid = 0;
map<nodeid, string> strings;

enum ThingType {BOUND, CONST, BOUND_BNODE, UNBOUND_BNODE, UNBOUND};

typedef unsigned BnodeOrigin;
typedef unsigned BnodeIndex;
typedef vector<Thing> Locals;

map<BnodeIndex,Locals> bnodes;

struct Thing
{
    ThingType type;
    union
    {
        Thing *binding;
        nodeid const_value;
        struct
        {
            BnodeOrigin bnode_origin;
            Locals *bindings;
        };
    };
};

union unbinder{coro c; char magic;};

struct cpppred_state;
struct cpppred_state
{
    int entry=0;
    Locals locals;
    unbinder su,ou;
    Thing *s, *o;
    vector<cpppred_state> children;
};

















struct coro_state
{
    int entry=0;
}




#include "pyco_output.cpp"
