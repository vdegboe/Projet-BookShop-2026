SELECT
    ID,
    CATEGORY_ID,
    CODE,
    INTITULE,
    ISBN_10,
    ISBN_13,
    CREATED_AT
FROM {{ ref('stg_books') }}