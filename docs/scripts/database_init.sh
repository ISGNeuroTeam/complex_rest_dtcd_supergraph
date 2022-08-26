#!/bin/bash

# Creates the initial Root node and re-installs constrains and indexes.

# <project>/plugins/<this-plugin>/
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

# go to project's directory
cd $SCRIPT_DIR/../..

# use project's venv
python="venv/bin/python"

# limit the loaded plugins to this particular one
export COMPLEX_REST_PLUGIN_NAME="complex_rest_dtcd_supergraph"

# re-install labels
$python complex_rest/manage.py install_labels --reset

# initialize Root
$python complex_rest/manage.py create_default_root_node
