#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFY_STAMP="$ROOT/.verify_passed"

rm -f "$VERIFY_STAMP"

cd "$ROOT/build"

echo "🔐 Verificando assinatura Ed25519..."
go run ../tools/svca-crypto/main.go verify --pub ../capsule/pubkey.pem --in manifest.sha256 --sig signature.bin

echo "📦 Verificando hash do binário..."
sha256sum -c manifest.sha256

cd "$ROOT"

echo "🔁 Checking deterministic replay..."
if ! ./build.sh; then
    echo "BUILD FAILED — INTERDIÇÃO"
    exit 1
fi

echo "PASS" > "$VERIFY_STAMP"
echo "✅ verify PASS: cadeia causal liberada para artifact."
