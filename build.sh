#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export TZ=UTC

ROOT="$(pwd)"
BUILD_DIR="$ROOT/build"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

echo "🔧 Compilando módulo Go (WASM) com flags determinísticas..."
GOOS=js GOARCH=wasm \
  go build -trimpath -ldflags="-s -w -buildid=" \
  -o module.wasm "$ROOT/src/module.go"

echo "📝 Gerando manifesto e assinatura Ed25519..."
sha256sum module.wasm > manifest.sha256
cat > manifest.json <<MANIFEST
{
  "capsule": "module.wasm",
  "timestamp": "",
  "signature": "signature.bin",
  "compiler": {
    "go": "1.22.3"
  }
}
MANIFEST

if [[ ! -f "$ROOT/capsule/secret.key" ]]; then
  echo "🔑 Gerando par de chaves Ed25519 (primeira execução)..."
  go run "$ROOT/tools/svca-crypto/main.go" keygen --pub "$ROOT/capsule/pubkey.pem" --sec "$ROOT/capsule/secret.key"
fi

go run "$ROOT/tools/svca-crypto/main.go" sign --sec "$ROOT/capsule/secret.key" --in manifest.sha256 --out signature.bin

echo "✅ Artefato pronto:"
ls -lh module.wasm signature.bin manifest.sha256 manifest.json
sha256sum module.wasm
