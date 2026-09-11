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

## Estrutura e organização

```
.
├── .gitignore
├── README.md
├── docs/
│   └── memorando_de_decisao_grupo18.md
├── notebook/
│   └── coleta_de_dados.ipynb
```

O ambiente virtual `.venv/` é utilizado localmente para executar o projeto, mas não é versionado. Portanto, antes de executar o projeto, confirme se o ambiente virtual está ativo para manter as dependências isoladas.
