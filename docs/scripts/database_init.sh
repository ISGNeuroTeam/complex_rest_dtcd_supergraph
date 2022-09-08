#!/bin/bash

# Database initialization script for this plugin.
# Prepares PostgreSQL and Neo4j databases for work. Does the following:
# - Uses PostgreSQL to create a role and a database.
# - Creates the initial Root node and re-installs constrains and indexes.

PLUGIN="complex_rest_dtcd_supergraph"
USER=$PLUGIN
PASSWORD=$USER
DATABASE=$PLUGIN

# Setup
# go to this plugins directory
# <project>/plugins/<this-plugin>/
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
# go to project's directory
cd $SCRIPT_DIR/../..
# use project's venv
source venv/bin/activate
python="venv/bin/python"

# PostgreSQL settings
export PGUSER=postgres
export PGPASSWORD=$(cat ./postgres_config/postgres_password)
export PGPORT=5433
# create a role and a database for this plugin
## role
psql -U postgres << EOF
create user $USER with password '$PASSWORD';
EOF
## database
psql << EOF
create database $DATABASE;
grant all privileges on database $DATABASE to $USER;
EOF

# Neo4j settings
# limit the loaded plugins to this particular one
export COMPLEX_REST_PLUGIN_NAME="complex_rest_dtcd_supergraph"
# re-install labels
$python complex_rest/manage.py install_labels --reset
# initialize Root
$python complex_rest/manage.py create_default_root_node
