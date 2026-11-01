"""Configuração da interface de medição (alvos, janelas e caminhos)."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_INTERFACE = RAIZ / "notebook" / "arvore" / "interface"

# Detector de estado atual (OK / RISCO / FALHA). Usa o primeiro arquivo que existir.
# A floresta é a aprovada para o projeto; a árvore oficial fica como reserva.
CANDIDATOS_DETECTOR = [
    RAIZ / "notebook" / "data_ripe_atlas" / "models" / "floresta_oficial.joblib",
    RAIZ / "data_ripe_atlas" / "models" / "arvore_oficial.joblib",
]

# Baseline (o "normal" da rede de quem está usando). É local de cada máquina e não vai para o Git.
ARQ_BASELINE = Path(__file__).resolve().parent / "dados" / "baseline_local.json"

# Destinos testados por ICMP. O estado geral é a mediana do estado de cada destino.
ALVOS = [
    ("Cloudflare", "1.1.1.1"),
    ("Google", "8.8.8.8"),
    ("Quad9", "9.9.9.9"),
]

PACOTES_POR_RAJADA = 3      # mesmo formato do mesh do RIPE Atlas (3 pacotes por medição)
TIMEOUT_PACOTE_S = 2        # espera máxima por resposta de cada pacote
RODADAS = 5                 # medições seguidas por destino (a janela n5 do modelo tem 5)
RAJADAS_CALIBRACAO = 20     # tamanho da referência provisória criada no primeiro uso
PISO_BASELINE = 1500        # mínimo de RTTs válidos para um baseline completo (RFC, Tarefa 2)
MIN_RAJADAS_VALIDAS_CALIBRACAO = 10
