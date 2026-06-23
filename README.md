# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Implementação do desafio de **Pull / Otimização / Push / Avaliação** de prompts no
LangSmith Prompt Hub, com pipeline em Python + LangChain + LangSmith Evaluations.

O objetivo é partir de um prompt de **baixa qualidade** (`leonanluppi/bug_to_user_story_v1`),
refatorá-lo aplicando técnicas avançadas de Prompt Engineering, publicar a versão
otimizada como `{seu_usuario}/bug_to_user_story_v2` (público) e atingir **≥ 0.8 em todas
as 5 métricas** do `evaluate.py`.

---

## Sumário

- [Estrutura do projeto](#estrutura-do-projeto)
- [A) Técnicas Aplicadas (Fase 2)](#a-técnicas-aplicadas-fase-2)
- [B) Resultados Finais](#b-resultados-finais)
- [C) Como Executar](#c-como-executar)
- [Critério de Aprovação](#critério-de-aprovação)
- [Testes de validação](#testes-de-validação)
- [O que não alterar](#o-que-não-alterar)

---

## Estrutura do projeto

```
mba-ia-pull-evaluation-prompt/
├── .env.example
├── requirements.txt
├── README.md
├── prompts/
│   ├── bug_to_user_story_v1.yml    # baixado via pull_prompts.py
│   └── bug_to_user_story_v2.yml    # versão otimizada (autoral)
├── datasets/
│   └── bug_to_user_story.jsonl     # 15 bugs (5 simples / 7 médios / 3 complexos)
├── src/
│   ├── pull_prompts.py             # pull do Hub -> YAML local
│   ├── push_prompts.py             # YAML local -> Hub (público)
│   ├── evaluate.py                 # avaliação com 5 métricas (≥ 0.8)
│   ├── metrics.py                  # F1, Clarity, Precision via LLM-as-Judge
│   └── utils.py                    # helpers (LLM, YAML, env, formatação)
└── tests/
    └── test_prompts.py             # 6 testes pytest sobre o v2
```

---

## A) Técnicas Aplicadas (Fase 2)

O `prompts/bug_to_user_story_v2.yml` combina seis técnicas, cada uma escolhida para
endereçar uma fraqueza específica observada no v1 (instruções vagas, sem persona, sem
exemplos, sem regras, sem formato e sem tratamento de edge cases).

| # | Técnica | Por que escolhi | Como aparece no v2 |
|---|---------|-----------------|---------------------|
| 1 | **Role Prompting** | O v1 não definia papel, gerando respostas genéricas. Atribuir uma persona sênior calibra tom, profundidade e vocabulário esperados. | `"Você é um Product Owner sênior com 12 anos de experiência..."` no início do system prompt. |
| 2 | **Few-Shot Learning** (obrigatório pela spec) | O v1 não tinha exemplo algum, então o modelo improvisava formato. Few-shot ancora estrutura, vocabulário e nível de detalhe. | 4 pares `BUG REPORT: ... / USER STORY: ...` cobrindo SIMPLES (2), MÉDIO (1) e COMPLEXO (1) — alinhados às 3 complexidades do dataset. |
| 3 | **Chain of Thought (CoT) via scratchpad implícito** | Bugs complexos exigem raciocínio multietapa (escolher persona, identificar valor, listar critérios, capturar edge cases). CoT melhora a qualidade sem poluir a resposta final. | Seção `## RACIOCÍNIO ESTRUTURADO` instrui o modelo a "pensar passo a passo" sobre 5 dimensões antes de escrever, mantendo o raciocínio interno. |
| 4 | **Explicit Rules** | Sem regras, o LLM tendia a usar linguagem vaga e a copiar literalmente o bug. Regras com `SEMPRE`/`NUNCA` reduzem variabilidade. | Bloco `## REGRAS` com 8 regras (template obrigatório, formato Given-When-Then, persona específica, preservação de detalhes técnicos, etc.). |
| 5 | **Explicit Output Format** | Critérios "soltos" são difíceis de testar; padronizar o formato facilita avaliação automática e leitura por humanos. | Blocos `## FORMATO DE SAÍDA` separando SIMPLES/MÉDIO (template inline) de COMPLEXO (seções `=== ... ===`), todos usando Given-When-Then em PT. |
| 6 | **Edge Case Handling** | Datasets reais têm relatos vagos, multi-plataforma, com severidade crítica ou de segurança. Sem instrução explícita, o modelo dispara o caminho feliz e ignora esses casos. | Seção `## EDGE CASES` com 4 regras (relato vago, multi-plataforma, severidade crítica, segurança/OWASP). |

> Bônus: separação **System vs User Prompt** (system traz contexto + regras + exemplos;
> human traz só `{bug_report}` e a instrução de execução) e **Positive Framing**
> (escrever o que o usuário quer ver funcionando, não "consertar o bug").

### Detecção pelos testes

O `tests/test_prompts.py` valida automaticamente que **6 técnicas** estão presentes
(o mínimo da spec é 2):

```
Role Prompting | Few-Shot Prompting | Explicit Rules
Edge Case Handling | Chain-of-Thought | Explicit Output Format
```

---

## B) Resultados Finais

> Esta seção será preenchida após rodar `python src/evaluate.py` (Fase 6 do plano).
> O prompt v2 **já está publicado** no LangSmith Hub e a validação estática (`pytest`)
> está verde.

### Prompt publicado

- **Hub:** [`maicors95test1/bug_to_user_story_v2`](https://smith.langchain.com/hub/maicors95test1/bug_to_user_story_v2)
- **Visibilidade:** público
- **Última publicação:** ver commit mais recente no Hub
- **Metadados:** descrição + 10 tags (`bug-analysis`, `user-story`, `product-owner`,
  `few-shot`, `chain-of-thought`, `role-prompting`, `edge-cases`, `given-when-then`,
  `agile`, `optimized`).

### Tabela comparativa v1 vs v2

| Métrica       | v1 (esperado) | v2 (obtido) | Δ |
|---------------|---------------|-------------|---|
| Helpfulness   | _a preencher_ | _a preencher_ | _a preencher_ |
| Correctness   | _a preencher_ | _a preencher_ | _a preencher_ |
| F1-Score      | _a preencher_ | _a preencher_ | _a preencher_ |
| Clarity       | _a preencher_ | _a preencher_ | _a preencher_ |
| Precision     | _a preencher_ | _a preencher_ | _a preencher_ |
| **Média**     | _a preencher_ | _a preencher_ | _a preencher_ |

> Como preencher: rode `python src/evaluate.py` com o `LLM_PROVIDER` configurado.
> Cada execução loga as 5 métricas no terminal e publica os resultados no projeto
> LangSmith definido em `LANGSMITH_PROJECT`.

### Evidências no LangSmith (placeholders)

- **Projeto LangSmith:** `https://smith.langchain.com/projects/prompt-optimization-challenge-resolved`
- **Dataset de avaliação:** 15 exemplos (5 simples / 7 médios / 3 complexos) criado
  automaticamente pelo `evaluate.py` em `{LANGSMITH_PROJECT}-eval`.
- **Screenshots:** (a adicionar após avaliação)
  - `docs/screenshots/01-overview.png` — visão geral das execuções
  - `docs/screenshots/02-metrics.png` — métricas com notas ≥ 0.8
  - `docs/screenshots/03-tracing.png` — tracing detalhado de ao menos 3 exemplos

---

## C) Como Executar

### Pré-requisitos

- Python 3.9+ (testado em 3.12).
- Conta no [LangSmith](https://smith.langchain.com/) com API key.
- API key de **um** provedor de LLM:
  - **Gemini (free):** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — limite 15 req/min, 1500 req/dia.
  - **OpenAI:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys) — custo estimado ~$1–5 para completar o desafio.

### 1. Clonar e instalar

```bash
git clone <seu-fork>.git
cd mba-ia-pull-evaluation-prompt

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar `.env`

```bash
cp .env.example .env
# edite o .env e preencha:
#   LANGSMITH_API_KEY=...
#   USERNAME_LANGSMITH_HUB=<seu-handle-no-hub>
#   LLM_PROVIDER=google     (ou openai)
#   GOOGLE_API_KEY=...      (ou OPENAI_API_KEY=...)
```

Para descobrir seu `USERNAME_LANGSMITH_HUB`: publique qualquer prompt no LangSmith Hub,
abra-o e clique no ícone de cadeado (🔒) — o handle aparece no topo.

### 3. Pull do prompt v1

```bash
python src/pull_prompts.py
# Saída: prompts/bug_to_user_story_v1.yml
```

### 4. Editar o v2 (opcional — já vem pronto)

```bash
# prompts/bug_to_user_story_v2.yml já está com a versão otimizada autoral.
# Edite à vontade para iterar — só lembre de fazer push depois.
```

### 5. Push do v2 para o Hub (público)

```bash
python src/push_prompts.py
# Publica {USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2 público,
# com descrição e 10 tags em PROMPT_METADATA.
```

### 6. Avaliação automática

```bash
python src/evaluate.py
# Cria dataset {LANGSMITH_PROJECT}-eval com os 15 exemplos,
# puxa o prompt v2 do Hub, roda contra o dataset,
# calcula F1/Clarity/Precision + derivadas Helpfulness/Correctness,
# imprime tabela e publica resultados no LangSmith.
```

Saída esperada (uma vez que todas as métricas estejam ≥ 0.8):

```
==================================================
Prompt: {seu_usuario}/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.94 ✓
  - Correctness: 0.96 ✓

Métricas Base:
  - F1-Score: 0.93 ✓
  - Clarity: 0.95 ✓
  - Precision: 0.92 ✓

✅ STATUS: APROVADO - Todas as métricas >= 0.8
```

### 7. Testes pytest

```bash
pytest tests/test_prompts.py -v
# 6 passed
```

---

## Critério de Aprovação

```
- Helpfulness >= 0.8
- Correctness >= 0.8
- F1-Score    >= 0.8
- Clarity     >= 0.8
- Precision   >= 0.8

MÉDIA das 5 métricas >= 0.8
```

**IMPORTANTE:** TODAS as 5 métricas devem estar `>= 0.8`, não apenas a média.

---

## Testes de validação

O arquivo [`tests/test_prompts.py`](tests/test_prompts.py) cobre, via `pytest`, os
6 testes obrigatórios da spec:

| Teste | Verifica |
|-------|----------|
| `test_prompt_has_system_prompt` | Campo `system` existe nas `messages` e não está vazio. |
| `test_prompt_has_role_definition` | Persona explícita (`"Você é..."`) no system prompt. |
| `test_prompt_mentions_format` | Formato exigido (Markdown, Given-When-Then ou User Story padrão). |
| `test_prompt_has_few_shot_examples` | Pelo menos um par `BUG REPORT / USER STORY` no system prompt. |
| `test_prompt_no_todos` | Nenhum `[TODO]`, `TODO`, `FIXME` ou `XXX` restante. |
| `test_minimum_techniques` | Pelo menos 2 técnicas de prompt engineering detectadas. |

---

## O que não alterar

Conforme regra da spec:

- `src/metrics.py` — lógica das 5 métricas via LLM-as-Judge.
- `src/utils.py` — helpers de YAML, env, LLM provider e formatação.
- `datasets/bug_to_user_story.jsonl` — 15 exemplos de referência.
- A lógica de `src/evaluate.py` (o limiar de aprovação foi alinhado em `0.8` conforme
  `.cursor/docs/specs.md` — mudança apenas de apresentação, sem mexer no cálculo das
  métricas).

---

## Iteração esperada

A spec orienta **3–5 iterações** entre `editar v2 → push → evaluate` até atingir o
critério. Na primeira passada com o v2 atual, a expectativa é passar com folga, mas
caso alguma métrica fique abaixo de 0.8, use o tracing do LangSmith para inspecionar
as execuções que falharam e refine o prompt (adicionar exemplo similar à falha,
reforçar uma regra, ajustar formato).

## Links úteis

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Repositório template do desafio](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)
