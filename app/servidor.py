"""Servidor local da interface. Uso:  python -m app.servidor [--simular ok|risco|falha] [--calibrar N]"""
from __future__ import annotations

import argparse
import threading
import webbrowser

from flask import Flask, jsonify, render_template, request

from .configuracao import RAJADAS_CALIBRACAO
from .historico import carregar_pings_previstos, carregar_previsoes_historicas
from .monitor import ErroMedicao, Monitor, MonitorOcupado, SemBaseline
from .rede import PingIndisponivel
from .simulacao import CENARIOS


def criar_app(monitor: Monitor) -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False

    @app.get("/")
    def inicio():
        return render_template("index.html")

    @app.post("/api/medicao")
    def medicao():
        try:
            return jsonify(monitor.medir())
        except MonitorOcupado as e:
            return jsonify(erro=str(e)), 429
        except SemBaseline as e:
            return jsonify(erro=str(e)), 409
        except (ErroMedicao, PingIndisponivel) as e:
            return jsonify(erro=str(e)), 503
        except Exception as e:  # noqa: BLE001 - mostra a causa na tela em vez de um erro genérico
            app.logger.exception("Erro inesperado na medição")
            return jsonify(erro=f"Erro interno ({e.__class__.__name__}: {e}). Veja o terminal do servidor."), 500

    @app.post("/api/calibracao")
    def iniciar_calibracao():
        try:
            monitor.iniciar_calibracao()
        except MonitorOcupado as e:
            return jsonify(erro=str(e)), 429
        return jsonify(monitor.estado_calibracao()), 202

    @app.get("/api/calibracao")
    def estado_calibracao():
        return jsonify(monitor.estado_calibracao())

    @app.delete("/api/calibracao")
    def cancelar_calibracao():
        monitor.cancelar_calibracao()
        return jsonify(monitor.estado_calibracao())

    @app.get("/api/previsoes-historicas")
    def previsoes_historicas():
        return jsonify(carregar_previsoes_historicas())

    @app.get("/api/pings-previstos")
    def pings_previstos():
        try:
            offset = int(request.args.get("offset", "0"))
            limite = int(request.args.get("limite", "500"))
        except ValueError:
            return jsonify(erro="offset e limite devem ser números inteiros."), 400
        if offset < 0:
            return jsonify(erro="offset deve ser um inteiro não negativo."), 400
        if not 1 <= limite <= 1000:
            return jsonify(erro="limite deve estar entre 1 e 1000."), 400
        return jsonify(carregar_pings_previstos(offset, limite))

    return app


def main():
    p = argparse.ArgumentParser(description="Interface do classificador de degradação de rede")
    p.add_argument("--porta", type=int, default=5000)
    p.add_argument("--simular", choices=CENARIOS, help="modo demonstração: não usa a rede, gera o cenário escolhido")
    p.add_argument("--calibrar", type=int, nargs="?", const=RAJADAS_CALIBRACAO, metavar="N",
                   help=f"refaz o baseline com N medições por alvo e sai (padrão {RAJADAS_CALIBRACAO}, o baseline completo)")
    args = p.parse_args()

    monitor = Monitor(cenario=args.simular)
    if args.calibrar is not None:
        print(f"Calibrando com {args.calibrar} medições por alvo (deixe a rede funcionando normalmente)...")
        def progresso(feitas, total):
            if feitas % max(1, total // 50) == 0 or feitas == total:
                print(f"\r  {feitas / total:4.0%} ({feitas}/{total})", end="", flush=True)

        resultado = monitor.calibrar(args.calibrar, progresso)
        print()
        for host, ficha in resultado.items():
            print(f"  {host}: " + (f"normal = {ficha.mediana:.1f} ms ({ficha.n_validos} amostras válidas)" if ficha
                                   else "sem respostas suficientes, baseline não atualizado"))
        return

    url = f"http://127.0.0.1:{args.porta}"
    print(f"Interface em {url}" + (f"  [DEMONSTRAÇÃO: cenário '{args.simular}']" if args.simular else ""))
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    criar_app(monitor).run(host="127.0.0.1", port=args.porta, threaded=True)


if __name__ == "__main__":
    main()
