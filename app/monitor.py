"""Orquestra a medição: ping nos alvos -> métricas relativas ao baseline -> modelo -> estado da rede."""
from __future__ import annotations

import json
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime

import pandas as pd

from . import simulacao
from .classificador import Detector
from .configuracao import ALVOS, ARQ_BASELINE, PISO_BASELINE, RAJADAS_CALIBRACAO, RODADAS
from .metricas import Ficha, calcular_metricas, criar_ficha
from .rede import Rajada, executar_ping

GRAVIDADE = {"OK": 0, "RISCO": 1, "FALHA": 2}
POR_GRAVIDADE = {v: k for k, v in GRAVIDADE.items()}


class MonitorOcupado(RuntimeError):
    """Já existe uma medição em andamento."""


class ErroMedicao(RuntimeError):
    """Não foi possível concluir a medição (mensagem própria para o usuário)."""


def _num(x, casas=1):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), casas)


class Monitor:
    def __init__(self, detector=None, alvos=ALVOS, ping=executar_ping, arquivo_baseline=ARQ_BASELINE, cenario=None):
        self.detector = detector or Detector()
        self.alvos = list(alvos)
        self.ping = ping
        self.arquivo_baseline = arquivo_baseline
        self.cenario = cenario              # None = medição real; "ok"/"risco"/"falha" = demonstração
        self._lock = threading.Lock()

    # ---------- baseline ----------
    def _ler_fichas(self) -> dict[str, Ficha]:
        try:
            dados = json.loads(self.arquivo_baseline.read_text(encoding="utf-8"))
            return {host: Ficha(**f) for host, f in dados.items()}
        except (FileNotFoundError, ValueError, TypeError):
            return {}

    def _gravar_fichas(self, fichas: dict[str, Ficha]) -> None:
        self.arquivo_baseline.parent.mkdir(parents=True, exist_ok=True)
        self.arquivo_baseline.write_text(
            json.dumps({h: asdict(f) for h, f in fichas.items()}, indent=2), encoding="utf-8")

    def _coletar_rajadas(self, host: str, n: int, simultaneas: int = 4) -> list[Rajada]:
        with ThreadPoolExecutor(simultaneas) as ex:
            return list(ex.map(lambda _: self.ping(host), range(n)))

    def calibrar(self, n_rajadas: int = RAJADAS_CALIBRACAO) -> dict[str, Ficha | None]:
        """Cria (ou refaz) a referência de cada alvo. Use com a rede funcionando normalmente."""
        fichas = self._ler_fichas()
        with ThreadPoolExecutor(len(self.alvos)) as ex:
            novas = list(ex.map(lambda a: criar_ficha(self._coletar_rajadas(a[1], n_rajadas, 6)), self.alvos))
        for (_, host), ficha in zip(self.alvos, novas):
            if ficha:
                fichas[host] = ficha
        self._gravar_fichas(fichas)
        return {host: f for (_, host), f in zip(self.alvos, novas)}

    # ---------- medição ----------
    def medir(self) -> dict:
        if not self._lock.acquire(blocking=False):
            raise MonitorOcupado("Já existe uma medição em andamento.")
        try:
            return self._medir()
        finally:
            self._lock.release()

    def _medir(self) -> dict:
        inicio = time.time()
        criada_agora = False
        if self.cenario:
            fichas = {host: simulacao.FICHA_SIMULADA for _, host in self.alvos}
        else:
            fichas = self._ler_fichas()
            if any(host not in fichas for _, host in self.alvos):
                self.calibrar()
                fichas = self._ler_fichas()
                criada_agora = True

        def medir_alvo(alvo):
            nome, host = alvo
            if self.cenario:
                rajadas = simulacao.rodadas_simuladas(self.cenario)
            else:
                rajadas = [self.ping(host) for _ in range(RODADAS)]
            return self._avaliar_alvo(nome, host, fichas.get(host), rajadas)

        with ThreadPoolExecutor(len(self.alvos)) as ex:
            alvos = list(ex.map(medir_alvo, self.alvos))

        avaliados = [a for a in alvos if a["status"] is not None]
        if not avaliados:
            raise ErroMedicao("Não foi possível criar a referência (normal) da rede: sem respostas "
                              "suficientes. Verifique a conexão e tente novamente.")
        gravidades = sorted(GRAVIDADE[a["status"]] for a in avaliados)
        status = POR_GRAVIDADE[gravidades[len(gravidades) // 2]]       # mediana; empate vale o pior

        return self._resposta(status, alvos, avaliados, fichas, criada_agora, time.time() - inicio)

    def _avaliar_alvo(self, nome, host, ficha, rajadas) -> dict:
        enviados = sum(r.enviados for r in rajadas)
        recebidos = sum(r.recebidos for r in rajadas)
        validos = [r.media for r in rajadas if r.recebidos]
        jitters = [r.jitter for r in rajadas if not math.isnan(r.jitter)]
        base = {
            "nome": nome, "endereco": host,
            "latencia_ms": _num(sum(validos) / len(validos)) if validos else None,
            "jitter_ms": _num(sum(jitters) / len(jitters), 2) if jitters else None,
            "perda_pct": _num((enviados - recebidos) / enviados * 100, 0),
            "normal_ms": _num(ficha.mediana) if ficha else None,
            "_linha": None,
        }
        if ficha is None:
            # Sem baseline, só dá para afirmar falha quando não há nenhuma resposta (RFC, seção 3).
            base["status"] = None if recebidos else "FALHA"
            return base
        linhas = calcular_metricas(ficha, rajadas)
        ultima = linhas.iloc[-1]
        base["status"] = self.detector.classificar(ultima)
        base["_linha"] = ultima
        return base

    # ---------- resposta para a tela ----------
    def _resposta(self, status, alvos, avaliados, fichas, criada_agora, duracao) -> dict:
        def media(chave, casas=1):
            v = [a[chave] for a in avaliados if a[chave] is not None]
            return _num(sum(v) / len(v), casas) if v else None

        lat, normal = media("latencia_ms"), media("normal_ms")
        variacao = _num((lat - normal) / normal * 100, 0) if lat is not None and normal else None
        amostras = min((f.n_validos for f in fichas.values()), default=0)
        provisoria = amostras < PISO_BASELINE
        resposta = {
            "status": status,
            "mensagem": self._mensagem(status, avaliados),
            "medido_em": datetime.now().strftime("%H:%M:%S"),
            "duracao_s": round(duracao, 1),
            "metricas": {
                "latencia_ms": lat, "normal_ms": normal, "variacao_pct": variacao,
                "jitter_ms": media("jitter_ms", 2), "perda_pct": media("perda_pct", 0),
            },
            "alvos": [{k: v for k, v in a.items() if k != "_linha"} for a in alvos],
            "referencia": {
                "amostras": amostras, "provisoria": provisoria, "criada_agora": criada_agora,
                "simulada": bool(self.cenario),
            },
        }
        return resposta

    @staticmethod
    def _mensagem(status, avaliados) -> str:
        if status == "OK":
            return "Rede dentro do comportamento normal."
        motivos = []
        linhas = [a["_linha"] for a in avaliados if a["_linha"] is not None]
        sem_resposta = any(a["status"] == "FALHA" and a["_linha"] is None for a in avaliados)
        if sem_resposta or any(l["n5_timeout"] >= 3 for l in linhas):
            motivos.append("falta de resposta")
        if any(l["perda_pct"] >= 10 for l in linhas) and "falta de resposta" not in motivos:
            motivos.append("perda de pacotes")
        if any(l["z_robusto"] >= 2 for l in linhas if not math.isnan(l["z_robusto"])):
            motivos.append("latência acima do normal")
        if any(l["jitter_relativo"] >= 3 for l in linhas if not math.isnan(l["jitter_relativo"])):
            motivos.append("instabilidade (jitter alto)")
        abertura = "Falha detectada" if status == "FALHA" else "Risco de degradação"
        return f"{abertura}: {', '.join(motivos)}." if motivos else f"{abertura}: comportamento fora do normal desta rede."
