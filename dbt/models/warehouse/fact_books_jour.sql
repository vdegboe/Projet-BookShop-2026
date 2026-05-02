SELECT
    B.ID AS BOOK_ID,
    B.INTITULE,
    V.JOUR,
    COUNT(V.ID) AS NB_VENTES,
    SUM(V.QTE) AS TOTAL_QTE,
    SUM(V.PU * V.QTE) AS TOTAL_CA
FROM {{ ref('fact_ventes') }} V
JOIN {{ ref('dim_books') }} B ON V.BOOKS_ID = B.ID
GROUP BY B.ID, B.INTITULE, V.JOUR