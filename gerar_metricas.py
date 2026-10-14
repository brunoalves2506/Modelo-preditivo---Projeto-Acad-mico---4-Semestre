import pandas as pd
import time
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

print("Iniciando o treinamento dos Modelos - Equipe 18...\n")

# Lendo os arquivos direto da pasta processada do projeto
try:
    df_treino = pd.read_csv('data_ripe_atlas/processed/treino.csv')
    df_teste = pd.read_csv('data_ripe_atlas/processed/teste.csv')
    print("Arquivos CSV carregados com sucesso!\n")
except FileNotFoundError:
    print("ERRO: O Python não achou os arquivos. Certifique-se de rodar o comando na pasta raiz do projeto.")
    exit()

# Mapeando OK = 0, RISCO = 1, FALHA = 2 (Exigência do XGBoost)
mapeamento_classes = {'OK': 0, 'RISCO': 1, 'FALHA': 2}

# Transformando a coluna de texto em números
df_treino['classe_num'] = df_treino['classe'].map(mapeamento_classes)
df_teste['classe_num'] = df_teste['classe'].map(mapeamento_classes)

# Limpando colunas inúteis (ID, data, IP, etc) para a IA ler apenas as métricas de rede
colunas_para_remover = [
    'fluxo_id', 'prb_id', 'dst_addr', 'measurement_id', 'timestamp', 
    'datetime_utc', 'pais_origem', 'pais_destino', 'rota', 'periodo', 
    'classe', 'classe_num', 'conjunto'
]

X_train = df_treino.drop(colunas_para_remover, axis=1)
y_train = df_treino['classe_num']
X_test = df_teste.drop(colunas_para_remover, axis=1)
y_test = df_teste['classe_num']

# Configurando os 3 modelos exigidos
modelos = {
    "Árvore de Decisão": DecisionTreeClassifier(max_depth=5, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
    "XGBoost": XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
}

resultados = []

# Treinando e gerando resultados
for nome, modelo in modelos.items():
    print(f"Treinando {nome}...")
    
    inicio_treino = time.time()
    modelo.fit(X_train, y_train)
    tempo_treino = time.time() - inicio_treino
    
    inicio_pred = time.time()
    y_pred = modelo.predict(X_test)
    tempo_pred = time.time() - inicio_pred
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='macro', zero_division=0)
    rec = recall_score(y_test, y_pred, average='macro', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
    
    resultados.append({
        'Modelo': nome,
        'Acurácia (%)': round(acc * 100, 2),
        'Precisão': round(prec, 3),
        'Recall': round(rec, 3),
        'F1-Score': round(f1, 3),
        'Treino (s)': round(tempo_treino, 4),
        'Predição (s)': round(tempo_pred, 4)
    })
    
    print(f"Matriz de Confusão do {nome}:")
    print(confusion_matrix(y_test, y_pred))
    print("-" * 40)

# Imprimindo a tabela final
df_resultados = pd.DataFrame(resultados)
print(df_resultados.to_markdown(index=False))