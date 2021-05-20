TREMOR_VSN=v0.11.3

mkdocs.yml: mkdocs.yml.in docs/tremor-script/stdlib docs/operations/cli.md docs/api.md
	python3 ./python_scripts/include_stdlib.py

tremor-runtime:
	-git clone https://github.com/tremor-rs/tremor-runtime
	cd tremor-runtime &&\
	git checkout $(TREMOR_VSN)

docs/tremor-script/stdlib: tremor-runtime
	cd tremor-runtime && make stdlib-doc
	-rm -r docs/tremor-script/stdlib
	cp -r tremor-runtime/docs docs/tremor-script/stdlib

docs/operations/cli.md: tremor-runtime
	python3 ./python_scripts/cli2md.py tremor-runtime/tremor-cli/src/cli.yaml > docs/operations/cli.md

docs/api.md: tremor-runtime
	python3 ./python_scripts/api2md.py tremor-runtime/static/openapi.yaml > docs/api.md

clean:
	rm -rf mkdocs.yml docs/operations/cli.md docs/api.md docs/tremor-script/stdlib

