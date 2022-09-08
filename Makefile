# Tutorials & docs:
# - https://makefiletutorial.com/
# - https://www.gnu.org/software/make/manual/make.html
# Guidelines: https://github.com/ISGNeuroTeam/Guidelines/blob/master/GUIDELINES.md
# Example: https://github.com/ISGNeuroTeam/Guidelines/blob/master/makefiles/Python/Makefile
.SILENT:
SHELL = /bin/bash

plugin := complex_rest_dtcd_supergraph
build_dir := make_build
target_dir := $(build_dir)/$(plugin)
requirements_file := production.txt
python_version := 3.9.7
version := $(shell fgrep -m 1 __version__ setup.py | cut -d = -f 2 | tr -d " '\"" )
# branch info is strange, but Jenkins uses it correctly
branch := $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | cut -d ^ -f1 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')


all:
	echo -e "Required section:\n\
 build - build project into build directory, with configuration file and environment\n\
 clean - clean all additional files, build directory and output archive file\n\
 test - run all tests\n\
 pack - make output archive, filename format \"$(plugin)_vX.Y.Z_BRANCHNAME.tar.gz\"\n\
Additional section:\n\
 venv - create conda virtual environment, then install the requirements\n\
"


.PHONY: pack
pack: build
	cd $(build_dir); tar --totals -czf ../$(plugin)-$(version)-$(branch).tar.gz $(plugin)

.PHONY: clean_pack
clean_pack: clean_build
	rm $(plugin)-*.tar.gz

.PHONY: build
build: $(build_dir)

$(build_dir): venv.tar.gz
	mkdir $(build_dir)
#   copy content and config files (dereference symlinks)
	cp -ruL $(plugin) $(build_dir)
	cp -u docs/supergraph.conf.example $(target_dir)/supergraph.conf
	cp -u *.md $(target_dir)
	cp -u *.py $(target_dir)
#	scripts
	cp -u docs/scripts/*.sh $(target_dir)
	chmod o+x $(target_dir)/*.sh
#   virtual environment
	mkdir $(target_dir)/venv
	tar -xzf ./venv.tar.gz -C $(target_dir)/venv

.PHONY: clean_build
clean_build: clean_venv
	rm -r $(build_dir)

venv:
	conda create --copy -p ./venv -y
	conda install -p ./venv python==$(python_version) -y
	./venv/bin/pip install --no-input -r requirements/$(requirements_file)

venv.tar.gz: venv
	conda pack -p ./venv -o ./venv.tar.gz

.PHONY: clean_venv
clean_venv:
	rm -r venv
	rm ./venv.tar.gz

.PHONY: clean
clean: clean_build clean_venv clean_pack clean_test

.PHONY: test
test: venv
#	Jenkins does not have Neo4j installed, so no tests for now
	echo "Testing..."

.PHONY: clean_test
clean_test:
	echo "Clean tests"

.PHONY: format
format:
	python3 -m black --extend-exclude "migrations" $(plugin) tests
