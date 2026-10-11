# Diário da Tarefa 3 — Primeira árvore de decisão

**Período:** 28/09/2026 a 04/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)

**Equipe:** 18 — Bruno Alves Ribeiro de Souza, Igor da Silva Alves Correa, Pedro Henrique Alexandre da Silva, Samuel de Oliveira Santos, Victoria Agatha Rodrigues Fagundes, Wendel Henrique da Silva Rocha  
**Scrum Master da tarefa:** ____________ *(preencher)*  
**Repositório GitHub:** [Modelo Preditivo - Projeto Académico](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre.git)

> Tarefa 1 coletou. Tarefa 2 fez o baseline e o rótulo. Esta tarefa **não refaz** a ficha nem a tabela de classes.
>
> O modelo é uma **árvore de decisão**. O entregável é a árvore: atributos de cada divisão, profundidade, folhas e as regras lidas em português. Não é um desfile de algoritmos.
>
> A árvore oficial usa só métricas relativas ao baseline do fluxo. Uma segunda árvore, de contraste, pode ver a rota ou o RTT absoluto — só para mostrar que ela aprende distância. Essa árvore de contraste **não** é o modelo do projeto.

> **Coleta usada:** v2 (`data_ripe_atlas/raw/v2/`). **Teste:** o arquivo `teste.csv` **não foi aberto** nesta tarefa; só foram conferidos o número de linhas (57.312) e as datas por fluxo, para confirmar o corte. Nenhum rótulo nem métrica do teste foi lido.  
> **Código:** `notebook/arvore/tarefa3_arvore_inicial.ipynb` (reproduz todos os números abaixo). **Entradas:** `data_ripe_atlas/processed/{treino,validacao,baseline_por_fluxo}.csv`. **Saídas:** `data_ripe_atlas/models/{arvore_oficial.joblib,arvore_oficial_params.json,arvore_oficial_texto.txt}`.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Ficha de baseline, dataset rotulado, corte temporal | Tarefa 2 — **os mesmos** |
| **Sai** | Árvore treinada só no treino, com profundidade e critério registrados | Tarefa 4 mexe nesta árvore, não no rótulo |
| **Sai** | Regras da árvore em texto e matriz 3×3 (OK, RISCO, FALHA) | Tarefa 4, para atacar o erro |
| **Sai** | Árvore de contraste (com rota ou RTT absoluto) e a frase do que ela aprendeu | Prova de que o modelo oficial não segue esse atalho |

**Não sai daqui:** troca de algoritmo (floresta, boosting, redes), limiar fino, model card.

- [X] Treino, validação e teste são os da Tarefa 2 — treino 95.406, validação 38.138 e teste 57.312 linhas (os mesmos N da Tarefa 2); classes do treino (OK 72.857 / RISCO 6.582 / FALHA 15.967) e da validação (27.180 / 3.388 / 7.570) idênticas às do diário da Tarefa 2; em todos os fluxos, treino < validação < teste no tempo; só Período B
- [X] A ficha de baseline não foi recalculada com o Período B — a ficha repetida em cada linha (`mediana`, `MAD`, `jitter_tipico`) é constante por fluxo e igual ao `baseline_por_fluxo.csv` do repositório (76 fluxos); esse baseline coincide com a ficha calculada só no Período A

---

## 1. Colunas que a árvore oficial pode usar

Entram: `z_robusto`, `aumento_pct`, `jitter_relativo`, `perda_pct`, `timeout_atual`, `n5_timeout`, `n5_aumento80`, `n5_risco`.

Não entram: país, IP, `rota_id`, `fluxo_id`, nome do destino, RTT em milissegundos no lugar das métricas relativas.

- [X] Lista de colunas do treino colada no diário
- [X] Conferido que a classe (`OK` / `RISCO` / `FALHA`) é o alvo, não uma feature

**Colunas usadas:** `z_robusto`, `aumento_pct`, `jitter_relativo`, `perda_pct`, `timeout_atual`, `n5_timeout`, `n5_aumento80`, `n5_risco` (8 colunas). **Alvo:** `classe`.

**Colunas do arquivo de treino que ficam de fora** (auditoria ou proibidas): `fluxo_id`, `prb_id`, `dst_addr`, `measurement_id`, `timestamp`, `datetime_utc`, `avg`, `rtt_min_ms`, `rtt_max_ms`, `sent`, `rcvd`, `jitter_ms`, `pais_origem`, `pais_destino`, `rota`, `periodo`, `mediana`, `MAD`, `jitter_tipico`, `crit_risco_ind`, `conjunto`.

**Valores vazios (treino):** `z_robusto` e `aumento_pct` vazios em 197 linhas (timeouts, RTT ausente) e `jitter_relativo` vazio em 261 (rajadas com menos de 2 respostas). Foram **mantidos vazios**, sem trocar por 0: o scikit-learn (>= 1.3) aceita `NaN` nas features da árvore.

## 2. A árvore

- [X] Uma árvore de decisão (CART: Gini ou entropia — declarar qual)
- [X] `max_depth` e `min_samples_leaf` escolhidos olhando **só a validação**, não o teste
- [X] Semente registrada se o treino for estocástico
- [X] Ajuste (`fit`) só no treino
- [X] Profundidade real, número de folhas e as primeiras divisões descritas
- [X] Pelo menos três regras no formato “se métrica ≤ limiar e … então classe”, copiadas da árvore (não inventadas)

**Critério, profundidade máxima pedida, profundidade obtida, folhas:**

- **Critério:** CART com índice de **Gini** (`DecisionTreeClassifier`, scikit-learn 1.9.1).
- **Semente:** `random_state = 42`.
- **Escolha dos hiperparâmetros (só validação):** grade de 11 profundidades (2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20) × 8 tamanhos mínimos de folha (1, 5, 10, 20, 50, 100, 200, 500) = 88 árvores, cada uma ajustada no treino e comparada pelo **F1 macro da validação**. O melhor F1 macro foi 0,9999 (`max_depth` 7, 17 folhas). Como a árvore precisa ser lida em português, aceitou-se até 0,005 abaixo do melhor (54 configurações) e ficou a de **menos folhas**.
- **Escolhida:** `max_depth` = **4**, `min_samples_leaf` = **100**. **Profundidade obtida: 4. Folhas: 8.** F1 macro na validação: 0,9969 (no treino, só referência: 0,9967).

| Profundidade pedida | Melhor F1 macro (validação) | Folhas |
|---|---|---|
| 2 | 0,6416 | 3 |
| 3 | 0,9357 | 5 |
| **4** | **0,9970** (com `min_samples_leaf` = 100: 0,9969) | **8** |
| 5 | 0,9980 | 12 |
| 6 | 0,9989 | 15 |
| 7 | 0,9999 | 17 |
| 8 ou mais | 0,9997 | 18 |

**Primeiras divisões:** a raiz é `z_robusto ≤ 3,50`. O ramo `> 3,50` já é folha FALHA. No ramo `≤ 3,50`, a segunda divisão é `n5_risco ≤ 1,5`. Importância das features: `z_robusto` 0,7516; `n5_risco` 0,1497; `jitter_relativo` 0,0901; `perda_pct` 0,0086; as demais, perto de 0 (`aumento_pct`, `n5_timeout` e `timeout_atual` não aparecem em nenhuma divisão).

```
|--- z_robusto <= 3.50
|   |--- n5_risco <= 1.50
|   |   |--- perda_pct <= 16.67
|   |   |   |--- n5_aumento80 <= 0.50
|   |   |   |   |--- class: OK
|   |   |   |--- n5_aumento80 >  0.50
|   |   |   |   |--- class: OK
|   |   |--- perda_pct >  16.67
|   |   |   |--- class: FALHA
|   |--- n5_risco >  1.50
|   |   |--- z_robusto <= 1.99
|   |   |   |--- jitter_relativo <= 3.00
|   |   |   |   |--- class: OK
|   |   |   |--- jitter_relativo >  3.00
|   |   |   |   |--- class: RISCO
|   |   |--- z_robusto >  1.99
|   |   |   |--- z_robusto <= 2.02
|   |   |   |   |--- class: RISCO
|   |   |   |--- z_robusto >  2.02
|   |   |   |   |--- class: RISCO
|--- z_robusto >  3.50
|   |--- class: FALHA
```

**Regras lidas da árvore** (cada regra é o caminho da raiz até uma folha; as contagens são do treino):

1. **SE** `z_robusto` > 3,50 **ENTÃO FALHA** — 15.659 medições, 100,0% FALHA.
2. **SE** `z_robusto` ≤ 3,50 **e** `n5_risco` ≤ 1 **e** `perda_pct` ≤ 16,67 **e** `n5_aumento80` ≤ 0 **ENTÃO OK** — 65.840 medições, 100,0% OK.
3. **SE** `z_robusto` ≤ 3,50 **e** `n5_risco` ≥ 2 **e** `z_robusto` > 1,99 **e** `z_robusto` > 2,02 **ENTÃO RISCO** (isto é, `z_robusto` entre 2,02 e 3,50 com pelo menos 2 medições de risco nas últimas 5) — 4.278 medições, 99,6% RISCO.
4. **SE** `z_robusto` ≤ 3,50 **e** `n5_risco` ≥ 2 **e** `z_robusto` ≤ 1,99 **e** `jitter_relativo` > 3,00 **ENTÃO RISCO** — 2.228 medições, 99,2% RISCO.
5. **SE** `z_robusto` ≤ 3,50 **e** `n5_risco` ≤ 1 **e** `perda_pct` > 16,67 **ENTÃO FALHA** — 156 medições, 100,0% FALHA.

*(Os limiares de contagem aparecem como inteiros: `n5_risco ≤ 1,5` na árvore vira `n5_risco ≤ 1`.)*

**Observação:** a primeira divisão da árvore (`z_robusto ≤ 3,50`) é a linha 3 da tabela de rotulagem da Tarefa 2, e `jitter_relativo > 3` e `z_robusto ≥ 2` também vêm dela. Como o rótulo foi definido a partir destas mesmas métricas relativas, a árvore está em boa parte **reencontrando a regra do rótulo**; o F1 alto mede isso, e não a capacidade de prever degradação futura.

## 3. Leitura do erro

No bloco de **validação** (o teste ficou fechado):

- [X] Matriz 3×3 com contagem
- [X] Precisão, recall e F1 de OK, RISCO e FALHA
- [X] F1 macro
- [X] Acurácia sozinha não decide: com maioria OK, ela fica alta mesmo errando FALHA
- [X] Dois erros concretos: uma medição de caminho longo estável que tenha caído em FALHA, ou uma FALHA de caminho curto que tenha caído em OK. Se não houver, dizer que o caso não apareceu na validação

**Matriz e F1 macro (validação):**

| | prevista OK | prevista RISCO | prevista FALHA |
|---|---|---|---|
| **real OK** | 27.172 | 8 | 0 |
| **real RISCO** | 11 | 3.377 | 0 |
| **real FALHA** | 41 | 12 | 7.517 |

| Classe | Precisão | Recall | F1 | Medições |
|---|---|---|---|---|
| OK | 0,9981 | 0,9997 | 0,9989 | 27.180 |
| RISCO | 0,9941 | 0,9968 | 0,9954 | 3.388 |
| FALHA | 1,0000 | 0,9930 | 0,9965 | 7.570 |

**F1 macro (validação): 0,9969.** Acurácia: 99,81% (só contexto). Como 71,27% da validação é OK, prever sempre OK já daria 71,27% sem acertar nenhuma FALHA; por isso o critério é o F1 por classe e o F1 macro. Total de erros: 72 em 38.138 (0,19%): FALHA→OK 41, FALHA→RISCO 12, RISCO→OK 11, OK→RISCO 8.

**Erros concretos (fluxo, timestamp, métricas, classe verdadeira, classe da árvore):**

Os dois casos que o roteiro cita **não apareceram na validação**: (a) caminho longo estável (mediana > 150 ms, |`z_robusto`| < 2, sem perda) previsto como FALHA — 0 casos; (b) FALHA de caminho curto (mediana < 5 ms) prevista como OK — 0 casos. Dois erros reais, dos pares mais importantes:

1. **FALHA que caiu em OK** — `6659|103.179.107.33` (caminho longo, mediana do fluxo 236,60 ms), 17/09/2026 02:20:07 UTC: RTT 237,09 ms, `z_robusto` 0,27, `aumento_pct` 0,21%, `jitter_relativo` 0,05, `perda_pct` **33,33%**, `n5_timeout` 0, `n5_aumento80` 0, `n5_risco` 2. **Classe verdadeira: FALHA** (linha 1 da Tarefa 2: `perda_pct` ≥ 10). **Árvore: OK.** Motivo: com `n5_risco` ≥ 2 a medição entra no ramo da direita, e esse ramo não consulta `perda_pct`. Dos 41 erros FALHA→OK, 27 são de linha 1 (perda), 9 de `n5_timeout` ≥ 3 e 5 de `n5_aumento80` ≥ 2.
2. **RISCO que caiu em OK** — `6659|148.163.220.5` (caminho curto, mediana do fluxo 0,79 ms), 16/09/2026 22:01:02 UTC: RTT 1,03 ms, `z_robusto` 1,58, `aumento_pct` **30,68%**, `jitter_relativo` 1,85, `perda_pct` 0, `n5_risco` 2. **Classe verdadeira: RISCO** (linha 5: `aumento_pct` entre 30 e 80). **Árvore: OK.** Motivo: a árvore nunca usa `aumento_pct`; só reconhece RISCO por `z_robusto` > ~2 ou `jitter_relativo` > 3. Em fluxos de caminho curto o RTT absoluto é pequeno e o `aumento_pct` passa de 30% antes de o `z_robusto` chegar a 2.

Os erros se concentram em poucos fluxos: `6659|148.163.220.5` (11), `6891|148.163.220.5` (8), `6891|156.154.184.254` (6). Dos 72 erros, 27 são em fluxos de caminho longo e 12 em fluxos de caminho curto.

## 4. Árvore de contraste (não é o modelo)

Treinar outra árvore, no mesmo treino, acrescentando a rota ou o RTT absoluto (mesmos `max_depth` = 4, `min_samples_leaf` = 100 e semente 42).

- [X] Dizer qual divisão apareceu perto da raiz (em geral a rota ou um corte fixo de milissegundos)
- [X] Declarar que essa árvore fica fora da entrega final

**O que a árvore de contraste usou na raiz:**

- **C1 — métricas relativas + RTT absoluto (`avg`):** a raiz continuou `z_robusto ≤ 3,50`; o RTT absoluto teve importância 0%. É a mesma árvore da oficial (F1 macro na validação 0,9969).
- **C2 — métricas relativas + rota (uma coluna por rota):** raiz `z_robusto ≤ 3,50`; a rota teve importância 0%; mesma árvore (F1 macro 0,9969).
- **C3 (extra) — só RTT absoluto e rota, sem as métricas relativas:** raiz `avg ≤ 341,97` ms, seguida de outros cortes fixos de milissegundos (`avg ≤ 42,78`, `avg ≤ 350,79`); importância 100% de RTT absoluto/rota; **F1 macro na validação 0,4873**.

**Frase:** quando só enxerga distância, a árvore aprende faixas fixas de RTT em milissegundos (que separam caminhos curtos de longos) e chega a apenas 0,49 de F1 macro; quando as métricas relativas estão disponíveis, ela **ignora** o RTT absoluto e a rota (C1 e C2 mantêm `z_robusto ≤ 3,50` na raiz). Essas árvores de contraste **ficam fora da entrega final**; o modelo do projeto é a árvore oficial da seção 2.

*Atenção:* o roteiro prevê que a raiz da árvore de contraste seja a rota ou um corte fixo de ms. Isso só ocorreu na variante C3. Em C1 e C2 o atalho **não foi usado**, porque as métricas relativas já separam as classes.

## 5. Scrum e diário

- [ ] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Bruno Alves Ribeiro de Souza | *(preencher)* | | |
| Igor da Silva Alves Correa | *(preencher)* | | |
| Pedro Henrique Alexandre da Silva | *(preencher)* | | |
| Samuel de Oliveira Santos | *(preencher)* | | |
| Victoria Agatha Rodrigues Fagundes | *(preencher)* | | |
| Wendel Henrique da Silva Rocha | *(preencher)* | | |

---

## Rubrica — Tarefa 3 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Árvore oficial | 1,5 | Uma árvore, critério e profundidade declarados, regras em português, fit só no treino | | |
| Métricas de três classes | 1,0 | Matriz 3×3, F1 por classe e F1 macro; acurácia não é o critério | | |
| Independência da rota | 1,0 | Colunas relativas apenas; árvore de contraste mostra o atalho da distância e é descartada | | |
| Scrum + diário | 0,5 | Board e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
