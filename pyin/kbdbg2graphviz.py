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
gv_handler.setFormatter(logging.Formatter('%(message)s.'))

gv_output_file_name = 'kbdbg.gv'
try:
	os.unlink(gv_output_file_name)
except FileNotFoundError:
	pass
gv_handler2 = logging.FileHandler(gv_output_file_name)
gv_handler2.setLevel(logging.DEBUG)
gv_handler2.setFormatter(logging.Formatter('%(message)s'))

logger=logging.getLogger("kbdbg")
logger.addHandler(gv_handler)
gv=logger.info

logger.addHandler(gv_handler2)

logger=logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.debug("hi")
log=logger.debug


def value(g, subject=None, predicate=rdflib.term.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#value'), object=None, default=None, any=False):
	return g.value(subject, predicate, object, default, any)

def gv_escape(string):
	return '"%s"' % string.replace('"', '\\"')
	#return urllib.parse.quote_plus(string)


def tell_if_is_last_element(x):
	for i, j in enumerate(x):
		yield j, (i == (len(x) - 1))



def process_input(lines):
	g = Graph(OrderedStore())
	i = "".join(lines)
	#					print("i:", i)
	g.parse(data=i, format='n3')

	if list(g.subjects(RDF.type, kbdbg.frame)) == []:
		return

	step = len(lines)

	#					now query g and generate one graphviz image
	gv("digraph frame"+str(step) + "{")

	#for rule in g.subjects(RDF.type, kbdbg.rule):
	#	emit_rule(rule)

	rrr = list(g.subjects(RDF.type, kbdbg.frame))
	for i, frame in enumerate(rrr):#g.subjects(RDF.type, kbdbg.frame):
		gv(get_frame_gv(i, g, frame))

	rrr = list(g.subject_objects(kbdbg.was_bound_to))
	for s,o in rrr:
		if g.value(s, kbdbg.was_unbound_from, o):
			continue
		source = object()
		target = object()
		source.thing = g.value(binding, kbdbg.has_source)
		source.string = g.value(source.thing, kbdbg.has_string)
		source.frame = g.value(source.thing, kbdbg.belongs_to_frame)
		source.rule = g.value(source.frame, kbdbg.belongs_to_rule)
		target.thing = g.value(binding, kbdbg.has_target)
		target.string = g.value(target.thing, kbdbg.has_string)
		target.frame = g.value(target.thing, kbdbg.belongs_to_frame)
		target.rule = g.value(target.frame, kbdbg.belongs_to_rule)




		#for source_port in g.values(source.rule, kbdbg.has_body_port):
		#	for target_port in g.values(target.rule, kbdbg.has_head_port):
		#			if target.string == g.value(target.port, kbdbg.belongs_to_thing_string)
		#				gv(source.frame + ":" + source.port + " -> " + target.frame + ":" + target.port)



	gv("}")


def get_frame_gv(i, g, frame):
	return gv_escape(frame) + " [label=<" + get_frame_html_label(g, frame) + ">];"
#gv_escape(frame) +
#"frame" + str(i)

def get_frame_html_label(g, frame):
		rule = g.value(frame, kbdbg.is_for_rule)
		head = g.value(rule, kbdbg.has_head)
		doc, tag, text = yattag.Doc().tagtext()
		with tag("table"):
			with tag("tr"):
				with tag("td"):
					text("{")
				if head:
					emit_term(tag, text, g, rule, True, 0, head)
				with tag("td"):
					text("} <= {")

				body_items_list_name = g.value(rule, kbdbg.has_body)
				#from IPython import embed;embed()
				if body_items_list_name:
					body_items_collection = Collection(g, body_items_list_name)
					term_idx = 0
					for body_item in body_items_collection:
						emit_term(tag, text, g, rule, False, term_idx, body_item)
						term_idx += 1
				with tag("td"):
					text('}')

		#here i want to print a table of variables

		return doc.getvalue()


def emit_term(tag, text, g, rule_uri, is_in_head, term_idx, term):#port_idx,
	pred = g.value(term, kbdbg.has_pred)
	with tag("td"):
		text(pred.n3() + '(')
	arg_idx = 0
	for arg, is_last in tell_if_is_last_element(Collection(g, g.value(term, kbdbg.has_args))):
		port_name = (
				('head' if is_in_head else 'body') + "term" +
				str(term_idx) + "arg" +
				str(arg_idx)
					)
		with tag('td', port=port_name):
			text(arg.n3())
		arg_idx += 1
		#port_idx += 1
		if not is_last:
			with tag("td"):
				text(', ')
	with tag("td"):
		text('). ')

def run():
	input_file = open("kbdbg.n3")
	lines = []
	while True:
		l = input_file.readline()
		if l == "":
			process_input(lines)
			break
		lines.append(l)




if __name__ == '__main__':
	run()