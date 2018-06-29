FINAL_SNAP:=045
GRAV?=GR
SNAP?=013
NFW_f?=002
DATA:=./out/trees/$(GRAV)/treedir_$(FINAL_SNAP)/tree_$(FINAL_SNAP).0.hdf5

SNAPS:=045 032 022 009 0

cmh: ./out/cmh.$(SNAP).f$(NFW_f).$(GRAV).csv
ids: ./out/ids.$(SNAP).$(GRAV).txt

./out/ids.$(SNAP).$(GRAV).txt: ./src/query.py $(DATA)
	$< $(DATA) $(SNAP) > $@

./out/cmh.$(SNAP).f$(NFW_f).$(GRAV).csv: ./src/cmh.py ./out/ids.$(SNAP).$(GRAV).txt
	$< \
		$(DATA) \
		./out/ids.$(SNAP).$(GRAV).txt \
		$(shell echo "$(NFW_f) / 100" | bc -l) \
		> $@
