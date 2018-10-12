#!/bin/bash

docker run -v $(pwd):$(pwd) -w $(pwd) bdevloed/eye kb_for_external_raw.n3 --query query_for_external_raw.n3 --nope


