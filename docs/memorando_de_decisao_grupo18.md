# Memorando de Decisão — Fonte de Dados do Projeto


| Campo | Informação |
|---|---|
| Curso / Disciplina | `CC` |
| Projeto integrador | `Modelo Preditivo de Rede` |
| Orientador(a) | `Andrea Ono Sakai` |
| Data de entrega desta etapa | `15/09/2026` |
| Integrantes do grupo | `Bruno Alves Ribeiro de Souza 42276047 -  Samuel de Oliveira Santos 41761782 - Victoria Agatha Rodrigues Fagundes 43756042 - Wendel Henrique da Silva Rocha 42614945 - Igor da Silva Alves Correa 41885163 - Pedro Henrique Alexandre da Silva 42947049`


---

> Preencha cada seção com o que você encontrou na pesquisa. Não deixe nenhum campo com o texto entre colchetes — substitua pelo seu conteúdo. Toda informação levantada nas Opções A e B precisa indicar a fonte de onde veio.

## 1. Situação

Para que o modelo preditivo de falhas de rede seja treinado, a equipe precisa decidir, com base em pesquisa, se os dados de latência, perda e jitter virão do 11-Day Starlink Ping Measurements Dataset (já publicado) ou de medições próprias coletadas via API RIPE Atlas.

## 2. Opção A — DATASET REAL - 11-Day Starlink Ping Measurements Dataset

- **Origem / link:** https://zenodo.org/records/14987305
- **Formato:** CSV
- **Período coberto:** 09/05/2024 até 20/05/2024
- **Campos disponíveis:** PacketLossCount, RTTAvg (latência), RTTMin e RTTMax (possibilitando o cálculo de jitter)
- **Licença de uso:** Creative Commons Attribution 4.0 (CC BY 4.0) — uso e redistribuição livres com crédito ao autor

**Resumo do que foi encontrado:**

O dataset consultado no repositório Zenodo contém medições contínuas de ping realizadas na rede Starlink durante um período de 11 dias em maio de 2024. Ele fornece um histórico tabular estruturado com métricas diretas de rede, como contagem de pacotes perdidos (PacketLossCount) e tempos mínimo, máximo e médio de ida e volta (RTT), oferecendo a base exata para derivar os parâmetros de latência, perda e jitter sem a necessidade de realizar novas medições ativas.


## 3. Opção B — API do RIPE Atlas

- **Documentação consultada (link):** https://atlas.ripe.net/docs/apis/rest-api-manual/
- **Autenticação exigida:** A REST API do RIPE Atlas requer autenticação baseada em chaves de API (API keys). Essas chaves são criadas no painel do usuário e devem ser enviadas no cabeçalho das requisições (como um parâmetro de autorização) para realizar operações que consomem créditos, como a criação de medições personalizadas.
- **Como se cria uma medição:** A criação de testes customizados (User-Defined Measurements) é feita enviando uma requisição POST para o endpoint [https://atlas.ripe.net/api/v2/measurements/](https://atlas.ripe.net/api/v2/measurements/). O payload da requisição deve conter, em formato JSON, a definição da medição (ex: protocolo ICMP para ping, alvo/destino) e a seleção das sondas (probes) de onde os pings partirão. Essa ação debita os créditos da conta associada à API key.
- **Como se consultam os resultados:** Após o teste ser concluído, os dados são recuperados enviando uma requisição GET para o endpoint de resultados da medição específica, seguindo o padrão da URL [https://atlas.ripe.net/api/v2/measurements/](https://atlas.ripe.net/api/v2/measurements/){id_da_medicao}/results/. A resposta da API retorna os dados detalhados da amostragem em formato JSON, incluindo os RTTs e pacotes perdidos.

**Resumo do que foi encontrado:**

A API RIPE Atlas permite consultar medições públicas existentes ou criar medições próprias (User-Defined Measurements), autenticando por chave de API ou sessão. A criação é feita via POST /api/v2/measurements/, informando o que será medido e de quais sondas; os resultados são obtidos via GET /api/v2/measurements/{id}/results/, em formato JSON. Medições personalizadas consomem créditos, que o grupo já garantiu ao hospedar uma probe própria.

## 4. Comparação

| Critério | Opção A — Dataset real | Opção B — API RIPE Atlas |
|---|---|---|
| Controle sobre a coleta |Controle absoluto de parâmetros, Disponibilidade total do hardware e Dados estáticos imutáveis para quem consome. |O Controle da API RIPE ATLAS é Limitado Compartilhado pois é preciso seguir as regras e diretrizes da plataforma. |
| Diversidade geográfica |Escopo Baixo, parâmetros baseados de um único ponto Palo Alto, EUA (Cliente) → Servidor Terrestre. |Escopo: Muito alto / Global,  a plataforma conta com uma rede distribuída de mais de 10.000 sondas ativas em mais de 170 países e milhares de Redes/ASNs diferentes. |
| Custo / complexidade de implementação |Custos Altos na coleta primária, muitos gastos com pacotes de internet, rede e infraestrutura porém, nenhum gasto para usuários que utilizam o dataset pronto já publicado e com o acesso aberto. Complexidade baixa para os que utilizam o pacote  publicado pois basta fazer o download do arquivo tabular no repositório público (Zenodo) e aplicar rotinas simples de análise (Python, R ou Excel) para processar os pings e derivar a perda e o jitter.  |Custo Financeiro Variável. A consulta a dados públicos e a obtenção de chaves básicas de API são gratuitas, mas testes personalizados(User Defined Measurements) consomem créditos do RIPE Atlas. Créditos são obtidos hospedando uma sonda física/virtual atrelada à comunidade ou por doações/parcerias formais. Complexidade Média Alta. Exige aprender a estrutura da REST API da plataforma, manipular requisições HTTP, controlar paginação de múltiplos pontos de vantagem e tratar o formato JSON de resposta antes de poder calcular latência, perda ou jitter. |
| Tempo até os primeiros dados estarem disponíveis |Imediato (para o usuário do dataset pronto) / Longo (caso você precisasse realizar a amostragem do zero). Análise: Por se tratar de um conjunto de dados histórico já coletado, formatado e disponibilizado em acesso aberto no repositório Zenodo, o tempo até os primeiros dados estarem disponíveis resume-se ao tempo de download dos arquivos .csv. No entanto, se fosse realizar uma nova amostragem idêntica na rede Starlink, seria necessário aguardar os 11 dias inteiros de execução da rotina de testes. |Tempo: Rápido, em alguns minutos ou horas. Análise: A plataforma permite acessar via API os resultados de mediçoes públicas passadas quase que instantaneamente. É possivel fazer novas medições personalizadas(User-Defined Measurement), o sistema agenda o teste com as sondas selecionadas e disponibiliza o retorno via requisição HTTP pouco tempo após o término da execução. |

## 5. Recomendação

Recomendamos a opção B, Ripe Atlas, como fonte de dados para o treinamento do modelo.

## 6. Justificativa

Optamos pela API pois é uma fonte de dados dinâmica, assim como os dados de rede que possuem n fatores que podem influenciar no treinamento do modelo. A adoção da Opção A, o dataset, colocaria em xeque essa dinâmica que buscamos, pois o mesmo representa apenas um retrato isolado da rede, limitando o treinamento do modelo apenas naquele período e naquela rede específica — limitação que não se repete com os dados dinâmicos provenientes da API. Embora a Opção A ofereça controle mais estável e imediato sobre os dados por já estar publicada e fechada, a Opção B compensa esse controle mais restrito com uma cobertura de rede muito mais ampla — mais de 10.000 sondas em mais de 170 países — e com a flexibilidade de adaptar novas coletas conforme as necessidades do modelo evoluam ao longo do treinamento e da validação, o que a torna mais adequada para essa fase do projeto.

## 7. Riscos e limitações

O principal risco para o uso da API é o consumo de créditos para medições personalizadas, o que pode limitar a quantidade de dados coletados se nós não planejarmos bem a coleta. Outro ponto relevante é a necessidade de lidar com a response da API, validando o JSON proveniente antes de transformar em dados para o treinamento. Para mitigar esses riscos, acumulamos créditos de API e monitoraremos o saldo, planejando a coleta e validando os dados antes do treinamento, de modo a reduzir erros de processamento.

## 8. Contribuição Individual dos Integrantes

### Integrante 1 — ` Bruno Alves Ribeiro de Souza `
- **O que fez nesta etapa:** `Disponibilizou e configurou uma máquina pessoal para a instalação da probe RIPE - Apresentou e analisou a possibilidade de utilização do dataset 11-Day Starlink Ping Measurements `
- **Tempo dedicado (aprox.):** `6h00`
- **Evidência da contribuição**:
<img width="900" height="1600" alt="probe_ripe" src="https://github.com/user-attachments/assets/ecc4cd95-e9c0-413e-9a0e-09c4083959f3" />
<img width="1174" height="892" alt="image" src="https://github.com/user-attachments/assets/dd0ab00c-c502-408b-9cf7-4825b3a58c2c" />

### Integrante 2 — `Samuel de Oliveira Santos `
- **O que fez nesta etapa:** Realizei pesquisas em grupo focadas na escolha mais adequada da API, utilizando fontes oferecidas em aula e fontes externas de pessoas com experiência no assunto. Também contribuí com um estudo sobre o uso da API em Python, que disponibilizei a todos os integrantes do grupo para que se familiarizassem com o conceito, já que é algo novo para todos.
* Trabalhei na Seção 4, construção da tabela comparativa entre API e Dataset, na qual foi realizada uma pesquisa minuciosa na documentação de ambos os métodos, para realizar uma comparação com precisão.

- **Tempo dedicado (aprox.):** `2h50`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
 https://github.com/Samulesantos20045/Evidencias.git

### Integrante 3 — `Pedro Henrique Alexandre da Silva `
- **O que fez nesta etapa:** `Realizei o estudo comparativo inicial entre o dataset da Starlink e a API do RIPE Atlas (Seção 4). Atuei como Revisor de Qualidade (QA) na reta final, realizando a auditoria do repositório: corrigi divergências na data de entrega, ajustei a ortografia do memorando, removi resquícios do template base, alinhei a árvore do README.md e garanti a ocultação de dados sensíveis nas evidências do grupo.`
- **Tempo dedicado (aprox.):** `1h15`
- **Evidência da contribuição**
- <img width="1317" height="367" alt="Captura de tela 2026-09-15 121636" src="https://github.com/user-attachments/assets/5bd2f1fd-0f8a-4a79-b46e-34de648b1d8a" />
- <img width="910" height="74" alt="Captura de tela 2026-09-15 111529" src="https://github.com/user-attachments/assets/d3d2532c-12d7-44f4-b42e-9a844d0582ee" />

### Integrante 4 — `Igor da Silva Alves Correa`
- **O que fez nesta etapa:** `Contribuiu com a pesquisa para o projeto`
- **Tempo dedicado (aprox.):** `2h30`
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

1. [https://atlas.ripe.net/docs/apis/rest-api-manual/]
2. [https://www.ripe.net/analyse/internet-measurements/ripe-atlas/make-a-measurement/]
3. [https://zenodo.org/records/14987305]
4. [https://creativecommons.org/licenses/by/4.0/legalcode.en]

