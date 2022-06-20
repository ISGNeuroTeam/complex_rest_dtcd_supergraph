
#.SILENT:
SHELL = /bin/bash


all:
	echo -e "Required section:\n\
 build - build project into build directory, with configuration file and environment\n\
 clean - clean all addition file, build directory and output archive file\n\
 test - run all tests\n\
 pack - make output archive, file name format \"complex_rest_dtcd_supergraph_vX.Y.Z_BRANCHNAME.tar.gz\"\n\
Addition section:\n\
 venv\n\
"

GENERATE_VERSION = $(shell cat setup.py | grep __version__ | head -n 1 | sed -re 's/[^"]+//' | sed -re 's/"//g' )
GENERATE_BRANCH = $(shell git name-rev $$(git rev-parse HEAD) | cut -d\  -f2 | sed -re 's/^(remotes\/)?origin\///' | tr '/' '_')
SET_VERSION = $(eval VERSION=$(GENERATE_VERSION))
SET_BRANCH = $(eval BRANCH=$(GENERATE_BRANCH))

pack: make_build
	$(SET_VERSION)
	$(SET_BRANCH)
	rm -f complex_rest_dtcd_supergraph-*.tar.gz
	echo Create archive \"complex_rest_dtcd_supergraph-$(VERSION)-$(BRANCH).tar.gz\"
	cd make_build; tar czf ../complex_rest_dtcd_supergraph-$(VERSION)-$(BRANCH).tar.gz complex_rest_dtcd_supergraph

clean_pack:
	rm -f complex_rest_dtcd_supergraph-*.tar.gz


complex_rest_dtcd_supergraph.tar.gz: build
	cd make_build; tar czf ../complex_rest_dtcd_supergraph.tar.gz complex_rest_dtcd_supergraph && rm -rf ../make_build

build: make_build

make_build: venv venv.tar.gz
	# required section
	echo make_build
	mkdir make_build

	cp -R ./complex_rest_dtcd_supergraph make_build
	rm make_build/complex_rest_dtcd_supergraph/complex_rest_dtcd_supergraph.conf
	mv make_build/complex_rest_dtcd_supergraph/complex_rest_dtcd_supergraph.conf.example make_build/complex_rest_dtcd_supergraph/complex_rest_dtcd_supergraph.conf
	cp *.md make_build/complex_rest_dtcd_supergraph/
	cp *.py make_build/complex_rest_dtcd_supergraph/
	if [ -s requirements.txt ]; then \
		mkdir make_build/complex_rest_dtcd_supergraph/venv;\
		tar -xzf ./venv.tar.gz -C make_build/complex_rest_dtcd_supergraph/venv; \
	fi

clean_build:
	rm -rf make_build

venv:
	if [ -s requirements.txt ]; then \
		echo Create venv; \
		conda create --copy -p ./venv -y; \
		conda install -p ./venv python==3.9.7 -y; \
		./venv/bin/pip install --no-input  -r requirements.txt; \
	fi

venv.tar.gz: venv
	if [ -s requirements.txt ]; then \
		conda pack -p ./venv -o ./venv.tar.gz; \
	fi

clean_venv:
	rm -rf venv
	rm -f ./venv.tar.gz


clean: clean_build clean_venv clean_pack clean_test

test: venv
	@echo "Testing..."


clean_test:
	@echo "Clean tests"






