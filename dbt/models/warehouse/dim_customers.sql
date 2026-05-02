SELECT
    ID,
    CODE,
    FIRST_NAME,
    LAST_NAME,
    FIRST_NAME || ' ' || LAST_NAME AS NOM,
    CREATED_AT
FROM {{ ref('stg_customers') }}