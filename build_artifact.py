#!/usr/bin/env python3
import hashlib
import json
import pathlib
import tarfile

ROOT = pathlib.Path(__file__).resolve().parent
BUILD = ROOT / "build"
ARTIFACT = ROOT / "artifact"
ARTIFACT.mkdir(exist_ok=True)

VERIFY_STAMP = ROOT / ".verify_passed"

if not VERIFY_STAMP.exists():
    raise SystemExit("verify PASS ausente. Rode ./verify.sh antes de gerar artifact.")

bundle_path = ARTIFACT / "bundle.tar.gz"
manifest_path = ARTIFACT / "manifest.json"
hashes_path = ARTIFACT / "hashes.txt"
commit_path = ARTIFACT / "commit.txt"

if not BUILD.exists():
    raise SystemExit("build/ não encontrado. Rode ./build.sh antes.")

with tarfile.open(bundle_path, "w:gz") as tar:
    for name in ["module.wasm", "manifest.sha256", "signature.bin", "manifest.json"]:
        src = BUILD / name
        if src.exists():
            tar.add(src, arcname=name)

sha_bundle = hashlib.sha256(bundle_path.read_bytes()).hexdigest()

build_commit = (ROOT / "BUILD_COMMIT").read_text().strip() if (ROOT / "BUILD_COMMIT").exists() else ""

manifest = {
    "bundle": bundle_path.name,
    "sha256": sha_bundle,
    "build_commit": build_commit,
}
manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

hashes_path.write_text(f"{sha_bundle}  {bundle_path.name}\n")
commit_path.write_text(build_commit + "\n")

print("artifact gerado em artifact/")
