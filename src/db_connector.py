# src/db_connector.py

import os
import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def get_db_connection():
    """Cria e retorna uma engine de conexão com o banco de dados SQL Server."""
    try:
        db_host = os.getenv('DB_SERVER')
        db_name = os.getenv('DB_DATABASE')
        db_user = os.getenv('DB_USERNAME')
        db_password = quote_plus(os.getenv('DB_PASSWORD'))
        db_driver = os.getenv('DB_DRIVER')

        db_url = (
            f"mssql+pyodbc://{db_user}:{db_password}@{db_host}/{db_name}"
            f"?driver={db_driver.replace(' ', '+')}"
        )
        
        engine = sqlalchemy.create_engine(db_url)
        return engine

    except Exception as e:
        print(f"ERRO ao conectar ao SQL Server: {e}")
        return None

def get_raw_data(query: str, engine) -> pd.DataFrame:
    """
    Executa uma consulta SQL e retorna os dados brutos como um DataFrame do Pandas.
    
    Args:
        query (str): A consulta SQL a ser executada.
        engine: A engine de conexão do SQLAlchemy.
    """
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"ERRO ao executar a consulta: {e}")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro

if __name__ == "__main__":
    # Exemplo de uso
    engine = get_db_connection()
    if engine:
        sample_query = "SELECT TOP 10 * FROM Veiculos"  # Substitua 'sua_tabela' pelo nome real da tabela
        df = get_raw_data(sample_query, engine)
        print(df.head())