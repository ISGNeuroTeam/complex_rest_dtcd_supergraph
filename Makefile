.SILENT:
SHELL = /bin/bash

plugin := dtcd_supergraph
build_dir := make_build
target_dir := $(build_dir)/$(plugin)
requirements_file := production.txt
url_neo4j := https://neo4j.com/artifact.php?name=neo4j-community-4.4.6-unix.tar.gz
# url_drive_neo4j := https://drive.google.com/uc?export=download&id=1YipGGkmYhEveSSJ4ZsPC0pIjxivBKxYu
version := $(shell fgrep -m 1 __version__ setup.py | cut -d = -f 2 | tr -d " '\"" )
branch := $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | cut -d ^ -f1 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')


all:
	echo -e "Required section:\n\
 build - build project into build directory, with configuration file and environment\n\
 clean - clean all addition file, build directory and output archive file\n\
 test - run all tests\n\
 pack - make output archive, file name format \"$(plugin)_vX.Y.Z_BRANCHNAME.tar.gz\"\n\
Addition section:\n\
 venv - create conda virtual environment, then install requirements\n\
"


.PHONY: pack
pack: build
	cd $(build_dir); tar -czf ../$(plugin)-$(version)-$(branch).tar.gz $(plugin)

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
#	cp -u docs/proc.conf.example $(target_dir)/proc.conf  # TODO deployment
	cp -u *.md $(target_dir)
	cp -u *.py $(target_dir)
#   virtual environment
	mkdir $(target_dir)/venv
	tar -xzf ./venv.tar.gz -C $(target_dir)/venv

.PHONY: clean_build
clean_build: clean_venv
	rm -r $(build_dir)

venv:
	conda create --copy -p ./venv -y
	conda install -p ./venv python==3.9.7 -y
	./venv/bin/pip install --no-input -r requirements/$(requirements_file)
# 	fix py2neo bug
	python docs/fix_py2neo.py venv/lib/python3.9

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
	echo "Testing..."

.PHONY: clean_test
clean_test:
	echo "Clean tests"

.PHONY: format
format:
	python3 -m black $(plugin) tests