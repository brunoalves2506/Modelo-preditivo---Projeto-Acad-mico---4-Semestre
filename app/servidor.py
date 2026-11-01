"""Servidor local da interface. Uso:  python -m app.servidor [--simular ok|risco|falha] [--calibrar N]"""
from __future__ import annotations

import argparse
import threading
import webbrowser

from flask import Flask, jsonify, send_from_directory

from .configuracao import DIR_INTERFACE, RAJADAS_CALIBRACAO
from .monitor import ErroMedicao, Monitor, MonitorOcupado
from .rede import PingIndisponivel
from .simulacao import CENARIOS


def criar_app(monitor: Monitor) -> Flask:
    app = Flask(__name__, static_folder=None)
    app.json.ensure_ascii = False

    @app.get("/")
    def inicio():
        return send_from_directory(DIR_INTERFACE, "index.html")

    @app.get("/<path:arquivo>")
    def estaticos(arquivo):
        return send_from_directory(DIR_INTERFACE, arquivo)

    @app.post("/api/medicao")
    def medicao():
        try:
            return jsonify(monitor.medir())
        except MonitorOcupado as e:
            return jsonify(erro=str(e)), 429
        except (ErroMedicao, PingIndisponivel) as e:
            return jsonify(erro=str(e)), 503

    return app


def main():
    p = argparse.ArgumentParser(description="Interface do classificador de degradação de rede")
    p.add_argument("--porta", type=int, default=5000)
    p.add_argument("--simular", choices=CENARIOS, help="modo demonstração: não usa a rede, gera o cenário escolhido")
    p.add_argument("--calibrar", type=int, nargs="?", const=RAJADAS_CALIBRACAO, metavar="N",
                   help=f"refaz o baseline com N medições por alvo e sai (padrão {RAJADAS_CALIBRACAO}; use 1500 para o baseline completo)")
    args = p.parse_args()

    monitor = Monitor(cenario=args.simular)
    if args.calibrar is not None:
        print(f"Calibrando com {args.calibrar} medições por alvo (deixe a rede funcionando normalmente)...")
        for host, ficha in monitor.calibrar(args.calibrar).items():
            print(f"  {host}: " + (f"normal = {ficha.mediana:.1f} ms ({ficha.n_validos} amostras válidas)" if ficha
                                   else "sem respostas suficientes, baseline não atualizado"))
        return

    url = f"http://127.0.0.1:{args.porta}"
    print(f"Interface em {url}" + (f"  [DEMONSTRAÇÃO: cenário '{args.simular}']" if args.simular else ""))
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    criar_app(monitor).run(host="127.0.0.1", port=args.porta, threaded=True)


if __name__ == "__main__":
    main()
