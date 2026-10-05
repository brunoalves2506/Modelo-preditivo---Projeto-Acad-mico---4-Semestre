from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_METADATA = ROOT / "data" / "metadata"

CSV_TRATADO = ROOT / "data" / "processed" / "tratado.csv"
