# SVCA Inescapável

**Self‑Verifying Computational Artifact**  
Um primitivo para ciência executável, offline e deterministicamente reproduzível.

[![Reproducible Build](https://github.com/MatVerse-py/svca-inescapavel/actions/workflows/ci.yml/badge.svg)](https://github.com/MatVerse-py/svca-inescapavel/actions/workflows/ci.yml)

## O que é

SVCA (Self‑Verifying Computational Artifact) é um objeto digital que:
- **Contém** o experimento (código + runtime)
- **Prova** sua própria integridade (assinatura Ed25519)
- **Reproduz** os mesmos bytes em qualquer máquina (build determinístico)
- **Executa** offline, sem qualquer infraestrutura externa

Isto inverte o fluxo da ciência computacional:  
**do “paper descreve o experimento”** → **para “o artefato é o experimento”.**

## Uso imediato

```bash
git clone https://github.com/MatVerse-py/svca-inescapavel.git
cd svca-inescapavel

./build.sh
./verify.sh
```

O artefato final estará em `build/module.wasm` e sua assinatura em `build/signature.bin`.

## Verificação de reprodutibilidade

`./verify.sh` executa:
1. Verificação da assinatura Ed25519 do manifesto
2. Checagem do hash SHA256 do binário gerado

## Build hermético (opcional com Docker)

```bash
docker build -t svca -f container/Dockerfile .
docker run --rm -v "$PWD:/app" svca bash -lc "cd /app && ./build.sh && ./verify.sh"
```

## Licença

MIT. Todo código e texto são livres para uso, modificação e citação.
