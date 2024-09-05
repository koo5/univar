#!/usr/bin/env python3


from pymantic import sparql
from concurrent.futures import ThreadPoolExecutor
import pyin
from pyin import *
import rdflib
import click
import common

server, this = None, None

default_graph = '<http://kbd.bg/#runs>'
pyin.default_graph = default_graph


@click.command()
@click.argument('kb', type=click.File('rb'))
@click.argument('goal', type=click.File('rb'))
@click.option('--nokbdbg', default=False)
@click.option('--nolog', default=False, type=bool)
@click.option('--visualize', default=False)
@click.option('--sparql_uri', default='', help='for example http://localhost:9999/blazegraph/sparql')
@click.option('--identification', default="")
@click.option('--base', default="")
def query_from_files(kb, goal, nokbdbg, nolog, visualize, sparql_uri, identification, base):
	global server, this

	pyin.kbdbg_file_name, pyin._rules_file_name, pyin.rules_jsonld_file_name, identification, base, this, runs_path = set_up(identification, base)
	pyin.this = this
	pyin.nolog = nolog
	common.nolog = nolog
	pyin.init_logging()
	common.log = pyin.log

	if sparql_uri != '':
		pyin.pool = ThreadPoolExecutor()#max_workers = , thread_name_prefix='sparql_updater'
		server = sparql.SPARQLServer(sparql_uri)
		server.update("""CLEAR GRAPHS""")
		pyin.server = server
	if sparql_uri != '':
		new = """kbdbg:latest kbdbg:is <""" + this + ">"
		pyin.kbdbg(new, default=True)
		uuu = (pyin.prefixes +
		#WITH """ + default_graph + """
		"""DELETE {kbdbg:latest kbdbg:is ?x} WHERE {kbdbg:latest kbdbg:is ?x}""")
		server.update(uuu)
		pyin.kbdbg_text('#'+uuu)
	if identification != "":
		nolog or pyin.kbdbg('<'+this +"> kbdbg:has_run_identification " + rdflib.Literal(identification).n3(), True)

	rules, query_rule, goal_graph = pyin.load(kb, goal, identification, base)

	for result in query(rules, query_rule, goal_graph):
		print ()
		r = ''
		for triple in result:
			r += triple.str()
		print(' RESULT : ' + r)
		print(' step :' + str(pyin.global_step_counter))
		sys.stdout.flush()
		nolog or pyin.kbdbg_text('#result: ' + r)
	print(' steps :' + str(pyin.global_step_counter))

	if sparql_uri != '':
		pyin.kbdbg("<" + this + "> kbdbg:is kbdbg:done", default=True)
		pyin.flush_sparql_updates()

	if sparql_uri != '':
		pyin.pool.shutdown()


if __name__ == "__main__":
	query_from_files()




#from IPython import embed; embed()
