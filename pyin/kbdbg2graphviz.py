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
	gv("digraph frame"+str(step) + "{")

	#for rule in g.subjects(RDF.type, kbdbg.rule):
	#	emit_rule(rule)

	rrr = list(g.subjects(RDF.type, kbdbg.frame))
	for i, frame in enumerate(rrr):#g.subjects(RDF.type, kbdbg.frame):
		gv(get_frame_gv(i, g, frame))

	for binding in g.subjects(RDF.type, kbdbg.binding):
		if g.value(binding, kbdbg.was_unbound) == rdflib.Literal(True):
			continue
		source_uri = g.value(binding, kbdbg.has_source)
		target_uri = g.value(binding, kbdbg.has_target)
		gv(gv_endpoint(g, source_uri) + "->" + gv_endpoint(g, target_uri))
	gv("}")

def gv_endpoint(g, uri):
	x = g.value(uri, kbdbg.is_in_head, default=False)
	is_in_head = (x == rdflib.Literal(True))
	term_idx = g.value(uri, kbdbg.term_idx, default=0)
	arg_idx  = g.value(uri, kbdbg.arg_idx)
	return str(g.value(uri, kbdbg.has_frame)) + ":" + port_name(is_in_head, term_idx, arg_idx)

def get_frame_gv(i, g, frame):
	return gv_escape(frame) + " [shape=none, margin=0, label=<" + get_frame_html_label(g, frame) + ">]"

def get_frame_html_label(g, frame):
		rule = g.value(frame, kbdbg.is_for_rule)
		head = g.value(rule, kbdbg.has_head)
		doc, tag, text = yattag.Doc().tagtext()
		with tag("table", border=2):
			with tag("tr"):
				with tag("td", border=0):
					text("{")
				if head:
					emit_term(tag, text, g, rule, True, 0, head)
				with tag("td", border=0):
					text("} <= {")

				body_items_list_name = g.value(rule, kbdbg.has_body)
				#from IPython import embed;embed()
				if body_items_list_name:
					body_items_collection = Collection(g, body_items_list_name)
					term_idx = 0
					for body_item in body_items_collection:
						emit_term(tag, text, g, rule, False, term_idx, body_item)
						term_idx += 1
				with tag("td", border=0):
					text('}')

		#here i want to print a table of variables

		return doc.getvalue()


def port_name(is_in_head, term_idx, arg_idx):
	return (
			('head' if is_in_head else 'body') + "term" +
			str(term_idx) + "arg" +
			str(arg_idx)
			)


def emit_term(tag, text, g, rule_uri, is_in_head, term_idx, term):#port_idx,
	pred = g.value(term, kbdbg.has_pred)
	with tag("td", border=0):
		text(pred.n3() + '(')
	arg_idx = 0
	for arg, is_last in tell_if_is_last_element(Collection(g, g.value(term, kbdbg.has_args))):
		with tag('td', port=port_name(is_in_head, term_idx, arg_idx), border=0):
			text(arg.n3())
		arg_idx += 1
		#port_idx += 1
		if not is_last:
			with tag("td", border=0):
				text(', ')
	with tag("td", border=0):
		text('). ')


gv_output_file = None

def run():
	global gv_output_file
	input_file = open("kbdbg.n3")
	lines = []
	frame = 0
	while True:
		l = input_file.readline()
		if l == "":
			break
		lines.append(l)

		g = Graph(OrderedStore())
		i = "".join(lines)
		g.parse(data=i, format='n3')
		if list(g.subjects(RDF.type, kbdbg.frame)) == []:
			continue
		step = len(lines)

		gv_output_file_name = 'kbdbg' + str(frame).zfill(9) + '.gv'
		try:
			os.unlink(gv_output_file_name)
		except FileNotFoundError:
			pass
		gv_output_file = open(gv_output_file_name, 'w')
		generate_gv_image(g, step)
		gv_output_file.close()
		frame += 1
		os.system("osage "+gv_output_file_name+" -Tsvg > "+gv_output_file_name+".svg")
		os.system("convert  -extent 8000x1000  "+gv_output_file_name+" -gravity NorthWest  -background white aaa"+gv_output_file_name+".png")


if __name__ == '__main__':
	run()