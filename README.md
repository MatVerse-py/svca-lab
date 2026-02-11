# SVCA Inescapável

Self-Verifying Computational Artifact  
Um primitivo mínimo para ciência executável, offline e deterministicamente reproduzível.

![Reproducible Build](https://github.com/MatVerse-py/svca-inescapavel/actions/workflows/ci.yml/badge.svg)

---

## 📖 O que é SVCA

SVCA (Self-Verifying Computational Artifact) é um objeto digital que:

- Contém o experimento (código + runtime)
- Prova sua própria integridade (assinatura Ed25519)
- Reproduz os mesmos bytes em qualquer máquina (build determinístico)
- Executa offline, sem infraestrutura externa

Isso inverte o paradigma da ciência computacional:

> de “paper descreve o experimento”  
> para “o artefato é o experimento”.

---

## 🔐 Invariantes Fundamentais

Um SVCA válido satisfaz simultaneamente:

1. **Integridade** – hash SHA256 fixo
2. **Executabilidade** – módulo WASM funcional
3. **Verificabilidade Pública** – assinatura Ed25519
4. **Reprodutibilidade Forte** – rebuild → mesmos bytes
5. **Autonomia** – sem dependências externas

Remover qualquer um invalida o primitivo.

---

## 🚀 Uso Imediato

```bash
git clone https://github.com/MatVerse-py/svca-inescapavel.git
cd svca-inescapavel

./build.sh
./verify.sh
```

---

## 📦 Artefatos Gerados

Após `build.sh`:

```
build/
├── module.wasm        # binário determinístico
├── module.wasm.br     # versão comprimida
├── manifest.sha256    # hash oficial
├── signature.bin      # assinatura Ed25519
└── manifest.json      # metadados estáticos
```

---

## 🔎 O que `build.sh` faz

- Compila `src/module.go` com:
  - `GOOS=js`
  - `GOARCH=wasm`
  - `-trimpath`
  - `-buildid=` (remove build ID)
- Remove qualquer timestamp implícito
- Gera SHA256 do binário
- Assina o manifesto usando chave Ed25519 estável
- Não gera chaves automaticamente
- Não acessa rede
- Não modifica chave pública versionada

Resultado: build determinístico.

---

## 🔍 O que `verify.sh` faz

- Valida assinatura Ed25519 contra `capsule/pubkey.pem`
- Executa `sha256sum -c manifest.sha256`
- Falha imediatamente se houver divergência

Isso garante que:

```
binary == manifesto == assinatura == chave pública
```

---

## 🌐 Execução do Capsule (Browser)

O `capsule/loader.js`:

- Carrega `manifest.json`
- Verifica assinatura antes de instanciar WASM
- Usa `wasm_exec.js` para runtime Go
- Só executa se integridade for válida

⚠️ O módulo **não é instanciado antes da verificação**.

---

## 🐳 Build Hermético com Docker

```bash
docker build -t svca -f container/Dockerfile .
docker run --rm -v "$PWD:/app" svca bash -lc "cd /app && ./build.sh && ./verify.sh"
```

A imagem base é pinned por digest SHA256.

Sem dependências implícitas.

---

## 🤖 CI – Reprodutibilidade Automática

O GitHub Actions:

- Executa `build.sh`
- Executa `verify.sh`
- Falha se qualquer byte divergir
- Garante que PRs não quebrem determinismo

Badge no topo reflete estado atual.

---

## 🔑 Modelo de Assinatura

- Algoritmo: Ed25519
- Chave pública: versionada em `capsule/pubkey.pem`
- Chave privada: não versionada
- Nunca rotacionada automaticamente

A raiz de confiança não muda entre clones.

---

## 🧪 Propriedade Fundamental

Se dois pesquisadores executarem:

```
./build.sh
sha256sum build/module.wasm
```

O hash será idêntico.

Isso é o núcleo do SVCA.

---

## 📜 Publicação Científica

Para submissão:

- `paper/svca.tex`
- Artefato `build/module.wasm.br`
- `manifest.sha256`
- `signature.bin`

O experimento não depende de link externo.

---

## 📄 Licença

MIT.

---

## 📌 Estado do Projeto

- Determinístico
- Offline
- Assinatura estável
- CI ativa
- Publicável

---

## 🧠 Citação

Mateus.  
*SVCA: Self-Verifying Computational Artifacts.*  
MatVerse, 2026.
