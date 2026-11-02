# Dicionário de Variáveis Brutas v0.1

**Projeto:** Preditor de degradação de rede com RTT normalizado
**Equipe:** Grupo 18
**Disciplina:** Estruturas de Dados II — Ciência da Computação
**Fonte:** RIPE Atlas, API v2, medição `msm_id = 1009` (Anchoring Mesh, ping IPv4)
**Versão:** v0.1 — somente variáveis brutas
**Data:** 20/09/2026

---

## Escopo deste dicionário

Este dicionário lista apenas as colunas **coletadas** ou **derivadas diretamente** da API do RIPE Atlas.

**Não entram aqui:**
- Rótulo OK / RISCO / FALHA
- `z_robusto`, `aumento_pct`, `jitter_relativo`, `latencia_relativa`
- `mediana`, `MAD`, `jitter_tipico`, `perda_tipica`, `prop_resposta`
- Qualquer métrica relativa ao baseline

Essas pertencem à Tarefa 2 e vão para o dicionário v0.2.

**Regra fundamental:** RTT ausente permanece **vazio** no CSV. Nunca é gravado como 0.

---

## Colunas

| Coluna | Tipo | Unidade | Origem | Papel |
|---|---|---|---|---|
| `timestamp` | inteiro | segundos (epoch UTC) | API | Ordenar o fluxo no tempo |
| `msm_id` | inteiro | — | API | Identidade da medição |
| `prb_id` | inteiro | — | API | Sonda de origem |
| `dst_addr` | texto | — | API | IP do destino |
| `dst_name` | texto | — | API | Nome do destino (auditoria) |
| `fluxo_id` | texto | — | derivado | `prb_id \| dst_addr` |
| `avg` | float | ms | API | RTT médio da rajada. Vazio se sem resposta |
| `min` | float | ms | API | RTT mínimo da rajada. Vazio se sem resposta |
| `max` | float | ms | API | RTT máximo da rajada. Vazio se sem resposta |
| `sent` | inteiro | pacotes | API | Pacotes enviados na rajada |
| `rcvd` | inteiro | pacotes | API | Pacotes respondidos na rajada |
| `perda_pct` | float | % | derivado | `(sent − rcvd) / sent × 100` |
| `jitter_ms` | float | ms | derivado | Desvio-padrão de `result[].rtt`, com 2+ respostas |
| `timeout_atual` | inteiro | 0/1 | derivado | 1 se `avg` vazio ou `perda_pct = 100` |
| `from` | texto | — | API | IP de origem (auditoria; muda com NAT) |
| `proto` | texto | — | API | Protocolo (`ICMP`) |
| `af` | inteiro | — | API | Família de endereço (4 ou 6) |
| `size` | inteiro | bytes | API | Tamanho do pacote |
| `ttl` | inteiro | — | API | TTL observado. Pode ser vazio |
| `mver` | texto | — | API | Versão do formato da medição. Pode ser vazio |
| `result` | lista | — | API | Lista de RTTs individuais da rajada |
| `lts` | inteiro | — | API | Timestamp local da sonda |
| `stored_timestamp` | inteiro | segundos | API | Quando a RIPE armazenou |
| `step` | inteiro | segundos | API | Intervalo entre medições (240 s no mesh) |

---

## Definições detalhadas

### `fluxo_id`
Derivado: `prb_id | dst_addr`. É a chave estável do fluxo. Mesmo probe + mesmo destino = mesmo fluxo. Outro probe = outro fluxo. Mesmo probe + outro destino = outro fluxo.

### `avg`, `min`, `max`
RTT da rajada (tipicamente 3 pacotes). Vazio quando não há resposta. **Não preencher com 0.** No CSV, a sentinela `-1` aparece em `min/max/avg` quando `rcvd = 0`; tratar como ausência antes de qualquer cálculo.

### `perda_pct`
Derivado: `(sent − rcvd) / sent × 100`. Se `sent` for vazio, a linha sai. Se `rcvd = 0`, a perda é 100%.

### `jitter_ms`
Derivado: desvio-padrão de `result[].rtt`. Só existe com 2 ou mais respostas na rajada. Com 0 ou 1 resposta, fica vazio. **Nunca 0** quando não há dado.

### `timeout_atual`
Derivado: 1 se `avg` vazio ou `perda_pct = 100`; senão 0. Timeout permanece no arquivo como evento, não é descartado.

### Colunas de auditoria
`from`, `dst_name`, `msm_id`, `lts`, `stored_timestamp` servem para rastrear e auditar. **Não entram como feature do modelo.**

### Colunas proibidas no modelo
País, IP, `rota_id`, `fluxo_id` e RTT absoluto como substituto das métricas relativas. Ficam no bruto apenas para auditoria.

---

## Relação com a Tarefa 2

O dicionário v0.2 (Tarefa 2) vai acrescentar:
- `mediana`, `MAD`, `jitter_tipico`, `perda_tipica`, `prop_resposta` (ficha do baseline)
- `latencia_relativa`, `z_robusto`, `aumento_pct`, `jitter_relativo` (métricas relativas)
- `n5_timeout`, `n5_aumento80`, `n5_risco` (persistência)
- `classe` (OK / RISCO / FALHA)

Nada disso existe no bruto.
