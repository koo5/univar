#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import ujson
import time
import pickle
import redislite, redis_collections
import click
from common import shorten
import html as html_module
import os
import sys
import logging
import urllib.parse
import subprocess
import rdflib
from rdflib import Graph
from rdflib.namespace import Namespace
from rdflib.namespace import RDF
from non_retarded_collection import Collection
from ordered_rdflib_store import OrderedAndIndexedStore
import yattag
from concurrent.futures import as_completed, ProcessPoolExecutor
from concurrent.futures._base import TimeoutError

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


kbdbg = Namespace('http://kbd.bg/#')

gv_handler = logging.StreamHandler(sys.stdout)
gv_handler.setLevel(logging.DEBUG)
gv_handler.setFormatter(logging.Formatter('%(message)s'))

logger=logging.getLogger("kbdbg")
logger.addHandler(gv_handler)

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(asctime)s %(message)s.'))
logger.addHandler(console)
logger.debug("hi")
log=logger.debug

arrow_width = 1
border_width = 1


def tell_if_is_last_element(x):
	for i, j in enumerate(x):
		yield j, (i == (len(x) - 1))

def value(g, subject=None, predicate=rdflib.term.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#value'), object=None, default=None, any=False):
	return g.value(subject, predicate, object, default, any)

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

	def __init__(s, g, gv_output_file, step):
		s.g, s.gv_output_file = g, gv_output_file
		s.step = step
		s.frame_templates = redis_collections.Dict(redis=strict_redis_connection)

	def gv(s, text):
		s.gv_output_file.write(text + '\n')

	def comment(s, text):
		s.gv('//'+text)

	def generate_gv_image(s):
		g = s.g

		s.gv("digraph frame"+str(s.step) + "{  ")#splines=ortho;
		#gv("pack=true")
		log ('frames.. ' + '[' + str(s.step) + ']')
		root_frame = None
		#current_result = None
		rrr = list(g.subjects(RDF.type, kbdbg.frame))
		last_frame = None
		for i, frame in enumerate(rrr):
			if g.value(frame, kbdbg.is_finished, default=False):
				continue
			f, text = s.get_frame_gv(i, frame)
			s.gv(f + text)
			#if last_frame:
			#	arrow(last_frame, f, color='yellow', weight=100)
			parent = g.value(frame, kbdbg.has_parent)
			if parent:# and not g.value(parent, kbdbg.is_finished, default=False):
				s.arrow(gv_escape(parent), f, color='yellow', weight=10000000)
			else:
				root_frame = f
			last_frame = f
			#if i == 0 and current_result:
			#	arrow(result_node, f)
		log ('bnodes.. ' + '[' + str(s.step) + ']')
		if s.step == 51:
			print ('eeee')
		for bnode in g.subjects(RDF.type, kbdbg.bnode):
			parent = g.value(bnode, kbdbg.has_parent)
			if g.value(parent, kbdbg.is_finished, default=False):
				continue
			(doc, tag, text) = yattag.Doc().tagtext()
			with tag("table", border=0, cellspacing=0):
				#for i in Collection(g, bnode):
				with tag('tr'):
					with tag('td', border=1):
						text((shorten(bnode.n3())))
				items = None
				for i in g.objects(bnode, kbdbg.has_items):
					items = i # find the latest ones
				if not items:
					continue
				for i in Collection(g,items):
					with tag('tr'):
						name = g.value(i, kbdbg.has_name)
						pn = gv_escape(name)
						with tag("td", border=1, port=pn):
							text(shorten(name))
							text(' = ')
							text(shorten(g.value(i, kbdbg.has_value)))
						#with tag("td", border=1):
						#	text(shorten(g.value(i, kbdbg.has_value)))
			s.gv(gv_escape(bnode) + ' [shape=none, cellborder=2, label=<' + doc.getvalue()+ '>]')
			s.arrow(gv_escape(parent), gv_escape(bnode), color='yellow', weight=100)

		last_bindings = get_last_bindings(s.step)
		log ('bindings...' + '[' + str(s.step) + ']')

		new_last_bindings = []
		for binding in g.subjects(RDF.type, kbdbg.binding):
			weight = 1
			source_uri = g.value(binding, kbdbg.has_source)
			target_uri = g.value(binding, kbdbg.has_target)
			if g.value(source_uri, kbdbg.is_bnode, default=False) and g.value(target_uri, kbdbg.is_bnode, default=False):
				weight = 0
			if g.value(binding, kbdbg.was_unbound) == rdflib.Literal(True):
				if (binding.n3() in last_bindings):
					s.comment("just unbound binding")
					s.arrow(s.gv_endpoint(source_uri), s.gv_endpoint(target_uri), color='orange', weight=weight, binding=True)
				continue
			if g.value(binding, kbdbg.failed) == rdflib.Literal(True):
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
		for i, result_uri in enumerate(g.subjects(RDF.type, kbdbg.result)):
			result_node = gv_escape(result_uri)
			r = result_node + ' [cellborder=2, shape=none, label=<'
			(doc, tag, text) = yattag.Doc().tagtext()
			with tag("table"):
				with tag('tr'):
					with tag("td"):
						text('RESULT'+str(i) +' ')
					emit_terms(s.g, tag, text, s.g.value(result_uri, RDF.value), 'result')
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
		s.gv("}")
		log ('}..' + '[' + str(s.step) + ']')

	def gv_endpoint(s, uri):
		g=s.g
		if(g.value(uri, kbdbg.is_bnode, default=False)):
			term_idx = g.value(uri, kbdbg.term_idx, default=' $\=st #-* -')
			port = gv_escape(term_idx)
			#if port == 'gv0121_y': #gv01080049_l1':
			#	print('x')
			return gv_escape(str(g.value(uri, kbdbg.has_frame))) + ":" + port
		else:
			x = g.value(uri, kbdbg.is_in_head, default=False)
			is_in_head = (x == rdflib.Literal(True))
			term_idx = g.value(uri, kbdbg.term_idx, default=0)
			arg_idx  = g.value(uri, kbdbg.arg_idx, None)
			if arg_idx == None:
				return gv_escape(str(g.value(uri, kbdbg.has_frame)))
			port = port_name(is_in_head, term_idx, arg_idx)
			return gv_escape(str(g.value(uri, kbdbg.has_frame))) + ":" +port

	def get_frame_gv(s, i, frame):
		r = ' [shape=none, margin=0, '
		isroot = False
		if not s.g.value(frame, kbdbg.has_parent):
			r += 'root=true, pin=true, pos="1000,100!", margin="10,0.055" , '#40
			isroot = True
		return gv_escape(frame), r + ' label=<' + s.get_frame_html_label(frame, isroot) + ">]"


	def get_frame_html_label(s, frame, isroot):
		rule = s.g.value(frame, kbdbg.is_for_rule)
		params = rule, isroot
		try:
			template = s.frame_templates[params]
		except KeyError:
			template = s._get_frame_html_label(s.g, *params)
			s.frame_templates[params] = template
		return template.replace(frame_name_template_var_name,html_module.escape(shorten(frame.n3())))

	@staticmethod
	def _get_frame_html_label(g, rule, isroot):

			doc, tag, text = yattag.Doc().tagtext()

			with tag("table", border=1, cellborder=0, cellpadding=0, cellspacing=0):
				with tag("tr"):
					with tag('td', border=border_width):
						if isroot:
							text('QUERY:')
						text(frame_name_template_var_name)
					with tag("td", border=border_width):
						text("{")
					emit_terms(g, tag, text, g.value(rule, kbdbg.has_original_head), True)
					with tag("td", border=border_width):
						text("} <= {")

					body_items_list_name = g.value(rule, kbdbg.has_body)
					if body_items_list_name:
						body_items_collection = Collection(g, body_items_list_name)
						term_idx = 0
						for body_item in body_items_collection:
							emit_term(g, tag, text, False, term_idx, body_item)
							term_idx += 1
					with tag("td", border=border_width):
						text('}')
			#todo print a table of variables, because showing bindings directly between args of triples is misleading? is it?
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

def emit_term(g, tag, text, is_in_head, term_idx, term):
	pred = g.value(term, kbdbg.has_pred)
	args_collection = Collection(g, g.value(term, kbdbg.has_args))
	if len(args_collection) == 2:
		def arrrr(arg_idx):
			with tag('td', port=port_name(is_in_head, term_idx, arg_idx), border=border_width):
				text(' ' + shorten(args_collection[arg_idx]) + ' ')
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

def emit_terms(g, tag, text, uri, is_head):
	items = Collection(g, uri)
	for term_idx, item in enumerate(items):
		emit_term(g, tag, text, is_head, term_idx, item)


def available_cpus():
	return len(os.sched_getaffinity(0))

futures = []
global_start = None

@click.command()
@click.option('--start', type=click.IntRange(0, None), default=0)
@click.option('--end', type=click.IntRange(-1, None), default=-1)
@click.option('--no-parallel', default=False, type=click.BOOL)
@click.option('--graphviz-workers', type=click.IntRange(0, 65536), default=8)
@click.option('--workers', type=click.IntRange(0, 65536), default=32)
@click.argument('input_file_name', type=click.Path(exists=True), default = 'kbdbg.n3')

def run(start, end, no_parallel, graphviz_workers, workers, input_file_name):
	global global_start
	global_start = start
	input_file = open(input_file_name)
	lines = []
	#os.system("rm -f kbdbg"+fn+'\\.*')

	if no_parallel:
		graphviz_workers = 0
	if graphviz_workers == -1:
		graphviz_workers = available_cpus()
	if graphviz_workers == None:
		graphviz_workers = 4
	if graphviz_workers == 0:
		no_parallel = True

	#graphviz_pool = ProcessPoolExecutor(max_workers = graphviz_workers)
	#worker_pool = ThreadPoolExecutor(max_workers = workers)
	worker_pool = ProcessPoolExecutor(max_workers = workers)

	g = Graph(OrderedAndIndexedStore())
	redis_fn = redislite.Redis().db

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
		if step < start - 1:
			log ("skipping ["+str(step) + ']')
			continue
		if step > end and end != -1:
			log ("ending")
			break

		log('parse ' + '[' + str(step) + ']')
		g.parse(data="".join(prefixes+lines), format='n3')
		lines = []
		log('pickle ' + '[' + str(step) + ']')
		pickled_graph = pickle.dumps(g)
		#pickled_graph = ujson.dumps(g)
		args = (pickled_graph, input_file_name, step, no_parallel, redis_fn)
		if no_parallel:
			work(*args)
		else:
			log('submit ' + '[' + str(step) + ']' + ' (queue size: ' + str(len(futures)) + ')' )
			if len(futures) > workers:
				time.sleep(len(futures) - workers)
			fut = worker_pool.submit(work, *args)
			fut.step = step
			futures.append(fut)
			log('submitted ' )
			check_futures()
		log('loop ' )

	worker_pool.shutdown()
	#graphviz_pool.shutdown()
	check_futures()

def check_futures():
	log('check_futures ' + ' (queue size: ' + str(len(futures)) + ')' )
	while True:
		if len(futures) == 0: return
		f = futures[0]
		log('futu ' + '[' + str(f.step) + ']' + ' (queue size: ' + str(len(futures)) + ')' )
		f.result()
		if f.done():
			log('remove ' + '[' + str(f.step) + ']' + ' (queue size: ' + str(len(futures)) + ')' )
			futures.remove(f)
		else:
			return


redis_connection = None
strict_redis_connection = None


def work(serialized_graph, input_file_name, step, no_parallel, redis_fn):
	global redis_connection, strict_redis_connection
	strict_redis_connection = redis_fn

	log('work ' + '[' + str(step) + ']')

	redis_connection = redislite.Redis(redis_fn)
	strict_redis_connection = redislite.StrictRedis(redis_fn)

	gv_output_file_name = input_file_name + '_' + str(step).zfill(5) + '.gv'

	log('loads ' + '[' + str(step) + ']')

	g = pickle.loads(serialized_graph)
	#g = Graph(OrderedAndIndexedStore())
	#for i in ujson.loads(serialized_graph):
	#	g.add(i)

	#log('work' + str(id(g)) + ' ' + str(id(g.store)) + ' ' + str(id(g.store.indexes))  + ' ' + str(id(g.store.indexes['ttft']))  + ' ' + str(id(g.store.indexes['ttft'][rdflib.URIRef('http://kbd.bg/Rule1')])))
	g.store.locked = True
	if list(g.subjects(RDF.type, kbdbg.frame)) == []:
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
	e = Emitter(g, gv_output_file, step)
	e.generate_gv_image()
	gv_output_file.close()

	if (step == global_start - 1):
		return

	log('convert..' + '[' + str(step) + ']')
	#cmd, args = subprocess.check_output, ("convert", '-regard-warnings', "-extent", '6000x3000',  gv_output_file_name, '-gravity', 'NorthWest', '-background', 'white', gv_output_file_name + '.svg')
	cmd, args = subprocess.check_output, ("dot", '-Tsvg',  gv_output_file_name, '-O')
	if True:
		try:
			r = cmd(args, stderr=subprocess.STDOUT)
			if r != b"":
				raise RuntimeError('[' + str(step) + '] ' + str(r))
		except subprocess.CalledProcessError as e:
			log ('[' + str(step) + ']' + e.output)
		log('convert done.' + '[' + str(step) + ']')
	else:
		def do_or_die(args):
			r = cmd(args, stderr=subprocess.STDOUT)
			if r != b"":
				log (r)
				raise RuntimeError(r)
				#exit()
		futures.append(graphviz_pool.submit(do_or_die, args))

	redis_connection._cleanup()
	strict_redis_connection._cleanup()


#from IPython import embed;embed()





if __name__ == '__main__':
	run()
