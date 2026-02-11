from pathlib import Path


def test_lab_structure_exists():
    required = [
        "src",
        "experiments",
        "tests",
        "artifact",
        "reproducibility",
        "pyproject.toml",
        "verify.sh",
        "build_artifact.py",
        "CONTAINER_DIGEST.md",
        "LAB_POLICY.md",
    ]
    root = Path(__file__).resolve().parents[1]
    for entry in required:
        assert (root / entry).exists(), f"faltando: {entry}"


def test_lab_policy_core_statements():
    root = Path(__file__).resolve().parents[1]
    policy = (root / "LAB_POLICY.md").read_text(encoding="utf-8")
    required_lines = [
        "Nothing is published without deterministic replay.",
        "Nothing is accepted without hash verification.",
        "Nothing is trusted without artifact.",
    ]
    for line in required_lines:
        assert line in policy, f"política ausente: {line}"


def test_artifact_depends_on_verify_stamp():
    root = Path(__file__).resolve().parents[1]
    content = (root / "build_artifact.py").read_text(encoding="utf-8")
    assert ".verify_passed" in content
    assert "Rode ./verify.sh" in content
