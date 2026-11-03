# MatVerse OCG — Fisiologia experimental v0.1

**Status deste pacote:** SPEC + IMPLEMENTATION_CANDIDATE / testes locais dependentes do CI.
**Não é:** prova de vida digital, autopoiese, consciência, eficácia científica, segurança certificada, assinatura criptográfica ou governança on-chain.

## Pergunta experimental

Um sistema persistente com restrições constitucionais estáticas e entradas variáveis consegue regular demanda, preservar estado e dividir uma colônia somente sob condições explicitamente modeladas?

O pacote implementa **um modelo sintético falsificável**, independente de LLM, API paga ou hardware especializado. Está desacoplado do Go/WASM e do mecanismo original de publicação do svca-lab.

## Fisiologia, sem confusão de papéis

| Sistema funcional | Papel canônico | Realizado aqui |
|---|---|---|
| SK-AI-NET / VPAI | Membrana, exposição e controle de ingestão | esquema de perturbação validado; sem feeds externos |
| Cassandra / IQG | interpretação e qualidade informacional | representação mínima de observações e backlog |
| URANO / UMJAM | alternativas, prova por simulação e falsificação | experimento Monte Carlo pareado |
| Ω-Gate / Trust Kernel | admissibilidade | função pura `authorize`, lei local congelada em código |
| SymbiOS | metabolismo e ação | `evolve`, controle de demanda, recurso e estado |
| ACOA | auto-regulação | `propose` com RECOVER / THROTTLE / WORK |
| MNB/MMNB | herança de informação | estado causal persistido no SQLite |
| EvidenceOS / Ledger | histórico e reconstrução | cadeia de hashes + replay integral |
| Colônia / Cube | projeção espacial | HTML/Canvas somente leitura, sem autoridade |
| CAPTALS | eficiência e sustentabilidade | `work`, `energy` sintéticos; sem receita demonstrada |

URANO propõe e testa hipóteses em sandbox. Não detém autoridade para instalar alterações em produção. A avaliação, autorização e execução são funções separadas; a versão 0.1 ainda **não** possui um autorizador independente de processo nem assinaturas de identidade.

## Lei vs. variação

`Constitution` é dataclass congelada, com SHA-256 do conteúdo canônico como identificador de versão **local**. Isso não impede um operador de editar Python e recalcular os hashes, e não equivale a SGX, assinatura digital ou ancoragem on-chain.

`Perturbation(demand, shock, supply, heterogeneity, coupling)` altera as condições da simulação. O organismo gera microflutuações internas determinísticas sem depender de pedidos humanos.

Risco da amostra no ciclo `t`:

`L_t = clip(0.70 shock + 0.20 clip(backlog/3) + 0.10 (1-coherence))`

`CVaR_.9(L)` = média integrada do pior decil das perdas registradas, considerando massa fracionária no quantil. **Antes de 10 pontos retorna UNKNOWN**, nunca 0. É estimativa do indicador de perdas sintético, não risco financeiro, risco médico, nem probabilidade de evento.

Pulso visível: `BPM = clip(60 + 125 |ΔCVaR|, 48, 120)` depois de amostras suficientes. Antes disso, é modulado por flutuação interna. A animação segue o BPM entre leituras, mas a interface indica quando o backend não avançou.

Fissão exige a conjunção:

- CVaR > 0.65 por pelo menos 3 ciclos;
- heterogeneidade >= 0.72 e acoplamento <= 0.25;
- energia >= 55 unidades sintéticas;
- total de nós < 4.

Sob fissão: `E_parent_new + E_child_new = E_parent_old - 6`. Não há criação gratuita de recursos; o novo nó continua executando nos ciclos seguintes. Não é prova de bifurcação física nem cálculo de Lyapunov.

## Execução

Requer Python >= 3.12, biblioteca padrão:

```bash
python -m physiology --db organism.sqlite3 init
python -m physiology --db organism.sqlite3 live --interval 1
# Em outro terminal:
python -m physiology --db organism.sqlite3 serve --port 8844
# Navegador: http://127.0.0.1:8844
# Experimentação dirigida:
python -m physiology --db study.sqlite3 demo --ticks 90
python -m physiology --db study.sqlite3 verify
python -m unittest discover -s tests -p test_physiology.py -v
python experiments/physiology_monte_carlo.py --runs 200 --ticks 120
```

**Cuidado:** Não execute duas instâncias `live` sobre o mesmo DB sem coordenação externa; cada execução usa transação SQLite, mas o desenho é single-writer. Serviço HTTP na interface loopback (127.0.0.1) e leitura apenas. Para ver de múltiplos locais, adicionar proxy TLS autenticado e broker de estado; não expor a porta local diretamente.

O `verify` recompõe o estado desde genesis usando todos os sinais armazenados e o mesmo código e checa hashes e snapshot. Detecta incoerência e alterações acidentais; sem testemunha externa, um atacante com controle do banco e código pode reconstruir a cadeia adulterada.

## Fronteiras em aberto (F0–F10)

| Estágio | Situação v0.1 | Critério que falta |
|---|---|---|
| F0 anatomia | implementada em subset sintético | auditar equivalência com componentes MatVerse reais |
| F1 integração | local no pacote | bindings versionados e testes entre repositórios |
| F2 fechamento causal | ciclo local implementado | observação de efeito externo não fabricada |
| F3 fisiologia temporal | `live` + persistência | supervisão, reinício e uptime medido |
| F4 homeostase | regulador experimental | recuperação robusta contra baselines e perfis reais |
| F5 imunidade / reparo | gate e bloqueio básico | quarentena, rollback e contenção adversarial |
| F6 adaptação governada | escolha de ação fixa | geração/teste/promotor independente de capabilities |
| F7 meta-adaptação | não implementada | atualizar estratégia de aprendizagem sem self-promotion |
| F8 continuidade entre máquinas | semântica de identidade local | migração testada entre hosts, quorum, replay remoto |
| F9 embodiment | não implementado | energia elétrica/sensores/atuadores instrumentados |
| F10 organismo demonstrado | NÃO demonstrado | estudo longitudinal e terceiros independentes |

## Critérios de engenharia e adversarial

- **Red team obrigatório:** logs truncados, estado adulterado, replay com sinal divergente, valores NaN, pico de demanda, falta de energia e tentativa de fissão infinita.
- **A3 / herança causal:** só registrar restrições candidatas nesta fase; não perpetuar bloqueios automaticamente a partir de correlações.
- **Constitucional:** hash local é identidade de configuração, não uma cadeia de autoridade.
- **CVaR:** não classificar amostra pequena como segura; correlacionamento temporal reduz informação estatística.
- **Autonomia econômica:** `work` e `energy` são unidades artificiais. Não existe receita, margem, CAC, ARR, preço de mercado nem prova de autosustento neste protótipo.
- **Propriedade intelectual:** este código genérico é uma referência pública de pesquisa. Não publicar implementações inéditas potencialmente patenteáveis sem revisão apropriada da estratégia de divulgação.

## Próxima verificação

A transição mais valiosa é conectar um sensor **real e sem poderes de escrita** (CPU, memória, fila, consumo) a um `PerturbationAdapter`, medir custo e recuperar de um processo encerrado. Só depois separar observação simulada de observação do mundo e avaliar `WORLD_REAL_PASS`.

O resultado da experiência pode ser negativo e ainda ser cientificamente útil. A constituição desta referência é estática; a validade de cada alegação não é.
