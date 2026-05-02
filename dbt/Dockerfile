FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/dbt

RUN pip install --no-cache-dir \
    dbt-core \
    dbt-snowflake \
    psycopg2-binary \
    snowflake-connector-python[pandas]

COPY . /opt/dbt

# Ensure dbt can find the profile
ENV DBT_PROFILES_DIR=/opt/dbt

ENTRYPOINT ["dbt"]
