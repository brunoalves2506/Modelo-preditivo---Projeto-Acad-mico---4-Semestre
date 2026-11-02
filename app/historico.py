"""Gera previsões retrospectivas por ping usando a floresta da Tarefa 4."""
from __future__ import annotations

from functools import lru_cache

import joblib
import pandas as pd

from .configuracao import ARQ_HISTORICO, ARQ_MODELO_HISTORICO

FEATURES = [
    "z_robusto_t_menos_1",
    "delta_z_robusto",
    "z_robusto",
    "perda_pct",
    "jitter_relativo",
    "n5_risco",
    "n5_timeout",
    "n5_aumento80",
]
CLASSES = ["OK", "RISCO", "FALHA"]
HORIZONTE_SEGUNDOS = 12 * 60
PRIORIDADE_STATUS = {"OK": 0, "RISCO": 1, "FALHA": 2}


@lru_cache(maxsize=1)
def _carregar_pings_modelados() -> pd.DataFrame:
    dados = pd.read_csv(ARQ_HISTORICO)
    modelo = joblib.load(ARQ_MODELO_HISTORICO)

    colunas_obrigatorias = {
        "fluxo_id",
        "rota",
        "timestamp",
        "z_robusto",
        "perda_pct",
        "jitter_relativo",
        "n5_risco",
        "n5_timeout",
        "n5_aumento80",
    }
    ausentes = colunas_obrigatorias.difference(dados.columns)
    if ausentes:
        raise ValueError(f"Colunas ausentes no histórico: {', '.join(sorted(ausentes))}")
    if list(modelo.feature_names_in_) != FEATURES:
        raise ValueError("As features da floresta histórica não correspondem às features esperadas.")

    dados["timestamp"] = pd.to_numeric(dados["timestamp"], errors="raise")
    dados = dados.sort_values(["fluxo_id", "timestamp"], kind="stable").copy()
    grupos = dados.groupby("fluxo_id", sort=False)
    dados["z_robusto_t_menos_1"] = grupos["z_robusto"].shift(1)
    dados["delta_z_robusto"] = dados["z_robusto"] - dados["z_robusto_t_menos_1"]

    probabilidades = modelo.predict_proba(dados[FEATURES])
    classes = list(modelo.classes_)
    indices_previsao = probabilidades.argmax(axis=1)
    dados["previsao"] = [classes[indice] for indice in indices_previsao]
    dados["confianca_pct"] = probabilidades.max(axis=1) * 100
    dados["data_prevista"] = pd.to_datetime(
        dados["timestamp"] + HORIZONTE_SEGUNDOS, unit="s", utc=True
    ).dt.strftime("%Y-%m-%d")
    dados = dados.sort_values(
        ["timestamp", "rota", "fluxo_id"], kind="stable"
    ).reset_index(drop=True)
    return dados


def carregar_pings_previstos(offset: int = 0, limite: int = 500) -> dict:
    dados = _carregar_pings_modelados()
    fim = min(offset + limite, len(dados))
    amostra = dados.iloc[offset:fim]
    pings = [
        {
            "indice": offset + posicao,
            "timestamp": int(linha.timestamp),
            "previsto_em": int(linha.timestamp) + HORIZONTE_SEGUNDOS,
            "rota": str(linha.rota),
            "fluxo_id": str(linha.fluxo_id),
            "status": str(linha.previsao),
            "confianca_pct": round(float(linha.confianca_pct), 1),
        }
        for posicao, linha in enumerate(amostra.itertuples(index=False))
    ]
    return {
        "total": len(dados),
        "inicio": int(dados["timestamp"].min()),
        "fim": int(dados["timestamp"].max()),
        "horizonte_minutos": HORIZONTE_SEGUNDOS // 60,
        "offset": offset,
        "limite": limite,
        "pings": pings,
    }


@lru_cache(maxsize=1)
def carregar_previsoes_historicas() -> dict:
    dados = _carregar_pings_modelados()
    contagens = (
        dados.groupby(["data_prevista", "rota", "previsao"], observed=True)
        .size()
        .unstack("previsao", fill_value=0)
        .reindex(columns=CLASSES, fill_value=0)
    )

    previsoes = []
    for (data, rota), contagem in contagens.iterrows():
        amostras = int(contagem.sum())
        status = max(
            CLASSES,
            key=lambda classe: (int(contagem[classe]), PRIORIDADE_STATUS[classe]),
        )
        previsoes.append(
            {
                "data": data,
                "rota": rota,
                "status": status,
                "amostras": amostras,
                "ok": int(contagem["OK"]),
                "risco": int(contagem["RISCO"]),
                "falha": int(contagem["FALHA"]),
                "falha_pct": round(int(contagem["FALHA"]) / amostras * 100, 1),
            }
        )

    datas = sorted({previsao["data"] for previsao in previsoes})
    if not datas:
        raise ValueError("O histórico não contém previsões para exibir no mapa.")

    return {
        "datas": datas,
        "inicio": datas[0],
        "fim": datas[-1],
        "horizonte_minutos": HORIZONTE_SEGUNDOS // 60,
        "previsoes": previsoes,
    }
