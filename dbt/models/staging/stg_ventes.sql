SELECT
    ID,
    CODE,
    TO_DATE(DATE_EDIT, 'YYYYMMDD') AS DATE_EDIT,
    FACTURES_ID,
    BOOKS_ID,
    PU,
    QTE,
    CREATED_AT
FROM {{ source('raw', 'VENTES') }}
