#include "globals.cpp"
#include "univar.cpp"
union unbinder{coro c; char magic; unbinder(){} unbinder(const unbinder&u){(void)u;} ~unbinder(){}};
struct cpppred_state;
struct cpppred_state {
int entry=0;
vector<Thing> locals;
unbinder su,ou;
Thing *s, *o;
vector<cpppred_state> states;
};
bool silent = false;/* forward declarations */
static int cpppred506(cpppred_state & __restrict__ state, int entry);
/* pred function definitions */
static Locals consts_cpppred506_0 = {Thing(NODE, 495), Thing(NODE, 514)};

static int cpppred506(cpppred_state & __restrict__ state, int entry){
char uuus;(void)uuus;
char uuuo;(void)uuuo;
switch(entry){
case 0:
//rule 0:
if (unify_with_const(state.s, (&consts_cpppred506_0[0]))){
if (unify_with_const(state.o, (&consts_cpppred506_0[1]))){
entry = 1;
return entry;
case 1:;
unbind_from_const(state.o);
}
unbind_from_const(state.s);
}
}return -1;}

static Locals consts_cppout_query_0 = {Thing(NODE, 566), Thing(NODE, 584)};

static int cppout_query(cpppred_state & __restrict__ state, int entry){
int entry0;
static int counter = 0;
static vector<Thing> prev_results;char uuus;(void)uuus;
char uuuo;(void)uuuo;
switch(entry){
case 0:
state.states.resize(1);
//rule 0:
entry = 1;
//body item0
entry0 = 0;
state.states[0].s = (&consts_cppout_query_0[0]);
state.states[0].o = (&consts_cppout_query_0[1]);
do{
entry0=cpppred506(state.states[0], entry0);
if(entry0 == -1) break;
{Thing * bisx, * biox;
bisx = getValue((&consts_cppout_query_0[0]));
biox = getValue((&consts_cppout_query_0[1]));
if(prev_results.size() == 2){	if (are_equal(prev_results[0], *bisx) && are_equal(prev_results[1], *biox) && (counter % 1024))goto skip;	prev_results[0] = *bisx;      prev_results[1] = *biox;}else {prev_results.push_back(*bisx);prev_results.push_back(*biox);}if (!silent) dout << unifys << " unifys "  ;
if (!silent) dout << " RESULT " << counter << ": ";
{Thing * bis, * bio;
bis = getValue((&consts_cppout_query_0[0]));
bio = getValue((&consts_cppout_query_0[1]));
Thing n1; if (is_unbound(*bis)) {bis = &n1; n1 = create_node(566);};
Thing n2; if (is_unbound(*bio)) {bio = &n2; n2 = create_node(584);};
if (!silent) dout << str(bis) << " <file://tests/simple/1#foo> " << str(bio) << ".";};
if (!silent) dout << "\n";}
skip:;counter++;
state.states[0].entry = entry0;
return entry;
case 1:;
entry0 = state.states[0].entry;
}while(true);
}return -1;}

void cppdict_init(){
cppdict[495] = "file://tests/simple/1#baz";
cppdict[514] = "file://tests/simple/1#bar";
cppdict[566] = "file://tests/simple/1?x";
cppdict[584] = "file://tests/simple/1?y";
}
#include "cppmain.cpp"

