# Diário da Tarefa 3 — Detector inicial com Random Forest

**Período:** 28/09/2026 a 04/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)

**Equipe:** 18 — Bruno Alves Ribeiro de Souza, Igor da Silva Alves Correa, Pedro Henrique Alexandre da Silva, Samuel de Oliveira Santos, Victoria Agatha Rodrigues Fagundes e Wendel Henrique da Silva Rocha
**Scrum Master da tarefa:** ____________ *(preencher)*  
**Repositório GitHub:** [Modelo Preditivo - Projeto Académico](https://github.com/brunoalves2506/Modelo-preditivo---Projeto-Acad-mico---4-Semestre.git)

> A Tarefa 2 definiu o baseline e os rótulos. Esta tarefa treina um **detector do estado atual** (`classe`); não afirma prever uma classe futura. A Tarefa 4 é o preditor de `status_futuro`, em cerca de 12 minutos, e precisa ser comparada com a persistência do estado atual.
>
> Conforme a orientação do professor, o modelo desta tarefa é uma **Random Forest**. A árvore componente apresentada no notebook é somente ilustrativa: a previsão oficial vem da votação do conjunto de árvores.

**Código:** [`notebook/arvore/tarefa3_arvore_inicial.ipynb`](../../notebook/arvore/tarefa3_arvore_inicial.ipynb).
**Entradas:** `treino.csv`, `validacao.csv` e `baseline_por_fluxo.csv` da Tarefa 2. O notebook não abre `teste.csv`; o teste permanece reservado para a avaliação final.

## Contrato da tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Baseline, dataset rotulado e corte temporal | Tarefa 2 |
| **Sai** | Random Forest treinada apenas com treino, com hiperparâmetros registrados | Detector do estado atual |
| **Sai** | Matriz 3×3, métricas por classe, F1 macro, importâncias e exemplos de erros | Análise da Tarefa 3 |
| **Sai** | Variantes de contraste com RTT absoluto/rota | Auditoria de possíveis atalhos; não são o modelo oficial |

## 1. Dados e atributos

- Treino: **95.406** medições; validação: **38.138** medições. Os blocos são temporais e pertencem ao Período B.
- Classes do treino: OK 72.857, RISCO 6.582 e FALHA 15.967.
- Classes da validação: OK 27.180, RISCO 3.388 e FALHA 7.570.
- A ficha de baseline é a da Tarefa 2 e não foi recalculada com o Período B.
- Alvo: `classe` da medição atual.
- Features: `z_robusto`, `aumento_pct`, `jitter_relativo`, `perda_pct`, `timeout_atual`, `n5_timeout`, `n5_aumento80` e `n5_risco`.
- País, IP, rota, identificadores de fluxo e RTT em milissegundos não entram na floresta oficial. Valores ausentes nas features permanecem `NaN`; não são substituídos por zero.

## 2. Random Forest oficial

- Algoritmo: `RandomForestClassifier`, critério Gini, **100 árvores**, `random_state=42`.
- Busca de hiperparâmetros: grade de `max_depth` = 6, 10 ou 14 e `min_samples_leaf` = 1, 10 ou 50. Os modelos são ajustados somente no treino e comparados na validação pela macro-F1. Entre os modelos a até 0,005 do melhor resultado, foi escolhido o de menor soma de folhas.
- Configuração escolhida: `max_depth=6`, `min_samples_leaf=50`. A melhor macro-F1 observada na grade foi 0,9994; a configuração escolhida obteve **0,9957** na validação.
- Profundidade média das árvores componentes: **5,96**; média de folhas por árvore: **19,49**.
- Features de maior importância: `z_robusto` (0,5855), `aumento_pct` (0,1880), `n5_risco` (0,1255) e `jitter_relativo` (0,0902).

## 3. Resultados no estado atual

Matriz de confusão na validação (linhas = classe real; colunas = classe prevista):

| | Prevista OK | Prevista RISCO | Prevista FALHA |
|---|---:|---:|---:|
| **Real OK** | 27.180 | 0 | 0 |
| **Real RISCO** | 17 | 3.371 | 0 |
| **Real FALHA** | 82 | 14 | 7.474 |

| Classe | Precisão | Recall | F1 | Medições |
|---|---:|---:|---:|---:|
| OK | 0,9964 | 1,0000 | 0,9982 | 27.180 |
| RISCO | 0,9959 | 0,9950 | 0,9954 | 3.388 |
| FALHA | 1,0000 | 0,9873 | 0,9936 | 7.570 |

**Macro-F1: 0,9957.** A acurácia foi 99,70%, mas não é o critério principal: como 71,27% das medições da validação são OK, prever sempre OK já produziria essa acurácia sem detectar RISCO ou FALHA.

O erro mais frequente foi FALHA prevista como OK (82 casos); houve também 17 casos de RISCO previstos como OK e 14 de FALHA previstos como RISCO. Os exemplos concretos e os critérios de rotulagem correspondentes estão no notebook.

**Limite da interpretação:** os rótulos são definidos por regras baseadas nas métricas relativas. Como a floresta recebe algumas dessas mesmas métricas, a macro-F1 alta indica que reproduz bem a regra do rótulo no estado atual; não demonstra capacidade de antecipar degradação. Essa avaliação futura é feita separadamente na Tarefa 4.

## 4. Auditoria de atalhos

As variantes de contraste não compõem a entrega oficial:

- Métricas relativas + RTT absoluto (`avg`): importância conjunta do atalho 6,8%; macro-F1 0,9956.
- Métricas relativas + rota: importância conjunta do atalho 7,2%; macro-F1 0,9921.
- Somente RTT absoluto e rota: importância conjunta 100%; macro-F1 0,5229.

Esses resultados são diagnósticos, não uma comparação para substituir o modelo: as variantes com atalhos têm outros conjuntos de features. A floresta oficial usa apenas as métricas relativas definidas no contrato.

## 5. Scrum e diário

- [ ] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| Bruno Alves Ribeiro de Souza | *(preencher)* | | |
| Igor da Silva Alves Correa | *(preencher)* | | |
| Pedro Henrique Alexandre da Silva | *(preencher)* | | |
| Samuel de Oliveira Santos | *(preencher)* | | |
| Victoria Agatha Rodrigues Fagundes | *(preencher)* | | |
| Wendel Henrique da Silva Rocha | *(preencher)* | | |

## Rubrica — Tarefa 3 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---:|---|---|---|
| Random Forest oficial | 1,5 | Features declaradas, ajuste apenas no treino, hiperparâmetros e semente registrados | | |
| Métricas de três classes | 1,0 | Matriz 3×3, métricas por classe e macro-F1 na validação | | |
| Independência de rota | 1,0 | Modelo oficial sem rota/RTT absoluto e análise de contraste | | |
| Scrum + diário | 0,5 | Board e diário dos integrantes | | |
| **Total** | **4,0** | | **___ / 4,0** | |
