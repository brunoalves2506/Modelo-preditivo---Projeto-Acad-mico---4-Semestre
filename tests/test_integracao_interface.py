"""Testes da integração interface <-> modelo (rodam sem rede, com ping simulado)."""
import math
import random
import warnings

import pytest

warnings.filterwarnings("ignore")

from app.classificador import Detector
from app.configuracao import ARQ_MODELO_FINAL
from app.metricas import Ficha, calcular_metricas, criar_ficha
import threading
import time

from app.monitor import Monitor, MonitorOcupado, SemBaseline
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


def test_metricas_calculam_lags_da_floresta_final():
    ficha = Ficha(20.0, 1.0, 2.0, 0.5, 0.0, 1.0, 1500, 1500, "x")
    df = calcular_metricas(
        ficha,
        [Rajada(3, [20.0, 20.0, 20.0]), Rajada(3, [21.0, 21.0, 21.0])],
    )

    assert math.isnan(df.loc[0, "z_robusto_t_menos_1"])
    assert df.loc[1, "z_robusto_t_menos_1"] == pytest.approx(df.loc[0, "z_robusto"])
    assert df.loc[1, "delta_z_robusto"] == pytest.approx(
        df.loc[1, "z_robusto"] - df.loc[0, "z_robusto"]
    )


def test_detector_carrega_a_floresta_final_da_tarefa4(detector):
    assert detector.arquivo == ARQ_MODELO_FINAL
    assert detector.colunas == [
        "z_robusto_t_menos_1",
        "delta_z_robusto",
        "z_robusto",
        "perda_pct",
        "jitter_relativo",
        "n5_risco",
        "n5_timeout",
        "n5_aumento80",
    ]


def test_medir_sem_calibrar_pede_a_calibracao(detector, tmp_path):
    m = monitor(detector, tmp_path, ping_falso())
    with pytest.raises(SemBaseline):
        m.medir()
    assert not (tmp_path / "baseline.json").exists()      # nada de baseline escondido


def test_calibrar_grava_baseline_e_a_medicao_usa_ele(detector, tmp_path):
    m = monitor(detector, tmp_path, ping_falso())
    fichas = m.calibrar(30)
    assert (tmp_path / "baseline.json").exists()
    assert all(f.n_validos == 30 and f.mediana == pytest.approx(15.0, abs=0.5) for f in fichas.values())
    r = m.medir()
    assert r["status"] == "OK" and r["horizonte_minutos"] == 12
    assert r["referencia"]["amostras"] == 30 and r["referencia"]["provisoria"]   # < 1500: avisa que é incompleto
    assert all(a["confianca_pct"] is not None for a in r["alvos"])


def test_rede_que_piora_vira_falha(detector, tmp_path):
    m = monitor(detector, tmp_path, ping_falso())
    m.calibrar(30)                                    # referência com a rede normal
    m.ping = ping_falso(centro=60.0, ruido=8.0, perdidos=1)
    assert m.medir()["status"] == "FALHA"


def test_prever_devolve_classe_e_confianca(detector):
    ficha = Ficha(20.0, 1.0, 2.0, 0.5, 0.0, 1.0, 1500, 1500, "x")
    linha = calcular_metricas(ficha, [Rajada(3, [20.0, 20.1, 19.9])] * 5).iloc[-1]
    classe, confianca = detector.prever(linha)
    assert classe in {"OK", "RISCO", "FALHA"} and 0 < confianca <= 100
    assert detector.classificar(linha) == classe


def test_calibracao_cancelada_nao_grava_nada(detector, tmp_path):
    m = monitor(detector, tmp_path, lambda host: (time.sleep(0.01), Rajada(3, [15.0, 15.2, 14.9]))[1])
    m.iniciar_calibracao(300)
    time.sleep(0.15)
    assert m.cancelar_calibracao()
    while m.estado_calibracao()["ativa"]:
        time.sleep(0.02)
    estado = m.estado_calibracao()
    assert estado["cancelada"] and estado["resultado"] is None
    assert not (tmp_path / "baseline.json").exists()


def test_nao_mede_durante_a_calibracao(detector, tmp_path):
    m = monitor(detector, tmp_path, lambda host: (time.sleep(0.02), Rajada(3, [15.0, 15.1, 14.9]))[1])
    m.iniciar_calibracao(100)
    with pytest.raises(MonitorOcupado, match="calibração"):
        m.medir()
    m.cancelar_calibracao()
    while m.estado_calibracao()["ativa"]:
        time.sleep(0.02)


def test_calibracao_incompleta_e_sinalizada(detector, tmp_path):
    m = monitor(detector, tmp_path, ping_falso())
    m.calibrar(20)
    m.iniciar_calibracao(20)
    while m.estado_calibracao()["ativa"]:
        time.sleep(0.02)
    resultado = m.estado_calibracao()["resultado"]
    assert resultado["completo"] is False                 # 20 < 1500 amostras
    assert [a["endereco"] for a in resultado["alvos"]] == ["1.1.1.1", "8.8.8.8", "9.9.9.9"]


@pytest.mark.parametrize("cenario,esperado", [("ok", "OK"), ("falha", "FALHA")])
def test_modo_demonstracao(detector, cenario, esperado):
    assert Monitor(detector=detector, cenario=cenario).medir()["status"] == esperado


def test_endpoint_devolve_json_valido(detector):
    cliente = criar_app(Monitor(detector=detector, cenario="ok")).test_client()
    r = cliente.post("/api/medicao")
    assert r.status_code == 200
    assert r.get_json()["status"] in {"OK", "RISCO", "FALHA"}
    assert cliente.get("/").status_code == 200


def test_interface_serve_template_e_arquivos_estaticos(detector):
    cliente = criar_app(Monitor(detector=detector, cenario="ok")).test_client()

    pagina = cliente.get("/")
    assert pagina.status_code == 200
    assert b"/static/css/style.css" in pagina.data
    assert b"/static/js/script.js" in pagina.data
    html = pagina.get_data(as_text=True)
    assert "Antecipando a degradação da rede" in html
    assert "<table" not in html
    assert "Quem mede quem" not in html
    assert "Grupo 18" in html
    assert "Bruno Alves Ribeiro de Souza" in html
    assert "Victoria Agatha Rodrigues Fagundes" in html
    assert "img/logo_bc_white.png" in html
    assert cliente.get("/static/css/style.css").status_code == 200
    assert cliente.get("/static/js/script.js").status_code == 200
    assert cliente.get("/static/img/mirai-logo.png").status_code == 200
    assert cliente.get("/static/img/logo_bc_white.png").status_code == 200


def test_endpoint_devolve_previsoes_historicas_por_dia(detector):
    cliente = criar_app(Monitor(detector=detector, cenario="ok")).test_client()
    resposta = cliente.get("/api/previsoes-historicas")

    assert resposta.status_code == 200
    historico = resposta.get_json()
    assert historico["inicio"] == "2026-09-13"
    assert historico["fim"] == "2026-09-20"
    assert historico["horizonte_minutos"] == 12
    assert historico["datas"] == sorted(historico["datas"])
    assert {item["rota"] for item in historico["previsoes"]} >= {"BR→BR", "BR→ZA"}
    for item in historico["previsoes"]:
        assert item["status"] in {"OK", "RISCO", "FALHA"}
        assert item["amostras"] == item["ok"] + item["risco"] + item["falha"]
        assert 0 <= item["falha_pct"] <= 100


def test_endpoint_devolve_previsao_individual_de_cada_ping(detector):
    cliente = criar_app(Monitor(detector=detector, cenario="ok")).test_client()
    resposta = cliente.get("/api/pings-previstos?offset=0&limite=2")

    assert resposta.status_code == 200
    pagina = resposta.get_json()
    assert pagina["total"] > 2
    assert pagina["offset"] == 0
    assert pagina["limite"] == 2
    assert [ping["indice"] for ping in pagina["pings"]] == [0, 1]
    assert [ping["timestamp"] for ping in pagina["pings"]] == sorted(
        ping["timestamp"] for ping in pagina["pings"]
    )
    for ping in pagina["pings"]:
        assert ping["status"] in {"OK", "RISCO", "FALHA"}
        assert ping["previsto_em"] - ping["timestamp"] == 12 * 60
        assert 0 <= ping["confianca_pct"] <= 100

    pagina_seguinte = cliente.get("/api/pings-previstos?offset=2&limite=2").get_json()
    assert [ping["indice"] for ping in pagina_seguinte["pings"]] == [2, 3]


@pytest.mark.parametrize(
    "query",
    ["offset=-1", "limite=0", "limite=1001", "offset=invalido"],
)
def test_endpoint_pings_rejeita_paginacao_invalida(detector, query):
    cliente = criar_app(Monitor(detector=detector, cenario="ok")).test_client()

    assert cliente.get(f"/api/pings-previstos?{query}").status_code == 400


def test_endpoints_de_calibracao_na_demonstracao(detector):
    cliente = criar_app(Monitor(detector=detector, cenario="ok")).test_client()
    assert cliente.get("/api/calibracao").get_json()["ativa"] is False
    assert cliente.post("/api/calibracao").status_code == 202
    assert cliente.post("/api/medicao").status_code == 429       # ocupado calibrando
    for _ in range(200):
        estado = cliente.get("/api/calibracao").get_json()
        if not estado["ativa"]:
            break
        time.sleep(0.05)
    assert estado["percentual"] == 100 and estado["resultado"]["simulada"] is True
    assert cliente.post("/api/medicao").status_code == 200


def test_endpoint_medicao_sem_baseline_devolve_409(detector, tmp_path):
    cliente = criar_app(monitor(detector, tmp_path, ping_falso())).test_client()
    r = cliente.post("/api/medicao")
    assert r.status_code == 409 and "Calibrar" in r.get_json()["erro"]


def test_pagina_tem_preditor_botao_calibrar_coruja_e_mapa(detector):
    html = criar_app(Monitor(detector=detector, cenario="ok")).test_client().get("/").get_data(as_text=True)
    assert "Preditor de degradação de rede" in html
    assert 'id="botao_calibrar"' in html and 'id="botao_acao"' in html
    assert "coruja-mirai.png" in html and "/static/js/preditor.js" in html
    assert html.index('id="meio_tela"') < html.index('id="mapa"') < html.index('id="container_integrantes"')


def test_erro_inesperado_na_medicao_vira_json_com_a_causa(detector):
    m = Monitor(detector=detector, cenario="ok")
    m.medir = lambda: (_ for _ in ()).throw(KeyError("z_robusto_t_menos_1"))
    r = criar_app(m).test_client().post("/api/medicao")
    assert r.status_code == 500
    assert "KeyError" in r.get_json()["erro"] and "z_robusto_t_menos_1" in r.get_json()["erro"]
