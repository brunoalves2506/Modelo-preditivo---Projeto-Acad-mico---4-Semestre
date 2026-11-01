"""Testes da integração interface <-> modelo (rodam sem rede, com ping simulado)."""
import math
import random
import warnings

import pytest

warnings.filterwarnings("ignore")

from app.classificador import Detector
from app.metricas import Ficha, calcular_metricas, criar_ficha
from app.monitor import Monitor
from app.rede import Rajada
from app.servidor import criar_app


@pytest.fixture(scope="module")
def detector():
    return Detector()


def ping_falso(centro=15.0, ruido=0.4, perdidos=0):
    rng = random.Random(1)
    def ping(host):
        return Rajada(3, [max(0.1, rng.gauss(centro, ruido)) for _ in range(3 - perdidos)])
    return ping


def monitor(detector, tmp_path, ping):
    return Monitor(detector=detector, ping=ping, arquivo_baseline=tmp_path / "baseline.json")


def test_ficha_ignora_timeouts():
    rajadas = [Rajada(3, [10.0, 10.2, 9.8])] * 12 + [Rajada(3, [])] * 4
    f = criar_ficha(rajadas)
    assert f.n_validos == 12 and f.n_total == 16
    assert f.mediana == pytest.approx(10.0) and f.prop_resposta == pytest.approx(0.75)


def test_sem_amostras_suficientes_nao_cria_ficha():
    assert criar_ficha([Rajada(3, [])] * 20) is None


def test_metricas_seguem_a_tabela_da_tarefa2():
    ficha = Ficha(20.0, 1.0, 2.0, 0.5, 0.0, 1.0, 1500, 1500, "x")
    df = calcular_metricas(ficha, [Rajada(3, [20.0, 20.0, 20.0]), Rajada(3, []), Rajada(3, [30.0, 30.0, 30.0])])
    assert df.loc[0, "z_robusto"] == pytest.approx(0.0)
    assert df.loc[1, "timeout_atual"] == 1 and math.isnan(df.loc[1, "z_robusto"])   # timeout nunca vira 0 ms
    assert df.loc[1, "perda_pct"] == 100
    assert df.loc[2, "aumento_pct"] == pytest.approx(50.0)
    assert df.loc[2, "n5_timeout"] == 1


def test_primeira_medicao_cria_baseline_e_reaproveita(detector, tmp_path):
    m = monitor(detector, tmp_path, ping_falso())
    r1 = m.medir()
    assert r1["referencia"]["criada_agora"] and r1["referencia"]["provisoria"]
    assert r1["status"] == "OK"
    assert (tmp_path / "baseline.json").exists()
    assert not m.medir()["referencia"]["criada_agora"]


def test_rede_que_piora_vira_falha(detector, tmp_path):
    m = monitor(detector, tmp_path, ping_falso())
    m.medir()                                         # cria a referência com a rede normal
    m.ping = ping_falso(centro=60.0, ruido=8.0, perdidos=1)
    assert m.medir()["status"] == "FALHA"


def test_sem_nenhuma_resposta_e_falha_mesmo_sem_baseline(detector, tmp_path):
    m = monitor(detector, tmp_path, lambda host: Rajada(3, []))
    r = m.medir()
    assert r["status"] == "FALHA" and r["metricas"]["perda_pct"] == 100


@pytest.mark.parametrize("cenario,esperado", [("ok", "OK"), ("falha", "FALHA")])
def test_modo_demonstracao(detector, cenario, esperado):
    assert Monitor(detector=detector, cenario=cenario).medir()["status"] == esperado


def test_endpoint_devolve_json_valido(detector):
    cliente = criar_app(Monitor(detector=detector, cenario="ok")).test_client()
    r = cliente.post("/api/medicao")
    assert r.status_code == 200
    assert r.get_json()["status"] in {"OK", "RISCO", "FALHA"}
    assert cliente.get("/").status_code == 200
