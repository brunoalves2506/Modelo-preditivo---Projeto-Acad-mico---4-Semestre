# Diário da Tarefa 2 — Baseline do fluxo e rotulagem OK, RISCO, FALHA

**Período:** 18/09/2026 a 30/09/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)

**Equipe: 18**  
**Integrantes:**
    Bruno Alves Ribeiro de Souza,
    Igor da Silva Alves Correa,
    Pedro Henrique Alexandre da Silva,
    Samuel de Oliveira Santos,
    Victoria Agatha Rodrigues Fagundes,
    Wendel Henrique da Silva Rocha, 
**Scrum Master da tarefa:** Wendel Henrique da Silva Rocha 
**Repositório GitHub:** [Modelo Preditivo - Projeto Académico](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre.git)

> Esta tarefa lê o `data/raw/` da Tarefa 1. Não troca a coleta sem versionar.
>
> O trabalho é **obter o baseline de cada fluxo e rotular o Período B** com a tabela desta página. A árvore não entra aqui. País, IP e rota não entram na tabela que a árvore vai ler.
>
> Ordem obrigatória: inspeção do bruto → ficha de baseline no Período A → métricas relativas no Período B → rótulo na ordem da tabela → só então o recorte temporal dentro de B.



### Contrato desta tarefa


|           | Artefato                                                              | Origem / destino                            |
| --------- | --------------------------------------------------------------------- | ------------------------------------------- |
| **Entra** | `data/raw/` e dicionário v0.1                                         | Tarefa 1                                    |
| **Sai**   | `baseline_por_fluxo.csv` (uma ficha por `fluxo_id`)                   | Tarefas 3 a 5                               |
| **Sai**   | Dataset rotulado do Período B, com a classe e as métricas abaixo      | Tarefa 3 **usa este arquivo e este rótulo** |
| **Sai**   | Recorte temporal dentro de B (treino mais antigo, teste mais recente) | Tarefas 3 a 5 — **o mesmo corte**           |
| **Sai**   | Dicionário v0.2 (bruto, ficha, métricas, classe, colunas proibidas)   | Tarefa 3                                    |


**Não sai daqui:** árvore treinada, profundidade escolhida, acurácia, F1.

- [X] O notebook lê o bruto da Tarefa 1

---



## 1. Inspeção do bruto (ainda sem rótulo)

`data/raw/` permanece intocado. A auditoria vai para o diário; a tabela de trabalho, para `data/interim/`.

- [X] Contagem de linhas, fluxos, duplicatas e RTT vazio
- [X] Nenhum RTT ausente foi gravado como 0
- [ ] Período A e Período B não compartilham timestamp do mesmo fluxo

**N bruto:** 89.071 registros
**N de fluxos:** 13.709 (`prb_id | dst_addr`)
**Probes distintas:** 13.709
**Destinos distintos:** 1 (A-root `198.41.0.4`)
**Duplicatas (timestamp, prb_id, dst_addr):** 0
**RTT vazio (sentinela -1):** 701
**Timeouts (rcvd = 0):** 701
**RTT (ms) — mínimo / mediana / máximo:** 0,19 / 24,23 / 2.485,03

**Evidências:**
* **Arquivo CSV:** [`data_ripe_atlas/raw/v1/ripe_atlas_m1009_20260914T030005Z.csv`](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre/blob/main/data_ripe_atlas/raw/v1/ripe_atlas_m1009_20260914T030005Z.csv)
* **Inspeção:** célula do notebook com `pandas` que gera as contagens acima.

**Observações:**
* A coluna `fluxo_id` foi criada no notebook a partir de `prb_id | dst_addr`, porque o CSV bruto não a trazia.
* Os 701 RTTs ausentes usam a sentinela `-1` nas colunas `min/max/avg`. Tratados como ausência, não como zero. Coincidem com os 701 timeouts (`rcvd = 0`).
* **Pendência:** a coleta cobre apenas 27 minutos (14/09/2026 02:33–03:00 UTC). Sem os 7 + 7 dias do RFC, não há como separar Período A e Período B. Este item depende de refazer a coleta com `start=06/09/2026 04:32 UTC` e `stop=20/09/2026 04:32 UTC`.

## 2. Como obter o baseline

Uma ficha por `fluxo_id`. Só o Período A. O Período B não entra na conta e não atualiza a ficha.


| Passo | O que fazer                                                                                                            |
| ----- | ---------------------------------------------------------------------------------------------------------------------- |
| 1     | Separar o fluxo e ordenar pelo timestamp.                                                                              |
| 2     | Período A = bloco inicial. Período B = bloco seguinte, sem amostra nos dois.                                           |
| 3     | RTT válido = medição com RTT presente. Timeout fica **fora** da mediana e do MAD, e **dentro** do dataset como evento. |
| 4     | Menos de **1.500** RTT válidos no A: `baseline_insuficiente`. Esse fluxo **não** recebe classe. Não inventar mediana.  |
| 5     | Gravar uma linha em `baseline_por_fluxo.csv` e congelar.                                                               |



| Campo da ficha  | Fórmula, somente Período A                                 |
| --------------- | ---------------------------------------------------------- |
| `mediana`       | mediana dos RTT válidos (ms)                               |
| `MAD`           | mediana()                                                   |
| `jitter_tipico` | mediana do jitter nas medições em que o jitter existe (ms) |
| `perda_tipica`  | mediana de `perda_pct`, inclusive timeout (%)              |
| `prop_resposta` | medições com RTT válido / medições do período              |


- [ ] Ficha conferida em pelo menos um fluxo curto e um fluxo longo (as medianas podem ser muito diferentes; as duas são “normal”)
- [X] Lista dos fluxos excluídos e o motivo (contagem abaixo de 1.500)

**Fluxos com ficha:**  0
**Fluxos excluídos:**  14.434 — motivo: nenhum fluxo atinge o piso de 1.500 RTTs válidos (máximo observado, somando as 3 coletas: 39 medições em um único fluxo)
**Exemplo auditável (fluxo curto: mediana; fluxo longo: mediana):** os dois fluxos acima, com a ressalva explícita de que os números vêm de um teste de validação da fórmula, não de uma ficha oficial (já que nenhum fluxo tem volume suficiente ainda)
**Achado a registrar no diário:** mudança abrupta de RTT do fluxo 7092 entre 14/09 e 26/09, como evidência de por que Período A precisa ser contínuo

## 3. Métricas de cada medição do Período B

Calcular só com a ficha congelada daquele `fluxo_id`.


| Métrica           | Fórmula                                                                 |
| ----------------- | ----------------------------------------------------------------------- |
| `z_robusto`       | (RTT atual − mediana) / (1,4826 × MAD)                                  |
| `aumento_pct`     | (RTT atual − mediana) / mediana × 100                                   |
| `jitter_relativo` | jitter atual / `jitter_tipico`                                          |
| `perda_pct`       | (enviados − recebidos) / enviados × 100                                 |
| `timeout_atual`   | 1 se não há RTT ou `perda_pct` = 100; senão 0                           |
| `n5_timeout`      | timeouts nas últimas 5 medições deste fluxo, incluindo a atual (0 a 5)  |
| `n5_aumento80`    | quantas das últimas 5 têm `aumento_pct` > 80                            |
| `n5_risco`        | quantas das últimas 5 cumprem o critério da linha 5 da tabela de rótulo |



| Situação                               | Conta                                                                           |
| -------------------------------------- | ------------------------------------------------------------------------------- |
| RTT ausente                            | Não calcular `z_robusto` nem `aumento_pct`. `timeout_atual` = 1. Não usar 0 ms. |
| MAD = 0 e RTT atual = mediana          | `z_robusto` = 0                                                                 |
| MAD = 0 e RTT atual ≠ mediana          | Denominador = max(IQR / 1,349, 1 ms)                                            |
| Jitter atual vazio                     | O critério de jitter não dispara                                                |
| `jitter_tipico` = 0 e jitter atual = 0 | `jitter_relativo` = 1                                                           |
| `jitter_tipico` = 0 e jitter atual > 0 | Tratar como `jitter_relativo` ≥ 3                                               |


## 4. Tabela de rotulagem — parar na primeira linha verdadeira

Cada linha do Período B, de um fluxo que tenha ficha. FALHA ganha de RISCO; RISCO ganha de OK.


| Ordem | Classe    | Métrica                                                                                                   | Limiar exato                                        |
| ----- | --------- | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| 1     | **FALHA** | `perda_pct`                                                                                               | ≥ 10 nesta medição (em 3 pacotes, 1 perda já é 33%) |
| 2     | **FALHA** | `n5_timeout`                                                                                              | ≥ 3                                                 |
| 3     | **FALHA** | `z_robusto`                                                                                               | ≥ 3,5 nesta medição, com RTT presente               |
| 4     | **FALHA** | `n5_aumento80`                                                                                            | ≥ 2                                                 |
| 5     | **RISCO** | nesta medição, pelo menos um: `2 ≤ z_robusto < 3,5`, ou `30 ≤ aumento_pct ≤ 80`, ou `jitter_relativo ≥ 3` | e `n5_risco` ≥ 2                                    |
| 6     | **OK**    | nenhuma linha anterior                                                                                    | pico isolado também é OK                            |


- [ ] Três exemplos auditáveis no diário: um OK de caminho longo (RTT alto e `z_robusto` baixo), um RISCO, um FALHA de caminho curto ou de timeout
- [ ] Contagem OK / RISCO / FALHA no Período B
- [ ] A classe **não** foi definida por “RTT > 100 ms” nem pelo nome da rota
- [ ] O Período A não foi rotulado
- [ ] Dicionário v0.2 lista as colunas proibidas na árvore: país, IP, `rota_id`, `fluxo_id`, RTT absoluto como substituto das métricas relativas

**Contagem OK / RISCO / FALHA:**  
**Evidências (três linhas reais, com as métricas e a ordem que disparou a classe):**

## 5. Recorte para a árvore (ainda sem treinar)

Dentro do Período B, por fluxo, em ordem de tempo:

- [ ] Treino = trecho mais antigo; validação = trecho do meio; teste = trecho mais recente
- [ ] Proporção de partida 50% / 20% / 30%, ajustada se um bloco ficar sem RISCO
- [ ] Nenhum registro do Período A no treino
- [ ] Corte com data e N de cada bloco

**Corte (datas e N treino / validação / teste):**

## 6. Scrum e diário

- [ ] Board atualizado

**Link do board:**


| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
| ---------- | ---------------------- | ------------ | ----------------------------- |
|            |                        |              |                               |


---



## Rubrica — Tarefa 2 (0 a 4,0)


| Critério                  | Peso    | Nota máxima                                                                                     | Nota          | Observações |
| ------------------------- | ------- | ----------------------------------------------------------------------------------------------- | ------------- | ----------- |
| Baseline por fluxo        | 1,5     | Ficha só com o Período A, fórmulas desta página, piso de 1.500, exclusões listadas, A congelado |               |             |
| Rotulagem                 | 1,5     | Tabela aplicada na ordem, exemplos curto/longo, timeout sem RTT = 0, contagem das três classes  |               |             |
| Independência da rota     | 0,5     | Rota e RTT absoluto fora do rótulo e fora das colunas da futura árvore                          |               |             |
| Recorte temporal + diário | 0,5     | Corte dentro de B, com N; diário de todos                                                       |               |             |
| **Total**                 | **4,0** |                                                                                                 | **___ / 4,0** |             |


