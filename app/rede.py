"""Medição de rede por ICMP, usando o comando `ping` do próprio sistema (não exige administrador)."""
from __future__ import annotations

import math
import re
import statistics
import subprocess
import sys
from dataclasses import dataclass, field

from .configuracao import PACOTES_POR_RAJADA, TIMEOUT_PACOTE_S

# Cobre Linux/macOS ("time=12.3 ms") e Windows em vários idiomas ("tempo=12ms", "tempo<1ms").
_RE_TEMPO = re.compile(r"(?:time|tempo|tiempo|zeit|temps)\s*([=<])\s*(\d+(?:[.,]\d+)?)\s*ms", re.I)


class PingIndisponivel(RuntimeError):
    """O `ping` não existe ou não pode ser executado neste computador."""


@dataclass
class Rajada:
    """Uma medição: N pacotes enviados a um destino (equivale a uma linha do dataset do projeto)."""
    enviados: int
    rtts: list[float] = field(default_factory=list)

    @property
    def recebidos(self) -> int:
        return len(self.rtts)

    @property
    def media(self) -> float:
        return statistics.fmean(self.rtts) if self.rtts else math.nan

    @property
    def jitter(self) -> float:
        # Mesma definição da coleta: desvio-padrão amostral dos RTTs, só com 2+ respostas.
        return statistics.stdev(self.rtts) if len(self.rtts) >= 2 else math.nan

    @property
    def perda_pct(self) -> float:
        if not self.enviados:
            return 100.0
        return (self.enviados - self.recebidos) / self.enviados * 100


def _comando(host: str, pacotes: int) -> list[str]:
    if sys.platform.startswith("win"):
        return ["ping", "-n", str(pacotes), "-w", str(TIMEOUT_PACOTE_S * 1000), host]
    if sys.platform == "darwin":
        return ["ping", "-c", str(pacotes), "-W", str(TIMEOUT_PACOTE_S * 1000), host]
    return ["ping", "-n", "-c", str(pacotes), "-i", "0.2", "-W", str(TIMEOUT_PACOTE_S), host]


def executar_ping(host: str, pacotes: int = PACOTES_POR_RAJADA) -> Rajada:
    kwargs = {}
    if sys.platform.startswith("win"):
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    try:
        proc = subprocess.run(
            _comando(host, pacotes), capture_output=True, text=True, encoding="latin-1",
            timeout=pacotes * (TIMEOUT_PACOTE_S + 1) + 5, **kwargs,
        )
    except FileNotFoundError as e:
        raise PingIndisponivel("O comando 'ping' não foi encontrado neste computador.") from e
    except subprocess.TimeoutExpired:
        return Rajada(pacotes, [])

    rtts = []
    for m in _RE_TEMPO.finditer(proc.stdout):
        valor = float(m.group(2).replace(",", "."))
        rtts.append(valor / 2 if m.group(1) == "<" else valor)   # "<1ms" vira 0,5 ms
    if not rtts and re.search(r"not permitted|permission denied|operação não permitida", proc.stderr, re.I):
        raise PingIndisponivel("Sem permissão para executar o 'ping' neste computador.")
    return Rajada(pacotes, rtts[:pacotes])
