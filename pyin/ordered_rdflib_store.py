"""
issues: should quads added during iteration of triples() be yielded during that call?
"""

#from rdflib.term import BNode
from rdflib.store import Store#, NO_STORE, VALID_STORE

__all__ = ['OrderedStore']

class OrderedStore(Store):

    context_aware = True
    formula_aware = True
    graph_aware = True
        # default context information for triples

    def __init__(self, configuration=None, identifier=None):
        super(OrderedStore, self).__init__(configuration)
        self.identifier = identifier
        self.quads = []
        self.__namespace = {}
        self.__prefix = {}
#?
        # default context information for triples
        self.__defaultContexts = None

    def add(self, xxx_todo_changeme, context, quoted=False):
        Store.add(self, xxx_todo_changeme, context, quoted)
        self.quads.append((xxx_todo_changeme, context, quoted))

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
	#todo: figure out why the Memory store doesnt check the context
        s1,p1,o1 = xxx_todo_changeme1
        quads = self.quads # self.quads may be modified during the following iteration
        for quad in quads:
            if quad not in self.quads: continue
            spo2,c2,_q2 = quad
            s2,p2,o2 = spo2
            if ((s1 == None) or (s1 == s2)) and ((p1 == None) or (p1 == p2)) and ((o1 == None) or (o1 == o2)) and (context == c2):
                self.quads.remove(quad)
                self.remove(xxx_todo_changeme1, context)

    def triples(self, triplein, context=None):
        #print("want ", triplein, " in ", context)
        if context is not None:
            if context == self:  # hmm...does this really ever happen?
                context = None
        s1,p1,o1 = triplein
        quads = self.quads # self.quads may be modified during the following iteration
        for spo2,c2,_q2 in quads:
            #print("trying", spo2,c2,_q2)
            s2,p2,o2 = spo2
            if ((s1 == None) or (s1 == s2)) and ((p1 == None) or (p1 == p2)) and ((o1 == None) or (o1 == o2)) and (context == c2):
                #print("matches")
                yield (s2,p2,o2),c2

