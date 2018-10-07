#!/usr/bin/env python
# -*- coding: utf-8 -*-

best = 6666666666
import time, os, sys
global_start = time.time()
r=0
count = 0
while r == 0 and count < 6:
	start = time.time()
	r = os.system(sys.argv[1])
	count += 1
	elapsed = time.time() - start
	if r == 0:
		if elapsed < best:
			best = elapsed
	print ("elapsed:", elapsed)
	print("best:", best)
	if time.time() - global_start > 360:
		break

