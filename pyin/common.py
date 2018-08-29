shortenings = {}
def shorten(term):
	# todo ? use https://github.com/RDFLib/rdflib/blob/master/docs/namespaces_and_bindings.rst
	s = str(term)
	for i in '/:#?':
		p = s.rfind(i)
		if p != -1:
			s = s[p:]
	if s in shortenings and shortenings[s] != term:
		return str(term)
	shortenings[s] = term
	return s

def traverse(item):
	for i in iter(item):
		for j in iter(i):
			yield j
