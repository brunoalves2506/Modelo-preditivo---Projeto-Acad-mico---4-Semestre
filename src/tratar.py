"""Transforma JSONs brutos em tabela limpa (CSV)."""
import json
from pathlib import Path

import pandas as pd

from config import CSV_TRATADO, DATA_RAW

def carregar_raws() -> pd.DataFrame:
    registros = []
    for arq in sorted(Path(DATA_RAW).glob("msm_*.json")):
        with open(arq, encoding="utf-8") as f:
            dados = json.load(f)
        if isinstance(dados, list):
            registros.extend(dados)
    if not registros:
        raise RuntimeError(f"Nenhum JSON encontrado em {DATA_RAW}")
    return pd.json_normalize(registros)

def tratar(df: pd.DataFrame) -> pd.DataFrame:
    colunas_esperadas = ["fw", "mver", "its", "dst_name", "af", "dst_addr", "src_addr", "proto", "ttl", "size", "result", "dup", "rcvd", "sent", "min", "max", "avg", "msm_id", "prb_id", "timestamp", "msm_name", "from", "type", "step", "stored_timestamp"]
    
    for c in colunas_esperadas:
        if c not in df.columns:
            df[c] = pd.NA

    for c in ("min", "max", "avg"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
        df.loc[df[c] < 0, c] = pd.NA

    df["rcvd"] = pd.to_numeric(df["rcvd"], errors="coerce").fillna(0).astype(int)
    df["sent"] = pd.to_numeric(df["sent"], errors="coerce").fillna(0).astype(int)
    df["dup"] = pd.to_numeric(df["dup"], errors="coerce").fillna(0).astype(int)

    df["sucesso"] = (df["rcvd"] > 0) & (df["min"].notna())
    df["perda_pacotes"] = (1 - df["rcvd"] / df["sent"]).where(df["sent"] > 0, pd.NA)
    
    return df

if __name__== "__main__":
    print("carregando dados brutos...")
    df_bruto = carregar_raws()

    print("Tratando dados...")
    df_tratado = tratar(df_bruto)

    print(f"Salvando arquivo em {CSV_TRATADO}...")
    df_tratado.to_csv(CSV_TRATADO, index=False)

    print("Concluido com sucesso!")
