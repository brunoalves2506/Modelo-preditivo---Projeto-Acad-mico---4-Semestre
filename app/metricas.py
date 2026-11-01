"""Baseline e métricas relativas, com as mesmas fórmulas da Tarefa 2 (docs/Tarefas/Tarefa2_Baseline_e_Rotulagem.md)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from .configuracao import MIN_RAJADAS_VALIDAS_CALIBRACAO, PISO_BASELINE
from .rede import Rajada


@dataclass
class Ficha:
    """Ficha de baseline de um destino: o 'normal' dessa rede, congelado."""
    mediana: float
    mad: float
    iqr: float
    jitter_tipico: float
    perda_tipica: float
    prop_resposta: float
    n_validos: int
    n_total: int
    criada_em: str

    @property
    def provisoria(self) -> bool:
        return self.n_validos < PISO_BASELINE


def criar_ficha(rajadas: list[Rajada]) -> Ficha | None:
    """Mediana/MAD dos RTT válidos (timeout fica fora). Sem amostras suficientes, não inventa mediana."""
    validos = np.array([r.media for r in rajadas if r.recebidos > 0], dtype=float)
    if len(validos) < MIN_RAJADAS_VALIDAS_CALIBRACAO:
        return None
    mediana = float(np.median(validos))
    jitters = [r.jitter for r in rajadas if not math.isnan(r.jitter)]
    return Ficha(
        mediana=mediana,
        mad=float(np.median(np.abs(validos - mediana))),
        iqr=float(np.percentile(validos, 75) - np.percentile(validos, 25)),
        jitter_tipico=float(np.median(jitters)) if jitters else 0.0,
        perda_tipica=float(np.median([r.perda_pct for r in rajadas])),
        prop_resposta=len(validos) / len(rajadas),
        n_validos=len(validos),
        n_total=len(rajadas),
        criada_em=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def _z_robusto(rtt: float, f: Ficha) -> float:
    if math.isnan(rtt):
        return math.nan
    if f.mad == 0:
        if rtt == f.mediana:
            return 0.0
        return (rtt - f.mediana) / max(f.iqr / 1.349, 1.0)
    return (rtt - f.mediana) / (1.4826 * f.mad)


def _jitter_relativo(jitter: float, f: Ficha) -> float:
    if math.isnan(jitter):
        return math.nan                      # jitter vazio: o critério de jitter não dispara
    if f.jitter_tipico == 0:
        return 1.0 if jitter == 0 else 3.0
    return jitter / f.jitter_tipico


def calcular_metricas(ficha: Ficha, rajadas: list[Rajada]) -> pd.DataFrame:
    """Uma linha por medição, em ordem de tempo, com as colunas que o modelo espera."""
    mediana = max(ficha.mediana, 1e-6)
    linhas = []
    for r in rajadas:
        rtt = r.media
        timeout = 1 if (math.isnan(rtt) or r.perda_pct == 100) else 0
        linhas.append({
            "rtt_ms": rtt,
            "jitter_ms": r.jitter,
            "z_robusto": _z_robusto(rtt, ficha),
            "aumento_pct": (rtt - mediana) / mediana * 100 if not math.isnan(rtt) else math.nan,
            "jitter_relativo": _jitter_relativo(r.jitter, ficha),
            "perda_pct": r.perda_pct,
            "timeout_atual": timeout,
        })
    df = pd.DataFrame(linhas)

    risco_individual = (
        ((df["z_robusto"] >= 2) & (df["z_robusto"] < 3.5))
        | ((df["aumento_pct"] >= 30) & (df["aumento_pct"] <= 80))
        | (df["jitter_relativo"] >= 3)
    ).astype(int)
    df["n5_timeout"] = df["timeout_atual"].rolling(5, min_periods=1).sum()
    df["n5_aumento80"] = (df["aumento_pct"] > 80).astype(int).rolling(5, min_periods=1).sum()
    df["n5_risco"] = risco_individual.rolling(5, min_periods=1).sum()
    return df
