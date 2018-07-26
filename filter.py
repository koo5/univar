@prefix kbdbg: <http://kbd.bg/#> .
@prefix : <file:///#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
{?x rdf:type kbdbg:rule. ?y kbdbg:is_for_rule ?x.} => {:this :result (?x ?y ?z).}.


