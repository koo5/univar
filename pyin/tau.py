#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pymantic import sparql
from concurrent.futures import ThreadPoolExecutor
import subprocess
import pyin
from pyin import *
import datetime
import rdflib
from ordered_rdflib_store import OrderedStore
import click




store = OrderedStore()
kb_graph = rdflib.Graph(store=store, identifier='@default')
kb_graph.parse('kb2', format='n3')


from IPython import embed; embed()
exit()


