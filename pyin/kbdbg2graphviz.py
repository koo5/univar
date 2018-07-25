#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html as html_module
import os
import sys
import logging
import urllib.parse
import rdflib
from rdflib import Graph
from rdflib.namespace import Namespace
from rdflib.namespace import RDF
from rdflib.collection import Collection
from ordered_rdflib_store import OrderedStore
import yattag

kbdbg = Namespace('http://kbd.bg/#')

gv_handler = logging.StreamHandler(sys.stdout)
gv_handler.setLevel(logging.DEBUG)
gv_handler.setFormatter(logging.Formatter('%(message)s'))

logger=logging.getLogger("kbdbg")
logger.addHandler(gv_handler)

logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.debug("hi")
log=logger.debug

arrow_width = 1
border_width = 0
gv_output_file = None

def gv(text):
	logging.getLogger("kbdbg").info(text)
	gv_output_file.write(text + '\n')

def value(g, subject=None, predicate=rdflib.term.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#value'), object=None, default=None, any=False):
	return g.value(subject, predicate, object, default, any)

#import memoized
#gv_escape_counter = 0
#@memoized.memoized
def gv_escape(string):
	#global gv_escape_counter
	#gv_escape_counter += 1
	#string = string.replace('"', '\\"')
	r = ""
	for i in string:
		r += str(ord(i)).zfill(4)
	#r += str(gv_escape_counter)
	r += '_'
	for i in string:
		if i.isalnum():
			r += i
	return "gv"+r
	return "<"+urllib.parse.quote_plus(string)+">"
	return '"%s"' % string

"""
import memoized
gv_escape_counter = 0
@memoized.memoized
def gv_escape(node, port=None):
	global gv_escape_counter
	if port:
		return gv_escape(node) + ":" + gv_escape(port)
	gv_escape_counter += 1
	r = "gv" + str(gv_escape_counter)
	r += '_'
	for i in node:
		if i.isalnum():
			r += i
	return r
"""

def tell_if_is_last_element(x):
	for i, j in enumerate(x):
		yield j, (i == (len(x) - 1))


last_bindings = []

def generate_gv_image(g, step):
	global arrow_width, last_bindings

	gv("digraph frame"+str(step) + "{")
	#gv("pack=true")

	#print rules somewhere on the side?
	#for rule in g.subjects(RDF.type, kbdbg.rule):
	#	emit_rule(rule)
	root_frame = None
	current_result = None
	rrr = list(g.subjects(RDF.type, kbdbg.frame))
	last_frame = None
	for i, frame in enumerate(rrr):
		if g.value(frame, kbdbg.is_finished, default=False):
			continue
		f, text = get_frame_gv(i, g, frame)
		gv(f + text)
		#if last_frame:
		#	arrow(last_frame, f, color='yellow', weight=100)
		parent = g.value(frame, kbdbg.has_parent)
		if parent:# and not g.value(parent, kbdbg.is_finished, default=False):
			arrow(gv_escape(parent), f, color='yellow', weight=10000000)
		else:
			root_frame = f
		last_frame = f
		#if i == 0 and current_result:
		#	arrow(result_node, f)

	for bnode in g.subjects(RDF.type, kbdbg.bnode):
		if g.value(g.value(bnode, kbdbg.has_parent), kbdbg.is_finished, default=False):
			continue
		(doc, tag, text) = yattag.Doc().tagtext()
		with tag("table", border=0, cellspacing=0):
			#for i in Collection(g, bnode):
			with tag('tr'):
				with tag('td', border=1):
					text((shorten(bnode.n3())))
			for i in g.objects(bnode, kbdbg.has_item):
				with tag('tr'):
					name = g.value(i, kbdbg.has_name)
					with tag("td", border=1, port=gv_escape(name)):
						text(shorten(name))
						text(' = ')
						text(shorten(g.value(i, kbdbg.has_value)))
					#with tag("td", border=1):
					#	text(shorten(g.value(i, kbdbg.has_value)))
		gv(gv_escape(bnode) + ' [shape=none, cellborder=2, label=<' + doc.getvalue()+ '>]')
		arrow(gv_escape(g.value(bnode, kbdbg.has_parent)), gv_escape(bnode), color='yellow', weight=100)


	new_last_bindings = []
	for binding in g.subjects(RDF.type, kbdbg.binding):
		source_uri = g.value(binding, kbdbg.has_source)
		target_uri = g.value(binding, kbdbg.has_target)
		if g.value(binding, kbdbg.was_unbound) == rdflib.Literal(True):
			if (binding.n3() in last_bindings):
				arrow(gv_endpoint(g, source_uri), gv_endpoint(g, target_uri), color='orange', binding=True)
			continue
		if g.value(binding, kbdbg.failed) == rdflib.Literal(True):
			if (binding.n3() in last_bindings):
				arrow(gv_endpoint(g, source_uri), gv_endpoint(g, target_uri), color='red', binding=True)
			continue
		arrow(gv_endpoint(g, source_uri), gv_endpoint(g, target_uri),
		      color=('black' if (binding.n3() in last_bindings) else 'purple' ), binding=True)
		new_last_bindings.append(binding)
	last_bindings.clear()
	for i in new_last_bindings:
		last_bindings.append(i.n3())

	last_result = root_frame
	for i, result_uri in enumerate(g.subjects(RDF.type, kbdbg.result)):
		result_node = gv_escape(result_uri)
		r = result_node + ' [cellborder=2, shape=none, label=<'
		(doc, tag, text) = yattag.Doc().tagtext()
		with tag("table"):
			with tag('tr'):
				with tag("td"):
					text('RESULT'+str(i) +' ')
				emit_terms(tag, text, g, g.value(result_uri, RDF.value))
		r += doc.getvalue()+ '>]'
		gv(r)
		false = rdflib.Literal(False)
		if g.value(result_uri, kbdbg.was_unbound, default = false) == false:
			current_result = result_node
			arrow_width = 2
		else:
			arrow_width = 1
		if last_result:
			arrow(last_result, result_node, color='yellow', weight=100)
		last_result = result_node


	gv("}")

def gv_endpoint(g, uri):
	if(g.value(uri, kbdbg.is_bnode, default=False)):
		term_idx = g.value(uri, kbdbg.term_idx, default=' $\=st #-* -')
		return gv_escape(str(g.value(uri, kbdbg.has_frame))) + ":" + gv_escape(term_idx)
	else:
		x = g.value(uri, kbdbg.is_in_head, default=False)
		is_in_head = (x == rdflib.Literal(True))
		term_idx = g.value(uri, kbdbg.term_idx, default=0)
		arg_idx  = g.value(uri, kbdbg.arg_idx)
		return gv_escape(str(g.value(uri, kbdbg.has_frame))) + ":" + port_name(is_in_head, term_idx, arg_idx)

def get_frame_gv(i, g, frame):
	r = ' [shape=none, margin=0, '
	isroot = False
	if not g.value(frame, kbdbg.has_parent):
		r += 'root=true, pin=true, pos="1000,100!", margin="10,0.055" , '#40
		isroot = True
	return gv_escape(frame), r + ' label=<' + get_frame_html_label(g, frame, isroot) + ">]"


frame_name_template_var_name = '%frame_name_template_var_name%'
def get_frame_html_label(g, frame, isroot):
	rule = g.value(frame, kbdbg.is_for_rule)
	return _get_frame_html_label(
		g, rule, isroot
	).replace(
		frame_name_template_var_name,html_module.escape(shorten(frame.n3()))
	)

import memoized
@memoized.memoized
def _get_frame_html_label(g, rule, isroot):
		head = g.value(rule, kbdbg.has_head)
		doc, tag, text = yattag.Doc().tagtext()

		with tag("table", border=1, cellborder=0, cellpadding=0, cellspacing=0):
			with tag("tr"):
				with tag('td', border=border_width):
					if isroot:
						text('QUERY:')
					text(frame_name_template_var_name)
				with tag("td", border=border_width):
					text("{")
				if head:
					emit_term(tag, text, g, True, 0, head)
				with tag("td", border=border_width):
					text("} <= {")

				body_items_list_name = g.value(rule, kbdbg.has_body)
				if body_items_list_name:
					body_items_collection = Collection(g, body_items_list_name)
					term_idx = 0
					for body_item in body_items_collection:
						emit_term(tag, text, g, False, term_idx, body_item)
						term_idx += 1
				with tag("td", border=border_width):
					text('}')
		#todo print a table of variables, because showing bindings directly between args of triples is misleading? is it?
		return doc.getvalue()

def emit_terms(tag, text, g, uri):
	body_items_collection = Collection(g, uri)
	for term_idx, body_item in enumerate(body_items_collection):
		emit_term(tag, text, g, False, term_idx, body_item)


def port_name(is_in_head, term_idx, arg_idx):
	return (
			('head' if is_in_head else 'body') + "term" +
			str(term_idx) + "arg" +
			str(arg_idx)
			)

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

def emit_term(tag, text, g, is_in_head, term_idx, term):
	pred = g.value(term, kbdbg.has_pred)
	args_collection = Collection(g, g.value(term, kbdbg.has_args))
	if len(args_collection) == 2:
		def arrrr(arg_idx):
			with tag('td', port=port_name(is_in_head, term_idx, arg_idx), border=border_width):
				text(shorten(args_collection[arg_idx]))
		arrrr(0)
		with tag("td", border=border_width):
			text(shorten(pred))
		arrrr(1)
		with tag("td", border=border_width):
			text('.')
	else:
		with tag("td", border=border_width):
			text(shorten(pred) + '( ')
		arg_idx = 0
		for arg, is_last in tell_if_is_last_element(args_collection):
			with tag('td', port=port_name(is_in_head, term_idx, arg_idx), border=border_width):
				text(shorten(arg))
			arg_idx += 1
			if not is_last:
				with tag("td", border=border_width):
					text(', ')
		with tag("td", border=border_width):
			text(').')

def arrow(x,y,color='black',weight=1, binding=False):
	r = x + '->' + y
	#if arrow_width != 1:
	r += ' [weight="'+str(weight)+'"color="'+color+'" penwidth = ' + str(arrow_width) + ' '
	if binding:
		r += 'constraint=false'
	r += ']'# + ', arrowhead = ' + str(arrow_width)
	gv(r)


def run():
	global gv_output_file
	if len(sys.argv) == 2:
		fn = sys.argv[1]
	else:
		fn = 'kbdbg.n3'
	input_file = open(fn)
	lines = []
	os.system("rm -f kbdbg"+fn+'\\.*')

	import multiprocessing
	pool=multiprocessing.Pool(4)

	g = Graph(OrderedStore())
	prefixes = []
	while True:
		l = input_file.readline()
		if l == "":
			break
		if l.startswith("#step"):
			step = int(l[5:l.find(' ')])
		elif l.startswith('@prefix'):
			prefixes.append(l)
			continue
		else:
			lines.append(l)
			continue

		i = "".join(prefixes+lines)
		g.parse(data=i, format='n3')
		lines = []
		if list(g.subjects(RDF.type, kbdbg.frame)) == []:
			continue

		gv_output_file_name = fn + '_' + str(step).zfill(5) + '.gv'
		try:
			os.unlink(gv_output_file_name)
		except FileNotFoundError:
			pass
		gv_output_file = open(gv_output_file_name, 'w')
		generate_gv_image(g, step)
		gv_output_file.close()
		#import threading#dot "+gv_output_file_name+" -Tsvg > "+gv_output_file_name+".svg;
		#threading.Thread(target=lambda:
		#	os.system("convert  -extent 8000x1000  "+gv_output_file_name+" -gravity NorthWest  -background white aaa"+gv_output_file_name+".png")).start()

		pool.apply_async(os.system, ("convert  -extent 6000x3000  "+gv_output_file_name+" -gravity NorthWest  -background white "+gv_output_file_name+".png",))




if __name__ == '__main__':
	run()



#from IPython import embed;embed()