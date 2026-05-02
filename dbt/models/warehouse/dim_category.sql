SELECT
    ID,
    INTITULE,
    CREATED_AT
FROM {{ ref('stg_category') }}