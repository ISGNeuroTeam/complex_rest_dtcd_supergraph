#!/bin/bash

# Creates the initial Root node and saves its UID 
# into a text file "default_root_uid.txt" in plugin's directory.

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

# use this plugin's venv
python="venv/bin/python"

# re-install labels
apps="models"
conf="supergraph.conf"
$python reinstall_labels.py $apps $conf

# initialize Root
$python create_default_root.py
