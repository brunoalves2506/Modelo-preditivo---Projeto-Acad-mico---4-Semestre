# Correção — Coleta de dados via API

## Identificação

| Campo | Informação |
|---|---|
| Curso / Disciplina | Ciência da Computação / Estruturas de Dados II |
| Turma | Noite |
| Projeto integrador | Modelo preditivo de rede |
| Equipe / Integrantes | Grupo 18 — Bruno Alves Ribeiro de Souza; Wendel Henrique da Silva Rocha; Victoria Agatha Rodrigues Fagundes; Samuel de Oliveira Santos; Pedro Henrique Alexandre da Silva; Igor da Silva Alves Correa |
| Repositório | https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre |
| Notebook avaliado | `notebook/coleta_de_dados.ipynb` (30 células; saídas da coleta salvas; `execution_count` 5–6 e 31–35; célula de verificação com `execution_count` 1 e `NameError`) |
| Materiais complementares | `data_ripe_atlas/raw/ripe_atlas_m1009_20260914T030005Z.{json,csv,_metadata.json}`; `docs/memorando_de_decisao_grupo18.md`; `README.md`. Há também célula Colab, não usada na corrida salva |
| Avaliador(a) | Andrea Ono Sakai |
| Data da avaliação | 20/09/2026 |
| Método | Inspeção estática do `.ipynb`, das saídas já registradas e dos arquivos `raw` versionados. A coleta não foi reexecutada (volume alto). A célula Colab não foi executada. |

---

## Rubrica de avaliação — total: 4,00 pontos

| Critério | O que deve ser avaliado | Nota máxima | Nota atribuída |
|---|---|---:|---:|
| 1. Organização e executabilidade do notebook | Sequência compreensível, parâmetros antes do uso, saídas coerentes, ordem de execução auditável. | 0,50 | 0,40 |
| 2. Segurança de credenciais e acesso à API | Sem segredo exposto; endpoint, parâmetros, timeout e status HTTP tratados. | 0,50 | 0,45 |
| 3. Unidade de observação e integridade | Cada linha identificável; `sent`/`rcvd`/`result`; distinção timeout vs RTT; validação mínima. | 0,50 | 0,40 |
| 4. Fonte, estratégia e cobertura temporal | Medição justificada; recorte delimitado; cobertura não reduzida a “número de linhas”. | 0,50 | 0,35 |
| 5. Preservação do bruto e salvamento | JSON original, camada tabular e metadados; destino dos arquivos indicado. | 0,50 | 0,50 |
| 6. Reprodutibilidade e idempotência | Parâmetros configuráveis; reexecução sem sobrescrita silenciosa; dependências reconhecíveis. | 0,50 | 0,40 |
| 7. Documentação das decisões e limitações | Markdown com ID, intervalo, formato, limitações da medição pública e volume coerente. | 0,50 | 0,40 |
| 8. Qualidade da entrega e registro de contribuições | Checklist, resumo final e contribuições individuais específicas com evidência. | 0,50 | 0,45 |
| **Nota final do grupo** | **Soma das notas atribuídas** | **4,00** | **3,35 / 4,00** |

Critérios 1 a 7 (iguais para o grupo): **2,90**. O critério 8 entra na nota do grupo; a evidência de cada aluno é pontuada à parte (0 a 4).

---

## A. Síntese da coleta realizada

O notebook, baseado no template de ingestão, identifica o Grupo 18 (data da coleta 14/09/2026) e justifica a medição pública **1009**: ping ICMP periódico ao A-root `198.41.0.4`, intervalo declarado de **0,45 h (27 minutos)**, CSV. Não há chave, token ou senha nas células ou saídas. Os parâmetros no código usam Unix UTC, `TIMEOUT_REQUISICAO = 60` e `Path("../data_ripe_atlas")`. Existe célula `google.colab` para Drive, sem execução nesta corrida.

As saídas da consulta mostram HTTP **200**, **89.071** registros e `DataFrame` 89.071 × 25, com `prb_id`, `timestamp`, `sent`, `rcvd`, `result`, `avg` e `dst_addr` `198.41.0.4`. O recorte impresso é 2026-09-14 **02:33–03:00 UTC** (`start` 1789353181, `stop` 1789354801). O salvamento imprimiu `..\data_ripe_atlas\raw\ripe_atlas_m1009_20260914T030005Z.{json,csv,_metadata.json}`. Os três arquivos estão no repositório; o metadados confirma HTTP 200, 89.071 registros e `coletado_em_utc` 2026-09-14T03:00:05Z. A célula de verificação (`assert` dos caminhos) foi reexecutada isoladamente (`In[1]`) e registrou `NameError: name 'caminho_json' is not defined`.

O Markdown da medição fala em volume alto de probes e em amostra próxima de 100 mil registros. O comentário de `HORAS_COLETA` menciona “2 a 5% de falhas de conexão”, sem célula que meça isso. O checklist afirma que não houve limpeza, agregação, rotulação ou treino.

---

## B. Quadro de decisões técnicas

| Decisão ou aspecto | Evidência encontrada | Classificação | Análise técnica | Orientação à equipe |
|---|---|---|---|---|
| Organização do notebook | Título, pipeline, identificação, tabela de decisões, seções 3–12, contribuições, checklist | Boa escolha técnica | A sequência configuração → API → inspeção → `DataFrame` → salvamento → resumo está documentada. Há célula 10.5 de pré-visualização. | Alinhar o comentário de `HORAS_COLETA` ao que o `DataFrame` realmente mostra (perda/timeout), não a uma taxa percentual não calculada. |
| Executabilidade | Saídas da coleta coerentes; parâmetros com saída e `execution_count` nulo; verificação com `NameError`; Colab não executado; contadores 5–6 depois 31–35 | Escolha aceitável com ressalvas | A ingestão local ocorreu e gravou arquivos. A ordem completa a partir de kernel novo **não** está auditável: a verificação quebrou ao rodar sozinha e a célula Colab permanece no caminho. | Reiniciar o kernel, escolher **só** o bloco local, executar até o `assert` e preservar os contadores. |
| Segurança de credenciais | Medição pública; nenhum segredo em código, URL ou saídas | Boa escolha técnica | Nada a revogar. A célula só lê `/results/`. | Manter assim. Não colar chave se passarem a criar medição. |
| Acesso à API | `/api/v2/measurements/1009/results/`; Unix UTC; timeout 60 s; `raise_for_status`; tipo lista e lista vazia rejeitados; HTTP 200 nas saídas e no metadados | Boa escolha técnica | Endpoint, parâmetros e falhas HTTP estão tratados e evidenciados. | Registrar no Markdown que a equipe não controla sondas, `step` (240 s na amostra) nem o anycast do A-root. |
| Unidade de observação | Uma linha = resultado de uma sonda; `sent`/`rcvd`/`result` no JSON e no `DataFrame` | Boa escolha técnica | A amostra tem três RTTs, `sent = 3`, `rcvd = 3`. Pacotes individuais permanecem em `result`. | Escrever essa frase no Markdown. Não agregar antes de decidir a janela. |
| Cobertura temporal | 27 min (0,45 h); 89.071 linhas; `step` 240 s na amostra; sem pontos por `prb_id` no notebook | Escolha aceitável com ressalvas | Muitas sondas, poucos instantes por fluxo. Volume de linhas não é duração nem história por enlace. | Declarar a coleta como amostra espacial de 27 minutos. Baseline por sonda exigiria nova janela, não reprocessamento só. |
| Integridade dos dados | `info()` nas saídas (nulos em `mver` e `ttl`); sem célula de duplicata nem de `avg` negativo / `"x"` em `result` | Escolha aceitável com ressalvas | Tipos e contagens existem. Falta distinguir timeout, perda e RTT baixo. | Uma célula de validação sobre o CSV já versionado resolve, sem nova coleta. |
| Preservação do bruto | JSON original + CSV + metadados no Git, sem agregação no notebook | Boa escolha técnica | A resposta da API não foi substituída por médias. O metadados liga URL, parâmetros, horário e volume aos nomes. | Não apagar esses três arquivos. Calcular jitter depois, a partir do JSON/`result`. |
| Salvamento | `Path("../data_ripe_atlas")`; timestamp no nome; prints dos três caminhos; arquivos no repositório | Boa escolha técnica | O `.ipynb` e o Git mostram o destino. A verificação por `assert` falhou numa reexecução isolada, mas os arquivos existem. | Manter o caminho relativo. Rodar o `assert` na mesma sessão da gravação. |
| Idempotência | Timestamp UTC `20260914T030005Z` no nome | Boa escolha técnica | Nova execução cria outro prefixo; a coleta de 14/09 permanece. | Dizer no resumo que `...030005Z` é a oficial desta entrega. |
| Reprodutibilidade | Parâmetros no topo; caminho local configurável; célula Colab alternativa; sem versões de biblioteca | Escolha aceitável com ressalvas | Quem clonar o repo e usar o `Path` local consegue repetir a lógica. A célula Colab, se executada sem editar, muda o destino. Dependências não têm versão no notebook. | Deixar um único `PASTA_PROJETO` no topo e documentar `requests`/`pandas`. |
| Anycast / destino único | Destino `198.41.0.4` (A-root) justificado como ping público de alto volume | Ponto a pensar e rever | O mesmo endereço anycast é servido por instâncias distintas. RTT de ~4 ms e ~98 ms na amostra do `head` não medem o mesmo caminho. | Documentar anycast. Não usar limiar global de RTT entre sondas como se fosse o mesmo enlace. |
| Volume versus justificativa | 89.071 nas saídas e no metadados; texto mira ~100 mil; comentário de 2–5% de falhas | Escolha aceitável com ressalvas | O número da corrida está coerente entre notebook e arquivo. A taxa de “falhas de conexão” não foi medida nesta ingestão. | Tirar a percentagem do parâmetro até haver célula que a calcule sobre `rcvd`/`sent`/`result`. |

---

## C. Boas escolhas que devem ser mantidas

- **Notebook em etapas**, com ID, intervalo e formato no Markdown.
- **Consulta pública sem credencial**, timeout, `raise_for_status` e recusa de lista vazia.
- **Unix UTC** e distinção entre intervalo da medição e `coletado_em_utc`.
- **Granularidade bruta** (`prb_id`, `sent`, `rcvd`, `result`) no `DataFrame`.
- **JSON + CSV + metadados com timestamp**, versionados em `data_ripe_atlas/raw/`.
- **Escopo do checklist:** sem rotular na ingestão.

---

## D. Escolhas aceitáveis com limitações

- **Caminho local `Path("../data_ripe_atlas")`**, com célula Colab presente mas não usada. Válido neste clone. Quem abrir só no Colab precisa da outra célula — e o raw oficial desta entrega já está no Git local, não no Drive.
- **27 minutos na 1009.** Bom para inspecionar a API e obter dezenas de milhares de linhas. Fraco como série por sonda (`step` 240 s).
- **CSV tabular.** Adequado à inspeção. O JSON continua sendo a cópia fiel da API.
- **Um destino (A-root).** Serve para estudar aquele alvo público. Não generaliza “a rede” se RTTs de sondas distantes forem misturados.

---

## E. Pontos que precisam ser pensados e revistos

### 1. Críticos

Não há chave exposta. O raw de 14/09 está no repositório. A coleta **não é irrecuperável**. O `NameError` da célula 10 é de reexecução fora de ordem, não evidência de que os arquivos não existam.

### 2. Importantes

- Anycast do A-root não discutido no Markdown.
- 27 minutos apresentados junto de um volume grande, sem cobertura por `prb_id`.
- Comentário de 2–5% de falhas sem suporte nas células.
- Contadores e célula de verificação impedem auditar uma corrida limpa do zero.
- Artigo Medium como evidência de Bruno é fraco para a atividade declarada (escolha de 0,45 h / execução).

### 3. Melhorias recomendadas

- Célula de metadados da medição 1009 (intervalo, `packets`, destino, anycast).
- Dicionário das 25 colunas no próprio notebook.
- `execution_count` contínuo após kernel novo.
- Versões de `requests` e `pandas`.

Nada disso exige abandonar a 1009 nem nova coleta obrigatória, salvo se quiserem mais profundidade temporal.

---

## F. Perguntas orientadoras para a equipe

1. Com `step` 240 s e 27 minutos, quantos pontos tem a sonda com menos dados?
2. O A-root é anycast. O que um `avg` de 4 ms versus 98 ms significa se as sondas estão em regiões diferentes?
3. O comentário de `HORAS_COLETA` fala em 2–5% de falhas. Qual coluna ou regra produz essa taxa neste `df_raw`?
4. A célula de verificação falhou com `caminho_json` indefinido. Qual sequência, a partir do kernel novo, chega ao `assert` sem passo manual?
5. A coleta oficial é `ripe_atlas_m1009_20260914T030005Z` do Git. Se o notebook rodar no Colab, esse arquivo continua sendo a base?
6. `timestamp` ou `stored_timestamp` será o eixo das janelas?
7. O artigo da Medium justifica 27 minutos desta medição pública, ou só um volume genérico de treino?
8. Reiniciando o kernel, a célula Colab deve ser pulada?

---

## G. Evidências que faltaram no notebook

- Corrida com `execution_count` sequencial e `assert` da seção 10 na mesma sessão da gravação.
- Célula de cobertura (sondas distintas, min/mediana/máximo de pontos por `prb_id`, `rcvd = 0`, timeouts).
- Metadados da medição 1009 lidos da API (`GET /measurements/1009/`), inclusive anycast.
- Dicionário das 25 colunas.
- Retirada ou cálculo da percentagem de “falhas” no parâmetro.
- Versões das bibliotecas.
- Evidência mais direta da escolha de 0,45 h para Bruno (commit, célula, saída), além do link Medium.

Os arquivos `raw` **não faltam** no repositório; falta amarrar a verificação executável a eles.

---

## H. Parecer formativo final

A coleta está **consistente**. A **principal qualidade** é a ingestão pública da 1009, em UTC, com HTTP 200, 89.071 registros, granularidade bruta e tríade JSON/CSV/metadados versionada, sem chave. O **principal risco** é tratar 27 minutos rumo a um destino anycast como série suficiente, e deixar a executabilidade integral sem uma corrida limpa (verificação com `NameError`). A **prioridade imediata** é documentar anycast e cobertura por sonda, e reexecutar do kernel novo só no caminho local. A preparação para a próxima etapa é **parcial**: o bruto permite regras sobre perda/timeout, mas o histórico por fluxo é curto. O notebook é **parcialmente executável**: as células de coleta têm saídas coerentes e arquivos no Git; a ordem completa não está demonstrada numa única sessão.

---

## Notas de evidência individual (0 a 4)

Escala da evidência no notebook:

- **4,00:** atividade específica, com verbos de ação, ligada a células ou arquivos, e evidência conferível (commit, arquivo no repo ou saída que identifique o aluno).
- **3,00:** relato específico e ligado a uma seção; evidência citada (Drive/Notion), não verificada neste parecer.
- **2,00:** contribuição identificável, porém genérica ou com evidência fraca.
- **1,00:** só menção vaga de etapa.
- **0,00:** ausente ou em branco.

| Integrante | O que registrou no notebook | Tempo | Evidência citada | Nota (0–4) | Motivo |
|---|---|---|---|---:|---|
| Bruno Alves Ribeiro de Souza | Análise do tempo de coleta (0,45 h), execução e célula 10.5 | 2h | Artigo Medium sobre volume para ML | 2,50 | Atividade ligada a `HORAS_COLETA` e à execução; o artigo é evidência fraca da tarefa feita no notebook. |
| Wendel Henrique da Silva Rocha | Identificação, decisões, path local, parâmetros e validação da resposta | 2h00 | SHAs `e85af6fecaa8d9e49913c0cac0def5522b326212` e `98b60765225b28cad1beeb13e95cfc12a6ddda43` | 3,50 | Relato específico por seção, com hashes conferíveis. |
| Victoria Agatha Rodrigues Fagundes | Seção 1 do memorando; correção do rótulo Colab/local e limpeza de erro na seção 4 | 1h30 | Commit `e1a65943` | 3,50 | Ação amarrada ao notebook e hash conferível. |
| Samuel de Oliveira Santos | Pesquisa da API, revisão da documentação e estudo de requisição | 2h | Repositório externo de evidências | 2,00 | Contribuição identificável, genérica em relação às células; evidência fora do repo do projeto. |
| Pedro Henrique Alexandre da Silva | QA: alinhamento de parâmetros, métricas do JSON, registro final, README e memorando | 3h15 | Commit `a7213faf` | 3,50 | Auditoria descrita com produto e hash conferível. |
| Igor da Silva Alves Correa | Registro final, checklist e correções no notebook | 1h30 | SHAs `0bf1aa2f88120fc2b89eedcd891b299c15874ba3` e `4640d6d112bf6c2518d972e23c403ea1e2dca238` | 3,00 | Seções nomeadas e hashes; o relato é mais curto que o dos commits de Wendel/Victoria/Pedro. |

Nota individual = critérios 1 a 7 do grupo (**2,90**) + evidência ÷ 8.

| Integrante | Grupo (1–7) | Evidência (0–4) | Contribuição (0–0,50) | Nota individual |
|---|---:|---:|---:|---:|
| Bruno Alves Ribeiro de Souza | 2,90 | 2,50 | 0,31 | 3,21 |
| Wendel Henrique da Silva Rocha | 2,90 | 3,50 | 0,44 | 3,34 |
| Victoria Agatha Rodrigues Fagundes | 2,90 | 3,50 | 0,44 | 3,34 |
| Samuel de Oliveira Santos | 2,90 | 2,00 | 0,25 | 3,15 |
| Pedro Henrique Alexandre da Silva | 2,90 | 3,50 | 0,44 | 3,34 |
| Igor da Silva Alves Correa | 2,90 | 3,00 | 0,38 | 3,28 |
