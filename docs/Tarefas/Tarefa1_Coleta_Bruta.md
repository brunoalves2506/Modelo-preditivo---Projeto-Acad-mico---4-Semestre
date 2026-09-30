# Diário da Tarefa 1 — Problema e coleta bruta (sem rótulo)

**Período:** 17/08/2026 a 17/09/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)  
**Modelo desta disciplina:** árvore de decisão. Nesta tarefa não se treina árvore.

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

> Esta tarefa entrega o problema e o **dado cru**. Não há classe OK, RISCO ou FALHA. Não há baseline, não há mediana e não há árvore. Quem rotular aqui mistura a coleta com a decisão da Tarefa 2.
>
> A rota entra na coleta só para haver caminhos curtos e longos no mesmo arquivo. RTT alto **não** é falha. País, IP e nome da rota **não** serão coluna da árvore.

### Contrato desta tarefa

| | Artefato | Quem usa depois |
|---|---|---|
| **Entra** | RFC do projeto | — |
| **Sai** | RFC preenchido pelo grupo (problema, horizonte, custo de errar FALHA, fora de escopo) | Tarefas 2 e 5 |
| **Sai** | Dicionário v0.1 só com colunas **brutas** da medição | Tarefa 2 |
| **Sai** | `data/raw/` + `config/` + `requirements.txt` | Tarefa 2 **é obrigada a usar este bruto** |
| **Sai** | Este diário | Tarefas seguintes |

**Não sai daqui:** baseline, rótulo, `z_robusto`, split, árvore, métrica de modelo.

---

## 1. Definição do problema

Responder no diário. A resposta tem de bater com o RFC.

| Pergunta | Resposta do grupo |
|---|---|
| Qual evento a árvore vai classificar? | Degradação do fluxo em relação ao **próprio** normal: OK, RISCO ou FALHA. Não é “rota longa” nem “RTT acima de 100 ms”. |
| O que é um fluxo? | `fluxo_id = probe_id \| dst_addr` (origem, destino e, se existir, `measurement_id`). |
| O que é cada linha do bruto? | Uma medição ICMP desse fluxo, com timestamp. |
| Qual horizonte fica para depois? | Detector: estado da medição atual. Preditor: estado 12 minutos à frente. A árvore só entra na Tarefa 3. |
| Quem usa o alerta? | Quem opera o enlace: investigar (FALHA), observar (RISCO) ou não agir (OK). |
| O que está proibido como definição de falha? | Limiar global de RTT, país, continente ou nome da rota. |

- [ X] RFC do grupo preenchido a partir desta tabela
- [ ] Dicionário v0.1 só com variáveis brutas

## 2. O que coletar (e o que não criar)

Fonte: medições públicas já existentes de ping IPv4 (mesh de Anchors do RIPE Atlas, somente `GET`). Não criar medição própria e não gastar crédito.

Cada registro bruto guarda, quando a API trouxer:

| Campo | Unidade | Papel agora |
|---|---|---|
| `timestamp` | UTC | Ordenar o fluxo |
| `msm_id` (`measurement_id`) | — | Identidade da medição |
| `prb_id` (`probe_id`) | — | Origem |
| `dst_addr` | — | Destino |
| `fluxo_id` | texto estável | `prb_id \| dst_addr` |
| RTT da rajada (`avg`) | ms | Medição. Vazio se não houver resposta. Nunca 0 |
| `sent`, `rcvd` | contagem | Utilizados no cálculo da perda (`perda_pct`) |
| `perda_pct` | % | `((sent - rcvd) / sent) * 100` |
| `jitter_ms` | ms | Desvio-padrão dos RTTs da rajada (com 2 ou mais respostas; senão, vazio) |
| `timeout_atual` | 0 ou 1 | 1 se não há RTT ou `perda_pct` = 100% |
| país ou rota (`dst_name`, `from`) | texto | Só auditoria de diversidade. Fora da futura árvore |

#### Regras da coleta:
- [x] Vários fluxos, com pelo menos um caminho curto e um caminho longo no mesmo período
- [x] A diversidade geográfica está documentada e não virou classe
- [x] Dois blocos de tempo contíguos, sem amostra nos dois: Período A (só para o baseline da Tarefa 2) e Período B (medições que serão rotuladas). Referência do projeto: 7 dias + 7 dias a partir de 06/09/2026 04:32 UTC
- [x] Timeout permanece no arquivo
- [x] JSON/CSV bruto preservado; a tabela tratada não apaga o bruto
- [x] Parâmetros (período, probes, destinos) em `config/`, não espalhados no código
- [x] HTTP com timeout, releitura em erro transitório e coleta idempotente (rodar de novo não duplica)
- [x] `requirements.txt` da coleta

**Evidências (notebook, commit, trecho do config):**
* **Repositório do Projeto:** [Modelo Preditivo - Projeto Académico](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre)
* **Ficheiro CSV com os dados brutos:** [`ripe_atlas_m1009_20260914T030005Z.csv`](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre/blob/main/data/raw/ripe_atlas_m1009_20260914T030005Z.csv)
* **Pasta de dados crus:** [`data/raw/`](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre/tree/main/data/raw)
* **Pasta de Configuração:** [`config/`](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre/tree/main/notebook)
* **Total de registros brutos analisados:** 89.071 medições
* **Total de fluxos únicos:** 13.709 fluxos (`prb_id | dst_addr`)
* **Exemplo de caminho curto:** `prb_id = 7092` (RTT mediano ~0,25 ms)
* **Exemplo de caminho longo:** `prb_id = 1015060` (RTT mediano ~761,78 ms)
* **Arquivo de exemplo de variáveis de ambiente:** [`.env.exemplo`](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre/blob/main/.env.example)
* **Total de timeouts identificados:** 701 registros sem resposta (`rcvd = 0`, RTT ausente preservado)

## 3. Relatório de qualidade — ainda sem classe

- [x] Registros por `fluxo_id`
- [x] Início e fim de cada fluxo
- [x] Campos ausentes (RTT vazio é ausência, não zero)
- [x] Duplicatas
- [x] Quantidade de timeouts
- [x] RTT e perda descritos (mínimo, mediana, máximo) **sem** dizer OK, RISCO ou FALHA

**N de registros brutos:** 89.071  
**N de fluxos:** 13.709 (`prb_id | dst_addr`)  
**Caminho curto e caminho longo presentes (quais):** 
* **Caminho curto:** `prb_id = 7092` (RTT mediano ~0,25 ms)
* **Caminho longo:** `prb_id = 1015060` (RTT mediano ~761,78 ms)

## 3.1 Dicionário v0.1 — variáveis brutas
... (NOVO — cole aqui)

## 4. Scrum

- [x] Product Owner = docente; Scrum Master da tarefa: [Nome do Aluno/Scrum Master]; time de desenvolvimento: Bruno Alves, Wendel, [Outros Integrantes]
- [X] Board com To do / Doing / Done
- [x] Pelo menos 3 histórias: coletar fluxos diversos; preservar o bruto com timeout; separar Período A e Período B sem rotular

**Histórias:**
1. **História 1 — Coleta de fluxos diversos:** Como analista de dados, quero extrair medições de múltiplos fluxos (com caminhos curtos e longos) via API do RIPE Atlas para ter diversidade geográfica sem viés regional.
2. **História 2 — Preservação de dados brutos com timeout:** Como engenheiro de dados, quero manter os registos originais em `data/raw/` preservando os timeouts (sem preencher RTT com zero) para garantir a integridade da medição.
3. **História 3 — Separação temporal sem rotulagem:** Como cientista de dados, quero estruturar os dados nos Períodos A e B sem atribuir classes (`OK`, `RISCO`, `FALHA`) para estar em conformidade com as restrições da Tarefa 1.

**Link do board:** [Quadro Kanban do Projeto (GitHub Projects / Trello)](https://github.com/users/brunoalves2506/projects/1/views/1)

## 5. Diário de bordo

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| **Bruno Alves Ribeiro de Souza** | | | |
| **Igor da Silva Alves Correa** | | | |
| **Pedro Henrique Alexandre da Silva** | | | |
| **Samuel de Oliveira Santos** | | | |
| **Victoria Agatha Rodrigues Fagundes** | | | |
| **Wendel Henrique da Silva Rocha** *(Scrum Master)* | | | |

## 6. Evidências gerais

- **Link do RFC:** [Guia do Projeto e Especificações RFC](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre/blob/main/docs/Guia_Coleta_RIPE_Atlas.md)
- **Link do dicionário v0.1:** [Dicionário de Variáveis Brutas v0.1](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre/blob/main/docs/Tarefa1_Coleta_Bruta.md#2-o-que-coletar-e-o-que-n%C3%A3o-criar)
- **Link dos commits:** [Histórico de Commits do Repositório](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre/commits/main/)
- **Link de `data/raw/` e do `config/`:**
  - [Diretório data/raw/](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre/tree/main/data/raw)
  - [Diretório config/](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre/tree/main/notebook)

---

## Rubrica — Tarefa 1 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Problema | 0,5 | Fluxo, unidade de análise e proibição de RTT absoluto como falha estão explícitos | | |
| Coleta bruta | 1,5 | Vários fluxos (curto e longo), timeout preservado, RTT vazio ≠ 0, config externa, bruto intocável | | |
| Período A e Período B sem rótulo | 1,0 | Dois blocos sem sobreposição; relatório de qualidade **sem** classe | | |
| Scrum + diário | 1,0 | Papéis, board, histórias e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
