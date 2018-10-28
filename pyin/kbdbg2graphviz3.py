#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

here i use complex queries to leave the hard work on the server side, and more importantly,
avoid so many round-trips. This was my first serious use of sparql, what i would do differently now:
avoid using a part of a graph name to store the step id,
save the step id in its own triple: graph has_step step.
However, from the viewpoint of a semantic desktop, it seems that
we should put each triple into its own (uniquely-named) graph a-priori.
Thats the only way to avoid having to remodel your data as soon as you want to for
example just annotate some triple. In RDR sytax, for example: <<:frame7 rdf:type :variable> :comment "seems like a bug introduced in version bla bla>.
or: https://ebiquity.umbc.edu/_file_directory_/papers/178.pdf

Once you have each triple in its own graph, you have to tie them together with more triples:
:graphForTriple7 is_part_of :graphForStep0

and we also need:
:graphForStep0 has_step 0,
must be better than extracting it from the name:)


now for two practical issues: a better triplestore is needed, blazegraph is flaky, especially under
parallel load. Or at least more ram is needed. Or a triplestore on aws.

into this ties a small change, if we avoid running multiple workers in parallel, we should at least
leave the file/convert io to another thread.

"""





import time
import click
import os
import sys
import logging
import urllib.parse
import subprocess
import yattag
import json
import html as html_module
import redislite, redis_collections
from rdflib.namespace import Namespace
from concurrent.futures import ProcessPoolExecutor
from pymantic import sparql
from sortedcontainers import SortedList
from common import shorten, fix_up_identification
from common import pyin_prefixes as prefixes
from collections import defaultdict


sparql_uri = 'http://localhost:9999/blazegraph/sparql'
are_other_graphs_present = False


range_start = '666'
range_end= '666'

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
info = logger.info

default_graph = 'http://kbd.bg/#runs'

arrow_width = 1
border_width = 1


stats = SortedList(key=lambda x: -x[0])



def profile(func, args=(), note=''):
	start = time.time()
	r = func(*args)
	end = time.time()
	stats.add((end - start, func, args, note))
	return r


def query_list(vars, list_uri, **kwargs):
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
	#try:
	rrr= profile(sparql_server.query, (q2,))['results']['bindings']
	#except sparql.SPARQLQueryException as e:
	#	log('exception:')
	#	from IPython import embed;embed()
	#	for k,v in e.items():
	#		log(k)
	#		for l in v.splitlines():
	#			log(l)
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
		raise Exception ("wanted one result, got "+str(l))
	return l[0]



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
current_step = '666'

class Emitter:

	def __init__(s):
		s.output = ''

	def gv(s, text):
		s.output += (text + '\n')

	def comment(s, text):
		s.gv('//'+text)

	def do_frames(s,frames_list):
		info ('frames.. ' + ss)
		#log(str(frames_list))
		root_frame = None
		#current_result = None
		last_frame = None
		log('len(frames_list):'+str(len(frames_list)))
		for i, frame in enumerate(frames_list):
			log('this is frame'+str(i)+':'+str(frame))
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

	def do_bnodes(s,bnodes_list):
		info ('bnodes.. ' + ss)
		for bnode_data in bnodes_list:
			bnode, parent, items_uri  = bnode_data['bnode'], bnode_data['frame'], bnode_data['items']
			bnode_gv_string = s.get_bnode(bnode, parent, items_uri)
			s.gv(gv_escape(bnode) + ' [shape=none, cellborder=2, label=<' + bnode_gv_string+ '>]')
			s.arrow(gv_escape(parent), gv_escape(bnode), color='yellow', weight=100)

	def get_bnode(s,bnode, parent, items_uri):
		try:
			while True:
				string = bnode_strings[bnode]
				if string == 'pending...':
					time.sleep(1)
				else:
					break
		except KeyError:
			info(bnode + ' not found in bnode cache..' + ss)
			bnode_strings[bnode] = 'pending...'
			string = s.get_bnode_string(bnode, parent, items_uri)
			bnode_strings[bnode] = string
		return string

	def get_bnode_string(s, bnode, parent, items_uri):
			log('querying bnode '+bnode + ' ' +ss)
			(doc, tag, text) = yattag.Doc().tagtext()
			with tag("table", border=0, cellspacing=0):
				with tag('tr'):
					with tag('td', border=1):
						text(shorten(bnode))
				items = query_list(('name', 'value'), items_uri,
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
			return doc.getvalue()

	def do_bindings(s, bindings_list):
		info ('bindings...' + ss)
		def arrr(color):
			se = x_endpoint('source')
			te = x_endpoint('target')
			s.arrow(se, te, color=color, weight=weight, binding=True)

		def x_endpoint(x):
			return s.gv_endpoint(
					binding_data[x+'_frame'],
					binding_data[x+'_is_bnode'],
					binding_data[x+'_is_in_head'],
					binding_data[x+'_term_idx'],
					binding_data[x+'_arg_idx'])

		for binding_data in bindings_list:
			binding = binding_data['x']
			weight = 1
			binding_created = relevant(binding_data['stepbinding_created'])
			binding_failed = relevant(binding_data['stepbinding_failed'])
			binding_unbound = relevant(binding_data['stepbinding_unbound'])
			source_uri = binding_data['source']
			target_uri = binding_data['target']
			if binding_data['source_is_bnode'] and binding_data['target_is_bnode']:
				weight = 0
			if (binding_unbound != None) and (binding_failed == None):
				if binding_unbound == current_step:
					s.comment("just unbound binding")
					arrr('orange')
			elif (binding_failed != None) and (binding_unbound == None):
				if binding_failed == current_step:
					s.comment("just failed binding")
					arrr('red')
			elif (binding_failed == None) and (binding_unbound == None):
				s.comment("binding " + binding)
				arrr('green' if (current_step == binding_created) else 'purple' )

	def do_results(s,results_list):
		info ('results..' + '[' + str(current_step) + ']')
		#last_result = root_frame
		for i, result_data in enumerate(results_list):
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
		params = rule
		try:
			while True:
				template = frame_templates[params]
				if template == 'pending...':
					time.sleep(1)
				else:
					break
		except KeyError:
			info(params + ' not found in template cache..' + ss)
			frame_templates[params] = 'pending...'
			info(params + ' set.')
			template = s._get_frame_html_label(rule, isroot)
			frame_templates[params] = template
		return template.replace(frame_name_template_var_name,html_module.escape(shorten(frame['frame'])))

	@staticmethod
	def _get_frame_html_label(rule, isroot):
			rule_data = query_one(('original_head', 'head','head_idx','body','gexists'),
				"""{
				OPTIONAL {<"""+rule+"""> kbdbg:has_original_head ?original_head} 
				OPTIONAL {<"""+rule+"""> kbdbg:has_head ?head}
				OPTIONAL {<"""+rule+"""> kbdbg:has_head_idx ?head_idx}
				OPTIONAL {<"""+rule+"""> kbdbg:has_body ?body}
				}""")
			body_items = list(query_list(('item',), rule_data['body']))
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
						emit_term(tag, text, True, rule_data['head_idx'], rule_data['head'])
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
	args_list = list(query_list(('item',), term_data['args']))
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
	items = list(query_list(('item',), uri))
	emit_terms_by_items( tag, text, items, is_head)


def emit_terms_by_items( tag, text, items, is_head):
	for term_idx, item in enumerate(items):
		emit_term(tag, text, is_head, term_idx, item)


def relevant(event_step):
	"""return None if this thing happened after current step or outside the range of the query,
	otherwise return the step"""
	if event_step == None: return None
	r = int(event_step)
	if r > current_step: return None
	return r

def step_bind(id):
	return """
	  BIND  (STR(?g{id}) AS ?strg{id}).
	  BIND  (STRAFTER(?strg{id}, "_") AS ?step{id}).
	  """.format(id=id)

def step_magic(id=0):
	return step_bind(id)+((("""
	  FILTER (STRSTARTS(?strg{id}, "{graph_name_start}")).""" if are_other_graphs_present else "")+"""
	  FILTER (?step{id} <= "{maxstep}").
	  """ + ("""(FILTER (?step{id} >= "{minstep}").""" if range_start != 0 else ""))
	  .format(id=id, graph_name_start=graphs_name_start,
				maxstep=str(range_end).rjust(10,'0'),
				minstep=str(range_start).rjust(10,'0')
						  ))

def frame_query(id=''):
	return ("""
				GRAPH ?g{id}_created {{
					?{id}frame rdf:type kbdbg:frame
				}}.""" + step_magic(id+'_created') + """
				OPTIONAL {{
					GRAPH ?g{id}_finished {{
						?{id}frame kbdbg:is_finished true
					}}.""" +
			step_bind(id+'_finished') +
			"""
				}}.
			""").format(id=id)

frames_done_count = 0


def work(identification, graph_name, _range_start, _range_end, redis_fn):
	global redis_connection, strict_redis_connection, sparql_server, current_step, range_start, range_end, ss, just_unbound_bindings,frames_done_count,frame_templates,bnode_strings
	range_start, range_end = _range_start, _range_end
	sparql_server = sparql.SPARQLServer(sparql_uri)
	redis_connection = redislite.Redis(redis_fn)
	strict_redis_connection = redislite.StrictRedis(redis_fn)
	frame_templates = redis_collections.Dict(key='frames',redis=strict_redis_connection,writeback=True)
	bnode_strings = redis_collections.Dict(key='bnodes',redis=strict_redis_connection,writeback=True)

	raw = defaultdict(list)
	#todo limit queries with range_start, then uncomment this
	#if range_start != 0:
	#	raw = redis_load('checkpoint'+str(range_start - 1))

	raw['frames'] += list(query(('frame','parent', 'is_for_rule', 'step_finished', 'step_created'),
	"""WHERE
	{
		"""+frame_query()+"""
		OPTIONAL {?frame kbdbg:has_parent ?parent}.
		?frame kbdbg:is_for_rule ?is_for_rule. 
	}"""))

	raw['bnodes'] += list(query(('bnode','frame','items','step_created','step_finished'),
		"""WHERE
		{
		?bnode kbdbg:has_items ?items.
		?bnode kbdbg:has_parent ?frame.
		GRAPH ?g_created {?bnode rdf:type kbdbg:bnode}.
		"""+step_magic('_created')+"""
		OPTIONAL {
			GRAPH ?g_finished{?frame kbdbg:is_finished true}.
			"""+step_bind('_finished')+"""
		}
		}"""))

	raw['results'] += list(query(('uri','value', 'step_unbound'),
			"""WHERE {GRAPH ?g_created 
			{
				?uri rdf:type kbdbg:result.
				?uri rdf:value ?value.
			}."""+step_magic('_created')+"""
			OPTIONAL {GRAPH ?g_unbound {?uri kbdbg:was_ubound true}.}.""" +
			step_bind('_unbound')+'}'))

	raw['bindings'] += list(
			query(
				('x','source','target','source_frame','target_frame','source_is_bnode','target_is_bnode',
				 'source_term_idx','target_term_idx','source_is_in_head','target_is_in_head',
				'source_arg_idx','target_arg_idx','stepbinding_unbound','stepbinding_failed', 'stepbinding_created')
		,"""WHERE 
		{
		GRAPH ?gbinding_created {?x rdf:type kbdbg:binding.}.
		"""+step_magic('binding_created')+"""
		OPTIONAL {GRAPH ?gbinding_unbound {?x kbdbg:was_unbound true}.
		"""+step_bind('binding_unbound')+"""
		}.
		OPTIONAL {GRAPH ?gbinding_failed  {?x kbdbg:failed true}.
		"""+step_bind('binding_failed')+"""
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
		}"""))

	current_step = range_end
	redis_save('checkpoint'+str(range_end), filter_out_irrelevant_stuff(raw))
	current_step = '666'

	last_bindings = raw['bindings'][:]
	for i in range(range_start, range_end + 1):
		current_step = i
		ss = '[' + str(current_step) + ']'
		info('work ' + ss)
		state = filter_out_irrelevant_stuff(raw)
		if len(state['frames']) == 0:
			info('no frames.' + ss)
			continue

		#wont work with euler-style steps
		#if last_bindings == state['bindings']:
		#	return 'end'

		#todo make emitter save data to output, not to file
		e = Emitter()
		e.gv("digraph frame"+str(current_step) + "{  ")#splines=ortho;#gv("pack=true")
		e.do_frames(state['frames'])
		e.do_bnodes(state['bnodes'])
		e.do_results(state['results'])
		e.do_bindings(state['bindings'])
		e.gv("}")
		info ('}..' + ss)

		args = (ss, identification + '_' + str(current_step).zfill(7) + '.gv', e.output)
		while len(graphviz_futures) > 10000:
			info('sleeping')
			time.sleep(10)
			check_futures2(graphviz_futures)

		graphviz_futures.append(graphviz_pool.submit(output, *args))
		check_futures2(graphviz_futures)

	#print_stats()
	redis_connection._cleanup()
	strict_redis_connection._cleanup()

def output(ss, gv_output_file_name, output):
		try:
			os.unlink(gv_output_file_name)
		except FileNotFoundError:
			pass
		gv_output_file = open(gv_output_file_name, 'w')
		gv_output_file.write(output)
		gv_output_file.close()
		info('convert..' + ss)
		cmd, args = subprocess.check_output, ("dot", '-Tsvg',  gv_output_file_name, '-O')
		try:
			r = cmd(args, stderr=subprocess.STDOUT)
			if r != b"":
				raise RuntimeError(ss + str(r))
		except subprocess.CalledProcessError as e:
			info (ss + str(e.output))
			raise e
		info('convert done.' + ss)
		frames_done_count = redis_connection.incr('frames_done_count')
		elapsed = time.perf_counter() - start_time
		secs_per_frame = str(elapsed/frames_done_count)
		info('done ' + str(frames_done_count) + ' frames in ' + str(elapsed) + 'secs (' + secs_per_frame + 'secs/frame')

def only_existing(range_list):
	r = []
	for b in range_list:
		step_finished = relevant(b['step_finished'])
		if step_finished == None:
			step_created = relevant(b['step_created'])
			if step_created != None:
				r.append(b)
	return r

def filter_out_irrelevant_stuff(raw):
	result = defaultdict(list)
	result['frames'] = only_existing(raw['frames'])
	result['bnodes'] = only_existing(raw['bnodes'])
	for r in raw['results']:
		step_unbound = relevant(r['step_unbound'])
		if step_unbound == None:
			result['results'].append(r)
	for binding_data in raw['bindings']:
		binding_created = relevant(binding_data['stepbinding_created'])
		if binding_created == None:	continue
		binding_failed = relevant(binding_data['stepbinding_failed'])
		binding_unbound = relevant(binding_data['stepbinding_unbound'])
		if (binding_failed != None and binding_failed < current_step or
			binding_unbound != None and binding_unbound < current_step):
			continue
		result['bindings'].append(binding_data)
	return result

def print_stats():
	if len(stats):
		info('longest queries:')
		for elapsed, func, args, note in stats[:3]:
			info(str(elapsed)+':')
			for l in args[0].splitlines():
				info(l)

def available_cpus():
	return len(os.sched_getaffinity(0))

def check_futures():
	return check_futures2(futures, do_log=True)

def check_futures2(futures, do_log=False):
	if do_log: log('check_futures ' + ' (queue size: ' + str(len(futures)) + ')' )
	while True:
		if len(futures) == 0: return
		f = futures[0]
		if do_log: log('futu ' + '[' + str(f.step) + ']' + ' (queue size: ' + str(len(futures)) + ')' )
		f.result()
		if f.done():
			if do_log: log('remove ' + '[' + str(f.step) + ']' + ' (queue size: ' + str(len(futures)) + ')' )
			futures.remove(f)
			if f.result() == 'end':
				info ('found the end')
				return 'end'
		else:
			return

def redis_load(key):
	return json.loads(redis_connection.blpop([key])[1])

def redis_save(key, value):
	redis_connection.lpush(key, json.dumps(value))


secs_per_frame = 30
futures = []
graphviz_futures = []
global_start = None
graphviz_pool= 666

@click.command()
@click.option('--quiet', type=click.BOOL, default=False)
@click.option('--start', type=click.IntRange(0, None), default=0)
@click.option('--end', type=click.IntRange(-1, None), default=-1)
@click.option('--workers', type=click.IntRange(0, 65536), default=(os.cpu_count() or 1))
def run(quiet, start, end, workers):
	global global_start, graphs_name_start, sparql_server,start_time,graphviz_pool
	if start:
		raise Exception("--start functionality needs updating")
	global_start = start
	if quiet:
		logger.setLevel(logging.INFO)
	sparql_server = sparql.SPARQLServer(sparql_uri)
	redis_fn = redislite.Redis().db
	info('redis is '+redis_fn)
	if workers:
		worker_pool = ProcessPoolExecutor(max_workers = workers)
	graphviz_pool = ProcessPoolExecutor(max_workers = 128)
	graphs_name_start = query_one('x', "{kbdbg:latest kbdbg:is ?x}")
	identification0 = query_one('y', "{<"+graphs_name_start+"> kbdbg:has_run_identification ?y}")
	path='runs/'+fix_up_identification(identification0)
	info ('output path:'+path)
	os.system('mkdir -p '+path)
	identification = path+'/'+fix_up_identification(graphs_name_start)
	graph_list_position = graphs_name_start
	step_to_submit = -1
	done = False
	range_start = None
	start_time = time.perf_counter()
	range_size = 200000
	while not done:
		step_to_submit+=1
		if step_to_submit < start - 1:
			info ("skipping ["+str(step_to_submit) + ']')
			continue
		if range_start == None:
			range_start = step_to_submit
		range_end = step_to_submit
		if range_end - range_start == range_size or (range_end >= end and end != -1):
			args = (identification, 'step_graph_uri', range_start, range_end, redis_fn)
			if not workers:
				work(*args)
			else:
				if check_futures() == 'end':
					info ("ending")
					done = True
					break
				while len(futures) > workers+1:
					info('sleeping')
					time.sleep(10)
					if check_futures() == 'end':
						info ("ending")
						done = True
						break
				info('submit ' + str(range_start)+'-'+str(range_end) + ' (queue size: ' + str(len(futures)) + ')' )
				fut = worker_pool.submit(work, *args)
				fut.step = step_to_submit
				futures.append(fut)
				log('submitted ' )
				time.sleep(secs_per_frame)
				if check_futures() == 'end':
					info ("ending")
					done = True
					break
			range_start = range_end + 1
			range_size = range_size * 5
			if range_size >= 100000:
				range_size = 100000

		if range_start > end and end != -1:
			info ("ending")
			done = True
			break
		log('loop' +str(step_to_submit))
	if workers:
		while len(futures) != 0:
			check_futures()
			info('waiting for workers to end')
			time.sleep(10)
		worker_pool.shutdown()
		check_futures()

	while len(graphviz_futures) != 0:
		check_futures2(graphviz_futures)
		info('waiting for graphviz workers to end')
		time.sleep(2)
	graphviz_pool.shutdown()

if __name__ == '__main__':
	run()

#from IPython import embed;embed()

#"""RDR?"""

#cmd, args = subprocess.check_output, ("convert", '-regard-warnings', "-extent", '6000x3000',  gv_output_file_name, '-gravity', 'NorthWest', '-background', 'white', gv_output_file_name + '.svg')


	#if step != 0 and step != global_start - 1:
	#	just_unbound_bindings = json.loads(redis_connection.blpop([step - 1])[1])
	#redis_connection.lpush(step, json.dumps(new_just_unbound_bindings))


			#false = rdflib.Literal(False)
			#if g.value(result_uri, kbdbg.was_unbound, default = false) == false:
				#current_result = result_node
				#arrow_width = 2
			#else:
				#arrow_width = 1
			#if last_result:
			#	s.arrow(last_result, result_node, color='yellow', weight=100)
			#last_result = result_node




# https://openproceedings.org/2016/conf/edbt/paper-168.pdf
