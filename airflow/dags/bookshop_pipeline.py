"""
DAG principal de la librairie Bookshop
Projet Big Data M2 IA — DIT
Auteur : DEGBOE Viwossin
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import sys
import os
import logging

sys.path.append('/opt/ingestion')
from load_to_snowflake import main as run_ingestion

logger = logging.getLogger(__name__)

# Variables d'environnement Snowflake transmises aux tâches dbt
ENV_SNOWFLAKE = {
    'SNOWFLAKE_ACCOUNT':   os.getenv('SNOWFLAKE_ACCOUNT',   ''),
    'SNOWFLAKE_USER':      os.getenv('SNOWFLAKE_USER',      ''),
    'SNOWFLAKE_PASSWORD':  os.getenv('SNOWFLAKE_PASSWORD',  ''),
    'SNOWFLAKE_ROLE':      os.getenv('SNOWFLAKE_ROLE',      'SYSADMIN'),
    'SNOWFLAKE_WAREHOUSE': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
    'SNOWFLAKE_DATABASE':  os.getenv('SNOWFLAKE_DATABASE',  'BOOKSHOP'),
}

parametres_par_defaut = {
    'owner': 'viwossin.degboe',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
    'execution_timeout': timedelta(minutes=30),
}

documentation = """
## Pipeline Bookshop — Architecture Big Data M2

Orchestration quotidienne du pipeline ETL de la librairie Bookshop.
**Auteur :** DEGBOE Viwossin | **Cours :** Architecture Big Data | **DIT**

### Flux de données
```
PostgreSQL (source locale)
    ↓  [ingest_vers_snowflake]
Snowflake → BOOKSHOP.RAW        (5 tables brutes)
    ↓  [dbt_staging]
Snowflake → BOOKSHOP.STAGING    (5 vues stg_*)
    ↓  [dbt_warehouse]
Snowflake → BOOKSHOP.WAREHOUSE  (3 dimensions + 5 tables de faits)
    ↓  [dbt_marts]
Snowflake → BOOKSHOP.MARTS      (OBT_SALES — table de reporting)
    ↓  [dbt_tests]
Validation de la qualité des données
```

### Outils utilisés
- **Orchestration :** Apache Airflow 2.8.1
- **Source :** PostgreSQL 15 (Docker)
- **Cloud DW :** Snowflake
- **Transformation :** dbt-core + dbt-snowflake
- **Visualisation :** Streamlit
"""

with DAG(
    dag_id='bookshop_pipeline',
    default_args=parametres_par_defaut,
    description='ETL Bookshop : PostgreSQL → Snowflake RAW → dbt (STAGING / WAREHOUSE / MARTS)',
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1,
    tags=['bookshop', 'big-data', 'm2', 'dit', 'snowflake', 'dbt'],
    doc_md=documentation,
) as dag:

    debut = EmptyOperator(task_id='debut')

    # Étape 1 : Ingestion des données brutes
    tache_ingestion = PythonOperator(
        task_id='ingest_vers_snowflake',
        python_callable=run_ingestion,
        doc_md="Extrait les 5 tables de PostgreSQL et les charge dans Snowflake.RAW.",
    )

    # Étape 2 : Transformation RAW → STAGING
    tache_staging = BashOperator(
        task_id='dbt_staging',
        bash_command='cd /opt/dbt && dbt run --select staging --profiles-dir /opt/dbt',
        env=ENV_SNOWFLAKE,
        append_env=True,
        doc_md="Conversion des dates (YYYYMMDD → DATE), copie des tables dans STAGING.",
    )

    # Étape 3 : Transformation STAGING → WAREHOUSE
    tache_warehouse = BashOperator(
        task_id='dbt_warehouse',
        bash_command='cd /opt/dbt && dbt run --select warehouse --profiles-dir /opt/dbt',
        env=ENV_SNOWFLAKE,
        append_env=True,
        doc_md="Construction des dimensions (dim_*) et tables de faits (fact_*) avec décomposition temporelle.",
    )

    # Étape 4 : Transformation WAREHOUSE → MARTS
    tache_marts = BashOperator(
        task_id='dbt_marts',
        bash_command='cd /opt/dbt && dbt run --select marts --profiles-dir /opt/dbt',
        env=ENV_SNOWFLAKE,
        append_env=True,
        doc_md="Consolidation de toutes les informations dans MARTS.OBT_SALES pour le reporting.",
    )

    # Étape 5 : Tests de qualité dbt
    tache_tests = BashOperator(
        task_id='dbt_tests',
        bash_command='cd /opt/dbt && dbt test --profiles-dir /opt/dbt',
        env=ENV_SNOWFLAKE,
        append_env=True,
        doc_md="Vérification des contraintes : unicité, non-nullité, valeurs acceptées (mois, jour).",
    )

    fin = EmptyOperator(task_id='fin')

    debut >> tache_ingestion >> tache_staging >> tache_warehouse >> tache_marts >> tache_tests >> fin
