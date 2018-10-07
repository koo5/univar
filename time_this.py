#!/usr/bin/env python
# -*- coding: utf-8 -*-

best = 6666666666
import time, os
global_start = time.time()

while True:
	start = time.time()
	print(os.system('./timed.sh'))
	elapsed = time.time() - start
	if elapsed < best:
		best = elapsed
	print ("elapsed:", elapsed)
	print("best:", best)
	if time.time() - global_start > 360:
		break

