#.SILENT:
SHELL = /bin/bash

plugin_name := dtcd_server
build_dir := make_build
plugin_dir := $(build_dir)/$(plugin_name)
requirements_file := requirements.txt
url_neo4j := https://neo4j.com/artifact.php?name=neo4j-community-4.4.6-unix.tar.gz
# url_drive_neo4j := https://drive.google.com/uc?export=download&id=1YipGGkmYhEveSSJ4ZsPC0pIjxivBKxYu


all:
	echo -e "Required section:\n\
 build - build project into build directory, with configuration file and environment\n\
 clean - clean all addition file, build directory and output archive file\n\
 test - run all tests\n\
 pack - make output archive, file name format \"$(plugin_name)_vX.Y.Z_BRANCHNAME.tar.gz\"\n\
Addition section:\n\
 venv\n\
"

GENERATE_VERSION = $(shell cat setup.py | grep __version__ | head -n 1 | sed -re 's/[^"]+//' | sed -re 's/"//g' )
GENERATE_BRANCH = $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | cut -d ^ -f1 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')
SET_VERSION = $(eval VERSION=$(GENERATE_VERSION))
SET_BRANCH = $(eval BRANCH=$(GENERATE_BRANCH))

pack: make_build
	$(SET_VERSION)
	$(SET_BRANCH)
	rm -f $(plugin_name)-*.tar.gz
	cd $(build_dir); tar czf ../$(plugin_name)-$(VERSION)-$(BRANCH).tar.gz $(plugin_name)

clean_pack: clean_build
	rm -f $(plugin_name)-*.tar.gz

dtcd_server.tar.gz: build
	cd $(build_dir); tar czf ../$(plugin_name).tar.gz $(plugin_name) && rm -rf ../$(build_dir)

build: make_build

make_build: venv.tar.gz
	mkdir $(build_dir)
	cp -r $(plugin_name) $(build_dir)

	# copy configuration files
	rm -rf $(plugin_dir)/serialization.json 2> /dev/null
	rm -rf $(plugin_dir)/exchange.json 2> /dev/null
	cp docs/dtcd_server.conf.example $(plugin_dir)/dtcd_server.conf
	cp docs/log_configuration.json.example $(plugin_dir)/log_configuration.json
	cp docs/serialization.json.example $(plugin_dir)/serialization.json
	cp docs/exchange.json.example $(plugin_dir)/exchange.json
#	cp docs/proc.conf.example $(plugin_dir)/proc.conf  # TODO deployment

	mkdir $(plugin_dir)/tmp
	mkdir $(plugin_dir)/pages
	mkdir $(plugin_dir)/plugins
	mkdir $(plugin_dir)/public
	mkdir $(plugin_dir)/workspaces

	cp *.md $(plugin_dir)
	cp *.py $(plugin_dir)

	# virtual environment
	mkdir $(plugin_dir)/venv
	tar -xzf ./venv.tar.gz -C $(plugin_dir)/venv

clean_build: clean_venv
	rm -rf $(build_dir)

venv:
	conda create --copy -p ./venv -y
	conda install -p ./venv python==3.9.7 -y
	./venv/bin/pip install --no-input -r $(requirements_file)

venv.tar.gz: venv
	conda pack -p ./venv -o ./venv.tar.gz

clean_venv:
	rm -rf venv
	rm -f ./venv.tar.gz

complex_rest:
	@echo "Should clone complex_rest repository in future..."
# 	git clone git@github.com:ISGNeuroTeam/complex_rest.git
# 	{ cd ./complex_rest; git checkout develop; make venv; make redis; }
# 	ln -s ../../../../dtcd_server/dtcd_server ./complex_rest/complex_rest/plugins/dtcd_server

clean_complex_rest:
ifneq (,$(wildcard ./complex_rest))
	{ cd ./complex_rest; make clean;}
	rm -f ./complex_rest/plugins/dtcd_server
	rm -rf ./complex_rest
endif

clean: clean_build clean_venv clean_pack clean_test clean_complex_rest

test: venv complex_rest
	@echo "Testing..."
# 	./complex_rest/venv/bin/python ./complex_rest/complex_rest/manage.py test ./tests --settings=core.settings.test

clean_test: clean_complex_rest
	@echo "Clean tests"