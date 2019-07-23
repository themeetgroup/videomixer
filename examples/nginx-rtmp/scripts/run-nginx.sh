#!/bin/bash -u

NGINX_CONF=/usr/local/nginx/nginx.conf

# run nginx
nginx -c ${NGINX_CONF}
