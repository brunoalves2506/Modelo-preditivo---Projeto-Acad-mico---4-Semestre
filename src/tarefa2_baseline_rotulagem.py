import pandas as pd
import numpy as np
from pathlib import Path
from config import DATA_PROCESSED, DATA_RAW

# ==========================================
# 1. CONFIGURAÇÕES INICIAIS E CAMINHOS
# ==========================================
CSV_PERIODO_A = DATA_RAW.parent.parent / "data_ripe_atlas" / "raw" / "v2" / "ripe_atlas_mesh_v2_ping_ipv4_periodo_a.csv"
CSV_PERIODO_B = DATA_RAW.parent.parent / "data_ripe_atlas" / "raw" / "v2" / "ripe_atlas_mesh_v2_ping_ipv4_periodo_b.csv"

# Mapeamento de colunas (v2 -> Padrão do projeto)
COLUNAS_MAP = {
    "latencia_ms": "avg",
    "enviados": "sent",
    "recebidos": "rcvd",
    "probe_id": "prb_id"
}

# ==========================================
# 2. FUNÇÕES AUXILIARES
# ==========================================
def calcular_mad(serie):
    """Calcula o Desvio Absoluto Mediano (MAD)."""
    mediana = serie.median()
    return (serie - mediana).abs().median()

def calcular_metricas_baseline(df_a):
    """Calcula a ficha de baseline para o Período A."""
    print("[Baseline] Calculando fichas para o Período A...")
    
    # Agrupa por fluxo (prb_id + dst_addr)
    fluxos = df_a.groupby(["prb_id", "dst_addr"])
    
    resultados = []
    fluxos_excluidos = []
    
    for (prb_id, dst_addr), grupo in fluxos:
        # Pega apenas RTTs válidos (não nulos)
        rtt_validos = grupo["avg"].dropna()
        
        # Regra 4: Piso de 1.500 RTTs válidos
        if len(rtt_validos) < 1500:
            fluxos_excluidos.append({"prb_id": prb_id, "dst_addr": dst_addr, "n_validos": len(rtt_validos)})
            continue
            
        mediana = rtt_validos.median()
        mad = calcular_mad(rtt_validos)
        
        # Jitter típico (mediana do jitter onde ele existe)
        jitter_tipico = grupo["jitter"].dropna().median() if "jitter" in grupo.columns else 0
        
        # Perda típica (mediana do percentual de perda)
        perda_tipica = grupo["perda_pct"].median() if "perda_pct" in grupo.columns else 0
        
        # Proporção de resposta
        prop_resposta = len(rtt_validos) / len(grupo)
        
        resultados.append({
            "prb_id": prb_id,
            "dst_addr": dst_addr,
            "fluxo_id": f"{prb_id}|{dst_addr}",
            "mediana": mediana,
            "MAD": mad,
            "jitter_tipico": jitter_tipico,
            "perda_tipica": perda_tipica,
            "prop_resposta": prop_resposta,
            "status": "ok"
        })
        
    df_baseline = pd.DataFrame(resultados)
    df_excluidos = pd.DataFrame(fluxos_excluidos)
    
    print(f"[Baseline] Fichas geradas: {len(df_baseline)} | Excluídos: {len(df_excluidos)}")
    return df_baseline, df_excluidos

# ==========================================
# 3. FUNÇÕES DE MÉTRICAS DO PERÍODO B
# ==========================================
def calcular_metricas_b(df_b, df_baseline):
    """Calcula as métricas relativas do Período B usando o baseline congelado."""
    print("[Métricas B] Calculando métricas relativas...")
    
    # Merge com o baseline
    df = df_b.merge(df_baseline[["prb_id", "dst_addr", "mediana", "MAD", "jitter_tipico"]], 
                    on=["prb_id", "dst_addr"], how="inner")
    
    # 1. z_robusto (com fallback para MAD=0)
    # Fallback: max(IQR / 1.349, 1 ms). Como não temos IQR explícito, usamos uma aproximação ou o próprio MAD.
    # Para simplificar e seguir a regra, se MAD=0, usamos max(MAD, 1) como denominador.
    denominador = df["MAD"].apply(lambda x: max(x * 1.4826, 1) if x == 0 else x * 1.4826)
    df["z_robusto"] = (df["avg"] - df["mediana"]) / denominador
    
    # Se MAD = 0 e RTT atual = mediana, z_robusto = 0
    df.loc[(df["MAD"] == 0) & (df["avg"] == df["mediana"]), "z_robusto"] = 0
    
    # 2. aumento_pct
    df["aumento_pct"] = (df["avg"] - df["mediana"]) / df["mediana"] * 100
    
    # 3. jitter_relativo
    df["jitter_relativo"] = df["jitter"] / df["jitter_tipico"].replace(0, np.nan)
    # Tratamento: jitter_tipico=0 e jitter atual=0 -> 1; jitter_tipico=0 e jitter>0 -> >=3
    df.loc[(df["jitter_tipico"] == 0) & (df["jitter"] == 0), "jitter_relativo"] = 1
    df.loc[(df["jitter_tipico"] == 0) & (df["jitter"] > 0), "jitter_relativo"] = 3
    
    # 4. perda_pct
    df["perda_pct"] = (df["sent"] - df["rcvd"]) / df["sent"] * 100
    
    # 5. timeout_atual
    df["timeout_atual"] = 0
    df.loc[df["avg"].isna() | (df["perda_pct"] == 100), "timeout_atual"] = 1
    
    # 6. Janela deslizante (n5)
    # Ordenar por fluxo e timestamp para a janela funcionar
    df = df.sort_values(by=["prb_id", "dst_addr", "timestamp"])
    
    df["n5_timeout"] = df.groupby(["prb_id", "dst_addr"])["timeout_atual"].transform(
        lambda x: x.rolling(window=5, min_periods=1).sum()
    )
    
    df["n5_aumento80"] = df.groupby(["prb_id", "dst_addr"])["aumento_pct"].transform(
        lambda x: (x > 80).rolling(window=5, min_periods=1).sum()
    )
    
    # Critério individual de RISCO (linha 5)
    cond_risco_ind = (
        ((df["z_robusto"] >= 2) & (df["z_robusto"] < 3.5)) |
        ((df["aumento_pct"] >= 30) & (df["aumento_pct"] <= 80)) |
        (df["jitter_relativo"] >= 3)
    )
    df["crit_risco_ind"] = cond_risco_ind.astype(int)
    
    df["n5_risco"] = df.groupby(["prb_id", "dst_addr"])["crit_risco_ind"].transform(
        lambda x: x.rolling(window=5, min_periods=1).sum()
    )
    
    return df

# ==========================================
# 4. FUNÇÃO DE ROTULAGEM
# ==========================================
def aplicar_rotulagem(df):
    """Aplica a tabela de rotulagem na ordem exata."""
    print("[Rotulagem] Aplicando regras de OK, RISCO e FALHA...")
    
    # Inicializa como OK
    df["classe"] = "OK"
    
    # Linha 1: FALHA - perda_pct >= 10
    cond1 = df["perda_pct"] >= 10
    df.loc[cond1, "classe"] = "FALHA"
    
    # Linha 2: FALHA - n5_timeout >= 3
    cond2 = (df["classe"] == "OK") & (df["n5_timeout"] >= 3)
    df.loc[cond2, "classe"] = "FALHA"
    
    # Linha 3: FALHA - z_robusto >= 3.5 (com RTT presente)
    cond3 = (df["classe"] == "OK") & (df["z_robusto"] >= 3.5) & (df["avg"].notna())
    df.loc[cond3, "classe"] = "FALHA"
    
    # Linha 4: FALHA - n5_aumento80 >= 2
    cond4 = (df["classe"] == "OK") & (df["n5_aumento80"] >= 2)
    df.loc[cond4, "classe"] = "FALHA"
    
    # Linha 5: RISCO - critério individual E n5_risco >= 2
    cond5 = (df["classe"] == "OK") & (df["crit_risco_ind"] == 1) & (df["n5_risco"] >= 2)
    df.loc[cond5, "classe"] = "RISCO"
    
    return df

# ==========================================
# 5. FUNÇÃO DE RECORTE TEMPORAL (50/20/30)
# ==========================================
def recorte_temporal(df_b):
    """Divide o Período B em Treino (50%), Validação (20%) e Teste (30%) por fluxo."""
    print("[Recorte] Dividindo em Treino, Validação e Teste...")
    
    df_treino = []
    df_val = []
    df_teste = []
    
    for (prb_id, dst_addr), grupo in df_b.groupby(["prb_id", "dst_addr"]):
        n = len(grupo)
        n_treino = int(n * 0.5)
        n_val = int(n * 0.2)
        
        df_treino.append(grupo.iloc[:n_treino])
        df_val.append(grupo.iloc[n_treino:n_treino+n_val])
        df_teste.append(grupo.iloc[n_treino+n_val:])
        
    return pd.concat(df_treino), pd.concat(df_val), pd.concat(df_teste)

# ==========================================
# 6. EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("=== INICIANDO TAREFA 2 ===")
    
    # 1. Carregar dados
    print("Carregando dados brutos...")
    df_a = pd.read_csv(CSV_PERIODO_A)
    df_b = pd.read_csv(CSV_PERIODO_B)
    
    # Renomear colunas se necessário (v2 -> Padrão)
    df_a = df_a.rename(columns=COLUNAS_MAP)
    df_b = df_b.rename(columns=COLUNAS_MAP)
    
    # 2. Calcular Baseline (Período A)
    df_baseline, df_excluidos = calcular_metricas_baseline(df_a)
    
    # Salvar Baseline
    caminho_baseline = DATA_PROCESSED / "baseline_por_fluxo.csv"
    df_baseline.to_csv(caminho_baseline, index=False)
    print(f"Baseline salvo em: {caminho_baseline}")
    
    # 3. Calcular Métricas do Período B
    df_b_metricas = calcular_metricas_b(df_b, df_baseline)
    
    # 4. Rotular Período B
    df_b_rotulado = aplicar_rotulagem(df_b_metricas)
    
    # 5. Recorte Temporal
    df_treino, df_val, df_teste = recorte_temporal(df_b_rotulado)
    
    # Salvar arquivos finais
    df_b_rotulado.to_csv(DATA_PROCESSED / "dataset_rotulado_b.csv", index=False)
    df_treino.to_csv(DATA_PROCESSED / "treino.csv", index=False)
    df_val.to_csv(DATA_PROCESSED / "validacao.csv", index=False)
    df_teste.to_csv(DATA_PROCESSED / "teste.csv", index=False)
    
    print("\n=== RESUMO DA TAREFA 2 ===")
    print(f"Total de medições rotuladas: {len(df_b_rotulado)}")
    print(df_b_rotulado["classe"].value_counts())
    print("\nRecorte Temporal:")
    print(f"Treino: {len(df_treino)} | Validação: {len(df_val)} | Teste: {len(df_teste)}")
    print("\nConcluído com sucesso!")
