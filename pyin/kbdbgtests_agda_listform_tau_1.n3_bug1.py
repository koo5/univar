from query_kbdbg_with_pyin import *

query(
term(Var(), rdf.type, kbdbg.frame, ),
term(dummy quickndirty.notIncludes :f kbdbg:is_finished true.}.
		:kbdbg log:includes {:f kbdbg:is_for_rule :r.}.
		:kbdbg log:includes {:b a kbdbg:binding. :b kbdbg:has_source [kbdbg:has_frame :y].}.
		:kbdbg log:includes {:b kbdbg:has_target :t.}.
		:kbdbg log:includes {:t kbdbg:has_frame :tf.}.


result = server.query("""
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX kbdbg: <http://kbd.bg/#>
PREFIX : <file:///#>
SELECT * 
FROM :step1
FROM :step2
WHERE
{
	:Tolkien :wrote ?what. ?what :is ?rating.
}
""")#?what :is ?rating.
print ('yo')
print(result)
server.update("""
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX kbdbg: <http://kbd.bg/#> 
PREFIX : <file:///#> 
INSERT 
{
	:step1 rdf:a :result. :step2 rdf:a :result.
} WHERE {}
""")

result = server.query("""
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX kbdbg: <http://kbd.bg/#>
PREFIX : <file:///#>
SELECT * 
FROM ?result
WHERE
{
	?result rdf:a :result. :Tolkien :wrote ?what. ?what :is ?rating.
}
""")#?what :is ?rating.
print ('yo')
print(result)
exit()
