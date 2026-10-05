import pandas as pd
from config import CSV_TRATADO # Supondo que o CSV tratado seja a entrada

def enriquecer_dados(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona informações de país e ASN do probe aos dados."""
    print("[enriquecer] Adicionando metadados do probe...")
    # Exemplo: Se você tivesse um dicionário de mapeamento probe_id -> país
    # mapeamento_probe = {6977: {'pais': 'BR', 'asn': '12345'}, ...}
    # df['pais_probe'] = df['prb_id'].map(lambda x: mapeamento_probe.get(x, {}).get('pais', 'Desconhecido'))
    
    # Por enquanto, apenas cria colunas vazias para não quebrar o pipeline
    df['pais_probe'] = 'N/A'
    df['asn_probe'] = 'N/A'
    df['cidade_probe'] = 'N/A'
    return df

if __name__ == "__main__":
    print("[enriquecer] Carregando dados tratados...")
    df = pd.read_csv(CSV_TRATADO)
    df_enriquecido = enriquecer_dados(df)
    # Salva o arquivo final
   caminho_saida = CSV_TRATADO.parent / (CSV_TRATADO.stem + '_enriquecido' + CSV_TRATADO.suffix)
    df_enriquecido.to_csv(caminho_saida, index=False)
    print(f"[enriquecer] Arquivo salvo em: {caminho_saida}")
