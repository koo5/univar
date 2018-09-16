shortenings = {}
def shorten(term):
	# todo ? use https://github.com/RDFLib/rdflib/blob/master/docs/namespaces_and_bindings.rst instead
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

def join_generators(a, b):
	for i in a:
		for j in b:
			yield True

def kbdbg_file_path(fn):
	return 'runs/'+fn+ '/'

def kbdbg_file_name(fn):
	return kbdbg_file_path(fn) + fn

def fix_up_identification(i):
	return "".join([ch if ch.isalnum() else "_" for ch in i])
