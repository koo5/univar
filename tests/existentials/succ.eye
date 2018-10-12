kb
@prefix : <#>.
#zero a Nat.
:zero :a :Nat.
#forall ?x , exists ?y , such that if ?x a nat, then (?x has_suc ?y and ?y also a nat)
{?x :a :Nat} => {?x :has_succ ?y. ?y :a :Nat}.
fin.


query
@prefix : <#>.
#infiloop
{?what :a :Nat.} => {?what :a :Nat.}.
fin.
