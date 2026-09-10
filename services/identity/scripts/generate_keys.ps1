$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path 'secrets' | Out-Null
openssl genrsa -out secrets/private.pem 2048
openssl rsa -in secrets/private.pem -pubout -out secrets/public.pem
Write-Host 'Generated secrets/private.pem and secrets/public.pem'
