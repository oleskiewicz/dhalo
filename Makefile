SNAP?=013
DATA?=./data/cache.pkl
NFW_f?=002

ids: ./out/ids.$(SNAP).txt
cmh: ./out/cmh.$(SNAP).f$(NFW_f).txt

./out/ids.$(SNAP).txt: ./src/query.py $(DATA)
	$< $(DATA) $(SNAP) > $@

./out/cmh.$(SNAP).f$(NFW_f).txt: ./src/cmh.py $(DATA) ./out/ids.$(SNAP).txt
	$< \
		$(DATA) \
		./out/ids.$(SNAP).txt \
		$(shell echo "$(NFW_f) / 100" | bc -l) \
		> $@
