class Triple(object):
	def __init__(s, pred, args):
		s.pred = pred
		s.args = args

class Rule(object):
	def __init__(s, head, body=[]):
		s.head = head
		s.body = body
		s.locals_template = make_locals(head, body)
		s.ep_heads = []

	def unify(s, args):
		depth = 0
		max_depth = len(args) + len(s.body)
		locals = s.locals_template[:]#copy
		while True:
			if len(generators) <= depth:
				generator = None

				if depth < args.len():
					generator = unify(args[arg_index], locals[head.args[arg_index]])
				else:
					body_item_index = depth - args.len()
					triple = body[body_item_index]
					
					bi_args = []
					for i in triple.args:
						if is_var(i):
							a = get_value(locals[i])
						else:
							a = i
						bi_args.append(a)
					generator = pred(triple.pred, bi_args))
				generators.append(generator)
		
			if generators[depth].next():
				if (depth < max_depth):
					depth++
				else:
					yield "NYAN"#this is when it finishes a rule
			else
				if (depth > 0): 
					depth--
				else:
					break#if it's tried all the possibilities for finishing a rule

	def find_ep(s, args):
		for former_args in s.ep_pairs:
			if ep_match(args, former_args):
				return True
	
	def ep_match(a, b):
		assert len(a) == len(b)
		for i, j in enumerate(a):
			if type(j) != type(b[i]):
				return
			if type(j) == str and b[i] != j:
				return
		return True


class Var(object):
	def __init__(s, debug_name):
		s.debug_name = debug_name
		s.bound_to = None

def make_locals(head, body):
	locals = {}
	for triple in [head] + body:
		for a in triple.args:
			if is_var(a):
				locals[a] = Var(debug_name)


def pred(p, args):
	for i in args:
		assert getValue(i) == i
    for rule in preds[p]:
        if(rule.find_ep(args)): continue;
        rule.ep_heads.append(args[:])
        while rule.unify(args):
            rule.ep_heads.pop()
            yield True
            rule.ep_heads.append(args[:])
        rule.ep_heads.pop()


from collections import defaultdict

if __name__ == "__main__":
	preds = defaultdict([])
	for r in [
	Rule(Triple('a', ['?X', 'mortal']), [Triple('a', ['?X', 'man']), Triple('not', ['?X', 'superman'])]),
	Rule(Triple('a', ['socrates', 'man'])),
	Rule(Triple('not', ['?nobody', 'superman']))]:
		preds[r.head.pred].append(r)
	for nyan in preds['a'](['socrates', 'mortal']):
		print nyan


				
"""		
		
		while unify(s, locals[head.s]):
			while unify(o, locals[head.o]):
				body_item_index = 0
				while True:
				  triple = body[body_item_index]
				  //what is generators?
				  //this abstracts our array of states, python abstracts this away, if you call a function that has a yield somewhere, you get a generator
				  //so, this is the array of states
				  
				  if (generators.len() <= body_item_index:
					generators.append(pred(locals[triple.s], triple.p, locals[triple.o]))
				//so this runs the next rule to try for a body item?
				//this resumes the pred function call / closure / , which probably resumes some rule closure
				if generators[body_item_index].next():
					body_item_index++
				else
					body_item_index--
					//and this is when it's tried all the possibilities for finishing a rule//right
					if (body_item_index == -1):
					  break
				//so this is when it finishes a rule//right
				if (body_item_index == len(body)):
					body_item_index = len(body) - 1
					yield True
	"""
