from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_ROOT = ROOT / "data_ripe_atlas"

# O conjunto de dados real usado pelo projeto está em raw/v2.
DATA_RAW = DATA_ROOT / "raw" / "v2"
DATA_RAW_V1 = DATA_ROOT / "raw" / "v1"

# Pasta de saída para artefatos processados/rotulados.
DATA_PROCESSED = DATA_ROOT / "processed"

# Os metadados do RIPE Atlas v2 ficam junto ao conjunto bruto em raw/v2.
DATA_METADATA = DATA_RAW

CSV_TRATADO = DATA_PROCESSED / "tratado.csv"
