# Diário da Tarefa 5 — Árvore final e teste único

**Período:** 12/10/2026 a 25/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)

**Equipe:** Equipe 18  
**Scrum Master da tarefa:** [PREENCHER]  
**Repositório GitHub:** [PREENCHER link]

> A árvore que entra aqui é a da Tarefa 4. O baseline e o rótulo são os da Tarefa 2. O teste, guardado desde a Tarefa 2, é medido **uma vez**.
>
> Continua sendo uma árvore de decisão. O grupo entrega as regras, a matriz e o que a árvore faz num fluxo que ela não viu — desde que esse fluxo tenha a própria ficha de baseline, calculada só no período inicial dele.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Corte da Tarefa 2 e ficha de baseline | Tarefa 2 |
| **Entra** | Árvore ajustada e regras | Tarefa 4 |
| **Sai** | Teste único: matriz 3×3, F1 por classe, F1 macro | Entrega |
| **Sai** | Checagem de fluxo não visto, com baseline próprio | Entrega |
| **Sai** | Ficha da árvore (abaixo) e dicionário v0.4 igual às colunas usadas | Entrega |

Não há tarefa seguinte.

- [x] A profundidade não foi escolhida de novo olhando o teste
- [x] O baseline do teste não usou medição do próprio teste

---

## 1. Árvore que será medida

- [x] Critério, profundidade, mínimo de amostras na folha, colunas
- [x] Três regras em português, as mesmas da Tarefa 4 ou as revistas **antes** de abrir o teste
- [x] Confirmação de que país, IP, rota e RTT absoluto não estão na árvore

**Parâmetros:**  
Modelo aprovado para o projeto: floresta aleatória (a floresta da Tarefa 4), com os mesmos hiperparâmetros escolhidos na validação da Tarefa 4 e **sem nova busca**:

- 200 árvores, critério **Gini**, `max_depth` = 10, `min_samples_leaf` = 10, sem `class_weight`, semente 42
- Profundidade média obtida: 10,0 (todas as árvores chegam ao limite); folhas médias: 237,5 por árvore
- Alvo: classe do mesmo fluxo na 3ª medição seguinte (cerca de 12 minutos à frente, tolerância de 60 s)
- Ajuste (`fit`) **só no treino**, sem os dois fluxos novos: 92.655 linhas elegíveis em 74 fluxos (validação: 36.658 linhas)
- Parâmetros e uma assinatura do modelo foram gravados (`floresta_final_params.json`) **antes** de abrir o teste

**Colunas (8):**  
`z_robusto`, `z_robusto_t_menos_1`, `delta_z_robusto`, `perda_pct`, `jitter_relativo`, `n5_risco`, `n5_timeout`, `n5_aumento80`.  
País, IP, rota, `fluxo_id` e RTT absoluto (média, mediana e MAD em ms) **não** estão na floresta; o notebook confere isso por verificação automática. A classe atual (`classe`) só serve para a comparação com a persistência e nunca é feature.

**Regras:**  
Uma floresta não tem um conjunto único de regras. As três abaixo vêm de uma **árvore substituta rasa** (profundidade 3), treinada para imitar as previsões da floresta, com **fidelidade de 98,46%** na validação. São **ilustrativas** e foram geradas antes de abrir o teste. (A melhor folha de cada classe de uma das 200 árvores está em `floresta_final_regras.txt`.)

1. Se o `z_robusto` atual for maior que 3,50 **e** o da medição anterior (`z_robusto_t_menos_1`) for maior que 3,36, então **FALHA** (folha com 11.432 amostras; pureza de 98,2%).
2. Se o `z_robusto` atual for no máximo 2,49 **e** `n5_risco` for no máximo 3, então **OK** (folha com 72.311 amostras; pureza de 99,9%).
3. Se o `z_robusto` atual for maior que 2,86 **e** o da medição anterior estiver entre 2,29 e 3,36, então **RISCO** (folha com 1.674 amostras; pureza de 80,1%).

Importância das features na floresta: `z_robusto` 0,42 e `z_robusto_t_menos_1` 0,38 (cerca de 80% juntas), `n5_risco` 0,09, `delta_z_robusto` 0,07, `jitter_relativo` 0,03; `n5_aumento80`, `n5_timeout` e `perda_pct` ficam perto de zero.

## 2. Teste temporal (uma vez)

Fluxos conhecidos, período mais recente do Período B.

- [x] Matriz 3×3 com contagem, não só porcentagem
- [x] Precisão, recall e F1 de OK, RISCO e FALHA
- [x] F1 macro
- [x] Recall de FALHA e a troca RISCO ↔ FALHA comentados
- [ ] Dois casos: um acerto em caminho longo estável (classe OK) e um erro relevante (dizer o fluxo e o timestamp) — **Caso 1 pendente**

**Matriz:**  
54.582 linhas de teste em 74 fluxos conhecidos. Classes reais: OK 40.003 (73,3%), RISCO 5.588 (10,2%), FALHA 8.991 (16,5%).

Floresta (contagem):

| | prevista OK | prevista RISCO | prevista FALHA |
|---|---|---|---|
| **real OK** | 39.249 | 400 | 354 |
| **real RISCO** | 3.195 | 2.109 | 284 |
| **real FALHA** | 2.667 | 409 | 5.915 |

Precisão, recall e F1 por classe (a persistência, "repetir a classe atual", está na mesma passada, para comparação):

| Classe | Floresta: precisão / recall / F1 | Persistência: precisão / recall / F1 |
|---|---|---|
| OK | 0,870 / 0,981 / 0,922 | 0,890 / 0,890 / 0,890 |
| RISCO | 0,723 / 0,377 / 0,496 | 0,466 / 0,466 / 0,466 |
| FALHA | 0,903 / 0,658 / 0,761 | 0,697 / 0,696 / 0,697 |

Matriz da persistência (contagem): real OK = 35.612 / 2.369 / 2.022; real RISCO = 2.286 / 2.604 / 698; real FALHA = 2.122 / 611 / 6.258 (colunas: prevista OK / RISCO / FALHA).

**F1 macro no teste:** floresta **0,7264**; persistência **0,6842**. Para comparação, na validação a floresta teve 0,7168 e a persistência 0,6869.

**Leitura do recall de FALHA e da troca RISCO ↔ FALHA:**  
O recall de FALHA da floresta é de **65,8%**. Das 8.991 FALHAs reais, 2.667 (29,7%) foram previstas como OK e 409 como RISCO. A troca direta entre RISCO e FALHA é pequena (284 RISCOs previstos como FALHA e 409 FALHAs previstas como RISCO). O erro dominante é **confundir degradação com OK**: 57,2% dos RISCOs reais foram previstos como OK. O recall de FALHA da floresta é menor que o da persistência (0,658 contra 0,696), assim como o de RISCO (0,377 contra 0,466): a floresta deixou passar 5.862 de 14.579 degradações (40,2%), contra 4.408 (30,2%) da persistência. Em compensação, ela gerou bem menos falsos alarmes: marcou como RISCO ou FALHA 754 medições reais OK (1,9%), contra 4.391 (11,0%) da persistência.

**Casos:**

- **Caso 1 — acerto em caminho longo estável (classe OK):** [PENDENTE: colar aqui a linha impressa por `print(acerto.head(1)[cols_caso].to_string(index=False))`, com fluxo, timestamp, métricas, classe real e previsão.]
- **Caso 2 — erro relevante:** fluxo `6396|185.32.189.249` (Munique → Lisboa, mediana de 42,26 ms), medição de **18/09/2026 às 02:53:13 UTC**. O RTT estava em 42,26 ms (`z_robusto` = 0,01), sem perda e com `n5_risco` = 0, ou seja, estado atual normal (OK). Doze minutos depois (03:05:13 UTC) a classe real era **FALHA**, e tanto a floresta quanto a persistência previram OK. Trata-se de um evento abrupto, sem sinal prévio nas features da medição atual nem da anterior.

## 3. Fluxo que a árvore não viu

Separar um ou mais `fluxo_id` inteiros que não estejam no treino. A ficha desse fluxo sai só do período inicial dele (o mesmo piso: 1.500 RTT válidos; abaixo disso o fluxo não é avaliado).

- [x] O fluxo novo não aparece no treino
- [x] A mediana e o MAD não usam o trecho avaliado
- [x] Dizer se um caminho longo estável permaneceu OK e se uma degradação foi marcada RISCO ou FALHA
- [x] Se não houver fluxo sobrando com baseline suficiente, escrever isso e não forçar a conta (não se aplica: havia fluxos com ficha válida)

**Fluxos separados:**  
Escolha automática, usando **só treino e validação** (o teste não foi olhado). Os dois fluxos saíram inteiros do treino e da validação; a ficha deles é a do Período A (`status = ok` no `baseline_por_fluxo.csv`, piso de 1.500 RTT válidos atendido):

1. `6977|102.222.103.100` (BR→ZA, São Paulo → Cidade do Cabo, mediana de 339,49 ms): **caminho longo estável**. Em treino e validação, 99,3% das medições eram OK (1.748 de 1.761).
2. `6977|148.163.220.5` (BR→BR, São Paulo → São Paulo, mediana de 1,63 ms): **caminho curto com degradação** (94,3% OK, 55 RISCO e 45 FALHA em treino e validação).

**Resultado:**  
Os fluxos novos foram avaliados no Período B inteiro (alvo: classe 12 minutos à frente).

| Fluxo | Mediana | Linhas | Real OK | Prevista OK | Degradações reais | Detectadas (RISCO ou FALHA) |
|---|---|---|---|---|---|---|
| 6977\|102.222.103.100 (BR→ZA) | 339,49 ms | 2.505 | 99,1% | 100,0% | 22 | 0 |
| 6977\|148.163.220.5 (BR→BR) | 1,63 ms | 2.509 | 93,4% | 99,7% | 165 | 2 |

Matriz nos dois fluxos (contagem): real OK = 4.821 / 4 / 2; real RISCO = 98 / 0 / 0; real FALHA = 87 / 2 / 0 (colunas: prevista OK / RISCO / FALHA). F1 macro: floresta 0,3269 e persistência 0,3605.

- **O caminho longo estável permaneceu OK:** a floresta previu OK em 100% das linhas do fluxo BR→ZA (real: 99,1%).
- **A degradação quase não foi marcada:** apenas **2 das 187** degradações reais (1,1%) foram marcadas RISCO ou FALHA, ambas no fluxo curto; nenhuma das 22 no fluxo longo. Nesses fluxos novos, a floresta se comportou como um classificador de "sempre OK", e a persistência foi um pouco melhor (F1 macro de 0,3605 contra 0,3269).

## 4. O que declarar

- [x] Se a árvore só repete a tabela de rótulo, dizer isso: o rótulo foi feito com as mesmas métricas, então a árvore está aprendendo a política, não um ticket de roteador
- [x] Se o alvo for o estado 12 minutos à frente, comparar com a regra "repetir a classe atual". Sem ganho nessa comparação, o entregável é um **detector** do estado atual, não um preditor
- [x] Limitações: baseline fixo não acompanha troca de rota; rajada curta estima mal o jitter; Anchors não são a rede do campus

**A floresta aprende a política de rotulagem.** O rótulo foi construído com as mesmas métricas que a floresta recebe (`z_robusto`, perda, contagens das últimas 5 medições). As regras lidas da árvore substituta usam os mesmos cortes da tabela de rótulo (FALHA com `z_robusto` ≥ 3,5; RISCO entre 2 e 3,5). Ela não aprende um ticket de roteador nem um evento real de rede.

**Comparação com "repetir a classe atual" (critério declarado antes do teste: F1 macro).** No teste, a floresta supera a persistência em F1 macro (0,7264 contra 0,6842, diferença de +0,0422), então pode ser chamada de **preditor, mas conservador e com ressalvas**:

- O ganho vem principalmente da **precisão**: a floresta gera muito menos falsos alarmes (754 contra 4.391 OK reais marcados como RISCO ou FALHA).
- Em contrapartida, tem **recall menor** em RISCO (0,377 contra 0,466) e em FALHA (0,658 contra 0,696), e a acurácia balanceada também é menor (0,672 contra 0,684): ela deixa passar mais degradações.
- Nos fluxos novos, ela quase não detectou degradação (2 de 187), e a persistência teve F1 macro maior.
- O F1 macro do teste (0,7264) ficou próximo ao da validação (0,7168), o que indica que a escolha dos hiperparâmetros não foi superajustada à validação.

**Limitações:**

- Baseline fixo não acompanha troca de rota: se o caminho muda depois do Período A, o desvio vira "degradação".
- Rajada curta estima mal o jitter e a perda: com 3 pacotes por medição, 1 pacote perdido já dá 33% e é FALHA pela tabela, evento abrupto que a floresta não antecipa (ver Caso 2).
- Rotas curtas têm MAD minúsculo, e desvios de décimos de milissegundo geram `z_robusto` alto.
- Os dois fluxos novos têm a **mesma origem** (probe 6977), que continua no treino com outros destinos, e somam apenas 187 degradações. A conclusão sobre generalização é frágil.
- O teste cobre o fim do Período B, que inclui o fim de semana, enquanto o treino é majoritariamente de dias úteis.
- As regras em português são ilustrativas; a previsão oficial é a votação das 200 árvores.
- Anchors do RIPE Atlas não são a rede do campus.

## 5. Ficha da árvore

| Campo | Conteúdo |
|---|---|
| Problema | Classe OK, RISCO ou FALHA pelo desvio ao baseline do fluxo (alvo: 12 minutos à frente) |
| Unidade | Uma medição de um `fluxo_id` no Período B |
| Baseline | Período A, mediana e MAD, piso de 1.500 RTT válidos |
| Colunas | `z_robusto`, `z_robusto_t_menos_1`, `delta_z_robusto`, `perda_pct`, `jitter_relativo`, `n5_risco`, `n5_timeout`, `n5_aumento80` |
| Árvore | Floresta aleatória: 200 árvores, critério Gini, `max_depth` 10, `min_samples_leaf` 10, profundidade média 10,0, folhas médias 237,5 por árvore, semente 42 |
| Teste (uma vez) | F1 macro 0,7264; recall de FALHA 0,6579 (persistência: 0,6842 e 0,6960) |
| O que ela não faz | Não classifica distância. Não opera em fluxo sem ficha. Não antecipa degradações abruptas e detectou poucas nos fluxos novos |
| Como reproduzir | `requirements.txt`, notebook `tarefa5_arvore_final.ipynb`, `config/` (semente 42) |

**Dicionário v0.4:** [PREENCHER link do arquivo no repositório]

## 6. Scrum e diário

- [ ] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Bruno | Montei o notebook final da Tarefa 5, escolhi os fluxos novos, congelei a floresta e medi o teste uma única vez; reuni as métricas, os casos, a ficha e o dicionário v0.4 | Ambiente sem o `joblib` (kernel diferente do das tarefas anteriores); saídas longas cortadas no notebook; definir o critério de ganho sobre a persistência antes de abrir o teste | Manter a trava de teste único e o congelamento do modelo; no futuro, separar fluxos novos de origens diferentes e testar uma árvore única para ter regras exatas |
| [PREENCHER integrante] | | | |
| [PREENCHER integrante] | | | |

---

## Rubrica — Tarefa 5 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Árvore final legível | 1,0 | Regras em português, colunas relativas, parâmetros da Tarefa 4 | | |
| Teste único | 1,5 | Matriz 3×3 em contagem, F1 por classe, F1 macro, casos curto/longo; teste não escolheu a árvore | | |
| Fluxo novo com baseline próprio | 1,0 | Ficha só no período inicial; ou limitação declarada se faltou fluxo | | |
| Ficha + diário | 0,5 | Ficha preenchida e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
