TREMOR_VSN=spike-modularity-combined

mkdocs.yml: mkdocs.yml.in docs/tremor-script/stdlib
	files=`find docs/tremor-script/stdlib -type f`;\
	idx=$$(for f in $$files; do \
		name=`echo $$f | sed -e 's;docs/tremor-script/stdlib/\(.*\).md;\1;' | sed -e 's;/;::;'`;\
		file=`echo $$f | sed -e 's;docs/;;'`;\
		echo "$${name}0      - '$$name': $$file";\
	done | sort | sed -e 's/^.*\?0//' | awk 1 ORS='\\n');\
	sed -e "s;      - STDLIB;$${idx};" mkdocs.yml.in > mkdocs.yml


docs/tremor-script/stdlib:
	-git clone https://github.com/wayfair-tremor/tremor-runtime
	cd tremor-runtime &&\
	git checkout $(TREMOR_VSN) &&\
	make stdlib-doc;
	-rm -r docs/tremor-script/stdlib
	cp -r tremor-runtime/docs docs/tremor-script/stdlib
