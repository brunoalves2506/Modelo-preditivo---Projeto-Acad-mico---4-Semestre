import pandas as pd
from config import CSV_TRATADO

def validar_dados(df: pd.DataFrame) -> bool:
    """Verifica a integridade dos dados."""
    print("[validar] Iniciando validação...")
    erros = []
    
    # Verifica se há valores nulos em colunas críticas
    if df['rcvd'].isnull().any():
        erros.append("Coluna 'rcvd' contém valores nulos.")
    
    # Verifica se a perda de pacotes está entre 0 e 1
    if not df['perda_pacotes'].between(0, 1).all():
        erros.append("Valores de perda de pacotes fora do intervalo [0, 1].")
        
    if erros:
        print("[validar] Erros encontrados:")
        for erro in erros:
            print(f" - {erro}")
        return False
    else:
        print("[validar] Validação concluída com sucesso! Nenhum erro encontrado.")
        return True

if __name__ == "__main__":
    print("[validar] Carregando dados para validação...")
    df = pd.read_csv(CSV_TRATADO) # Ou o caminho do arquivo enriquecido
    validar_dados(df)
