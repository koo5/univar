#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import redislite, redis_collections
import click
from common import shorten, fix_up_identification
import html as html_module
import os
import sys
import logging
import urllib.parse
import subprocess
import yattag
import rdflib
from rdflib import ConjunctiveGraph, Graph, URIRef, Literal
from rdflib.namespace import Namespace
from rdflib.namespace import RDF
from rdflib.plugins.stores import sparqlstore
from non_retarded_collection import Collection
from concurrent.futures import ProcessPoolExecutor
from pymantic import sparql
from sortedcontainers import SortedList

sparql_uri = 'http://localhost:9999/blazegraph/sparql'

redis_connection = None
strict_redis_connection = None

kbdbg = Namespace('http://kbd.bg/#')

gv_handler = logging.StreamHandler(sys.stdout)
gv_handler.setLevel(logging.DEBUG)
gv_handler.setFormatter(logging.Formatter('%(message)s'))

logger=logging.getLogger("kbdbg")
logger.addHandler(gv_handler)

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.addHandler(console)
logger.debug("hi")
log=logger.debug

default_graph = 'http://kbd.bg/#runs'

arrow_width = 1
border_width = 1


stats = SortedList(key=lambda x: -x[0])

prefixes = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX kbdbg: <http://kbd.bg/#> 
PREFIX : <file:///#> 
"""


def profile(func, args=(), note=''):
	start = time.time()
	r = func(*args)
	end = time.time()
	stats.add((end - start, func, args, note))
	return r


def fetch_list(vars, list_uri, additional):
	return query(vars, 'WHERE {<'+list_uri+'> rdf:rest*/rdf:first ?item.' +
				 additional + '}')

def query(vars, q):
	if isinstance(vars, str):
		vars = (vars,)
	q2 = prefixes + 'SELECT '+' '.join('?'+x for x in vars)+' ' + q
	log(q2)
	rrr= profile(sparql_server.query, (q2,))['results']['bindings']
	for i in rrr:
		r = {}
		for k in vars:
			if k in i:
				v = i[k]
				if v['type'] == 'uri':
					r[k] = v['value']
				else:
					r[k] = v['value']
			else:
				r[k] = None
		if len(vars) == 1:
			rrrr= r[k]
		else:
			rrrr = r
		log(rrrr)
		yield rrrr


def query_one(vars, q):
	l = list(query(vars, q))
	if len(l) != 1:
		raise 666
	return l[0]

def get_last_bindings(step):
	log ('get last bindings...' + '[' + str(step) + ']')
	if step == 0:
		return []
	if step == global_start - 1:
		return []
	sss = step - 1
	return redis_connection.blpop([sss])

def put_last_bindings(step, new_last_bindings):
	redis_connection.lpush(step, new_last_bindings)



def tell_if_is_last_element(x):
	for i, j in enumerate(x):
		yield j, (i == (len(x) - 1))

import memoized
#@memoized.memoized
def gv_escape(string):
	r = ""
	for i in string:
		enc = str(ord(i)).zfill(4)
		r += enc
		if len(enc) > 4: raise "opps, gotta increase the zfill length here"
	r += '_'
	for i in string:
		if i.isalnum():
			r += i
	return "gv"+r
	return "<"+urllib.parse.quote_plus(string)+">"
	return '"%s"' % string


frame_name_template_var_name = '%frame_name_template_var_name%'

class Emitter:

	def __init__(s, gv_output_file, step):
		s.gv_output_file = gv_output_file
		s.step = step
		s.frame_templates = redis_collections.Dict(redis=strict_redis_connection)

	def gv(s, text):
		s.gv_output_file.write(text + '\n')

	def comment(s, text):
		s.gv('//'+text)

	def generate_gv_image(s, frames_list):
		log ('frames.. ' + '[' + str(s.step) + ']')
		#log(str(frames_list))
		root_frame = None
		#current_result = None
		last_frame = None
		for i, frame in enumerate(frames_list):
			log(frame)
			f, text = s.get_frame_gv(i, frame)
			s.gv(f + text)
			#if last_frame:
			#	arrow(last_frame, f, color='yellow', weight=100)
			parent = frame['parent']
			if parent:# and not g.value(parent, kbdbg.is_finished, default=False):
				s.arrow(gv_escape(parent), f, color='yellow', weight=10000000)
			else:
				root_frame = f
			last_frame = f
			#if i == 0 and current_result:
			#	arrow(result_node, f)


		log ('bnodes.. ' + '[' + str(s.step) + ']')

		bnode_list = list(query(('bnode','parent', 'items'),
		"""WHERE
		{
			{
				SELECT (?frame AS ?parent) WHERE
				{
					GRAPH ?g {
						?frame rdf:type kbdbg:frame
					}.""" + step_magic() + """
					FILTER NOT EXISTS {
						GRAPH ?gg 
						{
							?frame kbdbg:is_finished true
						}.""" + step_magic('gg') + """
					}
				}
			}
			?bnode kbdbg:has_parent ?frame.
			?bnode kbdbg:has_items ?items.
		}"""))

		for bnode_data in bnode_list:
			bnode, parent, items_uri  = bnode_data['bnode'],bnode_data['parent'],bnode_data['items']
			(doc, tag, text) = yattag.Doc().tagtext()
			with tag("table", border=0, cellspacing=0):
				with tag('tr'):
					with tag('td', border=1):
						text(shorten(bnode))
				items = fetch_list(('item','name','value'), items_uri,
					"""	?item kbdbg:has_name ?name.
                		?item kbdbg:has_value ?value.""")
				for i in items:
					with tag('tr'):
						name = i['name']
						pn = gv_escape(name)
						with tag("td", border=1, port=pn):
							text(shorten(name))
							text(' = ')
							text(shorten(i['value']))
						#with tag("td", border=1):
						#	text(shorten(g.value(i, kbdbg.has_value)))
			s.gv(gv_escape(bnode) + ' [shape=none, cellborder=2, label=<' + doc.getvalue()+ '>]')
			s.arrow(gv_escape(parent), gv_escape(bnode), color='yellow', weight=100)

		last_bindings = get_last_bindings(s.step)
		log ('bindings...' + '[' + str(s.step) + ']')

		new_last_bindings = []
		"""
		
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX kbdbg: <http://kbd.bg/#> 

select * 
{
	  ?x rdf:type kbdbg:binding.
      FILTER NOT EXISTS {?x kbdbg:was_unbound true}.
      #FILTER NOT EXISTS {?x kbdbg:failed true}.
      OPTIONAL {?x kbdbg:failed ?failed}.
      ?x kbdbg:has_source ?source.
      ?x kbdbg:has_target ?target.
      OPTIONAL {?source kbdbg:is_bnode ?source_is_bnode.}.
      OPTIONAL {?target kbdbg:is_bnode ?target_is_bnode.}.
      ?source kbdbg:term_idx ?source_term_idx.
      ?target kbdbg:term_idx ?target_term_idx.
      OPTIONAL {?source kbdbg:is_in_head ?source_is_in_head.}.
      OPTIONAL {?target kbdbg:is_in_head ?target_is_in_head.}.
      OPTIONAL {?source kbdbg:arg_idx ?source_arg_idx.}.
      OPTIONAL {?target kbdbg:arg_idx ?target_arg_idx.}.
}
		
		"""
		for binding in subjects(RDF.type, kbdbg.binding):
			weight = 1
			source_uri = value(binding, kbdbg.has_source)
			target_uri = value(binding, kbdbg.has_target)
			if value(source_uri, kbdbg.is_bnode, default=False) and value(target_uri, kbdbg.is_bnode, default=False):
				weight = 0
			if value(binding, kbdbg.was_unbound) == rdflib.Literal(True):
				if (binding.n3() in last_bindings):
					s.comment("just unbound binding")
					s.arrow(s.gv_endpoint(source_uri), s.gv_endpoint(target_uri), color='orange', weight=weight, binding=True)
				continue
			if value(binding, kbdbg.failed) == rdflib.Literal(True):
				if (binding.n3() in last_bindings):
					s.comment("just failed binding")
					s.arrow(s.gv_endpoint(source_uri), s.gv_endpoint(target_uri), color='red', weight=weight, binding=True)
				continue
			s.comment("binding " + binding.n3())
			s.arrow(s.gv_endpoint(source_uri), s.gv_endpoint(target_uri),
				  color=('black' if (binding.n3() in last_bindings) else 'purple' ), weight=weight, binding=True)
			new_last_bindings.append(binding.n3())

		put_last_bindings(s.step, new_last_bindings)
		del new_last_bindings

		log ('results..' + '[' + str(s.step) + ']')
		last_result = root_frame
		for i, result_uri in enumerate(subjects(RDF.type, kbdbg.result)):
			result_node = gv_escape(result_uri)
			r = result_node + ' [cellborder=2, shape=none, label=<'
			(doc, tag, text) = yattag.Doc().tagtext()
			with tag("table"):
				with tag('tr'):
					with tag("td"):
						text('RESULT'+str(i) +' ')
					s.emit_terms(tag, text, value(result_uri, RDF.value), 'result')
			r += doc.getvalue()+ '>]'
			s.gv(r)
			false = rdflib.Literal(False)
			#if g.value(result_uri, kbdbg.was_unbound, default = false) == false:
				#current_result = result_node
				#arrow_width = 2
			#else:
				#arrow_width = 1
			if last_result:
				s.arrow(last_result, result_node, color='yellow', weight=100)
			last_result = result_node

	def gv_endpoint(s, uri):
		"""merge? is_bnode, is_in_head, . get term_idx, arg_idx"""
		if(value(uri, kbdbg.is_bnode, default=False)):
			term_idx = value(uri, kbdbg.term_idx, default=' $\=st #-* -')
			port = gv_escape(term_idx)
			#if port == 'gv0121_y': #gv01080049_l1':
			#	print('x')
			return gv_escape(str(value(uri, kbdbg.has_frame))) + ":" + port
		else:
			x = value(uri, kbdbg.is_in_head, default=False)
			is_in_head = (x == rdflib.Literal(True))
			term_idx = value(uri, kbdbg.term_idx, default=0)
			arg_idx  = value(uri, kbdbg.arg_idx, None)
			if arg_idx == None:
				return gv_escape(str(value(uri, kbdbg.has_frame)))
			port = port_name(is_in_head, term_idx, arg_idx)
			return gv_escape(str(value(uri, kbdbg.has_frame))) + ":" +port

	def get_frame_gv(s, i, frame_data):#"""pass parent here"""
		r = ' [shape=none, margin=0, '
		isroot = False
		if not frame_data['parent']:
			r += 'root=true, pin=true, pos="1000,100!", margin="10,0.055" , '#40
			isroot = True

		frame = frame_data['frame']
		return gv_escape(frame), r + ' label=<' + s.get_frame_html_label(frame_data, isroot) + ">]"


	def get_frame_html_label(s, frame, isroot):
		rule = frame['is_for_rule']
		params = (rule, isroot)
		try:
			template = s.frame_templates[params]
		except KeyError:
			template = s._get_frame_html_label(*params)
			s.frame_templates[params] = template
		return template.replace(frame_name_template_var_name,html_module.escape(shorten(frame['frame'])))

	@staticmethod
	def _get_frame_html_label(rule, isroot):
			rule_data = query_one(('original_head', 'head','body'),
				'{OPTIONAL {<'+rule+"""> kbdbg:has_original_head ?original_head.}. 
				OPTIONAL { <"""+rule+"""> kbdbg:has_head ?head.}
				OPTIONAL { <"""+rule+"""> kbdbg:has_body ?body.}}""")
			body_items = list(query('item', '{<'+rule_data['body']+'> rdf:rest*/rdf:first ?item.}'))
			doc, tag, text = yattag.Doc().tagtext()
			with tag("table", border=1, cellborder=0, cellpadding=0, cellspacing=0):
				with tag("tr"):
					with tag('td', border=border_width):
						if isroot:
							text('QUERY:')
						text(frame_name_template_var_name)
					with tag("td", border=border_width):
						text("{")
					if len(body_items):
						emit_terms(tag, text, rule_data['original_head'], True)
					else:
						emit_term(tag, text, True, 0, rule_data['head'])
					with tag("td", border=border_width):
						text("}")
					if len(body_items):
						with tag("td", border=border_width):
							text(" <= {")
						emit_terms_by_items(tag, text, body_items, False)
						with tag("td", border=border_width):
							text('}')
			return doc.getvalue()

	def arrow(s,x,y,color='black',weight=1, binding=False):
		r = x + '->' + y
		#if arrow_width != 1:
		r += ' [weight="'+str(weight)+'"color="'+color+'" penwidth = ' + str(arrow_width) + ' '
		if binding:
			r += 'constraint=false'
		r += ']'# + ', arrowhead = ' + str(arrow_width)
		s.gv(r)

def port_name(is_in_head, term_idx, arg_idx):
	return (
			('head' if is_in_head else 'body') + "term" +
			str(term_idx) + "arg" +
			str(arg_idx)
			)

def emit_term(tag, text, is_in_head, term_idx, term):
	term_data = query_one(('pred', 'args'), '{<'+term+'> kbdbg:has_pred ?pred. <'+term+'> kbdbg:has_args ?args.}')
	pred = term_data['pred']
	args_list = list(query('item', '{<'+term_data['args']+'> rdf:rest*/rdf:first ?item.}'))
	if len(args_list ) == 2:
		def arrrr(arg_idx):
			with tag('td', port=port_name(is_in_head, term_idx, arg_idx), border=border_width):
				text(' ' + shorten(args_list [arg_idx]) + ' ')
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
		for arg, is_last in tell_if_is_last_element(args_list ):
			with tag('td', port=port_name(is_in_head, term_idx, arg_idx), border=border_width):
				text(shorten(arg))
			arg_idx += 1
			if not is_last:
				with tag("td", border=border_width):
					text(', ')
		with tag("td", border=border_width):
			text(').')

def emit_terms( tag, text, uri, is_head):
	if uri == None: return
	items = list(query('item', '{<'+uri+'> rdf:rest*/rdf:first ?item.}'))
	emit_terms_by_items( tag, text, items, is_head)


def emit_terms_by_items( tag, text, items, is_head):
	for term_idx, item in enumerate(items):
		emit_term(tag, text, is_head, term_idx, item)


def step_magic(graph_var_name='g'):
	return """
	  BIND  (STR(?"""+graph_var_name+""") AS ?strg).
	  FILTER (STRSTARTS(?strg, """+'"'+graph_name_start+'"'+""")).
	  BIND  (STRAFTER(?strg, "_") AS ?step).
	  FILTER (?step < """+'"'+str(step+1).rjust(10,'0')+'").'+"""
	"""

futures = []
global_start = None

@click.command()
@click.option('--start', type=click.IntRange(0, None), default=0)
@click.option('--end', type=click.IntRange(-1, None), default=-1)
@click.option('--workers', type=click.IntRange(0, 65536), default=32)
def run(start, end, workers):
	global global_start, graph_name_start, sparql_server
	global_start = start
	sparql_server = sparql.SPARQLServer(sparql_uri)

	redis_fn = redislite.Redis().db
	if workers:
		worker_pool = ProcessPoolExecutor(max_workers = workers)

	graph_name_start = query_one('x', "{kbdbg:latest kbdbg:is ?x}")
	identification = fix_up_identification(graph_name_start)
	graph_list_position = graph_name_start
	step_to_submit = -1
	while True:
		step_graph_positions = list(query(('to','item'),
			""" {{    
			SELECT ?to WHERE {
			SERVICE bd:alp { 
			<"""+graph_name_start+"""> rdf:rest ?to. 
			hint:Prior hint:alp.pathExpr true .
			hint:Group hint:alp.lowerBound 0 .
			hint:Group hint:alp.upperBound 100 .
			}}}
			?to rdf:first ?item.
			}"""))
		if len(step_graph_positions) == 0: break
		graph_list_position = step_graph_positions[-1]['to']
		for rrr in step_graph_positions:
			step_graph_uri = rrr['item']
			step_to_submit+=1
			if step_to_submit < start - 1:
				log ("skipping ["+str(step_to_submit) + ']')
				continue
			if step_to_submit > end and end != -1:
				log ("ending")
				break
			args = (identification, step_graph_uri, step_to_submit, redis_fn)
			if not workers:
				work(*args)
			else:
				log('submit ' + '[' + str(step_to_submit) + ']' + ' (queue size: ' + str(len(futures)) + ')' )
				if len(futures) > workers:
					time.sleep(len(futures) - workers)
				fut = worker_pool.submit(work, *args)
				fut.step = step_to_submit
				futures.append(fut)
				log('submitted ' )
				check_futures()
			log('loop ' )

	if workers:
		worker_pool.shutdown()
	check_futures()



def work(identification, graph_name, step_to_do, redis_fn):
	global redis_connection, strict_redis_connection, sparql_server, step, step_graph
	step = step_to_do

	log('work ' + '[' + str(step) + ']')

	#for Collections
	step_graph = ConjunctiveGraph(sparqlstore.SPARQLStore(sparql_uri), graph_name)

	sparql_server = sparql.SPARQLServer(sparql_uri)
	redis_connection = redislite.Redis(redis_fn)
	strict_redis_connection = redislite.StrictRedis(redis_fn)

	gv_output_file_name = identification + '_' + str(step).zfill(7) + '.gv'

	frames_list = list(query(('frame','parent', 'is_for_rule'),
	"""WHERE
	{
		{
			SELECT ?frame WHERE
			{
				GRAPH ?g {
					?frame rdf:type kbdbg:frame
				}.""" + step_magic() + """
				FILTER NOT EXISTS {
					GRAPH ?gg 
					{
						?frame kbdbg:is_finished true
					}.""" + step_magic('gg') + """
				}
			}
		}
		OPTIONAL {?frame kbdbg:has_parent ?parent}.
		?frame kbdbg:is_for_rule ?is_for_rule. 
	}"""))
	if len(frames_list) == 0:
		log('no frames.' + '[' + str(step) + ']')
		put_last_bindings(step, [])
		return

	if (step == global_start - 1):
		gv_output_file_name = 'dummy'
	try:
		os.unlink(gv_output_file_name)
	except FileNotFoundError:
		pass

	gv_output_file = open(gv_output_file_name, 'w')
	e = Emitter(gv_output_file, step)
	e.gv("digraph frame"+str(step) + "{  ")#splines=ortho;#gv("pack=true")
	e.generate_gv_image(frames_list)
	e.gv("}")
	log ('}..' + '[' + str(step) + ']')
	gv_output_file.close()

	if (step == global_start - 1):
		return

	log('convert..' + '[' + str(step) + ']')
	#cmd, args = subprocess.check_output, ("convert", '-regard-warnings', "-extent", '6000x3000',  gv_output_file_name, '-gravity', 'NorthWest', '-background', 'white', gv_output_file_name + '.svg')
	cmd, args = subprocess.check_output, ("dot", '-Tsvg',  gv_output_file_name, '-O')
	try:
		r = cmd(args, stderr=subprocess.STDOUT)
		if r != b"":
			raise RuntimeError('[' + str(step) + '] ' + str(r))
	except subprocess.CalledProcessError as e:
		log ('[' + str(step) + ']' + str(e.output))
	log('convert done.' + '[' + str(step) + ']')

	if len(stats):
		print('stats:')
		for elapsed, func, args, note in stats[:3]:
			print(elapsed,args)
		#stats.clear()

	redis_connection._cleanup()
	strict_redis_connection._cleanup()



def available_cpus():
	return len(os.sched_getaffinity(0))

def check_futures():
	log('check_futures ' + ' (queue size: ' + str(len(futures)) + ')' )
	while True:
		if len(futures) == 0: return
		f = futures[0]
		log('futu ' + '[' + str(f.step) + ']' + ' (queue size: ' + str(len(futures)) + ')' )
		if f.done():
			log('remove ' + '[' + str(f.step) + ']' + ' (queue size: ' + str(len(futures)) + ')' )
			futures.remove(f)
		else:
			return


if __name__ == '__main__':
	run()

#from IPython import embed;embed()

#"""RDR?"""
