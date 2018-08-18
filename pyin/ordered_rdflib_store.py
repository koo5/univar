"""
issues: should quads added during iteration of triples() be yielded during that call?
"""
from collections import defaultdict
# from rdflib.term import BNode
from rdflib.store import Store  # , NO_STORE, VALID_STORE

__all__ = ['OrderedStore', 'OrderedAndIndexedStore']


class OrderedStore(Store):
	context_aware = True
	formula_aware = True
	graph_aware = True

	# default context information for triples

	def __init__(self, configuration=None, identifier=None):
		super(OrderedStore, self).__init__(configuration)
		self.identifier = identifier
		self.quads = []
		self.quoted_info = []
		self.__namespace = {}
		self.__prefix = {}
		# ?
		# default context information for triples
		self.__defaultContexts = None

	def copy(self):

		r = self.__class__()
		assert len(self.__namespace) == 0
		assert len(self.__prefix) == 0
		r.quads = self.quads[:]
		r.quoted_info = self.quoted_info[:]
		return r

	def add(self, xxx_todo_changeme, context, quoted=False):
		Store.add(self, xxx_todo_changeme, context, quoted)
		s1, p1, o1 = xxx_todo_changeme
		self.quads.append(((s1, p1, o1), context))
		self.quoted_info.append(quoted)

	"""
	def bind(self, prefix, namespace):
		self.__prefix[namespace] = prefix
		self.__namespace[prefix] = namespace

	def namespace(self, prefix):
		return self.__namespace.get(prefix, None)

	def prefix(self, namespace):
		return self.__prefix.get(namespace, None)

	def namespaces(self):
		for prefix, namespace in self.__namespace.items():
			yield prefix, namespace
	"""

	def remove(self, xxx_todo_changeme1, context=None):
		# todo: figure out why the Memory store doesnt check the context
		s1, p1, o1 = xxx_todo_changeme1
		quads = self.quads[:]  # self.quads may be modified during the following iteration
		for quad in quads:
			if quad not in self.quads: continue
			(s2, p2, o2), c2 = quad
			if ((s1 == None) or (s1 == s2)) and ((p1 == None) or (p1 == p2)) and ((o1 == None) or (o1 == o2)) and (
					context == c2):
				i = self.quads.index(quad)
				del self.quoted_info[i]
				del self.quads[i]
				self.remove(xxx_todo_changeme1, context)

	# from collections import defaultdict
	# stats = defaultdict(lambda : 0)

	def triples(self, triplein, context=None):
		# print("want ", triplein, " in ", context)
		if context is not None:
			if context == self:  # hmm...does this really ever happen?
				context = None
		s1, p1, o1 = triplein
		# self.__class__.stats["".join([('0' if (x == None) else '1') for x in (s1,p1,o1,context)])] += 1
		# print (self.__class__.stats)
		quads = self.quads[:]  # self.quads may be modified during the following iteration
		if (s1 != None) and (p1 != None) and (o1 == None) and (context != None):
			def filter_func(x):
				(s2, p2, o2), c2 = x
				return (s1 == s2) and (p1 == p2) and (context == c2)

			return filter(filter_func, quads)
		# return filter(lambda x: (s1 == x[0][0]) and (p1 == x[0][1]) and (context == x[1]), quads)
		else:
			return self.general_triple_helper(s1, p1, o1, context, quads)

	#    for (s2,p2,o2),c2,_q2 in quads:
	#        if (s1 == s2) and (p1 == p2) and (context == c2):
	#            yield (s2,p2,o2),c2

	def general_triple_helper(self, s1, p1, o1, context, quads):
		for spo2, c2 in quads:
			s2, p2, o2 = spo2
			# print("trying", spo2,c2,_q2)
			if ((s1 == None) or (s1 == s2)) and ((p1 == None) or (p1 == p2)) and ((o1 == None) or (o1 == o2)) and (
					context == c2):
				# print("matches")
				yield spo2, c2



patterns = ['ttft']
"""
def new_i(idx):
	def fun():
		if idx == 4:
			return list()
		else:
			return defaultdict(new_i(idx+1))
	return fun
"""

def new_0():
	return defaultdict(new_1)
def new_1():
	return defaultdict(new_2)
def new_2():
	return defaultdict(new_3)
def new_3():
	return defaultdict(list)

class OrderedAndIndexedStore(Store):
	context_aware = True
	formula_aware = True
	graph_aware = True

	# default context information for triples

	def __init__(self, configuration=None, identifier=None):
		super().__init__(configuration)
		self.identifier = identifier
		self.quads = []
		self.quoted_info = []
		self.__namespace = {}
		self.__prefix = {}
		# ?
		# default context information for triples
		self.__defaultContexts = None
		#self.indexes = defaultdict(new_i(0))
		self.indexes = defaultdict(new_0)

	def copy(self):
		r = self.__class__()
		assert len(self.__namespace) == 0
		assert len(self.__prefix) == 0
		#r.quads = self.quads[:]
		#r.quoted_info = self.quoted_info[:]
		from copy import deepcopy
		return deepcopy(self)

	def get_pattern(self, spoc):
		return "".join(('f' if x == None else 't') for x in spoc)

	def add(self, xxx_todo_changeme, context, quoted=False):
		assert not quoted
		Store.add(self, xxx_todo_changeme, context, quoted)
		s1, p1, o1 = xxx_todo_changeme
		incoming = s1, p1, o1, context
		for pat in patterns:
			i = self.indexes[pat]
			for incoming_idx, l in enumerate(pat):
				if l == 'f':
					i = i[None]
				else:
					i = i[incoming[incoming_idx]]
			i.append((xxx_todo_changeme, context))
		self.quads.append((xxx_todo_changeme, context))


	def remove(self, xxx_todo_changeme1, context=None):
		assert False
		# todo: figure out why the Memory store doesnt check the context
		s1, p1, o1 = xxx_todo_changeme1
		quads = self.quads[:]  # self.quads may be modified during the following iteration
		for quad in quads:
			if quad not in self.quads: continue
			(s2, p2, o2), c2 = quad
			if ((s1 == None) or (s1 == s2)) and ((p1 == None) or (p1 == p2)) and ((o1 == None) or (o1 == o2)) and (
					context == c2):
				i = self.quads.index(quad)
				del self.quoted_info[i]
				del self.quads[i]
				self.remove(xxx_todo_changeme1, context)

	# from collections import defaultdict
	# stats = defaultdict(lambda : 0)

	def triples(self, triplein, context=None):
		#print("want ", triplein, " in ", context)
		if context is not None:
			if context == self:  # hmm...does this really ever happen?
				context = None
		s1, p1, o1 = triplein
		# self.__class__.stats["".join([('0' if (x == None) else '1') for x in (s1,p1,o1,context)])] += 1
		# print (self.__class__.stats)

		pattern = self.get_pattern((s1, p1, o1, context))
		if pattern in self.indexes:
			r = self.indexes[pattern][s1][p1][o1][context]
			#print ('return ', r)
			return r


		if (s1 != None) and (p1 != None) and (o1 == None) and (context != None):
			def filter_func(x):
				(s2, p2, o2), c2 = x
				return (s1 == s2) and (p1 == p2) and (context == c2)
			#print ('return filter')
			return filter(filter_func, self.quads)

		#print ('return general')
		return self.general_triple_helper(s1, p1, o1, context, self.quads)


	def general_triple_helper(self, s1, p1, o1, context, quads):
		for spo2, c2 in quads:
			s2, p2, o2 = spo2
			# print("trying", spo2,c2,_q2)
			if ((s1 == None) or (s1 == s2)) and ((p1 == None) or (p1 == p2)) and ((o1 == None) or (o1 == o2)) and (
					context == c2):
				# print("matches")
				yield spo2, c2
