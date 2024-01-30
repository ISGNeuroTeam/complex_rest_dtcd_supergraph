#!/bin/sh
cp /complex_rest/docs/docker_dev/keycloak/policies/policies.jar /opt/keycloak/providers/
/opt/keycloak/bin/kc.sh build
/opt/keycloak/bin/kc.sh import --optimized --dir /complex_rest/docs/docker_dev/keycloak/realm_config
exec "$@"