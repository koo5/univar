#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
r = requests.post("http://localhost:3000/convert", data={'n3': open('DATA').read()})
if r.status_code == 200:
	print(r.content)
print(r.status_code, r.reason)
