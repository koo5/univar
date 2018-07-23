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
border_width = 1
gv_output_file = None

def gv(text):
	logging.getLogger("kbdbg").info(text)
	gv_output_file.write(text + '\n')

def value(g, subject=None, predicate=rdflib.term.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#value'), object=None, default=None, any=False):
	return g.value(subject, predicate, object, default, any)

def gv_escape(string):
	return '"%s"' % string.replace('"', '\\"')
	#return urllib.parse.quote_plus(string)


def tell_if_is_last_element(x):
	for i, j in enumerate(x):
		yield j, (i == (len(x) - 1))



def generate_gv_image(g, step):
	global arrow_width

	gv("digraph frame"+str(step) + "{")

	#print rules somewhere on the side?
	#for rule in g.subjects(RDF.type, kbdbg.rule):
	#	emit_rule(rule)

	current_result = None
	for i, result_uri in enumerate(g.subjects(RDF.type, kbdbg.result)):
		result_node = gv_escape(result_uri)
		r = result_node + ' [label=<'
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

	rrr = list(g.subjects(RDF.type, kbdbg.frame))
	for i, frame in enumerate(rrr):
		f, text = get_frame_gv(i, g, frame)
		gv(f + text)
		if i == 0 and current_result:
			arrow(result_node, f)

	for binding in g.subjects(RDF.type, kbdbg.binding):
		if g.value(binding, kbdbg.was_unbound) == rdflib.Literal(True):
			continue
		if g.value(binding, kbdbg.failed) == rdflib.Literal(True):
			continue
		source_uri = g.value(binding, kbdbg.has_source)
		target_uri = g.value(binding, kbdbg.has_target)
		arrow(gv_endpoint(g, source_uri), gv_endpoint(g, target_uri))

	"""
	for bnode in g.subjects(RDF.type, kbdbg.bnode):
		r = result_node + gv_escape(bnode) + ' [label=<'
		(doc, tag, text) = yattag.Doc().tagtext()
		with tag("table"):
			for i in Collection(bnode):
				g.object(i, kbdbg.has_name)
				with tag('tr'):
					with tag("td"):
	"""

	gv("}")

def gv_endpoint(g, uri):
	x = g.value(uri, kbdbg.is_in_head, default=False)
	is_in_head = (x == rdflib.Literal(True))
	term_idx = g.value(uri, kbdbg.term_idx, default=0)
	arg_idx  = g.value(uri, kbdbg.arg_idx)
	return gv_escape(str(g.value(uri, kbdbg.has_frame))) + ":" + port_name(is_in_head, term_idx, arg_idx)

def get_frame_gv(i, g, frame):
	return gv_escape(frame), " [shape=none, margin=0, label=<" + get_frame_html_label(g, frame) + ">]"

def get_frame_html_label(g, frame):
		rule = g.value(frame, kbdbg.is_for_rule)
		head = g.value(rule, kbdbg.has_head)
		doc, tag, text = yattag.Doc().tagtext()
		with tag("table", border=0, cellborder=2, cellpadding=0, cellspacing=0):
			with tag("tr"):
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


def arrow(x,y):
	r = x + '->' + y
	if arrow_width != 1:
		r += ' [penwidth = ' + str(arrow_width) + ']'# + ', arrowhead = ' + str(arrow_width)
	gv(r)


def run():
	global gv_output_file
	input_file = open("kbdbg.n3")
	lines = []
	os.system("rm kbdbg*gv")
	os.system("rm aaakbdbg*png")
	os.system("rm kbdbg*svg")
	while True:
		l = input_file.readline()
		if l == "":
			break
		if l.startswith("#step"):
			step = int(l[5:l.find(' ')])
		else:
			lines.append(l)
			continue

		g = Graph(OrderedStore())
		i = "".join(lines)
		g.parse(data=i, format='n3')
		if list(g.subjects(RDF.type, kbdbg.frame)) == []:
			continue

		gv_output_file_name = 'kbdbg' + str(step).zfill(9) + '.gv'
		try:
			os.unlink(gv_output_file_name)
		except FileNotFoundError:
			pass
		gv_output_file = open(gv_output_file_name, 'w')
		generate_gv_image(g, step)
		gv_output_file.close()
		import threading#dot "+gv_output_file_name+" -Tsvg > "+gv_output_file_name+".svg;
		threading.Thread(target=lambda:
			os.system("convert  -extent 8000x1000  "+gv_output_file_name+" -gravity NorthWest  -background white aaa"+gv_output_file_name+".png")).start()


if __name__ == '__main__':
	run()



#from IPython import embed;embed()