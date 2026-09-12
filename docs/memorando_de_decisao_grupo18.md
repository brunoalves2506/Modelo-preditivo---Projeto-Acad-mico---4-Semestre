# Memorando de Decisão — Fonte de Dados do Projeto


| Campo | Informação |
|---|---|
| Curso / Disciplina | `CC` |
| Projeto integrador | `Modelo Preditivo de Rede` |
| Orientador(a) | `Andrea Ono Sakai` |
| Data de entrega desta etapa | `08/09/2026` |
| Integrantes do grupo | `Bruno Alves Ribeiro de Souza 42276047 -  Samuel de Oliveira Santos 41761782 - Victoria Agatha Rodrigues Fagundes 43756042 - Wendel Henrique da Silva Rocha 42614945 - Igor da Silva Alves Correa 41885163 - Pedro Henrique Alexandre da Silva 42947049`


---

> Preencha cada seção com o que você encontrou na pesquisa. Não deixe nenhum campo com o texto entre colchetes — substitua pelo seu conteúdo. Toda informação levantada nas Opções A e B precisa indicar a fonte de onde veio.

## 1. Situação

<!-- Em uma frase: qual decisão precisa ser tomada e por quê. 
O pipeline do projeto já está definido: qualquer fonte de dados precisa produzir registros que se transformem em janelas e, por fim, em X = [latência, perda, jitter]. Falta decidir de onde virão esses dados na próxima fase. A equipe do projeto precisa recomendar, com base em pesquisa e não em preferência pessoal, se a próxima etapa deve usar um dataset real já publicado ou a API do RIPE Atlas. O grupo deve produzir um memorando de decisão com a recomendação da tomada de decisão. A recomendação só tem valor se for sustentada por pesquisa real — não existe resposta pronta para copiar; ela precisa ser construída a partir do que vocês encontraram.
-->

Preferimos utilizar a Opção B (API RIPE Atlas) porque, diante das dimensões comparadas que devem ser realizadas, ela se destaca em atualidade do arquivo e diversidade geográfica - uma rede que possui mais de 10.000 sondas ativas, com dinamismo em todos os dados, e o principal, poder trabalhar com atualizações entre as métricas de rede (latência, perda, jitter) que variam conforme os fatores externos, o modelo se encaixa perfeitamente ao atuar com as coletas de amostras contínuas e sob demanda, ao invés de ficar restrito a um único recorte histórico de um certo período ou a uma única rede, como por exemplo a opção A (Dataset). A Opção A também possui os seus benefícios como um controle mais estável e imediato sobre os dados, por se tratar de um conjunto já fechado e publicado, além de menor complexidade de análise. Através desses fatos, para a fase de treinamento e validação do modelo, a Opção B se destaca, sua diversidade geográfica e a flexibilidade de adaptar as necessidades específicas conforme o necessário, atendem melhor os pré-requisitos do objetivo do modelo.

## 2. Opção A — DATASET REAL - 11-Day Starlink Ping Measurements Dataset

<!-- O que foi encontrado sobre um dataset real de ICMP. Cite a fonte de cada informação. -->

- **Origem / link:** https://zenodo.org/records/14987305?preview_file=ping_metrics_2024-05-09.csv
- **Formato:** CSV
- **Período coberto:** 09/05/2024 até 20/05/2024
- **Campos disponíveis:** PacketLossCount, RTTAvg (latência), RTTMin e RTTMax (possibilitando o cálculo de jitter)
- **Licença de uso:** Creative Commons Attribution 4.0 (CC BY 4.0) — uso e redistribuição livres com crédito ao autor

**Resumo do que foi encontrado:**

O dataset consultado no repositório Zenodo contém medições contínuas de ping realizadas na rede Starlink durante um período de 11 dias em maio de 2024. Ele fornece um histórico tabular estruturado com métricas diretas de rede, como contagem de pacotes perdidos (PacketLossCount) e tempos mínimo, máximo e médio de ida e volta (RTT), oferecendo a base exata para derivar os parâmetros de latência, perda e jitter sem a necessidade de realizar novas medições ativas.


## 3. Opção B — API do RIPE Atlas

<!-- O que foi encontrado sobre a API: autenticação, criação e consulta de medições. Cite a fonte de cada informação. -->

- **Documentação consultada (link):** https://atlas.ripe.net/docs/apis/rest-api-manual/
- **Autenticação exigida:** A REST API do RIPE Atlas requer autenticação baseada em chaves de API (API keys). Essas chaves são criadas no painel do usuário e devem ser enviadas no cabeçalho das requisições (como um parâmetro de autorização) para realizar operações que consomem créditos, como a criação de medições personalizadas.
- **Como se cria uma medição:** A criação de testes customizados (User-Defined Measurements) é feita enviando uma requisição POST para o endpoint [https://atlas.ripe.net/api/v2/measurements/](https://atlas.ripe.net/api/v2/measurements/). O payload da requisição deve conter, em formato JSON, a definição da medição (ex: protocolo ICMP para ping, alvo/destino) e a seleção das sondas (probes) de onde os pings partirão. Essa ação debita os créditos da conta associada à API key.
- **Como se consultam os resultados:** Após o teste ser concluído, os dados são recuperados enviando uma requisição GET para o endpoint de resultados da medição específica, seguindo o padrão da URL [https://atlas.ripe.net/api/v2/measurements/](https://atlas.ripe.net/api/v2/measurements/){id_da_medicao}/results/. A resposta da API retorna os dados detalhados da amostragem em formato JSON, incluindo os RTTs e pacotes perdidos.

**Resumo do que foi encontrado:**

A API RIPE Atlas permite consultar medições públicas existentes ou criar medições próprias (User-Defined Measurements), autenticando por chave de API ou sessão. A criação é feita via POST /api/v2/measurements/, informando o que será medido e de quais sondas; os resultados são obtidos via GET /api/v2/measurements/{id}/results/, em formato JSON. Medições personalizadas consomem créditos, que o grupo já garantiu ao hospedar uma probe própria.

## 4. Comparação

<!-- Preencha a tabela com base no que você levantou nas seções 2 e 3. -->

| Critério | Opção A — Dataset real | Opção B — API RIPE Atlas |
|---|---|---|
| Controle sobre a coleta |Controle absoluto de parâmetros, Disponibilidade total do hardware e Dados estáticos imutáveis para quem consome . |Controle API RIPE ATLAS é Limitado Compartilhado pois é preciso serguir as regras e diretrizes da plataforma. |
| Diversidade geográfica |Escopo Baixo, parametros baseados de um unico ponto Palo Alto, EUA (Cliente) → Servidor Terrestre. |Escopo: Muito alto / Global,  a plataforma conta com uma rede distribuída de mais de 10.000 sondas ativas em mais de 170 países e milhares de Redes/ASNs diferentes. |
| Custo / complexidade de implementação |Custos Altos na coleta primaria, muitos gastos com pacotes de internet, rede e infraestrutura porém, nenhum gasto para usuarios que utilizam o dataset proto já publicado e com o acesso aberto. Complexidade baixa para os que utilizam o pacote  publicado pois basta fazer o download do arquivo tabular no repositório público (Zenodo) e aplicar rotinas simples de análise (Python, R ou Excel) para processar os pings e derivar a perda e o jitter.  |Custo Financeiro Variavel. A consulta a dados públicos e a obtenção de chaves basicas de API são gratuitas, mas testes personalizados(User Defined Measurements) consomem créditos do RIPE Atlas. Créditos são obtidos hospedando uma sonda física/virtual atrelada à comunidade ou por doaçoes/parcerias formais. Complexidade Média Alta. Exige aprender a estrutura da REST API da plataforma, manipular requisiçoes HTTP controlar paginação de múltiplos pontos de vantagem e tratar o formato JSON de resposta antes de poder calcular latência, perda ou jitter. |
| Tempo até os primeiros dados estarem disponíveis |Imediato (para o usuário do dataset pronto) / Longo (caso você precisasse realizar a amostragem do zero). Análise: Por se tratar de um conjunto de dados histórico já coletado, formatado e disponibilizado em acesso aberto no repositório Zenodo, o tempo até os primeiros dados estarem disponíveis resume-se ao tempo de download dos arquivos .csv. No entanto, se fosse realizar uma nova amostragem idêntica na rede Starlink, seria necessário aguardar os 11 dias inteiros de execução da rotina de testes. |Tempo: Rápido, em alguns minutos ou horas. Análise: A plataforma permite acessar via API os resultados de mediçoes públicas passadas quase que instantaneamente é possivel fazer novas mediçoes personalizadas(User-Defined Measurement), o sistema agenda o teste com as sondas selecionadas e disponibiliza o retorno via requisição HTTP pouco tempo após o término da execução. |

## 5. Recomendação

 Recomendamos a opção B, Ripe Atlas, como fonte de dados para o treinamento do modelo.

## 6. Justificativa

 Optamos pela API pois é uma fonte de dados dinâmica, assim como os dados de rede que possuem n fatores que podem influenciar no treinamento do modelo. A adoção da opção A, o dataset, colocaria em cheque essa dinâmica que buscamos, pois o mesmo representa apenas um retrato isolado da rede, limitando o treinamento do modelo apenas naquele período, maleficio esse que não se repete com os dados dinâmicos provenientes da API. Além disso, a API fornece um controle maior sobre os dados, o que garante que as medições sejam feitas em cenários mais próximos da realidade operacional. Para mais, a API oferece maior diversidade geográfica e maior flexibilidade para adaptar a coleta às necessidades do modelo, o que torna a opção mais adequada para a fase de treinamento de validação.

## 7. Riscos e limitações

 O principal risco para o uso da API é consumo de créditos para medições personalizadas, o que pode limitar a quantidade de dados coletados se nós não planejarmos bem a coleta. Outro ponto relevante é a necessidade de lidar com a response da API, validando o JSON proveniente antes de transformar em dados para o treinamento. Para mitigar esses riscos, acumulamos créditos de API e monitoraremos o saldo, planejando a coleta e validando os dados antes do treinamento, de modo a reduzir erros de processamento.

## 8. Contribuição Individual dos Integrantes

<!-- cada integrante deve descrever, com suas próprias palavras, o que efetivamente fez nesta etapa. Contribuições genéricas como "ajudei em tudo" não serão aceitas. Use verbos de ação e seja específico (ex.: "pesquisei , analisei, testei, ... apresentei prós/contras ao grupo, ...").-->

### Integrante 1 — ` Bruno Alves Ribeiro de Souza `
- **O que fez nesta etapa:** `[Disponibilizou e configurou uma máquina pessoal para a instalação da probe RIPE]`
- **Tempo dedicado (aprox.):** `[6h00]`
- **Evidência da contribuição**:
<img width="900" height="1600" alt="probe_ripe" src="https://github.com/user-attachments/assets/ecc4cd95-e9c0-413e-9a0e-09c4083959f3" />

### Integrante 2 — `Samuel de Oliveira Santos `
- **O que fez nesta etapa:** Realizei pesquisas em grupo focadas na escolha mais adequada da API, utilizando fontes oferecidas em aula e fontes externas de pessoas com experiência no assunto. Também contribuí com um estudo sobre o uso da API em Python, que disponibilizei a todos os integrantes do grupo para que se familiarizassem com o conceito, já que é algo novo para todos.
- **Tempo dedicado (aprox.):** `2h50`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
  <img width="720" height="1600" alt="3c1b4de0-b6be-4fbc-a747-e9ade5f1bdf3" src="https://github.com/user-attachments/assets/9e714658-873c-4602-9a5a-d067c958f3da" />
  <img width="720" height="1600" alt="image" src="https://github.com/user-attachments/assets/51eea31a-d57e-4a6b-b4a0-8c0a29e81518" />
  <img width="1628" height="1046" alt="image" src="https://github.com/user-attachments/assets/bb73ab55-e13c-4bab-b7d7-bd1408e4ea7c" />

### Integrante 3 — `Pedro Henrique Alexandre da Silva `
- **O que fez nesta etapa:** `[Realizei um estudo sobre as alternativas de fonte de dados consideradas pelo grupo, buscando principalmente as diferenças entre usar um dataset já disponível e realizar a coleta por meio da API do RIPE Atlas. A partir dessa análise, organizei os principais pontos relacionados ao controle da coleta, diversidade geográfica, complexidade de implementação e disponibilidade dos dados, levando essas considerações para discussão com o grupo e contribuindo para a comparação entre as opções.]`
- **Tempo dedicado (aprox.):** `[1h15]`
- **Evidência da contribuição** *(<img width="709" height="1536" alt="image" src="https://github.com/user-attachments/assets/f988fc0a-089b-41f1-9648-3c59789df2c3" />)*

### Integrante 4 — `Igor da Silva Alves Correa`
- **O que fez nesta etapa:** `[Contribuiu com a pesquisa para o projeto]`
- **Tempo dedicado (aprox.):** `[2h30]`
- **Evidência da contribuição:**
  <img width="877" height="760" alt="image" src="https://github.com/user-attachments/assets/56a0a29f-0060-4ac4-afae-c9ab2fc89e1d" />

### Integrante 5 — `Victoria Agatha Rodrigues Fagundes`
- **O que fez nesta etapa:** `Auxiliou na escolha do modelo, realizou pesquisas sobre os assuntos a fim de trazer uma visão sobre o tema na hora de decidir qual utilizar, citando os pontos fortes e fracos de cada decisão.`
- **Tempo dedicado (aprox.):** `1h`
- **Evidência da contribuição:**
  <img width="897" height="852" alt="Captura de tela 2026-09-08 203310" src="https://github.com/user-attachments/assets/cb5f8175-4137-4d09-9e86-ef9406260dec" />
  <img width="840" height="812" alt="Captura de tela 2026-09-08 203404" src="https://github.com/user-attachments/assets/dda9c9af-461f-4e5e-92bf-ed3019ace469" />

### Integrante 6 — `Wendel Henrique da Silva Rocha`
- **O que fez nesta etapa:** `Contribuiu para a escolha do modelo utilizado, opinando nos benefícios e malefícios de cada escolha, além de explicar como chamar a API. Também definiu e revisou itens do documento, implementando explicações e reformulando frases.`
- **Tempo dedicado (aprox.):** `1h30`
- **Evidência da contribuição:** <img width="1171" height="476" alt="image" src="https://github.com/user-attachments/assets/8843477f-1358-4696-9939-55c24afa2f17" />


---

## Fontes consultadas

<!-- Mínimo de 3 fontes. Liste todas as páginas de documentação, artigos ou repositórios usados. -->

1. [https://atlas.ripe.net/docs/apis/rest-api-manual/]
2. [https://www.ripe.net/analyse/internet-measurements/ripe-atlas/make-a-measurement/]
3. [https://zenodo.org/records/14987305]
4. [https://creativecommons.org/licenses/by/4.0/legalcode.en]

