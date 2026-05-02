SELECT
    V.ID AS VENTE_ID,
    V.ANNEES,
    V.MOIS,
    V.JOUR,
    V.PU,
    V.QTE,
    (V.PU * V.QTE) AS MONTANT_LIGNE,
    F.ID AS FACTURE_ID,
    F.CODE AS FACTURE_CODE,
    F.QTE_TOTALE,
    F.TOTAL_AMOUNT,
    F.TOTAL_PAID,
    B.CODE AS BOOK_CODE,
    B.INTITULE AS BOOK_TITLE,
    B.ISBN_10,
    B.ISBN_13,
    C.INTITULE AS CATEGORY_TITLE,
    CU.CODE AS CUSTOMER_CODE,
    CU.NOM AS CUSTOMER_NAME
FROM {{ ref('fact_ventes') }} V
JOIN {{ ref('fact_factures') }} F ON V.FACTURES_ID = F.ID
JOIN {{ ref('dim_books') }} B ON V.BOOKS_ID = B.ID
JOIN {{ ref('dim_category') }} C ON B.CATEGORY_ID = C.ID
JOIN {{ ref('dim_customers') }} CU ON F.CUSTOMERS_ID = CU.ID
