import pandas as pd
import sys


def mostrar_tudo_parquet(caminho_arquivo):
    try:
        df = pd.read_parquet(caminho_arquivo)

        # Exibe todas as linhas e colunas
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", None)
        pd.set_option("display.max_colwidth", None)

        print(df)

    except FileNotFoundError:
        print("Arquivo não encontrado.")
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py arquivo.parquet")
    else:
        arquivo = sys.argv[1]
        mostrar_tudo_parquet(arquivo)