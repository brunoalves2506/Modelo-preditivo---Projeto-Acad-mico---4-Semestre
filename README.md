# Modelo Preditivo de Rede

## Objetivo

Desenvolver um modelo preditivo capaz de antecipar falhas em redes de computadores a partir de métricas de qualidade de conexão (latência, perda de pacotes e jitter), coletadas via medições de rede reais.

## Descrição

Este projeto integra a disciplina de Ciência da Computação (CC), sob orientação da professora Andrea Ono Sakai. O pipeline do projeto transforma registros de medições de rede em janelas temporais que alimentam o vetor de características X = [latência, perda, jitter], utilizado para treinar o modelo preditivo.

Como fonte de dados, o grupo avaliou duas opções — um dataset real já publicado (11-Day Starlink Ping Measurements Dataset, no Zenodo) e a API do RIPE Atlas — e, após pesquisa documentada em memorando de decisão, optou pela **API do RIPE Atlas**, por permitir controle total sobre as medições coletadas e maior aderência aos objetivos acadêmicos do projeto.

## Integrantes do grupo

| Nome | RGM |
|---|---|
| Bruno Alves Ribeiro de Souza | 42276047 |
| Samuel de Oliveira Santos | 41761782 |
| Victoria Agatha Rodrigues Fagundes | 43756042 |
| Wendel Henrique da Silva Rocha | 42614945 |
| Igor da Silva Alves Correa | 41885163 |
| Pedro Henrique Alexandre da Silva | 42947049 |

## Turma

Grupo 18 - Ciência da computação (Noite)

## Link do repositório

[Modelo preditivo de Rede](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre)

## Branch principal utilizada

main

## Documentação

- [Memorando de decisão](docs/memorando_de_decisao_grupo18.md)
- [Dicionário de variáveis brutas v0.1](docs/dicionario_v0.1.md)
- [Tarefa 1 — Coleta bruta](docs/Tarefa1_Coleta_Bruta.md)
- [Tarefa 2 — Baseline e rotulagem](docs/Tarefa2_Baseline_e_Rotulagem.md)
- [RFC — Preditor de degradação](docs/RFC_Preditor_Degradacao_Rede.md)
- [Guia da coleta RIPE Atlas](docs/Guia_Coleta_RIPE_Atlas.md)

## Estrutura e organização

```text
.
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── config/
│   └── parametros.yaml
├── data_ripe_atlas/
│   └── raw/
│       ├── ripe_atlas_m1009_...json
│       ├── ripe_atlas_m1009_...csv
│       └── ripe_atlas_m1009_..._metadata.json
├── docs/
│   ├── dicionario_v0.1.md
│   ├── memorando_de_decisao_grupo18.md
│   ├── Tarefa1_Coleta_Bruta.md
│   ├── Tarefa2_Baseline_e_Rotulagem.md
│   ├── RFC_Preditor_Degradacao_Rede.md
│   └── Guia_Coleta_RIPE_Atlas.md
└── notebook/
    └── coleta_de_dados.ipynb
```
