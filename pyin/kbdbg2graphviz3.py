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


def fetch_list(vars, list_uri, **kwargs):
	return query(vars, 'WHERE { ' + list_subquery(list_uri, **kwargs) + '}')

def list_subquery(start, additional='', upper_bound=2147483647):
	return """
						{    
							SELECT ?cell WHERE 
							{
								SERVICE bd:alp 
								{ 
									<""" + start + """> rdf:rest ?cell. 
									hint:Prior hint:alp.pathExpr true .
									hint:Group hint:alp.lowerBound 0 .
									hint:Group hint:alp.upperBound """+str(upper_bound)+""" .
								}
							}
						}
						?cell rdf:first ?item.
	""" + additional


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

		bnode_list = list(query(('bnode','frame', 'items'),
		"""WHERE
		{
		?bnode kbdbg:has_items ?items.
		?bnode kbdbg:has_parent ?frame.
		GRAPH ?g0 {?bnode rdf:type kbdbg:bnode}.
		"""+step_magic(0)+"""
		GRAPH ?g1 {?frame rdf:type kbdbg:frame}.
		"""+step_magic(1)+"""
		FILTER NOT EXISTS
        {
			GRAPH ?g2{?frame kbdbg:is_finished true}.
			"""+step_magic(2)+"""
		}
		}"""))

		for bnode_data in bnode_list:
			bnode, parent, items_uri  = bnode_data['bnode'],bnode_data['frame'],bnode_data['items']
			(doc, tag, text) = yattag.Doc().tagtext()
			with tag("table", border=0, cellspacing=0):
				with tag('tr'):
					with tag('td', border=1):
						text(shorten(bnode))
				items = fetch_list(('name','value'), items_uri,
					additional="""?item kbdbg:has_name ?name.
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
		for binding_data in query(
				('x','source','target','source_frame','target_frame','source_is_bnode','target_is_bnode',
				 'source_term_idx','target_term_idx','source_is_in_head','target_is_in_head',
				'source_arg_idx','target_arg_idx','unbound','failed')

		,"""WHERE 
		{
		GRAPH ?gbinding {?x rdf:type kbdbg:binding.}.
		"""+step_magic('binding ')+"""
		OPTIONAL {GRAPH ?gbinding_unbound {?x kbdbg:was_unbound ?unbound}.
		"""+step_magic('binding_unbound ')+"""
		}.
		OPTIONAL {GRAPH ?gbinding_failed  {?x kbdbg:failed ?failed}
		"""+step_magic('binding_failed ')+"""
		}.
		?x kbdbg:has_source ?source.
		?x kbdbg:has_target ?target.
		?source kbdbg:has_frame ?source_frame.
		?target kbdbg:has_frame ?target_frame.
		OPTIONAL {?source kbdbg:is_bnode ?source_is_bnode.}.
		OPTIONAL {?target kbdbg:is_bnode ?target_is_bnode.}.
		?source kbdbg:term_idx ?source_term_idx.
		?target kbdbg:term_idx ?target_term_idx.
		OPTIONAL {?source kbdbg:is_in_head ?source_is_in_head.}.
		OPTIONAL {?target kbdbg:is_in_head ?target_is_in_head.}.
		OPTIONAL {?source kbdbg:arg_idx ?source_arg_idx.}.
		OPTIONAL {?target kbdbg:arg_idx ?target_arg_idx.}.
		}"""):
			binding = binding_data['x']
			weight = 1
			source_uri = binding_data['source']
			target_uri = binding_data['target']
			if binding_data['source_is_bnode'] and binding_data['target_is_bnode']:
				weight = 0
			source_endpoint = s.gv_endpoint(
				binding_data['source_frame'],
				binding_data['source_is_bnode'],
				binding_data['source_is_in_head'],
				binding_data['source_term_idx'],
				binding_data['source_arg_idx'])
			target_endpoint = s.gv_endpoint(
				binding_data['target_frame'],
				binding_data['target_is_bnode'],
				binding_data['target_is_in_head'],
				binding_data['target_term_idx'],
				binding_data['target_arg_idx'])
			if binding_data['unbound']:
				if binding in last_bindings:
					s.comment("just unbound binding")
					s.arrow(source_endpoint, target_endpoint, color='orange', weight=weight, binding=True)
				continue
			if binding_data['failed']:
				s.comment("just failed binding")
				s.arrow(source_endpoint, target_endpoint, color='red', weight=weight, binding=True)
				continue
			s.comment("binding " + binding)
			s.arrow(source_endpoint, target_endpoint,
				  color=('black' if (binding in last_bindings) else 'purple' ), weight=weight, binding=True)
			new_last_bindings.append(binding)

		put_last_bindings(s.step, new_last_bindings)
		del new_last_bindings

		log ('results..' + '[' + str(s.step) + ']')
		#last_result = root_frame
		for i, result_data in enumerate(query(('uri','value'),
			"""WHERE {GRAPH ?g0 
			{
				?uri rdf:type kbdbg:result.
				FILTER NOT EXISTS {?uri kbdbg:was_ubound true}.
				?uri rdf:value ?value.
			}."""+step_magic(0)+'}')):
			result_uri = result_data['uri']
			value = result_data['value']
			result_node = gv_escape(result_uri)
			r = result_node + ' [cellborder=2, shape=none, label=<'
			(doc, tag, text) = yattag.Doc().tagtext()
			with tag("table"):
				with tag('tr'):
					with tag("td"):
						text('RESULT'+str(i) +' ')
					s.emit_terms(tag, text, value, 'result')
			r += doc.getvalue()+ '>]'
			s.gv(r)
			#false = rdflib.Literal(False)
			#if g.value(result_uri, kbdbg.was_unbound, default = false) == false:
				#current_result = result_node
				#arrow_width = 2
			#else:
				#arrow_width = 1
			#if last_result:
			#	s.arrow(last_result, result_node, color='yellow', weight=100)
			#last_result = result_node

	def gv_endpoint(s, frame, is_bnode, is_in_head, term_idx, arg_idx):
		if is_bnode:
			return gv_escape(frame) + ":" + gv_escape(term_idx)
		else:
			if arg_idx == None:
				return gv_escape(frame)
			port = port_name(is_in_head, term_idx, arg_idx)
			return gv_escape(frame) + ":" +port

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
			body_items = list(fetch_list(('item',), rule_data['body']))
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
	args_list = list(fetch_list(('item',), term_data['args']))
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
	items = list(fetch_list(('item',),uri))
	emit_terms_by_items( tag, text, items, is_head)


def emit_terms_by_items( tag, text, items, is_head):
	for term_idx, item in enumerate(items):
		emit_term(tag, text, is_head, term_idx, item)


def step_magic(id=0):
	return """
	  BIND  (STR(?g{id}) AS ?strg{id}).
	  FILTER (STRSTARTS(?strg{id}, "{graph_name_start}")).
	  BIND  (STRAFTER(?strg{id}, "_") AS ?step{id}).
	  FILTER (?step{id} < "{maxstep}").
	  """.format(id=id, graph_name_start=graphs_name_start,
				 maxstep=str(step+1).rjust(10,'0'))


futures = []
global_start = None

@click.command()
@click.option('--start', type=click.IntRange(0, None), default=0)
@click.option('--end', type=click.IntRange(-1, None), default=-1)
@click.option('--workers', type=click.IntRange(0, 65536), default=32)
def run(start, end, workers):
	global global_start, graphs_name_start, sparql_server
	global_start = start
	sparql_server = sparql.SPARQLServer(sparql_uri)
	redis_fn = redislite.Redis().db
	if workers:
		worker_pool = ProcessPoolExecutor(max_workers = workers)
	graphs_name_start = query_one('x', "{kbdbg:latest kbdbg:is ?x}")
	identification = fix_up_identification(graphs_name_start)
	graph_list_position = graphs_name_start
	step_to_submit = -1
	done = False
	while not done:
		step_list_data = list(fetch_list(('cell','item'),graph_list_position, upper_bound=50))
		if len(step_list_data ) == 0: break
		graph_list_position = step_list_data [-1]['cell']
		for rrr in step_list_data[:-1] :
			step_graph_uri = rrr['item']
			step_to_submit+=1
			if step_to_submit < start - 1:
				log ("skipping ["+str(step_to_submit) + ']')
				continue
			if step_to_submit > end and end != -1:
				log ("ending")
				done = True
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

def frame_query(id=''):
	return ("""
				GRAPH ?g{id}1 {{
					?{id}frame rdf:type kbdbg:frame
				}}.""" + step_magic(id+'1') + """
				FILTER NOT EXISTS {{
					GRAPH ?g{id}2 
					{{
						?{id}frame kbdbg:is_finished true
					}}.""" + step_magic(id+'2') + """
				}}.
			""").format(id=id)

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
		{SELECT ?frame WHERE{"""+frame_query()+"""}}
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
