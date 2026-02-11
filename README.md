# svca-lab

Laboratório de ciência executável com verificação criptográfica e replay determinístico.

## Estrutura

```text
svca-lab/
├── src/
├── experiments/
├── tests/
├── artifact/
├── reproducibility/
├── pyproject.toml
├── verify.sh
├── build_artifact.py
├── CONTAINER_DIGEST.md
└── LAB_POLICY.md
```

## Ativação limpa do laboratório

```bash
./lab_setup.sh
```

## Pipeline causal (obrigatório)

```text
sem verify PASS
→ sem artifact
→ sem publisher
→ sem DOI
```

Comandos operacionais:

```bash
./build.sh
./verify.sh
python3 build_artifact.py
```

`build_artifact.py` só gera saída quando o carimbo `.verify_passed` foi emitido por `verify.sh`.
