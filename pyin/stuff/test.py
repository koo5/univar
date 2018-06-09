
"""
def test1():
	input_rules = [
		Rule(Triple('a', ['?X', 'mortal']),
		Graph([Triple('a', ['?X', 'man']), Triple('not', ['?X', 'superman'])])),
		Rule(Triple('a', ['socrates', 'man'])),
		Rule(Triple('a', ['koo', 'man'])),
		Rule(Triple('not', ['?nobody', 'superman']))]
	input_query = Graph([Triple('a', ['socrates', 'mortal'])])
	for nyan in query(input_rules, input_query):
		print ("#he's mortal, and he's dead")
	print ("#who is mortal?")
	#for nyan in pred('a', [v, 'mortal']):
	#v = Var('?who who')
	w = '?who'
	input_query = Graph([Triple('a', [w, 'mortal'])])
	for nyan in query(input_rules, input_query):
		print ('#'+str(nyan[w]) + " is mortal, and he's dead")
"""
