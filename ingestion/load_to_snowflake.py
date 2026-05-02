"""
Ingestion PostgreSQL → Snowflake RAW
Projet Big Data M2 — DIT
Auteur : DEGBOE Viwossin
"""
import os
import time
import logging
import psycopg2
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

TABLES = ['category', 'books', 'customers', 'factures', 'ventes']


def get_pg_connection():
    """Connexion à la base PostgreSQL source."""
    return psycopg2.connect(
        host=os.getenv('PG_HOST', 'postgres-local'),
        port=os.getenv('PG_PORT', '5432'),
        database=os.getenv('PG_DB'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASSWORD')
    )


def get_sf_connection():
    """Connexion au Data Warehouse Snowflake (schéma RAW)."""
    return snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        role=os.getenv('SNOWFLAKE_ROLE', 'SYSADMIN'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
        database=os.getenv('SNOWFLAKE_DATABASE', 'BOOKSHOP'),
        schema=os.getenv('SNOWFLAKE_SCHEMA', 'RAW')
    )


def ingest_table(table_name: str, pg_conn, sf_conn, schema: str = 'RAW') -> dict:
    """Extrait une table de PostgreSQL et la charge dans Snowflake."""
    debut = time.time()
    resultat = {'table': table_name, 'lignes': 0, 'succes': False, 'duree_s': 0}

    try:
        logger.info(f"[{table_name.upper()}] Extraction depuis PostgreSQL...")
        df = pd.read_sql(f"SELECT * FROM {table_name}", pg_conn)
        df.columns = [c.upper() for c in df.columns]
        logger.info(f"[{table_name.upper()}] {len(df)} ligne(s) extraite(s).")

        curseur = sf_conn.cursor()
        curseur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        curseur.execute(f"TRUNCATE TABLE IF EXISTS {schema}.{table_name.upper()}")

        logger.info(f"[{table_name.upper()}] Chargement dans Snowflake.{schema}...")
        succes, nb_chunks, nb_lignes, _ = write_pandas(
            conn=sf_conn,
            df=df,
            table_name=table_name.upper(),
            schema=schema,
            auto_create_table=True,
            overwrite=False,
        )

        resultat['lignes'] = nb_lignes
        resultat['succes'] = succes
        if succes:
            logger.info(f"[{table_name.upper()}] OK — {nb_lignes} lignes chargées en {nb_chunks} bloc(s).")
        else:
            logger.error(f"[{table_name.upper()}] Échec du chargement.")

    except Exception as erreur:
        logger.error(f"[{table_name.upper()}] Erreur : {erreur}")

    resultat['duree_s'] = round(time.time() - debut, 2)
    return resultat


def main():
    logger.info("=" * 60)
    logger.info("BOOKSHOP — Ingestion PostgreSQL → Snowflake RAW")
    logger.info("Auteur : DEGBOE Viwossin | DIT | M2 IA")
    logger.info("=" * 60)
    debut_pipeline = time.time()

    schema = os.getenv('SNOWFLAKE_SCHEMA', 'RAW')
    pg_conn = get_pg_connection()
    sf_conn = get_sf_connection()

    bilan = []
    try:
        for table in TABLES:
            res = ingest_table(table, pg_conn, sf_conn, schema)
            bilan.append(res)
    finally:
        pg_conn.close()
        sf_conn.close()

    logger.info("=" * 60)
    logger.info("BILAN DE L'INGESTION")
    logger.info(f"{'Table':<15} {'Statut':<10} {'Lignes':>8} {'Durée':>8}")
    logger.info("-" * 45)
    total_lignes = 0
    for r in bilan:
        statut = "OK" if r['succes'] else "ERREUR"
        logger.info(f"{r['table']:<15} {statut:<10} {r['lignes']:>8} {r['duree_s']:>7}s")
        total_lignes += r['lignes']
    logger.info("-" * 45)
    duree_totale = round(time.time() - debut_pipeline, 2)
    logger.info(f"{'TOTAL':<15} {'':<10} {total_lignes:>8} {duree_totale:>7}s")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
