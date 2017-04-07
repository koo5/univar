#include "globals.cpp"
#include "univar.cpp"
union unbinder {
    coro c;
    char magic;
    unbinder() {} unbinder(const unbinder&u) {
        (void)u;
    } ~unbinder() {}
};
struct cpppred_state;
struct cpppred_state {
    int entry=0;
    vector<Thing> locals;
    unbinder su,ou;
    Thing *s, *o;
    vector<cpppred_state> states;
};
bool silent = false;/* forward declarations */
static int cpppred227(cpppred_state & __restrict__ state, int entry);
static int cpppred1906(cpppred_state & __restrict__ state, int entry);
static int cpppred1937(cpppred_state & __restrict__ state, int entry);
static int cpppred1967(cpppred_state & __restrict__ state, int entry);
static int cpppred1997(cpppred_state & __restrict__ state, int entry);
static int cpppred2030(cpppred_state & __restrict__ state, int entry);
static int cpppred2220(cpppred_state & __restrict__ state, int entry);
static int cpppred3407(cpppred_state & __restrict__ state, int entry);
static int cpppred3710(cpppred_state & __restrict__ state, int entry);
/* pred function definitions */
static Locals consts_cpppred227_0 = {(Thing)0x1ff1, (Thing)0x22e5};
static Locals consts_cpppred227_1 = {(Thing)0x25cd, (Thing)0x22e5};
static Locals consts_cpppred227_2 = {(Thing)0x2b99, (Thing)0x22e5};
static Locals consts_cpppred227_3 = {(Thing)0x3165, (Thing)0x3451};
static Locals consts_cpppred227_4 = {(Thing)0x36c5, (Thing)0x391d};
static Locals consts_cpppred227_5 = {(Thing)0x3b75, (Thing)0x3dcd};

static int cpppred227(cpppred_state & __restrict__ state, int entry) {
    char uuus;
    (void)uuus;
    char uuuo;
    (void)uuuo;
    switch(entry) {
    case 0:
//rule 0:
        if (unify_with_const(state.s, (&consts_cpppred227_0[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred227_0[1]))) {
                entry = 1;
                return entry;
            case 1:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 1:
        if (unify_with_const(state.s, (&consts_cpppred227_1[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred227_1[1]))) {
                entry = 2;
                return entry;
            case 2:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 2:
        if (unify_with_const(state.s, (&consts_cpppred227_2[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred227_2[1]))) {
                entry = 3;
                return entry;
            case 3:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 3:
        if (unify_with_const(state.s, (&consts_cpppred227_3[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred227_3[1]))) {
                entry = 4;
                return entry;
            case 4:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 4:
        if (unify_with_const(state.s, (&consts_cpppred227_4[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred227_4[1]))) {
                entry = 5;
                return entry;
            case 5:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 5:
        if (unify_with_const(state.s, (&consts_cpppred227_5[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred227_5[1]))) {
                entry = 6;
                return entry;
            case 6:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
    }
    return -1;
}

static Locals consts_cpppred1906_0 = {(Thing)0x3fe9, (Thing)0x3e69};
static Locals consts_cpppred1906_1 = {(Thing)0x41f9, (Thing)0x3e69};
static Locals consts_cpppred1906_2 = {(Thing)0x4185, (Thing)0x4111};
static Locals consts_cpppred1906_3 = {(Thing)0x4435, (Thing)0x43c1};
static Locals consts_cpppred1906_4 = {(Thing)0x4835, (Thing)0x474d};
static Locals consts_cpppred1906_5 = {(Thing)0x47c1, (Thing)0x474d};
static Locals consts_cpppred1906_6 = {(Thing)0x4ca5, (Thing)0x4c31};
static Locals consts_cpppred1906_7 = {(Thing)0x49fd, (Thing)0x4989};
static Locals consts_cpppred1906_8 = {(Thing)0x426d, (Thing)0x4989};

static int cpppred1906(cpppred_state & __restrict__ state, int entry) {
    char uuus;
    (void)uuus;
    char uuuo;
    (void)uuuo;
    switch(entry) {
    case 0:
//rule 0:
        if (unify_with_const(state.s, (&consts_cpppred1906_0[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1906_0[1]))) {
                entry = 1;
                return entry;
            case 1:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 1:
        if (unify_with_const(state.s, (&consts_cpppred1906_1[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1906_1[1]))) {
                entry = 2;
                return entry;
            case 2:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 2:
        if (unify_with_const(state.s, (&consts_cpppred1906_2[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1906_2[1]))) {
                entry = 3;
                return entry;
            case 3:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 3:
        if (unify_with_const(state.s, (&consts_cpppred1906_3[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1906_3[1]))) {
                entry = 4;
                return entry;
            case 4:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 4:
        if (unify_with_const(state.s, (&consts_cpppred1906_4[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1906_4[1]))) {
                entry = 5;
                return entry;
            case 5:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 5:
        if (unify_with_const(state.s, (&consts_cpppred1906_5[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1906_5[1]))) {
                entry = 6;
                return entry;
            case 6:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 6:
        if (unify_with_const(state.s, (&consts_cpppred1906_6[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1906_6[1]))) {
                entry = 7;
                return entry;
            case 7:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 7:
        if (unify_with_const(state.s, (&consts_cpppred1906_7[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1906_7[1]))) {
                entry = 8;
                return entry;
            case 8:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 8:
        if (unify_with_const(state.s, (&consts_cpppred1906_8[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1906_8[1]))) {
                entry = 9;
                return entry;
            case 9:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
    }
    return -1;
}

static Locals consts_cpppred1937_0 = {(Thing)0x3fe9, (Thing)0x3ee9};
static Locals consts_cpppred1937_1 = {(Thing)0x41f9, (Thing)0x4111};
static Locals consts_cpppred1937_2 = {(Thing)0x4185, (Thing)0x3ee9};
static Locals consts_cpppred1937_3 = {(Thing)0x4435, (Thing)0x4589};
static Locals consts_cpppred1937_4 = {(Thing)0x4835, (Thing)0x3f69};
static Locals consts_cpppred1937_5 = {(Thing)0x47c1, (Thing)0x4989};
static Locals consts_cpppred1937_6 = {(Thing)0x4ca5, (Thing)0x4d89};
static Locals consts_cpppred1937_7 = {(Thing)0x49fd, (Thing)0x3f69};
static Locals consts_cpppred1937_8 = {(Thing)0x426d, (Thing)0x4111};

static int cpppred1937(cpppred_state & __restrict__ state, int entry) {
    char uuus;
    (void)uuus;
    char uuuo;
    (void)uuuo;
    switch(entry) {
    case 0:
//rule 0:
        if (unify_with_const(state.s, (&consts_cpppred1937_0[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1937_0[1]))) {
                entry = 1;
                return entry;
            case 1:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 1:
        if (unify_with_const(state.s, (&consts_cpppred1937_1[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1937_1[1]))) {
                entry = 2;
                return entry;
            case 2:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 2:
        if (unify_with_const(state.s, (&consts_cpppred1937_2[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1937_2[1]))) {
                entry = 3;
                return entry;
            case 3:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 3:
        if (unify_with_const(state.s, (&consts_cpppred1937_3[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1937_3[1]))) {
                entry = 4;
                return entry;
            case 4:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 4:
        if (unify_with_const(state.s, (&consts_cpppred1937_4[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1937_4[1]))) {
                entry = 5;
                return entry;
            case 5:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 5:
        if (unify_with_const(state.s, (&consts_cpppred1937_5[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1937_5[1]))) {
                entry = 6;
                return entry;
            case 6:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 6:
        if (unify_with_const(state.s, (&consts_cpppred1937_6[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1937_6[1]))) {
                entry = 7;
                return entry;
            case 7:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 7:
        if (unify_with_const(state.s, (&consts_cpppred1937_7[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1937_7[1]))) {
                entry = 8;
                return entry;
            case 8:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 8:
        if (unify_with_const(state.s, (&consts_cpppred1937_8[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1937_8[1]))) {
                entry = 9;
                return entry;
            case 9:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
    }
    return -1;
}

static Locals consts_cpppred1967_0 = {(Thing)0x3fe9, (Thing)0x4111};
static Locals consts_cpppred1967_1 = {(Thing)0x41f9, (Thing)0x43c1};
static Locals consts_cpppred1967_2 = {(Thing)0x4185, (Thing)0x4589};
static Locals consts_cpppred1967_3 = {(Thing)0x4435, (Thing)0x474d};
static Locals consts_cpppred1967_4 = {(Thing)0x4835, (Thing)0x4989};
static Locals consts_cpppred1967_5 = {(Thing)0x47c1, (Thing)0x4c31};
static Locals consts_cpppred1967_6 = {(Thing)0x4ca5, (Thing)0x4dfd};
static Locals consts_cpppred1967_7 = {(Thing)0x49fd, (Thing)0x4d89};
static Locals consts_cpppred1967_8 = {(Thing)0x426d, (Thing)0x5111};

static int cpppred1967(cpppred_state & __restrict__ state, int entry) {
    char uuus;
    (void)uuus;
    char uuuo;
    (void)uuuo;
    switch(entry) {
    case 0:
//rule 0:
        if (unify_with_const(state.s, (&consts_cpppred1967_0[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1967_0[1]))) {
                entry = 1;
                return entry;
            case 1:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 1:
        if (unify_with_const(state.s, (&consts_cpppred1967_1[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1967_1[1]))) {
                entry = 2;
                return entry;
            case 2:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 2:
        if (unify_with_const(state.s, (&consts_cpppred1967_2[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1967_2[1]))) {
                entry = 3;
                return entry;
            case 3:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 3:
        if (unify_with_const(state.s, (&consts_cpppred1967_3[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1967_3[1]))) {
                entry = 4;
                return entry;
            case 4:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 4:
        if (unify_with_const(state.s, (&consts_cpppred1967_4[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1967_4[1]))) {
                entry = 5;
                return entry;
            case 5:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 5:
        if (unify_with_const(state.s, (&consts_cpppred1967_5[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1967_5[1]))) {
                entry = 6;
                return entry;
            case 6:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 6:
        if (unify_with_const(state.s, (&consts_cpppred1967_6[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1967_6[1]))) {
                entry = 7;
                return entry;
            case 7:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 7:
        if (unify_with_const(state.s, (&consts_cpppred1967_7[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1967_7[1]))) {
                entry = 8;
                return entry;
            case 8:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 8:
        if (unify_with_const(state.s, (&consts_cpppred1967_8[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1967_8[1]))) {
                entry = 9;
                return entry;
            case 9:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
    }
    return -1;
}

static Locals consts_cpppred1997_0 = {};
static Locals consts_cpppred1997_1 = {(Thing)0x3e69, (Thing)0x22dd};

static int cpppred1997(cpppred_state & __restrict__ state, int entry) {
    static ep_t ep0;
    int entry0;
    int entry1;
    int entry2;
    int entry3;
    char uuus;
    (void)uuus;
    char uuuo;
    (void)uuuo;
    switch(entry) {
    case 0:
        state.states.resize(4);
//rule 0:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            uuuo = unify_with_var(state.o, (&state.locals[1]));
            if (uuuo & 1) {
                state.ou.magic = uuuo;
                if (!cppout_find_ep(&ep0, state.s, state.o)) {
                    ep0.push_back(thingthingpair(state.s, state.o));
                    entry = 1;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[2]));
                    state.states[0].o = getValue_nooffset((&state.locals[3]));
                    do {
                        entry0=cpppred3710(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[2]));
                        state.states[1].o = getValue_nooffset((&state.locals[0]));
                        do {
                            entry1=cpppred1967(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[3]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1906(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[0]));
                                state.states[3].o = getValue_nooffset((&state.locals[1]));
                                do {
                                    entry3=cpppred2220(state.states[3], entry3);
                                    if(entry3 == -1) break;
                                    ASSERT(ep0.size());
                                    ep0.pop_back();

                                    state.states[0].entry = entry0;
                                    state.states[1].entry = entry1;
                                    state.states[2].entry = entry2;
                                    state.states[3].entry = entry3;
                                    return entry;
                                case 1:
                                    ;
                                    entry0 = state.states[0].entry;
                                    entry1 = state.states[1].entry;
                                    entry2 = state.states[2].entry;
                                    entry3 = state.states[3].entry;
                                    ep0.push_back(thingthingpair(state.s, state.o));
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep0.size());
                    ep0.pop_back();
                }
                unbind_from_var(state.ou.magic, state.o, (&state.locals[1]));
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
//rule 1:
        if (unify_with_const(state.s, (&consts_cpppred1997_1[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred1997_1[1]))) {
                entry = 2;
                return entry;
            case 2:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
    }
    return -1;
}

static Locals consts_cpppred2030_0 = {};
static Locals consts_cpppred2030_1 = {(Thing)0x3ee9, (Thing)0x22dd};
static Locals consts_cpppred2030_2 = {(Thing)0x3f69, (Thing)0x22dd};

static int cpppred2030(cpppred_state & __restrict__ state, int entry) {
    static ep_t ep0;
    int entry0;
    int entry1;
    int entry2;
    int entry3;
    char uuus;
    (void)uuus;
    char uuuo;
    (void)uuuo;
    switch(entry) {
    case 0:
        state.states.resize(4);
//rule 0:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            uuuo = unify_with_var(state.o, (&state.locals[1]));
            if (uuuo & 1) {
                state.ou.magic = uuuo;
                if (!cppout_find_ep(&ep0, state.s, state.o)) {
                    ep0.push_back(thingthingpair(state.s, state.o));
                    entry = 1;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[2]));
                    state.states[0].o = getValue_nooffset((&state.locals[3]));
                    do {
                        entry0=cpppred3407(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[2]));
                        state.states[1].o = getValue_nooffset((&state.locals[0]));
                        do {
                            entry1=cpppred1967(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[3]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1937(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[0]));
                                state.states[3].o = getValue_nooffset((&state.locals[1]));
                                do {
                                    entry3=cpppred2220(state.states[3], entry3);
                                    if(entry3 == -1) break;
                                    ASSERT(ep0.size());
                                    ep0.pop_back();

                                    state.states[0].entry = entry0;
                                    state.states[1].entry = entry1;
                                    state.states[2].entry = entry2;
                                    state.states[3].entry = entry3;
                                    return entry;
                                case 1:
                                    ;
                                    entry0 = state.states[0].entry;
                                    entry1 = state.states[1].entry;
                                    entry2 = state.states[2].entry;
                                    entry3 = state.states[3].entry;
                                    ep0.push_back(thingthingpair(state.s, state.o));
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep0.size());
                    ep0.pop_back();
                }
                unbind_from_var(state.ou.magic, state.o, (&state.locals[1]));
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
//rule 1:
        if (unify_with_const(state.s, (&consts_cpppred2030_1[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred2030_1[1]))) {
                entry = 2;
                return entry;
            case 2:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 2:
        if (unify_with_const(state.s, (&consts_cpppred2030_2[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred2030_2[1]))) {
                entry = 3;
                return entry;
            case 3:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
    }
    return -1;
}

static Locals consts_cpppred2220_0 = {(Thing)0x22dd, (Thing)0x1f61};
static Locals consts_cpppred2220_1 = {(Thing)0x22dd, (Thing)0x1f61};
static Locals consts_cpppred2220_2 = {(Thing)0x22dd, (Thing)0x1f61};
static Locals consts_cpppred2220_3 = {(Thing)0x22dd, (Thing)0x1f61};
static Locals consts_cpppred2220_4 = {(Thing)0x22dd, (Thing)0x1f61};
static Locals consts_cpppred2220_5 = {(Thing)0x22dd, (Thing)0x1f61};
static Locals consts_cpppred2220_6 = {(Thing)0x22dd, (Thing)0x1f61};
static Locals consts_cpppred2220_7 = {(Thing)0x22dd, (Thing)0x1f61};
static Locals consts_cpppred2220_8 = {(Thing)0x22dd, (Thing)0x1f61};
static Locals consts_cpppred2220_9 = {(Thing)0x1f61, (Thing)0x22dd};

static int cpppred2220(cpppred_state & __restrict__ state, int entry) {
    static ep_t ep0;
    static ep_t ep1;
    static ep_t ep2;
    static ep_t ep3;
    static ep_t ep4;
    static ep_t ep5;
    static ep_t ep6;
    static ep_t ep7;
    static ep_t ep8;
    static ep_t ep9;
    int entry0;
    int entry1;
    int entry2;
    int entry3;
    int entry4;
    char uuus;
    (void)uuus;
    char uuuo;
    (void)uuuo;
    switch(entry) {
    case 0:
        state.states.resize(5);
//rule 0:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            if (unify_with_const(state.o, (&consts_cpppred2220_0[0]))) {
                if (!cppout_find_ep(&ep0, state.s, state.o)) {
                    ep0.push_back(thingthingpair(state.s, state.o));
                    entry = 1;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[1]));
                    state.states[0].o = getValue_nooffset((&state.locals[2]));
                    do {
                        entry0=cpppred1906(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[1]));
                        state.states[1].o = getValue_nooffset((&state.locals[3]));
                        do {
                            entry1=cpppred1937(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[1]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1967(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[2]));
                                state.states[3].o = (&consts_cpppred2220_0[1]);
                                do {
                                    entry3=cpppred1997(state.states[3], entry3);
                                    if(entry3 == -1) break;
//body item4
                                    entry4 = 0;
                                    state.states[4].s = getValue_nooffset((&state.locals[3]));
                                    state.states[4].o = (&consts_cpppred2220_0[1]);
                                    do {
                                        entry4=cpppred2030(state.states[4], entry4);
                                        if(entry4 == -1) break;
                                        ASSERT(ep0.size());
                                        ep0.pop_back();

                                        state.states[0].entry = entry0;
                                        state.states[1].entry = entry1;
                                        state.states[2].entry = entry2;
                                        state.states[3].entry = entry3;
                                        state.states[4].entry = entry4;
                                        return entry;
                                    case 1:
                                        ;
                                        entry0 = state.states[0].entry;
                                        entry1 = state.states[1].entry;
                                        entry2 = state.states[2].entry;
                                        entry3 = state.states[3].entry;
                                        entry4 = state.states[4].entry;
                                        ep0.push_back(thingthingpair(state.s, state.o));
                                    } while(true);
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep0.size());
                    ep0.pop_back();
                }
                unbind_from_const(state.o);
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
//rule 1:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            if (unify_with_const(state.o, (&consts_cpppred2220_1[0]))) {
                if (!cppout_find_ep(&ep1, state.s, state.o)) {
                    ep1.push_back(thingthingpair(state.s, state.o));
                    entry = 2;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[1]));
                    state.states[0].o = getValue_nooffset((&state.locals[2]));
                    do {
                        entry0=cpppred1906(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[1]));
                        state.states[1].o = getValue_nooffset((&state.locals[3]));
                        do {
                            entry1=cpppred1937(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[1]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1967(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[2]));
                                state.states[3].o = (&consts_cpppred2220_1[1]);
                                do {
                                    entry3=cpppred1997(state.states[3], entry3);
                                    if(entry3 == -1) break;
//body item4
                                    entry4 = 0;
                                    state.states[4].s = getValue_nooffset((&state.locals[3]));
                                    state.states[4].o = (&consts_cpppred2220_1[1]);
                                    do {
                                        entry4=cpppred2030(state.states[4], entry4);
                                        if(entry4 == -1) break;
                                        ASSERT(ep1.size());
                                        ep1.pop_back();

                                        state.states[0].entry = entry0;
                                        state.states[1].entry = entry1;
                                        state.states[2].entry = entry2;
                                        state.states[3].entry = entry3;
                                        state.states[4].entry = entry4;
                                        return entry;
                                    case 2:
                                        ;
                                        entry0 = state.states[0].entry;
                                        entry1 = state.states[1].entry;
                                        entry2 = state.states[2].entry;
                                        entry3 = state.states[3].entry;
                                        entry4 = state.states[4].entry;
                                        ep1.push_back(thingthingpair(state.s, state.o));
                                    } while(true);
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep1.size());
                    ep1.pop_back();
                }
                unbind_from_const(state.o);
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
//rule 2:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            if (unify_with_const(state.o, (&consts_cpppred2220_2[0]))) {
                if (!cppout_find_ep(&ep2, state.s, state.o)) {
                    ep2.push_back(thingthingpair(state.s, state.o));
                    entry = 3;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[1]));
                    state.states[0].o = getValue_nooffset((&state.locals[2]));
                    do {
                        entry0=cpppred1906(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[1]));
                        state.states[1].o = getValue_nooffset((&state.locals[3]));
                        do {
                            entry1=cpppred1937(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[1]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1967(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[2]));
                                state.states[3].o = (&consts_cpppred2220_2[1]);
                                do {
                                    entry3=cpppred1997(state.states[3], entry3);
                                    if(entry3 == -1) break;
//body item4
                                    entry4 = 0;
                                    state.states[4].s = getValue_nooffset((&state.locals[3]));
                                    state.states[4].o = (&consts_cpppred2220_2[1]);
                                    do {
                                        entry4=cpppred2030(state.states[4], entry4);
                                        if(entry4 == -1) break;
                                        ASSERT(ep2.size());
                                        ep2.pop_back();

                                        state.states[0].entry = entry0;
                                        state.states[1].entry = entry1;
                                        state.states[2].entry = entry2;
                                        state.states[3].entry = entry3;
                                        state.states[4].entry = entry4;
                                        return entry;
                                    case 3:
                                        ;
                                        entry0 = state.states[0].entry;
                                        entry1 = state.states[1].entry;
                                        entry2 = state.states[2].entry;
                                        entry3 = state.states[3].entry;
                                        entry4 = state.states[4].entry;
                                        ep2.push_back(thingthingpair(state.s, state.o));
                                    } while(true);
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep2.size());
                    ep2.pop_back();
                }
                unbind_from_const(state.o);
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
//rule 3:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            if (unify_with_const(state.o, (&consts_cpppred2220_3[0]))) {
                if (!cppout_find_ep(&ep3, state.s, state.o)) {
                    ep3.push_back(thingthingpair(state.s, state.o));
                    entry = 4;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[1]));
                    state.states[0].o = getValue_nooffset((&state.locals[2]));
                    do {
                        entry0=cpppred1906(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[1]));
                        state.states[1].o = getValue_nooffset((&state.locals[3]));
                        do {
                            entry1=cpppred1937(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[1]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1967(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[2]));
                                state.states[3].o = (&consts_cpppred2220_3[1]);
                                do {
                                    entry3=cpppred1997(state.states[3], entry3);
                                    if(entry3 == -1) break;
//body item4
                                    entry4 = 0;
                                    state.states[4].s = getValue_nooffset((&state.locals[3]));
                                    state.states[4].o = (&consts_cpppred2220_3[0]);
                                    do {
                                        entry4=cpppred2030(state.states[4], entry4);
                                        if(entry4 == -1) break;
                                        ASSERT(ep3.size());
                                        ep3.pop_back();

                                        state.states[0].entry = entry0;
                                        state.states[1].entry = entry1;
                                        state.states[2].entry = entry2;
                                        state.states[3].entry = entry3;
                                        state.states[4].entry = entry4;
                                        return entry;
                                    case 4:
                                        ;
                                        entry0 = state.states[0].entry;
                                        entry1 = state.states[1].entry;
                                        entry2 = state.states[2].entry;
                                        entry3 = state.states[3].entry;
                                        entry4 = state.states[4].entry;
                                        ep3.push_back(thingthingpair(state.s, state.o));
                                    } while(true);
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep3.size());
                    ep3.pop_back();
                }
                unbind_from_const(state.o);
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
//rule 4:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            if (unify_with_const(state.o, (&consts_cpppred2220_4[0]))) {
                if (!cppout_find_ep(&ep4, state.s, state.o)) {
                    ep4.push_back(thingthingpair(state.s, state.o));
                    entry = 5;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[1]));
                    state.states[0].o = getValue_nooffset((&state.locals[2]));
                    do {
                        entry0=cpppred1906(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[1]));
                        state.states[1].o = getValue_nooffset((&state.locals[3]));
                        do {
                            entry1=cpppred1937(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[1]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1967(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[2]));
                                state.states[3].o = (&consts_cpppred2220_4[1]);
                                do {
                                    entry3=cpppred1997(state.states[3], entry3);
                                    if(entry3 == -1) break;
//body item4
                                    entry4 = 0;
                                    state.states[4].s = getValue_nooffset((&state.locals[3]));
                                    state.states[4].o = (&consts_cpppred2220_4[0]);
                                    do {
                                        entry4=cpppred2030(state.states[4], entry4);
                                        if(entry4 == -1) break;
                                        ASSERT(ep4.size());
                                        ep4.pop_back();

                                        state.states[0].entry = entry0;
                                        state.states[1].entry = entry1;
                                        state.states[2].entry = entry2;
                                        state.states[3].entry = entry3;
                                        state.states[4].entry = entry4;
                                        return entry;
                                    case 5:
                                        ;
                                        entry0 = state.states[0].entry;
                                        entry1 = state.states[1].entry;
                                        entry2 = state.states[2].entry;
                                        entry3 = state.states[3].entry;
                                        entry4 = state.states[4].entry;
                                        ep4.push_back(thingthingpair(state.s, state.o));
                                    } while(true);
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep4.size());
                    ep4.pop_back();
                }
                unbind_from_const(state.o);
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
//rule 5:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            if (unify_with_const(state.o, (&consts_cpppred2220_5[0]))) {
                if (!cppout_find_ep(&ep5, state.s, state.o)) {
                    ep5.push_back(thingthingpair(state.s, state.o));
                    entry = 6;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[1]));
                    state.states[0].o = getValue_nooffset((&state.locals[2]));
                    do {
                        entry0=cpppred1906(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[1]));
                        state.states[1].o = getValue_nooffset((&state.locals[3]));
                        do {
                            entry1=cpppred1937(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[1]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1967(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[2]));
                                state.states[3].o = (&consts_cpppred2220_5[1]);
                                do {
                                    entry3=cpppred1997(state.states[3], entry3);
                                    if(entry3 == -1) break;
//body item4
                                    entry4 = 0;
                                    state.states[4].s = getValue_nooffset((&state.locals[3]));
                                    state.states[4].o = (&consts_cpppred2220_5[0]);
                                    do {
                                        entry4=cpppred2030(state.states[4], entry4);
                                        if(entry4 == -1) break;
                                        ASSERT(ep5.size());
                                        ep5.pop_back();

                                        state.states[0].entry = entry0;
                                        state.states[1].entry = entry1;
                                        state.states[2].entry = entry2;
                                        state.states[3].entry = entry3;
                                        state.states[4].entry = entry4;
                                        return entry;
                                    case 6:
                                        ;
                                        entry0 = state.states[0].entry;
                                        entry1 = state.states[1].entry;
                                        entry2 = state.states[2].entry;
                                        entry3 = state.states[3].entry;
                                        entry4 = state.states[4].entry;
                                        ep5.push_back(thingthingpair(state.s, state.o));
                                    } while(true);
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep5.size());
                    ep5.pop_back();
                }
                unbind_from_const(state.o);
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
//rule 6:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            if (unify_with_const(state.o, (&consts_cpppred2220_6[0]))) {
                if (!cppout_find_ep(&ep6, state.s, state.o)) {
                    ep6.push_back(thingthingpair(state.s, state.o));
                    entry = 7;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[1]));
                    state.states[0].o = getValue_nooffset((&state.locals[2]));
                    do {
                        entry0=cpppred1906(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[1]));
                        state.states[1].o = getValue_nooffset((&state.locals[3]));
                        do {
                            entry1=cpppred1937(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[1]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1967(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[2]));
                                state.states[3].o = (&consts_cpppred2220_6[0]);
                                do {
                                    entry3=cpppred1997(state.states[3], entry3);
                                    if(entry3 == -1) break;
//body item4
                                    entry4 = 0;
                                    state.states[4].s = getValue_nooffset((&state.locals[3]));
                                    state.states[4].o = (&consts_cpppred2220_6[1]);
                                    do {
                                        entry4=cpppred2030(state.states[4], entry4);
                                        if(entry4 == -1) break;
                                        ASSERT(ep6.size());
                                        ep6.pop_back();

                                        state.states[0].entry = entry0;
                                        state.states[1].entry = entry1;
                                        state.states[2].entry = entry2;
                                        state.states[3].entry = entry3;
                                        state.states[4].entry = entry4;
                                        return entry;
                                    case 7:
                                        ;
                                        entry0 = state.states[0].entry;
                                        entry1 = state.states[1].entry;
                                        entry2 = state.states[2].entry;
                                        entry3 = state.states[3].entry;
                                        entry4 = state.states[4].entry;
                                        ep6.push_back(thingthingpair(state.s, state.o));
                                    } while(true);
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep6.size());
                    ep6.pop_back();
                }
                unbind_from_const(state.o);
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
//rule 7:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            if (unify_with_const(state.o, (&consts_cpppred2220_7[0]))) {
                if (!cppout_find_ep(&ep7, state.s, state.o)) {
                    ep7.push_back(thingthingpair(state.s, state.o));
                    entry = 8;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[1]));
                    state.states[0].o = getValue_nooffset((&state.locals[2]));
                    do {
                        entry0=cpppred1906(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[1]));
                        state.states[1].o = getValue_nooffset((&state.locals[3]));
                        do {
                            entry1=cpppred1937(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[1]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1967(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[2]));
                                state.states[3].o = (&consts_cpppred2220_7[0]);
                                do {
                                    entry3=cpppred1997(state.states[3], entry3);
                                    if(entry3 == -1) break;
//body item4
                                    entry4 = 0;
                                    state.states[4].s = getValue_nooffset((&state.locals[3]));
                                    state.states[4].o = (&consts_cpppred2220_7[1]);
                                    do {
                                        entry4=cpppred2030(state.states[4], entry4);
                                        if(entry4 == -1) break;
                                        ASSERT(ep7.size());
                                        ep7.pop_back();

                                        state.states[0].entry = entry0;
                                        state.states[1].entry = entry1;
                                        state.states[2].entry = entry2;
                                        state.states[3].entry = entry3;
                                        state.states[4].entry = entry4;
                                        return entry;
                                    case 8:
                                        ;
                                        entry0 = state.states[0].entry;
                                        entry1 = state.states[1].entry;
                                        entry2 = state.states[2].entry;
                                        entry3 = state.states[3].entry;
                                        entry4 = state.states[4].entry;
                                        ep7.push_back(thingthingpair(state.s, state.o));
                                    } while(true);
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep7.size());
                    ep7.pop_back();
                }
                unbind_from_const(state.o);
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
//rule 8:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            if (unify_with_const(state.o, (&consts_cpppred2220_8[0]))) {
                if (!cppout_find_ep(&ep8, state.s, state.o)) {
                    ep8.push_back(thingthingpair(state.s, state.o));
                    entry = 9;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[1]));
                    state.states[0].o = getValue_nooffset((&state.locals[2]));
                    do {
                        entry0=cpppred1906(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[1]));
                        state.states[1].o = getValue_nooffset((&state.locals[3]));
                        do {
                            entry1=cpppred1937(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[1]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1967(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[2]));
                                state.states[3].o = (&consts_cpppred2220_8[0]);
                                do {
                                    entry3=cpppred1997(state.states[3], entry3);
                                    if(entry3 == -1) break;
//body item4
                                    entry4 = 0;
                                    state.states[4].s = getValue_nooffset((&state.locals[3]));
                                    state.states[4].o = (&consts_cpppred2220_8[1]);
                                    do {
                                        entry4=cpppred2030(state.states[4], entry4);
                                        if(entry4 == -1) break;
                                        ASSERT(ep8.size());
                                        ep8.pop_back();

                                        state.states[0].entry = entry0;
                                        state.states[1].entry = entry1;
                                        state.states[2].entry = entry2;
                                        state.states[3].entry = entry3;
                                        state.states[4].entry = entry4;
                                        return entry;
                                    case 9:
                                        ;
                                        entry0 = state.states[0].entry;
                                        entry1 = state.states[1].entry;
                                        entry2 = state.states[2].entry;
                                        entry3 = state.states[3].entry;
                                        entry4 = state.states[4].entry;
                                        ep8.push_back(thingthingpair(state.s, state.o));
                                    } while(true);
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep8.size());
                    ep8.pop_back();
                }
                unbind_from_const(state.o);
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
//rule 9:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0};
        uuus = unify_with_var(state.s, (&state.locals[0]));
        if (uuus & 1) {
            state.su.magic = uuus;
            if (unify_with_const(state.o, (&consts_cpppred2220_9[0]))) {
                if (!cppout_find_ep(&ep9, state.s, state.o)) {
                    ep9.push_back(thingthingpair(state.s, state.o));
                    entry = 10;
//body item0
                    entry0 = 0;
                    state.states[0].s = getValue_nooffset((&state.locals[1]));
                    state.states[0].o = getValue_nooffset((&state.locals[2]));
                    do {
                        entry0=cpppred1906(state.states[0], entry0);
                        if(entry0 == -1) break;
//body item1
                        entry1 = 0;
                        state.states[1].s = getValue_nooffset((&state.locals[1]));
                        state.states[1].o = getValue_nooffset((&state.locals[3]));
                        do {
                            entry1=cpppred1937(state.states[1], entry1);
                            if(entry1 == -1) break;
//body item2
                            entry2 = 0;
                            state.states[2].s = getValue_nooffset((&state.locals[1]));
                            state.states[2].o = getValue_nooffset((&state.locals[0]));
                            do {
                                entry2=cpppred1967(state.states[2], entry2);
                                if(entry2 == -1) break;
//body item3
                                entry3 = 0;
                                state.states[3].s = getValue_nooffset((&state.locals[2]));
                                state.states[3].o = (&consts_cpppred2220_9[1]);
                                do {
                                    entry3=cpppred1997(state.states[3], entry3);
                                    if(entry3 == -1) break;
//body item4
                                    entry4 = 0;
                                    state.states[4].s = getValue_nooffset((&state.locals[3]));
                                    state.states[4].o = (&consts_cpppred2220_9[1]);
                                    do {
                                        entry4=cpppred2030(state.states[4], entry4);
                                        if(entry4 == -1) break;
                                        ASSERT(ep9.size());
                                        ep9.pop_back();

                                        state.states[0].entry = entry0;
                                        state.states[1].entry = entry1;
                                        state.states[2].entry = entry2;
                                        state.states[3].entry = entry3;
                                        state.states[4].entry = entry4;
                                        return entry;
                                    case 10:
                                        ;
                                        entry0 = state.states[0].entry;
                                        entry1 = state.states[1].entry;
                                        entry2 = state.states[2].entry;
                                        entry3 = state.states[3].entry;
                                        entry4 = state.states[4].entry;
                                        ep9.push_back(thingthingpair(state.s, state.o));
                                    } while(true);
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                    ASSERT(ep9.size());
                    ep9.pop_back();
                }
                unbind_from_const(state.o);
            }
            unbind_from_var(state.su.magic, state.s, (&state.locals[0]));
        }
    }
    return -1;
}

static Locals consts_cpppred3407_0 = {(Thing)0x3fe9, (Thing)0x41f9};
static Locals consts_cpppred3407_1 = {(Thing)0x3fe9, (Thing)0x426d};
static Locals consts_cpppred3407_2 = {(Thing)0x4185, (Thing)0x4435};
static Locals consts_cpppred3407_3 = {(Thing)0x4835, (Thing)0x47c1};
static Locals consts_cpppred3407_4 = {(Thing)0x49fd, (Thing)0x4ca5};

static int cpppred3407(cpppred_state & __restrict__ state, int entry) {
    char uuus;
    (void)uuus;
    char uuuo;
    (void)uuuo;
    switch(entry) {
    case 0:
//rule 0:
        if (unify_with_const(state.s, (&consts_cpppred3407_0[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3407_0[1]))) {
                entry = 1;
                return entry;
            case 1:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 1:
        if (unify_with_const(state.s, (&consts_cpppred3407_1[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3407_1[1]))) {
                entry = 2;
                return entry;
            case 2:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 2:
        if (unify_with_const(state.s, (&consts_cpppred3407_2[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3407_2[1]))) {
                entry = 3;
                return entry;
            case 3:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 3:
        if (unify_with_const(state.s, (&consts_cpppred3407_3[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3407_3[1]))) {
                entry = 4;
                return entry;
            case 4:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 4:
        if (unify_with_const(state.s, (&consts_cpppred3407_4[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3407_4[1]))) {
                entry = 5;
                return entry;
            case 5:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
    }
    return -1;
}

static Locals consts_cpppred3710_0 = {(Thing)0x3fe9, (Thing)0x4185};
static Locals consts_cpppred3710_1 = {(Thing)0x41f9, (Thing)0x4435};
static Locals consts_cpppred3710_2 = {(Thing)0x4435, (Thing)0x47c1};
static Locals consts_cpppred3710_3 = {(Thing)0x4435, (Thing)0x4835};
static Locals consts_cpppred3710_4 = {(Thing)0x4835, (Thing)0x49fd};
static Locals consts_cpppred3710_5 = {(Thing)0x4835, (Thing)0x426d};
static Locals consts_cpppred3710_6 = {(Thing)0x47c1, (Thing)0x4ca5};

static int cpppred3710(cpppred_state & __restrict__ state, int entry) {
    char uuus;
    (void)uuus;
    char uuuo;
    (void)uuuo;
    switch(entry) {
    case 0:
//rule 0:
        if (unify_with_const(state.s, (&consts_cpppred3710_0[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3710_0[1]))) {
                entry = 1;
                return entry;
            case 1:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 1:
        if (unify_with_const(state.s, (&consts_cpppred3710_1[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3710_1[1]))) {
                entry = 2;
                return entry;
            case 2:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 2:
        if (unify_with_const(state.s, (&consts_cpppred3710_2[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3710_2[1]))) {
                entry = 3;
                return entry;
            case 3:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 3:
        if (unify_with_const(state.s, (&consts_cpppred3710_3[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3710_3[1]))) {
                entry = 4;
                return entry;
            case 4:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 4:
        if (unify_with_const(state.s, (&consts_cpppred3710_4[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3710_4[1]))) {
                entry = 5;
                return entry;
            case 5:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 5:
        if (unify_with_const(state.s, (&consts_cpppred3710_5[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3710_5[1]))) {
                entry = 6;
                return entry;
            case 6:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
//rule 6:
        if (unify_with_const(state.s, (&consts_cpppred3710_6[0]))) {
            if (unify_with_const(state.o, (&consts_cpppred3710_6[1]))) {
                entry = 7;
                return entry;
            case 7:
                ;
                unbind_from_const(state.o);
            }
            unbind_from_const(state.s);
        }
    }
    return -1;
}

static Locals consts_cppout_query_0 = {(Thing)0x5111, (Thing)0x4dfd};

static int cppout_query(cpppred_state & __restrict__ state, int entry) {
    int entry0;
    int entry1;
    int entry2;
    int entry3;
    int entry4;
    int entry5;
    int entry6;
    int entry7;
    int entry8;
    int entry9;
    int entry10;
    int entry11;
    int entry12;
    int entry13;
    int entry14;
    int entry15;
    int entry16;
    int entry17;
    int entry18;
    int entry19;
    int entry20;
    int entry21;
    int entry22;
    int entry23;
    int entry24;
    int entry25;
    int entry26;
    int entry27;
    int entry28;
    int entry29;
    int entry30;
    int entry31;
    static int counter = 0;
    char uuus;
    (void)uuus;
    char uuuo;
    (void)uuuo;
    switch(entry) {
    case 0:
        state.states.resize(32);
//rule 0:
        state.locals = {(Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0, (Thing)0};
        entry = 1;
//body item0
        entry0 = 0;
        state.states[0].s = (&consts_cppout_query_0[0]);
        state.states[0].o = getValue_nooffset((&state.locals[0]));
        do {
            entry0=cpppred2220(state.states[0], entry0);
            if(entry0 == -1) break;
//body item1
            entry1 = 0;
            state.states[1].s = (&consts_cppout_query_0[1]);
            state.states[1].o = getValue_nooffset((&state.locals[1]));
            do {
                entry1=cpppred2220(state.states[1], entry1);
                if(entry1 == -1) break;
//body item2
                entry2 = 0;
                state.states[2].s = (&consts_cppout_query_0[0]);
                state.states[2].o = getValue_nooffset((&state.locals[2]));
                do {
                    entry2=cpppred2220(state.states[2], entry2);
                    if(entry2 == -1) break;
//body item3
                    entry3 = 0;
                    state.states[3].s = (&consts_cppout_query_0[1]);
                    state.states[3].o = getValue_nooffset((&state.locals[3]));
                    do {
                        entry3=cpppred2220(state.states[3], entry3);
                        if(entry3 == -1) break;
//body item4
                        entry4 = 0;
                        state.states[4].s = (&consts_cppout_query_0[0]);
                        state.states[4].o = getValue_nooffset((&state.locals[4]));
                        do {
                            entry4=cpppred2220(state.states[4], entry4);
                            if(entry4 == -1) break;
//body item5
                            entry5 = 0;
                            state.states[5].s = (&consts_cppout_query_0[1]);
                            state.states[5].o = getValue_nooffset((&state.locals[5]));
                            do {
                                entry5=cpppred2220(state.states[5], entry5);
                                if(entry5 == -1) break;
//body item6
                                entry6 = 0;
                                state.states[6].s = (&consts_cppout_query_0[0]);
                                state.states[6].o = getValue_nooffset((&state.locals[6]));
                                do {
                                    entry6=cpppred2220(state.states[6], entry6);
                                    if(entry6 == -1) break;
//body item7
                                    entry7 = 0;
                                    state.states[7].s = (&consts_cppout_query_0[1]);
                                    state.states[7].o = getValue_nooffset((&state.locals[7]));
                                    do {
                                        entry7=cpppred2220(state.states[7], entry7);
                                        if(entry7 == -1) break;
//body item8
                                        entry8 = 0;
                                        state.states[8].s = (&consts_cppout_query_0[0]);
                                        state.states[8].o = getValue_nooffset((&state.locals[8]));
                                        do {
                                            entry8=cpppred2220(state.states[8], entry8);
                                            if(entry8 == -1) break;
//body item9
                                            entry9 = 0;
                                            state.states[9].s = (&consts_cppout_query_0[1]);
                                            state.states[9].o = getValue_nooffset((&state.locals[9]));
                                            do {
                                                entry9=cpppred2220(state.states[9], entry9);
                                                if(entry9 == -1) break;
//body item10
                                                entry10 = 0;
                                                state.states[10].s = (&consts_cppout_query_0[0]);
                                                state.states[10].o = getValue_nooffset((&state.locals[10]));
                                                do {
                                                    entry10=cpppred2220(state.states[10], entry10);
                                                    if(entry10 == -1) break;
//body item11
                                                    entry11 = 0;
                                                    state.states[11].s = (&consts_cppout_query_0[1]);
                                                    state.states[11].o = getValue_nooffset((&state.locals[11]));
                                                    do {
                                                        entry11=cpppred2220(state.states[11], entry11);
                                                        if(entry11 == -1) break;
//body item12
                                                        entry12 = 0;
                                                        state.states[12].s = (&consts_cppout_query_0[0]);
                                                        state.states[12].o = getValue_nooffset((&state.locals[12]));
                                                        do {
                                                            entry12=cpppred2220(state.states[12], entry12);
                                                            if(entry12 == -1) break;
//body item13
                                                            entry13 = 0;
                                                            state.states[13].s = (&consts_cppout_query_0[1]);
                                                            state.states[13].o = getValue_nooffset((&state.locals[13]));
                                                            do {
                                                                entry13=cpppred2220(state.states[13], entry13);
                                                                if(entry13 == -1) break;
//body item14
                                                                entry14 = 0;
                                                                state.states[14].s = (&consts_cppout_query_0[0]);
                                                                state.states[14].o = getValue_nooffset((&state.locals[14]));
                                                                do {
                                                                    entry14=cpppred2220(state.states[14], entry14);
                                                                    if(entry14 == -1) break;
//body item15
                                                                    entry15 = 0;
                                                                    state.states[15].s = (&consts_cppout_query_0[1]);
                                                                    state.states[15].o = getValue_nooffset((&state.locals[15]));
                                                                    do {
                                                                        entry15=cpppred2220(state.states[15], entry15);
                                                                        if(entry15 == -1) break;
//body item16
                                                                        entry16 = 0;
                                                                        state.states[16].s = (&consts_cppout_query_0[0]);
                                                                        state.states[16].o = getValue_nooffset((&state.locals[16]));
                                                                        do {
                                                                            entry16=cpppred2220(state.states[16], entry16);
                                                                            if(entry16 == -1) break;
//body item17
                                                                            entry17 = 0;
                                                                            state.states[17].s = (&consts_cppout_query_0[1]);
                                                                            state.states[17].o = getValue_nooffset((&state.locals[17]));
                                                                            do {
                                                                                entry17=cpppred2220(state.states[17], entry17);
                                                                                if(entry17 == -1) break;
//body item18
                                                                                entry18 = 0;
                                                                                state.states[18].s = (&consts_cppout_query_0[0]);
                                                                                state.states[18].o = getValue_nooffset((&state.locals[18]));
                                                                                do {
                                                                                    entry18=cpppred2220(state.states[18], entry18);
                                                                                    if(entry18 == -1) break;
//body item19
                                                                                    entry19 = 0;
                                                                                    state.states[19].s = (&consts_cppout_query_0[1]);
                                                                                    state.states[19].o = getValue_nooffset((&state.locals[19]));
                                                                                    do {
                                                                                        entry19=cpppred2220(state.states[19], entry19);
                                                                                        if(entry19 == -1) break;
//body item20
                                                                                        entry20 = 0;
                                                                                        state.states[20].s = (&consts_cppout_query_0[0]);
                                                                                        state.states[20].o = getValue_nooffset((&state.locals[20]));
                                                                                        do {
                                                                                            entry20=cpppred2220(state.states[20], entry20);
                                                                                            if(entry20 == -1) break;
//body item21
                                                                                            entry21 = 0;
                                                                                            state.states[21].s = (&consts_cppout_query_0[1]);
                                                                                            state.states[21].o = getValue_nooffset((&state.locals[21]));
                                                                                            do {
                                                                                                entry21=cpppred2220(state.states[21], entry21);
                                                                                                if(entry21 == -1) break;
//body item22
                                                                                                entry22 = 0;
                                                                                                state.states[22].s = (&consts_cppout_query_0[0]);
                                                                                                state.states[22].o = getValue_nooffset((&state.locals[22]));
                                                                                                do {
                                                                                                    entry22=cpppred2220(state.states[22], entry22);
                                                                                                    if(entry22 == -1) break;
//body item23
                                                                                                    entry23 = 0;
                                                                                                    state.states[23].s = (&consts_cppout_query_0[1]);
                                                                                                    state.states[23].o = getValue_nooffset((&state.locals[23]));
                                                                                                    do {
                                                                                                        entry23=cpppred2220(state.states[23], entry23);
                                                                                                        if(entry23 == -1) break;
//body item24
                                                                                                        entry24 = 0;
                                                                                                        state.states[24].s = (&consts_cppout_query_0[0]);
                                                                                                        state.states[24].o = getValue_nooffset((&state.locals[24]));
                                                                                                        do {
                                                                                                            entry24=cpppred2220(state.states[24], entry24);
                                                                                                            if(entry24 == -1) break;
//body item25
                                                                                                            entry25 = 0;
                                                                                                            state.states[25].s = (&consts_cppout_query_0[1]);
                                                                                                            state.states[25].o = getValue_nooffset((&state.locals[25]));
                                                                                                            do {
                                                                                                                entry25=cpppred2220(state.states[25], entry25);
                                                                                                                if(entry25 == -1) break;
//body item26
                                                                                                                entry26 = 0;
                                                                                                                state.states[26].s = (&consts_cppout_query_0[0]);
                                                                                                                state.states[26].o = getValue_nooffset((&state.locals[26]));
                                                                                                                do {
                                                                                                                    entry26=cpppred2220(state.states[26], entry26);
                                                                                                                    if(entry26 == -1) break;
//body item27
                                                                                                                    entry27 = 0;
                                                                                                                    state.states[27].s = (&consts_cppout_query_0[1]);
                                                                                                                    state.states[27].o = getValue_nooffset((&state.locals[27]));
                                                                                                                    do {
                                                                                                                        entry27=cpppred2220(state.states[27], entry27);
                                                                                                                        if(entry27 == -1) break;
//body item28
                                                                                                                        entry28 = 0;
                                                                                                                        state.states[28].s = (&consts_cppout_query_0[0]);
                                                                                                                        state.states[28].o = getValue_nooffset((&state.locals[28]));
                                                                                                                        do {
                                                                                                                            entry28=cpppred2220(state.states[28], entry28);
                                                                                                                            if(entry28 == -1) break;
//body item29
                                                                                                                            entry29 = 0;
                                                                                                                            state.states[29].s = (&consts_cppout_query_0[1]);
                                                                                                                            state.states[29].o = getValue_nooffset((&state.locals[29]));
                                                                                                                            do {
                                                                                                                                entry29=cpppred2220(state.states[29], entry29);
                                                                                                                                if(entry29 == -1) break;
//body item30
                                                                                                                                entry30 = 0;
                                                                                                                                state.states[30].s = (&consts_cppout_query_0[0]);
                                                                                                                                state.states[30].o = getValue_nooffset((&state.locals[30]));
                                                                                                                                do {
                                                                                                                                    entry30=cpppred2220(state.states[30], entry30);
                                                                                                                                    if(entry30 == -1) break;
//body item31
                                                                                                                                    entry31 = 0;
                                                                                                                                    state.states[31].s = (&consts_cppout_query_0[1]);
                                                                                                                                    state.states[31].o = getValue_nooffset((&state.locals[31]));
                                                                                                                                    do {
                                                                                                                                        entry31=cpppred2220(state.states[31], entry31);
                                                                                                                                        if(entry31 == -1) break;
                                                                                                                                    {   if (!(counter & 0b11111111111)) {
                                                                                                                                                if (!silent) dout << unifys << " unifys "  ;
                                                                                                                                                if (!silent) dout << " RESULT " << counter << ": ";
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[0]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-5814);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[1]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-5843);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[2]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-5872);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[3]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-5901);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[4]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-5930);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[5]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-5959);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[6]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-5988);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[7]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6017);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[8]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6046);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[9]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6075);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[10]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6104);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[11]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6133);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[12]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6162);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[13]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6191);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[14]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6220);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[15]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6249);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[16]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6278);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[17]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6307);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[18]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6336);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[19]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6365);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[20]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6394);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[21]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6423);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[22]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6452);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[23]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6481);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[24]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6510);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[25]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6539);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[26]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6568);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[27]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6597);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[28]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6626);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[29]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6655);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[0]));
                                                                                                                                                    bio = getValue((&state.locals[30]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(5188);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6684);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                {   Thing * bis, * bio;
                                                                                                                                                    bis = getValue((&consts_cppout_query_0[1]));
                                                                                                                                                    bio = getValue((&state.locals[31]));
                                                                                                                                                    Thing n1;
                                                                                                                                                    if (is_unbound(*bis)) {
                                                                                                                                                        bis = &n1;
                                                                                                                                                        n1 = create_node(4991);
                                                                                                                                                    };
                                                                                                                                                    Thing n2;
                                                                                                                                                    if (is_unbound(*bio)) {
                                                                                                                                                        bio = &n2;
                                                                                                                                                        n2 = create_node(-6713);
                                                                                                                                                    };
                                                                                                                                                    if (!silent) dout << str(bis) << " <:nand3> " << str(bio) << ".";
                                                                                                                                                };
                                                                                                                                                if (!silent) dout << "\n";
                                                                                                                                            }
                                                                                                                                        }
                                                                                                                                        counter++;
                                                                                                                                        state.states[0].entry = entry0;
                                                                                                                                        state.states[1].entry = entry1;
                                                                                                                                        state.states[2].entry = entry2;
                                                                                                                                        state.states[3].entry = entry3;
                                                                                                                                        state.states[4].entry = entry4;
                                                                                                                                        state.states[5].entry = entry5;
                                                                                                                                        state.states[6].entry = entry6;
                                                                                                                                        state.states[7].entry = entry7;
                                                                                                                                        state.states[8].entry = entry8;
                                                                                                                                        state.states[9].entry = entry9;
                                                                                                                                        state.states[10].entry = entry10;
                                                                                                                                        state.states[11].entry = entry11;
                                                                                                                                        state.states[12].entry = entry12;
                                                                                                                                        state.states[13].entry = entry13;
                                                                                                                                        state.states[14].entry = entry14;
                                                                                                                                        state.states[15].entry = entry15;
                                                                                                                                        state.states[16].entry = entry16;
                                                                                                                                        state.states[17].entry = entry17;
                                                                                                                                        state.states[18].entry = entry18;
                                                                                                                                        state.states[19].entry = entry19;
                                                                                                                                        state.states[20].entry = entry20;
                                                                                                                                        state.states[21].entry = entry21;
                                                                                                                                        state.states[22].entry = entry22;
                                                                                                                                        state.states[23].entry = entry23;
                                                                                                                                        state.states[24].entry = entry24;
                                                                                                                                        state.states[25].entry = entry25;
                                                                                                                                        state.states[26].entry = entry26;
                                                                                                                                        state.states[27].entry = entry27;
                                                                                                                                        state.states[28].entry = entry28;
                                                                                                                                        state.states[29].entry = entry29;
                                                                                                                                        state.states[30].entry = entry30;
                                                                                                                                        state.states[31].entry = entry31;
                                                                                                                                        return entry;
                                                                                                                                    case 1:
                                                                                                                                        ;
                                                                                                                                        entry0 = state.states[0].entry;
                                                                                                                                        entry1 = state.states[1].entry;
                                                                                                                                        entry2 = state.states[2].entry;
                                                                                                                                        entry3 = state.states[3].entry;
                                                                                                                                        entry4 = state.states[4].entry;
                                                                                                                                        entry5 = state.states[5].entry;
                                                                                                                                        entry6 = state.states[6].entry;
                                                                                                                                        entry7 = state.states[7].entry;
                                                                                                                                        entry8 = state.states[8].entry;
                                                                                                                                        entry9 = state.states[9].entry;
                                                                                                                                        entry10 = state.states[10].entry;
                                                                                                                                        entry11 = state.states[11].entry;
                                                                                                                                        entry12 = state.states[12].entry;
                                                                                                                                        entry13 = state.states[13].entry;
                                                                                                                                        entry14 = state.states[14].entry;
                                                                                                                                        entry15 = state.states[15].entry;
                                                                                                                                        entry16 = state.states[16].entry;
                                                                                                                                        entry17 = state.states[17].entry;
                                                                                                                                        entry18 = state.states[18].entry;
                                                                                                                                        entry19 = state.states[19].entry;
                                                                                                                                        entry20 = state.states[20].entry;
                                                                                                                                        entry21 = state.states[21].entry;
                                                                                                                                        entry22 = state.states[22].entry;
                                                                                                                                        entry23 = state.states[23].entry;
                                                                                                                                        entry24 = state.states[24].entry;
                                                                                                                                        entry25 = state.states[25].entry;
                                                                                                                                        entry26 = state.states[26].entry;
                                                                                                                                        entry27 = state.states[27].entry;
                                                                                                                                        entry28 = state.states[28].entry;
                                                                                                                                        entry29 = state.states[29].entry;
                                                                                                                                        entry30 = state.states[30].entry;
                                                                                                                                        entry31 = state.states[31].entry;
                                                                                                                                    } while(true);
                                                                                                                                } while(true);
                                                                                                                            } while(true);
                                                                                                                        } while(true);
                                                                                                                    } while(true);
                                                                                                                } while(true);
                                                                                                            } while(true);
                                                                                                        } while(true);
                                                                                                    } while(true);
                                                                                                } while(true);
                                                                                            } while(true);
                                                                                        } while(true);
                                                                                    } while(true);
                                                                                } while(true);
                                                                            } while(true);
                                                                        } while(true);
                                                                    } while(true);
                                                                } while(true);
                                                            } while(true);
                                                        } while(true);
                                                    } while(true);
                                                } while(true);
                                            } while(true);
                                        } while(true);
                                    } while(true);
                                } while(true);
                            } while(true);
                        } while(true);
                    } while(true);
                } while(true);
            } while(true);
        } while(true);
    }
    return -1;
}

void cppdict_init() {
    cppdict[-6713] = "?V2n";
    cppdict[-6684] = "?V1n";
    cppdict[-6655] = "?V2h";
    cppdict[-6626] = "?V1h";
    cppdict[-6597] = "?V2d";
    cppdict[-6568] = "?V1d";
    cppdict[-6539] = "?V2t";
    cppdict[-6510] = "?V1t";
    cppdict[-6481] = "?V2s";
    cppdict[-6452] = "?V1s";
    cppdict[-6423] = "?V2r";
    cppdict[-6394] = "?V1r";
    cppdict[-6365] = "?V2a";
    cppdict[-6336] = "?V1a";
    cppdict[-6307] = "?V2y";
    cppdict[-6278] = "?V1y";
    cppdict[-6249] = "?V2u";
    cppdict[-6220] = "?V1u";
    cppdict[-6191] = "?V2l";
    cppdict[-6162] = "?V1l";
    cppdict[-6133] = "?V2j";
    cppdict[-6104] = "?V1j";
    cppdict[-6075] = "?V2g";
    cppdict[-6046] = "?V1g";
    cppdict[-6017] = "?V2p";
    cppdict[-5988] = "?V1p";
    cppdict[-5959] = "?V2f";
    cppdict[-5930] = "?V1f";
    cppdict[-5901] = "?V2w";
    cppdict[-5872] = "?V1w";
    cppdict[-5843] = "?V2q";
    cppdict[-5814] = "?V1q";
    cppdict[2008] = "false";
    cppdict[2044] = "0X966AE2F598383F8B";
    cppdict[2231] = "true";
    cppdict[2233] = "0X892A6FD6E287E9F2";
    cppdict[2419] = "0XE5953676FC5F8E40";
    cppdict[2790] = "0XB2F597CF119447C3";
    cppdict[3161] = "0XFAC4EB6F90A4AFBE";
    cppdict[3348] = "0XA1DA409CC763A7A";
    cppdict[3505] = "0X920A8F211E6D82B";
    cppdict[3655] = "0X2423EE29747169E4";
    cppdict[3805] = "0X638A0D9636E8CC05";
    cppdict[3955] = "0X5C903E369BEA9199";
    cppdict[3994] = ":a";
    cppdict[4026] = ":b";
    cppdict[4058] = ":cin";
    cppdict[4090] = ":g1";
    cppdict[4164] = ":a11";
    cppdict[4193] = ":g3";
    cppdict[4222] = ":g2";
    cppdict[4251] = ":g9";
    cppdict[4336] = ":a12";
    cppdict[4365] = ":g4";
    cppdict[4450] = ":a13";
    cppdict[4563] = ":a14";
    cppdict[4592] = ":g6";
    cppdict[4621] = ":g5";
    cppdict[4706] = ":a15";
    cppdict[4735] = ":g8";
    cppdict[4876] = ":a16";
    cppdict[4905] = ":g7";
    cppdict[4962] = ":a17";
    cppdict[4991] = ":sum";
    cppdict[5188] = ":cout";
}
#include "cppmain.cpp"

