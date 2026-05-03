# BookShop — Pipeline ETL multicouche

Projet final Big Data — Master 2 IA, DIT (Bénin) — Viwossin DEGBOE.

Pipeline ETL complet pour une librairie : ingestion d'une base PostgreSQL locale vers Snowflake, transformations en couches avec dbt, orchestration via Airflow, restitution en dashboard Streamlit. L'ensemble est conteneurisé.

## Architecture

```
PostgreSQL (Docker)  →  Snowflake (RAW → STAGING → WAREHOUSE → MARTS)  →  Streamlit
        ▲                              ▲
        │                              │
     init.sql                     dbt (transformations)
                                       ▲
                                       │
                                Airflow (DAG bookshop_pipeline, @daily)
```

- **Extract & Load** : script Python ([ingestion/load_to_snowflake.py](ingestion/load_to_snowflake.py)) — `psycopg2` + `snowflake-connector` + `pandas` (`write_pandas`, `auto_create_table=True`).
- **Transform** : dbt-core + dbt-snowflake, 11 modèles répartis sur 3 couches.
- **Orchestrate** : Airflow 2.8.1, un seul DAG enchaînant 7 tâches.
- **Visualize** : Streamlit + Plotly, branché sur `MARTS.OBT_SALES`.

## Stack

| Composant         | Outil                          |
|-------------------|--------------------------------|
| Source            | PostgreSQL 15                  |
| Datawarehouse     | Snowflake (Free Trial)         |
| Transformations   | dbt-core + dbt-snowflake       |
| Orchestration     | Apache Airflow 2.8.1           |
| Dashboard         | Streamlit + Plotly             |
| Conteneurisation  | Docker Compose                 |

## Modèle de données

5 tables sources dans PostgreSQL : `category` (7), `books` (20), `customers` (12), `factures` (40), `ventes` (60). Jeu de test à coloration ouest-africaine (livres : *Doguicimi*, *L'Aventure ambiguë*, *Le Monde s'effondre*… ; clients : DEGBOE, OKAFOR, KOUASSI…). Devise affichée : FCFA.

> **Particularité** : `ventes.date_edit` et `factures.date_edit` sont stockées en `VARCHAR` au format `YYYYMMDD`. Conversion en `DATE` faite en couche STAGING via `TO_DATE(DATE_EDIT, 'YYYYMMDD')`.

## Couches dbt

- **STAGING** (5 modèles `stg_*`) — nettoyage, conversion des dates.
- **WAREHOUSE** (3 dimensions + 5 faits) — modèle en étoile :
  - `dim_customers` (avec `NOM = first_name || ' ' || last_name`), `dim_books`, `dim_category`
  - `fact_ventes`, `fact_factures` (avec colonnes dérivées `ANNEES`, `MOIS` et `JOUR` traduits en français)
  - `fact_books_annees`, `fact_books_mois`, `fact_books_jour` (agrégats)
- **MARTS** — `obt_sales` (One Big Table) consolidant ventes, factures, livres, catégories, clients + champ calculé `MONTANT_LIGNE = PU * QTE`.

**Tests dbt** : `unique` + `not_null` sur `obt_sales.VENTE_ID` ; `accepted_values` sur les colonnes `MOIS` (12 mois fr) et `JOUR` (7 jours fr).

## DAG Airflow

Fichier : [airflow/dags/bookshop_pipeline.py](airflow/dags/bookshop_pipeline.py)

```
debut → ingest_vers_snowflake → dbt_staging → dbt_warehouse → dbt_marts → dbt_tests → fin
```

Paramètres : `schedule_interval='@daily'`, `retries=2` (delay 3 min), `execution_timeout=30min`, `max_active_runs=1`. Variables Snowflake injectées via `env=ENV_SNOWFLAKE` dans chaque `BashOperator`.

## Structure du dépôt

```
bookshop/
├── airflow/         # DAG + config Airflow
├── dbt/             # Modèles staging/warehouse/marts + tests
├── ingestion/       # Script Python PostgreSQL → Snowflake
├── postgres/        # init.sql (DDL + données seed)
├── streamlit/       # Dashboard analytique
├── docker-compose.yml
└── .env             # Credentials Snowflake & PostgreSQL
```

## Réplication

### Pré-requis
- Docker + Docker Compose
- Compte Snowflake (Free Trial suffit) — base `BOOKSHOP` créée avec schémas `RAW`, `STAGING`, `WAREHOUSE`, `MARTS`

### Configuration

Renseigner `.env` à la racine avec les credentials :

```env
SNOWFLAKE_ACCOUNT=...
SNOWFLAKE_USER=...
SNOWFLAKE_PASSWORD=...
SNOWFLAKE_ROLE=...
SNOWFLAKE_WAREHOUSE=...
SNOWFLAKE_DATABASE=BOOKSHOP

POSTGRES_HOST=postgres
POSTGRES_DB=bookshop
POSTGRES_USER=...
POSTGRES_PASSWORD=...
```

### Démarrage

```bash
docker compose up -d --build
```

Si l'utilisateur admin Airflow n'a pas été créé automatiquement (race condition possible au premier démarrage) :

```bash
docker compose exec airflow-webserver airflow users create \
  --username admin --password admin \
  --firstname Admin --lastname Bookshop \
  --role Admin --email admin@bookshop.com
```

### Accès

| Service          | URL                       | Identifiants  |
|------------------|---------------------------|---------------|
| Airflow UI       | http://localhost:8080     | admin / admin |
| Streamlit        | http://localhost:8501     | —             |

### Lancer le pipeline

Activer puis déclencher le DAG `bookshop_pipeline` depuis l'UI Airflow. À la fin : 60 lignes attendues dans `MARTS.OBT_SALES`.

### Validation rapide (Snowflake)

```sql
USE DATABASE BOOKSHOP;
SELECT 'RAW.VENTES' AS T, COUNT(*) FROM RAW.VENTES
UNION ALL SELECT 'STAGING.STG_VENTES', COUNT(*) FROM STAGING.STG_VENTES
UNION ALL SELECT 'WAREHOUSE.FACT_VENTES', COUNT(*) FROM WAREHOUSE.FACT_VENTES
UNION ALL SELECT 'MARTS.OBT_SALES', COUNT(*) FROM MARTS.OBT_SALES;
-- Toutes les lignes doivent retourner 60.
```

## Dashboard

Branché sur `MARTS.OBT_SALES` (cache Streamlit pour limiter les requêtes). 6 KPIs (CA total en FCFA, ventes, factures, clients actifs, livres distincts, panier moyen) + 6 graphiques Plotly (évolution mensuelle, donut catégories, top 10 livres/clients, ventes par jour, encaissé vs impayé) + table exportable CSV. Filtres globaux multi-sélection : Année(s) et Catégorie(s).
