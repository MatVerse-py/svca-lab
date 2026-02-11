#!/usr/bin/env bash
set -euo pipefail

cd build

echo "🔐 Verificando assinatura Ed25519..."
go run ../tools/svca-crypto/main.go verify --pub ../capsule/pubkey.pem --in manifest.sha256 --sig signature.bin

echo "📦 Verificando hash do binário..."
sha256sum -c manifest.sha256

echo "✅ Tudo íntegro e reproduzível."
