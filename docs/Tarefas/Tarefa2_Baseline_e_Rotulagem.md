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

**Observação sobre a coleta:** esta tarefa usa a segunda coleta **(v2, `v2-ping-ipv4`)**, e não a v1. A v1 (medição 1009, cerca de 27 minutos) foi curta demais: nenhum fluxo atingiu 1.500 RTTs válidos. A v2 usa 14 dias do mesh de anchors (06/09 a 20/09/2026, `seed = 42`, 12 rotas, 322 requisições à API), com Período A de 06 a 13/09 e Período B de 13 a 20/09 (UTC). A troca foi versionada em `data_ripe_atlas/raw/v2/`, e o `raw` da v1 foi mantido intocado. Os nomes das colunas da v2 diferem do dicionário v0.1; o mapeamento fica no v0.2.

- [X] O notebook lê o bruto da Tarefa 1

---



## 1. Inspeção do bruto (ainda sem rótulo)

`data/raw/` permanece intocado. A auditoria vai para o diário; a tabela de trabalho, para `data/interim/`.

- [X] Contagem de linhas, fluxos, duplicatas e RTT vazio
- [X] Nenhum RTT ausente foi gravado como 0
- [X] Período A e Período B não compartilham timestamp do mesmo fluxo

**N bruto:** 442.587 registros (Período A: 221.520 | Período B: 221.067)
**N de fluxos:** 92 (`prb_id | dst_addr`) no Período A e 88 no Período B (total único de 92 fluxos)
**Probes distintas:** 24
**Destinos distintos:** 23
**Duplicatas (timestamp, prb_id, dst_addr):** 0
**RTT vazio (sentinela -1):** 701
**Timeouts (rcvd = 0):** 61.102
**RTT (ms) — mínimo / mediana / máximo:** 0,44 / 57,74 / 1.001,10

**Evidências:**
* **Arquivo CSV:** [`data_ripe_atlas/raw/v2/ripe_atlas_mesh_v2_ping_ipv4_periodo_a.csv`]
[`data_ripe_atlas/raw/v2/ripe_atlas_mesh_v2_ping_ipv4_periodo_b.csv`]
* **Metadados:** [`data_ripe_atlas/raw/v2/ripe_atlas_mesh_v2_ping_ipv4_metadata.json`]

**Observações:**
* RTTs ausentes/timeouts foram preservados como nulos ou com a sentinela [`-1`] e sinalizados em `timeout_atual = 1`, sem preenchimento artificial com zero.
* Os Períodos A e B possuem contiguidade temporal estrita de 7 dias cada (Período A: 06/09/2026 04:32 a 13/09/2026 04:32 UTC; Período B: 13/09/2026 04:32 a 20/09/2026 04:32 UTC). Não há sobreposição de timestamps no mesmo fluxo

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


- [X] Ficha conferida em pelo menos um fluxo curto e um fluxo longo (as medianas podem ser muito diferentes; as duas são “normal”)
- [X] Lista dos fluxos excluídos e o motivo (contagem abaixo de 1.500)

**Fluxos com ficha(`status = ok`):**  76
**Fluxos excluídos:**  16 — motivo: não atingiram o piso de 1.500 RTTs válidos no Período A.
**Lista dos 16 fluxos excluídos:**  [`6396|18.153.158.127`] (0), [`6447|18.153.158.127`] (0), [`6447|185.32.189.249`] (23), [`6447|212.119.5.254`] (21), [`6447|91.209.16.127`] (17), [`6826|18.153.158.127`] (0), [`6954|102.130.67.116`] (0), [`7269|102.130.67.116`] (0), [`7277|102.130.67.116`] (0), [`7375|102.130.67.116`] (0), [`7414|138.204.7.245`] (0), [`7414|190.124.192.162`] (0), [`7505|138.204.7.245`] (0), [`7542|138.204.7.245`] (0), [`7617|138.204.7.245`] (0), [`7618|18.153.158.127`] (0).
**Exemplo auditável (fluxo curto: mediana; fluxo longo: mediana):**
- Caminho Curto (`fluxo_id = 6659|148.163.220.5`):
    RTTs válidos no A: 2.519
    `mediana`: [`0,79 ms`] | MAD: [`0,10 ms`] | `jitter_tipico`: [`0,14 ms`] | `perda_tipica`: 0,0% | `prop_resposta`: 1,00 (100%)

- Caminho Longo (`fluxo_id = 6891|196.10.53.7`):
    RTTs válidos no A: 2.519
    `mediana`: [`356,18 ms`] | `MAD`: [`1,10 ms`] | `jitter_tipico`: [`0,16 ms`] | `perda_tipica`: 0,0% | `prop_resposta`: 1,00 (100%)

## 3. Métricas de cada medição do Período B

Calcular só com a ficha congelada daquele `fluxo_id`.


| Métrica           | Fórmula                                                                 |
| ----------------- | ----------------------------------------------------------------------- |
| `z_robusto`       | (RTT atual − mediana) / (1,4826 × MAD)                                  |
| `aumento_pct`     | (RTT atual − mediana) / mediana × 100                                   |
| `jitter_relativo` | jitter atual / `jitter_tipico`                                          |
| `perda_pct`       | (enviados − recebidos) / enviados × 100                                 |
| `timeout_atual`   | 1 se não há RTT ou `perda_pct` = 100; senão 0                          |
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


- [X] Três exemplos auditáveis no diário: um OK de caminho longo (RTT alto e `z_robusto` baixo), um RISCO, um FALHA de caminho curto ou de timeout
- [X] Contagem OK / RISCO / FALHA no Período B
- [X] A classe **não** foi definida por “RTT > 100 ms” nem pelo nome da rota
- [X] O Período A não foi rotulado
- [ ] Dicionário v0.2 lista as colunas proibidas na árvore: país, IP, `rota_id`, `fluxo_id`, RTT absoluto como substituto das métricas relativas

**Contagem OK / RISCO / FALHA:**  
- OK: [`142.384 medições`] (74,6%)
- FALHA: [`32.788 medições`] (17,2%)
- RISCO: [`15.684 medições`] (8,2%)
**Evidências (três linhas reais, com as métricas e a ordem que disparou a classe):**
**Exemplo OK:** (`fluxo_id = 6396|185.32.189.249`):

RTT: [`42,68 ms`] | z_robusto: [`2,74`] | aumento_pct: 0,99% | perda_pct: [`0`],0% | n5_timeout: [`0`] | Classe: `OK`

Regra de disparo: Nenhuma regra das linhas 1 a 5 disparou (pico isolado sem persistência acumulada).

**Exemplo RISCO:** (`fluxo_id = 6396|185.32.189.249`):

RTT: [`42,52 ms`] | z_robusto: [`1,72`] | aumento_pct: 0,62% | perda_pct: 0,0% | crit_risco_ind: [`1`] | n5_risco: [`2`] | Classe: `RISCO`

Regra de disparo: Linha 5 da tabela (`crit_risco_ind = 1` e `n5_risco >= 2`).

**Exemplo FALHA:** (`fluxo_id = 6396|185.32.189.249`):

RTT: [`42,94 ms`] | z_robusto: [`4,47`] | aumento_pct: 1,62% | perda_pct: [`0`],0% | n5_timeout: [`0`] | Classe: `FALHA`

Regra de disparo: Linha 3 da tabela (`z_robusto >= 3.5` nesta medição com RTT presente).

## 5. Recorte para a árvore (ainda sem treinar)

Dentro do Período B, por fluxo, em ordem de tempo:

- [X] Treino = trecho mais antigo; validação = trecho do meio; teste = trecho mais recente
- [X] Proporção de partida 50% / 20% / 30%, ajustada se um bloco ficar sem RISCO
- [X] Nenhum registro do Período A no treino
- [X] Corte com data e N de cada bloco

**Corte (datas e N treino / validação / teste):**
* Treino (50% mais antigo): [`N = 95.406`] | Início: `2026-09-13T04:32:06Z` | Fim: `2026-09-16T18:09:50Z`.

* Validação (20% do meio): [`N = 38.138`] | Início: `2026-09-16T14:10:11Z` | Fim: `2026-09-18T03:04:22Z`.

* Teste (30% mais recente): [`N = 57.312`] | Início: `2026-09-17T22:46:09Z` | Fim: `2026-09-20T04:31:38Z`.

## 6. Scrum e diário

- [ ] Board atualizado

**Link do board:**


| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
| ---------- | ---------------------- | ------------ | ----------------------------- |
|Bruno Alves Ribeiro de Souza            |Auxiliei no suporte ao ambiente e verificação da pipeline de dados.                        |Organização dos diretórios temporários.              |Manter a consistência na estrutura do pipeline.                               |
|Igor da Silva Alves Correa            |Apoiei o desvinculamento das variáveis de identificação geográfica em relação ao rótulo.                        |Garantir o isolamento das colunas de auditoria.              |Automatizar a validação das colunas proibidas.                               |
|Pedro Henrique Alexandre da Silva            |Revisão do diário e validação do cálculo das métricas relativas no Período B.                        |Entendimento das regras de fallback para MAD = 0.              |Manter o rigor conceitual nas análises.                               |
|Samuel de Oliveira Santos            |Atuei na inspeção dos dados brutos e na verificação do piso de 1.500 RTTs para a ficha de baseline.                        |Tratar adequadamente a grande quantidade de timeouts sem zerar o RTT.              |Manter o foco na qualidade da extração.                               |
|Victoria Agatha Rodrigues Fagundes            |Responsável pela documentação do Dicionário v0.2, discriminando colunas brutas, relativas e proibidas.                        |Separação estrita dos escopos das versões v0.1 e v0.2 do dicionário.              |Automatizar a checagem do schema de saída.                               |
|Wendel Henrique da Silva Rocha (Scrum Master)            |Coordenei a execução da tarefa, montagem das fichas congeladas no Período A e separação dos blocos temporalmente.                        |Garantir que a ordem de precedência da rotulagem fosse aplicada estritamente sem inversões.              |Ajustar e otimizar os fluxos do Scrum para a Tarefa 3.                               |



---



## Rubrica — Tarefa 2 (0 a 4,0)


| Critério                  | Peso    | Nota máxima                                                                                     | Nota          | Observações |
| ------------------------- | ------- | ----------------------------------------------------------------------------------------------- | ------------- | ----------- |
| Baseline por fluxo        | 1,5     | Ficha só com o Período A, fórmulas desta página, piso de 1.500, exclusões listadas, A congelado |               |             |
| Rotulagem                 | 1,5     | Tabela aplicada na ordem, exemplos curto/longo, timeout sem RTT = 0, contagem das três classes  |               |             |
| Independência da rota     | 0,5     | Rota e RTT absoluto fora do rótulo e fora das colunas da futura árvore                          |               |             |
| Recorte temporal + diário | 0,5     | Corte dentro de B, com N; diário de todos                                                       |               |             |
| **Total**                 | **4,0** |                                                                                                 | **___ / 4,0** |             |


