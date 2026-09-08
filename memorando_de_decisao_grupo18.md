# Memorando de Decisão — Fonte de Dados do Projeto


| Campo | Informação |
|---|---|
| Curso / Disciplina | `CC` |
| Projeto integrador | `[]` |
| Orientador(a) | `Andrea Ono Sakai` |
| Data de entrega desta etapa | `08/09/2026` |
| Integrantes do grupo | `Bruno Alves Ribeiro de Souza - 42276047 | Samuel de Oliveira Santos - 41761782` | 'Victoria Agatha Rodrigues Fagundes - 43756042' | Wendel Henrique da Silva Rocha - 42614945

---

> Preencha cada seção com o que você encontrou na pesquisa. Não deixe nenhum campo com o texto entre colchetes — substitua pelo seu conteúdo. Toda informação levantada nas Opções A e B precisa indicar a fonte de onde veio.

## 1. Situação

<!-- Em uma frase: qual decisão precisa ser tomada e por quê. 
O pipeline do projeto já está definido: qualquer fonte de dados precisa produzir registros que se transformem em janelas e, por fim, em X = [latência, perda, jitter]. Falta decidir de onde virão esses dados na próxima fase. A equipe do projeto precisa recomendar, com base em pesquisa e não em preferência pessoal, se a próxima etapa deve usar um dataset real já publicado ou a API do RIPE Atlas. O grupo deve produzir um memorando de decisão com a recomendação da tomada de decisão. A recomendação só tem valor se for sustentada por pesquisa real — não existe resposta pronta para copiar; ela precisa ser construída a partir do que vocês encontraram.
-->

Conseguimos definir a forma como vamos conseguir os dados, que é via API e já conseguimos os créditos para isso. Agora devemos definir o pipeline para podermos dar continuidade no projeto e mapear nossos passos.

## 2. Opção A — Dataset real

<!-- O que foi encontrado sobre um dataset real de ICMP. Cite a fonte de cada informação. -->

- **Origem / link:** [ ]
- **Formato:** [ ]
- **Período coberto:** [ ]
- **Campos disponíveis:** [ ]
- **Licença de uso:** [ ]

**Resumo do que foi encontrado:**

[Escreva aqui, citando a fonte consultada]

## 3. Opção B — API do RIPE Atlas

<!-- O que foi encontrado sobre a API: autenticação, criação e consulta de medições. Cite a fonte de cada informação. -->

- **Documentação consultada (link):** [ https://atlas.ripe.net/ ]
- **Autenticação exigida:** [ ]
- **Como se cria uma medição:** [ ]
- **Como se consultam os resultados:** [ ]

**Resumo do que foi encontrado:**

[Escreva aqui, citando a fonte consultada]

## 4. Comparação

<!-- Preencha a tabela com base no que você levantou nas seções 2 e 3. -->

| Critério | Opção A — Dataset real | Opção B — API RIPE Atlas |
|---|---|---|
| Controle sobre a coleta | | |
| Diversidade geográfica | | |
| Custo / complexidade de implementação | | |
| Tempo até os primeiros dados estarem disponíveis | | |

## 5. Recomendação

 Eu recomendaria a api do RIPE porque além de conseguir controlar quais medições fazer (ping, icmp, de quais probes e quais destinos), isso pesa em um cenário de projeto acadêmico, onde nós mesmos coletamos os dados e não dependemos de uma coleta de terceiros.

## 6. Justificativa

 Como dito na questão anterior, podemos ter total controle sobre as medições, aprendemos do zero como fazer na prática e dependendo da quantidade de mediçoes feitas, o modelo preditivo vai ficar bem mais preciso.

## 7. Riscos e limitações

 Para o nosso grupo, as formas de se conseguir os crétidos para a api era incerto. Não tinhamos certeza se conseguiríamos um pc que serviria de sonda para conseguir os créditos da RIPE. Além disso, depois de conseguir os créditos, não sabíamos se seriam suficientes - é uma limitação da api, as medições tem um custo, e esse custo é diário, limitando a quantidade de requisições por dia.

## 8. Contribuição Individual dos Integrantes

<!-- cada integrante deve descrever, com suas próprias palavras, o que efetivamente fez nesta etapa. Contribuições genéricas como "ajudei em tudo" não serão aceitas. Use verbos de ação e seja específico (ex.: "pesquisei , analisei, testei, ... apresentei prós/contras ao grupo, ...").-->

### Integrante 1 — `[ Bruno Alves Ribeiro de Souza ]`
- **O que fez nesta etapa:** `[Disponibilizou e configurou uma máquina pessoal para a instalação da probe RIPE]`
- **Tempo dedicado (aprox.):** `[ex.: 6h00]`
- **Evidência da contribuição**:
<img width="900" height="1600" alt="probe_ripe" src="https://github.com/user-attachments/assets/ecc4cd95-e9c0-413e-9a0e-09c4083959f3" />
`[]` 
`[]`

### Integrante 2 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
`[]` 
`[]`

### Integrante 3 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[]` 
`[]`

### Integrante 4 — `[Igor da Silva Alves Correa]`
- **O que fez nesta etapa:** `[Contribuiu com a pesquisa para o projeto]`
- **Tempo dedicado (aprox.):** `[ex.: 2h]`
- **Evidência da contribuição** <img width="877" height="760" alt="image" src="https://github.com/user-attachments/assets/56a0a29f-0060-4ac4-afae-c9ab2fc89e1d" />
 
`[]` 
`[]`

### Integrante 5 — `[Escreva nome completo do aluno ]`
- **O que fez nesta etapa:** `[]`
- **Tempo dedicado (aprox.):** `[ex.: 3h30]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[]` 
`[]`

### Integrante 6 — `Wendel Henrique da Silva Rocha`
- **O que fez nesta etapa:** `Contribuiu para a escolha do modelo utilizado, opinando nos benefícios e malefícios de cada escolha, além de explicar como chamar a API. Tambem definiiu o item 1. Situação.`
- **Tempo dedicado (aprox.):** `1h30`
- **Evidência da contribuição** **: 
<img width="540" height="1170" alt="image" src="https://github.com/user-attachments/assets/06c573a1-c1f7-4650-95b2-ab51186dcca0" />


---

## Fontes consultadas

<!-- Mínimo de 3 fontes. Liste todas as páginas de documentação, artigos ou repositórios usados. -->

1. [https://atlas.ripe.net/]
2. [https://www.ripe.net/analyse/internet-measurements/ripe-atlas/make-a-measurement/]
3. [ ]
