# -*- coding: utf-8 -*-

"""PYthon does the input, C++ does the Output"""


from weakref import ref as weakref
from rdflib import URIRef
import rdflib
import sys
import os
import logging
try:
	from urllib.parse import quote_plus
except ImportError:
	from urllib import quote_plus
from collections import defaultdict, OrderedDict
from common import shorten#, traverse, join_generators
from time import sleep
from common import pyin_prefixes as prefixes

nolog = False
kbdbg_prefix = URIRef('http://kbd.bg/#')
log, kbdbg_text = 666,666
pool = None
futures = []

if sys.version_info.major == 3:
	unicode = str


def query(input_rules, input_query):
	out('#include "pyco_static.cpp"')
	out('/*forward declarations*/')
	for r in input_rules+input_query:
		"static " + r.kbdbg_name + "(cpppred_state & __restrict__ state);"
	

