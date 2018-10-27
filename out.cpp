#include "pyco_static.cpp"static const unsigned _l0 = 0;
static const unsigned _v0 = 1;
static const unsigned _l1 = 2;
static const unsigned _v1 = 3;
static const unsigned _l2 = 4;
static const unsigned _v2 = 5;
static const unsigned _nil = 6;
static const unsigned _l0c = 7;
static const unsigned _Formula2 = 8;
static const unsigned _Formula3 = 9;
vector<string> strings = {
"http://jmv.fr#l0",
"http://jmv.fr#v0",
"http://jmv.fr#l1",
"http://jmv.fr#v1",
"http://jmv.fr#l2",
"http://jmv.fr#v2",
"http://www.w3.org/1999/02/22-rdf-syntax-ns#nil",
"http://jmv.fr#l0c",
"_:Formula2",
"_:Formula3",
};static ep_t ep10;
static _first(cpppred_state & __restrict__ state);
static _rest(cpppred_state & __restrict__ state);
static _clone_of(cpppred_state & __restrict__ state);
static _implies(cpppred_state & __restrict__ state);
static http___jmv_fr_first(cpppred_state & __restrict__ state);
static http___jmv_fr_rest(cpppred_state & __restrict__ state);
/* http://www.w3.org/1999/02/22-rdf-syntax-ns#first */
static Locals consts_of_rule_1 = [{CONST,_l0,0},{CONST,_v0,0}];
static Locals consts_of_rule_3 = [{CONST,_l1,0},{CONST,_v1,0}];
static Locals consts_of_rule_5 = [{CONST,_l2,0},{CONST,_v2,0}];
static _first(cpppred_state & __restrict__ state)
{
  goto case0 + state.entry;
  case0:
  state.states.resize(2);
  /* {<http://jmv.fr#l0> <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> <http://jmv.fr#v0>.} <= {} */
  /* http://jmv.fr#l0 */
  state.states[0] = unify(&state.incoming[0],&consts_of_rule_1[0]);
  while unify_coro(&state.states[0]))
  {
    /* http://jmv.fr#v0 */
    state.states[1] = unify(&state.incoming[1],&consts_of_rule_1[1]);
    while unify_coro(&state.states[1]))
    {
      if (!cppout_find_ep(&ep1, &state.incomings))
      {
        state.entry = case1;
        return state.entry;
        case1:
      }
    }
  }
  /* {<http://jmv.fr#l1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> <http://jmv.fr#v1>.} <= {} */
  /* http://jmv.fr#l1 */
  state.states[2] = unify(&state.incoming[0],&consts_of_rule_3[0]);
  while unify_coro(&state.states[2]))
  {
    /* http://jmv.fr#v1 */
    state.states[3] = unify(&state.incoming[1],&consts_of_rule_3[1]);
    while unify_coro(&state.states[3]))
    {
      if (!cppout_find_ep(&ep3, &state.incomings))
      {
        state.entry = case2;
        return state.entry;
        case2:
      }
    }
  }
  /* {<http://jmv.fr#l2> <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> <http://jmv.fr#v2>.} <= {} */
  /* http://jmv.fr#l2 */
  state.states[4] = unify(&state.incoming[0],&consts_of_rule_5[0]);
  while unify_coro(&state.states[4]))
  {
    /* http://jmv.fr#v2 */
    state.states[5] = unify(&state.incoming[1],&consts_of_rule_5[1]);
    while unify_coro(&state.states[5]))
    {
      if (!cppout_find_ep(&ep5, &state.incomings))
      {
        state.entry = case3;
        return state.entry;
        case3:
      }
    }
  }
}
/* http://www.w3.org/1999/02/22-rdf-syntax-ns#rest */
static Locals consts_of_rule_2 = [{CONST,_l0,0},{CONST,_l1,0}];
static Locals consts_of_rule_4 = [{CONST,_l1,0},{CONST,_l2,0}];
static Locals consts_of_rule_6 = [{CONST,_l2,0},{CONST,_nil,0}];
static _rest(cpppred_state & __restrict__ state)
{
  goto case0 + state.entry;
  case0:
  state.states.resize(2);
  /* {<http://jmv.fr#l0> <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> <http://jmv.fr#l1>.} <= {} */
  /* http://jmv.fr#l0 */
  state.states[0] = unify(&state.incoming[0],&consts_of_rule_2[0]);
  while unify_coro(&state.states[0]))
  {
    /* http://jmv.fr#l1 */
    state.states[1] = unify(&state.incoming[1],&consts_of_rule_2[1]);
    while unify_coro(&state.states[1]))
    {
      if (!cppout_find_ep(&ep2, &state.incomings))
      {
        state.entry = case1;
        return state.entry;
        case1:
      }
    }
  }
  /* {<http://jmv.fr#l1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> <http://jmv.fr#l2>.} <= {} */
  /* http://jmv.fr#l1 */
  state.states[2] = unify(&state.incoming[0],&consts_of_rule_4[0]);
  while unify_coro(&state.states[2]))
  {
    /* http://jmv.fr#l2 */
    state.states[3] = unify(&state.incoming[1],&consts_of_rule_4[1]);
    while unify_coro(&state.states[3]))
    {
      if (!cppout_find_ep(&ep4, &state.incomings))
      {
        state.entry = case2;
        return state.entry;
        case2:
      }
    }
  }
  /* {<http://jmv.fr#l2> <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> <http://www.w3.org/1999/02/22-rdf-syntax-ns#nil>.} <= {} */
  /* http://jmv.fr#l2 */
  state.states[4] = unify(&state.incoming[0],&consts_of_rule_6[0]);
  while unify_coro(&state.states[4]))
  {
    /* http://www.w3.org/1999/02/22-rdf-syntax-ns#nil */
    state.states[5] = unify(&state.incoming[1],&consts_of_rule_6[1]);
    while unify_coro(&state.states[5]))
    {
      if (!cppout_find_ep(&ep6, &state.incomings))
      {
        state.entry = case3;
        return state.entry;
        case3:
      }
    }
  }
}
/* http://jmv.fr#clone_of */
static Locals consts_of_rule_7 = [{CONST,_l0c,0},{CONST,_l0,0}];
static Locals consts_of_rule_11 = [];
static _clone_of(cpppred_state & __restrict__ state)
{
  goto case0 + state.entry;
  case0:
  state.states.resize(6);
  /* {<http://jmv.fr#l0c> <http://jmv.fr#clone_of> <http://jmv.fr#l0>.} <= {} */
  /* http://jmv.fr#l0c */
  state.states[0] = unify(&state.incoming[0],&consts_of_rule_7[0]);
  while unify_coro(&state.states[0]))
  {
    /* http://jmv.fr#l0 */
    state.states[1] = unify(&state.incoming[1],&consts_of_rule_7[1]);
    while unify_coro(&state.states[1]))
    {
      if (!cppout_find_ep(&ep7, &state.incomings))
      {
        state.entry = case1;
        return state.entry;
        case1:
      }
    }
  }
  /* {?rc <http://jmv.fr#clone_of> ?R.} <= {?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> ?F.. ?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> ?R.. ?LC <http://jmv.fr#clone_of> ?L.} */
  state.locals = [{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0}];
  /* rc */
  state.states[2] = unify(&state.incoming[0],&state.locals[0]);
  while unify_coro(&state.states[2]))
  {
    /* R */
    state.states[3] = unify(&state.incoming[1],&state.locals[5]);
    while unify_coro(&state.states[3]))
    {
      Thing *local, *value;
      local = &state.locals[0];
      value = get_value(local);
      if (!cppout_find_ep(&ep11, &state.incomings))
      {
        ep11.push_back(thingthingpair(state.incoming[0], state.incoming[1]));
        /* ?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> ?F. */
        state.states[4].incoming[0]=&state.locals[7];
        state.states[4].incoming[1]=&state.locals[3];
        state.states[4].entry = 0;
        while(_first(&state.states[4])!=-1)
        {
          /* ?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> ?R. */
          state.states[4].incoming[0]=&state.locals[7];
          state.states[4].incoming[1]=&state.locals[5];
          state.states[4].entry = 0;
          while(_rest(&state.states[4])!=-1)
          {
            /* ?LC <http://jmv.fr#clone_of> ?L. */
            state.states[4].incoming[0]=&state.locals[6];
            state.states[4].incoming[1]=&state.locals[7];
            state.states[4].entry = 0;
            while(_clone_of(&state.states[4])!=-1)
            {
              ASSERT(ep11.size())';
              ep11.pop_back();
              state.entry = case2;
              return state.entry;
              case2:
              ep11.push_back(thingthingpair(state.incoming[0], state.incoming[1]));
            }
          }
        }
      }
    }
  }
}
/* http://www.w3.org/2000/10/swap/log#implies */
static Locals consts_of_rule_8 = [{CONST,_Formula2,0},{CONST,_Formula3,0}];
static _implies(cpppred_state & __restrict__ state)
{
  goto case0 + state.entry;
  case0:
  state.states.resize(2);
  /* {<_:Formula2> <http://www.w3.org/2000/10/swap/log#implies> <_:Formula3>.} <= {} */
  /* _:Formula2 */
  state.states[0] = unify(&state.incoming[0],&consts_of_rule_8[0]);
  while unify_coro(&state.states[0]))
  {
    /* _:Formula3 */
    state.states[1] = unify(&state.incoming[1],&consts_of_rule_8[1]);
    while unify_coro(&state.states[1]))
    {
      if (!cppout_find_ep(&ep8, &state.incomings))
      {
        state.entry = case1;
        return state.entry;
        case1:
      }
    }
  }
}
/* http://jmv.fr#first */
static Locals consts_of_rule_9 = [];
static http___jmv_fr_first(cpppred_state & __restrict__ state)
{
  goto case0 + state.entry;
  case0:
  state.states.resize(6);
  /* {?LC <http://jmv.fr#first> ?F.} <= {?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> ?F.. ?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> ?R.. ?LC <http://jmv.fr#clone_of> ?L.} */
  state.locals = [{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0}];
  /* LC */
  state.states[0] = unify(&state.incoming[0],&state.locals[6]);
  while unify_coro(&state.states[0]))
  {
    /* F */
    state.states[1] = unify(&state.incoming[1],&state.locals[3]);
    while unify_coro(&state.states[1]))
    {
      if (!cppout_find_ep(&ep9, &state.incomings))
      {
        ep9.push_back(thingthingpair(state.incoming[0], state.incoming[1]));
        /* ?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> ?F. */
        state.states[2].incoming[0]=&state.locals[7];
        state.states[2].incoming[1]=&state.locals[3];
        state.states[2].entry = 0;
        while(_first(&state.states[2])!=-1)
        {
          /* ?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> ?R. */
          state.states[2].incoming[0]=&state.locals[7];
          state.states[2].incoming[1]=&state.locals[5];
          state.states[2].entry = 0;
          while(_rest(&state.states[2])!=-1)
          {
            /* ?LC <http://jmv.fr#clone_of> ?L. */
            state.states[2].incoming[0]=&state.locals[6];
            state.states[2].incoming[1]=&state.locals[7];
            state.states[2].entry = 0;
            while(_clone_of(&state.states[2])!=-1)
            {
              ASSERT(ep9.size())';
              ep9.pop_back();
              state.entry = case1;
              return state.entry;
              case1:
              ep9.push_back(thingthingpair(state.incoming[0], state.incoming[1]));
            }
          }
        }
      }
    }
  }
}
/* http://jmv.fr#rest */
static Locals consts_of_rule_10 = [];
static http___jmv_fr_rest(cpppred_state & __restrict__ state)
{
  goto case0 + state.entry;
  case0:
  state.states.resize(6);
  /* {?LC <http://jmv.fr#rest> ?rc.} <= {?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> ?F.. ?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> ?R.. ?LC <http://jmv.fr#clone_of> ?L.} */
  state.locals = [{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0},{UNBOUND,0,0}];
  /* LC */
  state.states[0] = unify(&state.incoming[0],&state.locals[6]);
  while unify_coro(&state.states[0]))
  {
    /* rc */
    state.states[1] = unify(&state.incoming[1],&state.locals[1]);
    while unify_coro(&state.states[1]))
    {
      Thing *local, *value;
      local = &state.locals[1];
      value = get_value(local);
      if (!cppout_find_ep(&ep10, &state.incomings))
      {
        ep10.push_back(thingthingpair(state.incoming[0], state.incoming[1]));
        /* ?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> ?F. */
        state.states[2].incoming[0]=&state.locals[7];
        state.states[2].incoming[1]=&state.locals[3];
        state.states[2].entry = 0;
        while(_first(&state.states[2])!=-1)
        {
          /* ?L <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> ?R. */
          state.states[2].incoming[0]=&state.locals[7];
          state.states[2].incoming[1]=&state.locals[5];
          state.states[2].entry = 0;
          while(_rest(&state.states[2])!=-1)
          {
            /* ?LC <http://jmv.fr#clone_of> ?L. */
            state.states[2].incoming[0]=&state.locals[6];
            state.states[2].incoming[1]=&state.locals[7];
            state.states[2].entry = 0;
            while(_clone_of(&state.states[2])!=-1)
            {
              ASSERT(ep10.size())';
              ep10.pop_back();
              state.entry = case1;
              return state.entry;
              case1:
              ep10.push_back(thingthingpair(state.incoming[0], state.incoming[1]));
            }
          }
        }
      }
    }
  }
}