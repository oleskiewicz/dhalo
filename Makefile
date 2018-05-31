SNAP?=013
DATA?=./data/cache.pkl
NFW_f?=002

ids: ./out/ids.$(SNAP).txt
cmh: ./out/cmh.$(SNAP).f$(NFW_f).txt

./out/ids.$(SNAP).txt: ./query.py $(DATA)
	python $< $(DATA) $(SNAP) > $@

./out/cmh.$(SNAP).f$(NFW_f).txt: ./main.py ./out/ids.$(SNAP).txt $(DATA)
	python $< \
		$(DATA) \
		$(shell echo "$(NFW_f) / 100" | bc -l) \
		-i $(shell cat ./out/ids.$(SNAP).txt | paste -s -d' ') \
		> $@
