SIM?=L62
SNAP?=013
NFW_f?=002
DATA:=./data/$(SIM).pkl

all: cmh
ids: ./out/$(SIM)/ids.$(SNAP).txt
cmh: ./out/$(SIM)/cmh.$(SNAP).f$(NFW_f).txt

./out/$(SIM)/ids.$(SNAP).txt: ./src/query.py $(DATA)
	$< $(DATA) $(SNAP) > $@

./out/$(SIM)/cmh.$(SNAP).f$(NFW_f).txt: ./src/cmh.py $(DATA) ./out/$(SIM)/ids.$(SNAP).txt
	$< \
		$(DATA) \
		./out/$(SIM)/ids.$(SNAP).txt \
		$(shell echo "$(NFW_f) / 100" | bc -l) \
		> $@
