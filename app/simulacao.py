"""Modo demonstração: gera medições sintéticas (sem rede) para apresentar os três estados."""
from __future__ import annotations

import random

from .configuracao import PACOTES_POR_RAJADA, RODADAS
from .metricas import Ficha
from .rede import Rajada

CENARIOS = ("ok", "risco", "falha")

# "Normal" fictício: 20 ms de mediana, pouca variação.
FICHA_SIMULADA = Ficha(
    mediana=20.0, mad=1.0, iqr=2.0, jitter_tipico=0.5, perda_tipica=0.0,
    prop_resposta=1.0, n_validos=1500, n_total=1500, criada_em="simulada",
)


def _rajada(rng: random.Random, centro: float, ruido: float, perdidos: int = 0) -> Rajada:
    n = PACOTES_POR_RAJADA - perdidos
    return Rajada(PACOTES_POR_RAJADA, [max(0.1, rng.gauss(centro, ruido)) for _ in range(n)])


def rodadas_simuladas(cenario: str) -> list[Rajada]:
    rng = random.Random()
    rajadas = []
    for i in range(RODADAS):
        degradada = i >= RODADAS - 3          # as 3 últimas medições mostram o problema
        if cenario == "ok" or not degradada:
            rajadas.append(_rajada(rng, 20.0, 0.4))
        elif cenario == "risco":
            rajadas.append(_rajada(rng, 24.5, 0.5))        # latência um pouco acima do normal (zona de risco)
        else:  # falha
            rajadas.append(_rajada(rng, 60.0, 8.0, perdidos=rng.choice([1, 2, 3])))
    return rajadas
