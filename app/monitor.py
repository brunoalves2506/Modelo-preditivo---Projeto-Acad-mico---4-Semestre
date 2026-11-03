"""Orquestra a medição e a calibração: ping nos alvos -> métricas relativas ao baseline -> floresta final -> previsão."""
from __future__ import annotations

import json
import math
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime

from . import simulacao
from .classificador import Detector
from .configuracao import (
    ALVOS, ARQ_BASELINE, CALIBRACAO_SIMULTANEAS, HORIZONTE_MINUTOS, PISO_BASELINE, RAJADAS_CALIBRACAO, RODADAS,
)
from .metricas import Ficha, calcular_metricas, criar_ficha
from .rede import Rajada, executar_ping

GRAVIDADE = {"OK": 0, "RISCO": 1, "FALHA": 2}
POR_GRAVIDADE = {v: k for k, v in GRAVIDADE.items()}


class MonitorOcupado(RuntimeError):
    """Já existe uma medição ou calibração em andamento."""


class ErroMedicao(RuntimeError):
    """Não foi possível concluir a medição (mensagem própria para o usuário)."""


class SemBaseline(ErroMedicao):
    """A rede ainda não foi calibrada."""


def _num(x, casas=1):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), casas)


def _hora_local(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).astimezone().strftime("%d/%m %H:%M")
    except ValueError:
        return iso


class Monitor:
    def __init__(self, detector=None, alvos=ALVOS, ping=executar_ping, arquivo_baseline=ARQ_BASELINE, cenario=None):
        self.detector = detector or Detector()
        self.alvos = list(alvos)
        self.ping = ping
        self.arquivo_baseline = arquivo_baseline
        self.cenario = cenario              # None = medição real; "ok"/"risco"/"falha" = demonstração
        self._lock = threading.Lock()       # uma operação de rede por vez (medir ou calibrar)
        self._calibrando = False
        self._cal = self._estado_inicial()
        self._cal_cancelar = threading.Event()
        self._cal_contador = threading.Lock()

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

    # ---------- calibração ----------
    @staticmethod
    def _estado_inicial() -> dict:
        return {"ativa": False, "feitas": 0, "total": 0, "inicio": None, "resultado": None,
                "erro": None, "cancelada": False}

    def calibrar(self, n_rajadas: int = RAJADAS_CALIBRACAO, progresso=None) -> dict[str, Ficha | None]:
        """Calibra de forma síncrona (usado pela linha de comando)."""
        self._reservar("calibração")
        try:
            self._cal = {**self._estado_inicial(), "ativa": True, "inicio": time.time()}
            return self._executar_calibracao(n_rajadas, progresso)
        finally:
            self._cal["ativa"] = False
            self._liberar()

    def iniciar_calibracao(self, n_rajadas: int = RAJADAS_CALIBRACAO) -> None:
        """Calibra em segundo plano; acompanhe por estado_calibracao()."""
        self._reservar("calibração")
        self._cal_cancelar.clear()
        self._cal = {**self._estado_inicial(), "ativa": True, "inicio": time.time()}

        def tarefa():
            try:
                self._executar_calibracao(n_rajadas)
            except Exception as e:  # noqa: BLE001 - qualquer falha vai para a tela, não derruba o servidor
                self._cal["erro"] = str(e) or e.__class__.__name__
            finally:
                self._cal["ativa"] = False
                self._liberar()

        threading.Thread(target=tarefa, daemon=True).start()

    def cancelar_calibracao(self) -> bool:
        if not self._cal["ativa"]:
            return False
        self._cal_cancelar.set()
        return True

    def estado_calibracao(self) -> dict:
        c = dict(self._cal)
        decorrido = time.time() - c["inicio"] if c["inicio"] else 0
        pct = c["feitas"] / c["total"] * 100 if c["total"] else 0
        restante = decorrido * (100 - pct) / pct if c["ativa"] and pct >= 3 else None
        return {
            "ativa": c["ativa"], "feitas": c["feitas"], "total": c["total"], "percentual": round(pct),
            "decorrido_s": round(decorrido), "restante_s": round(restante) if restante is not None else None,
            "cancelada": c["cancelada"], "erro": c["erro"], "resultado": c["resultado"],
        }

    def _executar_calibracao(self, n_rajadas, progresso=None) -> dict[str, Ficha | None]:
        total = n_rajadas * len(self.alvos)
        self._cal["total"] = total

        def avancar():
            with self._cal_contador:
                self._cal["feitas"] += 1
                feitas = self._cal["feitas"]
            if progresso:
                progresso(feitas, total)

        if self.cenario:                    # demonstração: finge o progresso, não mexe no baseline real
            for _ in range(total):
                if self._cal_cancelar.is_set():
                    break
                time.sleep(2.5 / total)
                avancar()
            self._cal["cancelada"] = self._cal_cancelar.is_set()
            self._cal["resultado"] = None if self._cal["cancelada"] else self._resultado_calibracao(
                {h: simulacao.FICHA_SIMULADA for _, h in self.alvos}, simulada=True)
            return {}

        def uma_rajada(host):
            if self._cal_cancelar.is_set():
                return None
            r = self.ping(host)
            avancar()
            return r

        def coletar(host):
            with ThreadPoolExecutor(CALIBRACAO_SIMULTANEAS) as ex:
                return [r for r in ex.map(lambda _: uma_rajada(host), range(n_rajadas)) if r is not None]

        with ThreadPoolExecutor(len(self.alvos)) as ex:
            coletas = list(ex.map(lambda a: coletar(a[1]), self.alvos))

        if self._cal_cancelar.is_set():     # cancelou: nada é gravado, o baseline anterior continua valendo
            self._cal["cancelada"] = True
            return {}
        novas = [criar_ficha(c) for c in coletas]
        fichas = self._ler_fichas()
        for (_, host), ficha in zip(self.alvos, novas):
            if ficha:
                fichas[host] = ficha
        if any(novas):
            self._gravar_fichas(fichas)
        resultado = {host: f for (_, host), f in zip(self.alvos, novas)}
        self._cal["resultado"] = self._resultado_calibracao(resultado)
        return resultado

    def _resultado_calibracao(self, fichas: dict, simulada=False) -> dict:
        alvos = []
        for nome, host in self.alvos:
            f = fichas.get(host)
            alvos.append({
                "nome": nome, "endereco": host,
                "normal_ms": _num(f.mediana) if f else None,
                "amostras": f.n_validos if f else 0,
                "ok": bool(f),
            })
        completo = all(a["ok"] and a["amostras"] >= PISO_BASELINE for a in alvos)
        return {"alvos": alvos, "completo": completo, "simulada": simulada}

    # ---------- medição ----------
    def _reservar(self, operacao: str) -> None:
        if not self._lock.acquire(blocking=False):
            raise MonitorOcupado("A calibração está em andamento. Aguarde terminar ou cancele."
                                 if self._calibrando else "Já existe uma medição em andamento.")
        self._calibrando = operacao == "calibração"

    def _liberar(self) -> None:
        self._calibrando = False
        self._lock.release()

    def medir(self) -> dict:
        self._reservar("medição")
        try:
            return self._medir()
        finally:
            self._liberar()

    def _medir(self) -> dict:
        inicio = time.time()
        if self.cenario:
            fichas = {host: simulacao.FICHA_SIMULADA for _, host in self.alvos}
        else:
            fichas = self._ler_fichas()
            if any(host not in fichas for _, host in self.alvos):
                raise SemBaseline("A rede ainda não foi calibrada. Clique em Calibrar antes de fazer a medição.")

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
            raise ErroMedicao("Não foi possível avaliar a rede: sem respostas suficientes. "
                              "Verifique a conexão e tente novamente.")
        gravidades = sorted(GRAVIDADE[a["status"]] for a in avaliados)
        status = POR_GRAVIDADE[gravidades[len(gravidades) // 2]]       # mediana; empate vale o pior

        return self._resposta(status, alvos, avaliados, fichas, time.time() - inicio)

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
            "confianca_pct": None,
            "_linha": None,
        }
        if ficha is None:
            # Sem baseline, só dá para afirmar falha quando não há nenhuma resposta (RFC, seção 3).
            base["status"] = None if recebidos else "FALHA"
            return base
        linhas = calcular_metricas(ficha, rajadas)
        ultima = linhas.iloc[-1]
        base["status"], confianca = self.detector.prever(ultima)
        base["confianca_pct"] = _num(confianca, 0)
        base["_linha"] = ultima
        return base

    # ---------- resposta para a tela ----------
    def _resposta(self, status, alvos, avaliados, fichas, duracao) -> dict:
        def media(chave, casas=1):
            v = [a[chave] for a in avaliados if a[chave] is not None]
            return _num(sum(v) / len(v), casas) if v else None

        lat, normal = media("latencia_ms"), media("normal_ms")
        variacao = _num((lat - normal) / normal * 100, 0) if lat is not None and normal else None
        usadas = [fichas[h] for _, h in self.alvos if h in fichas]
        amostras = min((f.n_validos for f in usadas), default=0)
        return {
            "status": status,
            "horizonte_minutos": HORIZONTE_MINUTOS,
            "mensagem": self._mensagem(status, avaliados),
            "medido_em": datetime.now().strftime("%H:%M:%S"),
            "duracao_s": round(duracao, 1),
            "metricas": {
                "latencia_ms": lat, "normal_ms": normal, "variacao_pct": variacao,
                "jitter_ms": media("jitter_ms", 2), "perda_pct": media("perda_pct", 0),
            },
            "alvos": [{k: v for k, v in a.items() if k != "_linha"} for a in alvos],
            "referencia": {
                "amostras": amostras, "provisoria": amostras < PISO_BASELINE, "simulada": bool(self.cenario),
                "calibrada_em": _hora_local(min((f.criada_em for f in usadas), default="")) if usadas else None,
            },
        }

    @staticmethod
    def _mensagem(status, avaliados) -> str:
        h = HORIZONTE_MINUTOS
        if status == "OK":
            return f"Previsão: rede estável nos próximos ~{h} minutos."
        abertura = (f"Previsão: falha em ~{h} minutos." if status == "FALHA"
                    else f"Previsão: risco de degradação em ~{h} minutos.")
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
            motivos.append("jitter alto")
        return f"{abertura} Sinais atuais: {', '.join(motivos)}." if motivos else abertura
