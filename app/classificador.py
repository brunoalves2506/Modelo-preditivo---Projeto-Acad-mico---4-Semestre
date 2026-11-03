"""Carrega a floresta final da Tarefa 4 e classifica como OK, RISCO ou FALHA."""
from __future__ import annotations

import joblib
import pandas as pd

from .configuracao import CANDIDATOS_DETECTOR


class Detector:
    def __init__(self, caminhos=CANDIDATOS_DETECTOR):
        for caminho in caminhos:
            if caminho.exists():
                self.arquivo = caminho
                self.modelo = joblib.load(caminho)
                break
        else:
            raise FileNotFoundError(
                "Nenhum modelo encontrado. Esperado em: " + ", ".join(str(c) for c in caminhos)
            )
        self.colunas = list(self.modelo.feature_names_in_)

    def prever(self, linha: pd.Series) -> tuple[str, float]:
        """Classe prevista para ~12 min à frente e a confiança (%) da floresta nessa classe."""
        X = pd.DataFrame([[linha[c] for c in self.colunas]], columns=self.colunas)
        proba = self.modelo.predict_proba(X)[0]
        i = int(proba.argmax())
        return str(self.modelo.classes_[i]), float(proba[i] * 100)

    def classificar(self, linha: pd.Series) -> str:
        """Classifica a última medição com as features e lags da floresta final."""
        return self.prever(linha)[0]
