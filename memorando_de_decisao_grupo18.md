# Memorando de Decisão — Fonte de Dados do Projeto


| Campo | Informação |
|---|---|
| Curso / Disciplina | `CC` |
| Projeto integrador | `Modelo Preditivo de Rede` |
| Orientador(a) | `Andrea Ono Sakai` |
| Data de entrega desta etapa | `08/09/2026` |
| Integrantes do grupo | `[Bruno Alves Ribeiro de Souza 42276047 -  Samuel de Oliveira Santos 41761782 - Victoria Agatha Rodrigues Fagundes 43756042 - Wendel Henrique da Silva Rocha 42614945 - Igor da Silva Alves Correa 41885163 - Pedro Henrique Alexandre da Silva 42947049]`


---

> Preencha cada seção com o que você encontrou na pesquisa. Não deixe nenhum campo com o texto entre colchetes — substitua pelo seu conteúdo. Toda informação levantada nas Opções A e B precisa indicar a fonte de onde veio.

## 1. Situação

<!-- Em uma frase: qual decisão precisa ser tomada e por quê. 
O pipeline do projeto já está definido: qualquer fonte de dados precisa produzir registros que se transformem em janelas e, por fim, em X = [latência, perda, jitter]. Falta decidir de onde virão esses dados na próxima fase. A equipe do projeto precisa recomendar, com base em pesquisa e não em preferência pessoal, se a próxima etapa deve usar um dataset real já publicado ou a API do RIPE Atlas. O grupo deve produzir um memorando de decisão com a recomendação da tomada de decisão. A recomendação só tem valor se for sustentada por pesquisa real — não existe resposta pronta para copiar; ela precisa ser construída a partir do que vocês encontraram.
-->

Conseguimos definir a forma como vamos conseguir os dados, que é via API e já conseguimos os créditos para isso. Agora devemos definir o pipeline para podermos dar continuidade no projeto e mapear nossos passos.

## 2. Opção A — DATASET REAL - 11-Day Starlink Ping Measurements Dataset

<!-- O que foi encontrado sobre um dataset real de ICMP. Cite a fonte de cada informação. -->

- **Origem / link:** [https://zenodo.org/records/14987305?preview_file=ping_metrics_2024-05-09.csv]
- **Formato:** [CSV]
- **Período coberto:** [09/05/2024 até 20/05/2024]
- **Campos disponíveis:** [PacketLossCount, RTTAvg (latência), RTTMin e RTTMax (possibilitando o cálculo de jitter)]
- **Licença de uso:** [Dados públicos para pesquisa e uso acadêmico/aberto]

**Resumo do que foi encontrado:**

O dataset 11-Day Starlink Ping Measurements é um conjunto de dados de 11 dias de medições de ping ICMP coletadas de uma antena Starlink localizada em Palo Alto, EUA. As medições foram realizadas como parte de uma avaliação do desempenho da rede Starlink.

Período de medição: 9 a 20 de maio de 2024 (11 dias)
Método de amostragem: Rajadas de 10 pacotes ICMP a cada 10 segundos
Localização: Palo Alto, EUA (Cliente) → Servidor Terrestre
Infraestrutura:
Terminal de usuário Starlink (antena parabólica)
Identificados GS e PoP em San Jose, EUA

## 3. Opção B — API do RIPE Atlas

<!-- O que foi encontrado sobre a API: autenticação, criação e consulta de medições. Cite a fonte de cada informação. -->

- **Documentação consultada (link):** [ https://atlas.ripe.net/ ]
- **Autenticação exigida:** [Link do repositório]
- **Como se cria uma medição:** [Com a utilização de créditos]
- **Como se consultam os resultados:** [Com chamados para o resultado desejado]

[A API Atlas utiliza de créditos oferecidos por hostear um probe em uma máquina em segundo plano após fornecer o link do repositório onde se vai utilizar a API,
(https://www.ripe.net/analyse/internet-measurements/ripe-atlas/make-a-measurement/)]

## 4. Comparação

<!-- Preencha a tabela com base no que você levantou nas seções 2 e 3. -->

| Critério | Opção A — Dataset real | Opção B — API RIPE Atlas |
|---|---|---|
| Controle sobre a coleta |Baixo, pois os dados já foram coletados e disponibilizados pelo projeto IODA. |Alto, pois o grupo pode definir as medições, probes e destinos utilizados. |
| Diversidade geográfica |Alta, por trabalhar com dados de conectividade em escala ampla. |Alta, dependendo dos probes disponíveis e selecionados pelo grupo. |
| Custo / complexidade de implementação |Baixo, pois os dados já estão disponíveis e não é necessário realizar uma nova coleta. |Médio/alto, pois exige configurar o acesso à API, utilizar créditos e estruturar a coleta dos dados. |
| Tempo até os primeiros dados estarem disponíveis |Imediato, pois o dataset já está disponível para consulta. |Depende da configuração e realização das medições, embora o grupo já tenha conseguido os créditos necessários. |

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

### Integrante 2 — `[Samuel de Oliveira Santos ]`
- **O que fez nesta etapa:** `Realizei pesquisas em grupo focadas na escolha mais adequada da API, pesquisa na qual utilizamos de fontes tanto oferecidas em em aula com
- nas fontes externas de pessoas capacitas que tem experiencia no assunto, também contribui com um estudo relacionado ao uso da API em python o quel disponibilizei a todos
- os integrantes no grupo para que todos fossem se familiarizando com o conceito já que é algo novo para todos.`
- **Tempo dedicado (aprox.):** `2:50
`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
- <img width="720" height="1600" alt="3c1b4de0-b6be-4fbc-a747-e9ade5f1bdf3" src="https://github.com/user-attachments/assets/9e714658-873c-4602-9a5a-d067c958f3da" />
-<img width="720" height="1600" alt="image" src="https://github.com/user-attachments/assets/51eea31a-d57e-4a6b-b4a0-8c0a29e81518" />
-<img width="1628" height="1046" alt="image" src="https://github.com/user-attachments/assets/bb73ab55-e13c-4bab-b7d7-bd1408e4ea7c" />

`[]` 
`[]`


### Integrante 3 — `[Pedro Henrique Alexandre da Silva ]`
- **O que fez nesta etapa:** `[Realizei um estudo sobre as alternativas de fonte de dados consideradas pelo grupo, buscando principalmente as diferenças entre usar um dataset já disponível e realizar a coleta por meio da API do RIPE Atlas. A partir dessa análise, organizei os principais pontos relacionados ao controle da coleta, diversidade geográfica, complexidade de implementação e disponibilidade dos dados, levando essas considerações para discussão com o grupo e contribuindo para a comparação entre as opções.]`
- **Tempo dedicado (aprox.):** `[1h:15]`
- **Evidência da contribuição** *(<img width="709" height="1536" alt="image" src="https://github.com/user-attachments/assets/f988fc0a-089b-41f1-9648-3c59789df2c3" />)*: 
`[]` 
`[]`

### Integrante 4 — `[Igor da Silva Alves Correa]`
- **O que fez nesta etapa:** `[Contribuiu com a pesquisa para o projeto]`
- **Tempo dedicado (aprox.):** `[ex.: 2h]`
- **Evidência da contribuição** <img width="877" height="760" alt="image" src="https://github.com/user-attachments/assets/56a0a29f-0060-4ac4-afae-c9ab2fc89e1d" />
 
`[]` 
`[]`

### Integrante 5 —'Victoria Agatha Rodrigues Fagundes'
- **O que fez nesta etapa: '[Auxiliou na escolha do modelo, realizou pesquisas sobre os assuntos afim de trazer uma visão sobre o assunto na hora de decidir qual utilizar, citando os pontos fortes e fracos ao tomar cada decisao]'
- **Tempo dedicado (aprox.):'[1h]'
- **Evidência da contribuição: 
<img width="897" height="852" alt="Captura de tela 2026-09-08 203310" src="https://github.com/user-attachments/assets/cb5f8175-4137-4d09-9e86-ef9406260dec" />
<img width="840" height="812" alt="Captura de tela 2026-09-08 203404" src="https://github.com/user-attachments/assets/dda9c9af-461f-4e5e-92bf-ed3019ace469" />


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
3. [https://catalog.caida.org/dataset/ioda]
