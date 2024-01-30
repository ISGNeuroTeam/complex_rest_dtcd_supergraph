#!/bin/sh
cp /complex_rest_dtcd_supergraph/docs/docker/keycloak/policies/policies.jar /opt/keycloak/providers/
/opt/keycloak/bin/kc.sh build
/opt/keycloak/bin/kc.sh import --optimized --dir /complex_rest_dtcd_supergraph/docs/docker/keycloak/realm_config
exec "$@"