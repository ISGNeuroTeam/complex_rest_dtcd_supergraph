FROM quay.io/keycloak/keycloak:22.0.1
ENV KEYCLOAK_ADMIN=admin
ENV KEYCLOAK_ADMIN_PASSWORD=admin
ENV KC_HTTP_PORT=8090
ADD ./docs/docker/keycloak/entrypoint.sh /opt/
ADD ./docs/docker/keycloak/realm_config /opt/keycloak/realm_config
ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["/opt/keycloak/bin/kc.sh", "start-dev"]
EXPOSE 8090