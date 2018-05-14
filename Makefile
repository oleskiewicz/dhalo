SRC:=./src/dhalo
OUT:=./output/dhalo
# IDS:=$(shell cat $(OUT)/ids.txt)
IDS:=37048400000752

plots: $(foreach ID,$(IDS),./plots/cmh_$(ID).pdf)
cmh: ./plots/cmh.pdf
ids: $(OUT)/ids.txt

$(OUT)/ids.txt: $(SRC)/query.py
	python $< $@

./plots/cmh_%.pdf: $(OUT)/cmh_%.dot
	dot -Tpdf -o $@ $<

$(OUT)/cmh_%.dot: $(SRC)/tree.py
	python $< $* $(OUT)/cmh.tsv

./plots/cmh.pdf: $(SRC)/plot.py $(OUT)/cmh.tsv
	python $< $(word 2,$^) $@

# only re-run after running submit.csh on new set if ids
$(OUT)/cmh.tsv: $(SRC)/forge.py
	python $< $@

clean:
	rm -f $(OUT)/*.dot

purge:
	rm -f $(OUT)/*

.PHONY: plots cmh purge clean docs
.PRECIOUS: $(OUT)/cmh_%.dot $(OUT)/cmh_%.tsv
