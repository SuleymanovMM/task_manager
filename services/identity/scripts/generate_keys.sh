#!/usr/bin/env sh
set -eu
mkdir -p secrets
openssl genrsa -out secrets/private.pem 2048
openssl rsa -in secrets/private.pem -pubout -out secrets/public.pem
chmod 600 secrets/private.pem
chmod 644 secrets/public.pem
echo "Generated secrets/private.pem and secrets/public.pem"
