"""
Dashboard analytique — Librairie Bookshop
Projet Big Data M2 IA — DIT
Auteur : DEGBOE Viwossin
"""
import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

FCFA = 655.957

def fmt(val):
    if abs(val) >= 1_000_000_000:
        return f"{val / 1_000_000:.1f} M FCFA".replace(".", ",")
    if abs(val) >= 1_000_000:
        return f"{val / 1_000:,.0f} K FCFA".replace(",", ".")
    return f"{val:,.0f} FCFA".replace(",", ".")

def echelle(col):
    m = col.max()
    if m >= 1_000_000_000:
        return col / 1_000_000, "M FCFA"
    if m >= 1_000_000:
        return col / 1_000, "K FCFA"
    return col, "FCFA"

def fmt_col(v, u):
    return f"{v:,.0f} {u}".replace(",", ".")

st.set_page_config(
    page_title="Bookshop Analytics — DIT",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .bloc-entete { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                   color: white; padding: 20px 28px; border-radius: 12px; margin-bottom: 20px; }
    .bloc-entete h1 { color: white; margin: 0; font-size: 1.8rem; }
    .bloc-entete p  { color: #aac4e0; margin: 4px 0 0; font-size: 0.9rem; }
    .stMetric label { font-size: 0.82rem; color: #555; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="bloc-entete">
  <h1>📚 Bookshop — Tableau de Bord Analytique</h1>
  <p>Projet Big Data M2 IA &nbsp;|&nbsp; DIT &nbsp;|&nbsp; DEGBOE Viwossin</p>
  <p style="font-size:0.8rem; color:#7fa8c9;">
    Pipeline : PostgreSQL → Snowflake (RAW / STAGING / WAREHOUSE / MARTS) &nbsp;|&nbsp; dbt + Airflow
  </p>
</div>
""", unsafe_allow_html=True)

# ── Connexion Snowflake ────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_conn():
    return snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        role=os.getenv('SNOWFLAKE_ROLE', 'SYSADMIN'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
        database=os.getenv('SNOWFLAKE_DATABASE', 'BOOKSHOP'),
        schema='MARTS',
        client_session_keep_alive=True,
    )

@st.cache_data(ttl=300, show_spinner=False)
def requete(sql: str) -> pd.DataFrame:
    try:
        return pd.read_sql(sql, get_conn())
    except snowflake.connector.errors.DatabaseError as e:
        if getattr(e, 'errno', None) == 390114:
            get_conn.clear()
            try:
                return pd.read_sql(sql, get_conn())
            except Exception as e2:
                st.error(f"Erreur Snowflake après reconnexion : {e2}")
                return pd.DataFrame()
        st.error(f"Erreur Snowflake : {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur de connexion Snowflake : {e}")
        return pd.DataFrame()

# ── Filtres (barre latérale) ───────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/book.png", width=60)
    st.title("Filtres")

    df_annees = requete("SELECT DISTINCT ANNEES FROM OBT_SALES ORDER BY 1")
    toutes_annees = df_annees['ANNEES'].tolist() if not df_annees.empty else []
    annees_sel = st.multiselect("Année(s)", toutes_annees, default=toutes_annees)

    df_cats = requete("SELECT DISTINCT CATEGORY_TITLE FROM OBT_SALES ORDER BY 1")
    toutes_cats = df_cats['CATEGORY_TITLE'].tolist() if not df_cats.empty else []
    cats_sel = st.multiselect("Catégorie(s)", toutes_cats, default=toutes_cats)

    st.divider()
    st.caption("DEGBOE Viwossin | M2 IA | DIT")

filtre_annee = f"ANNEES IN ({','.join(str(a) for a in annees_sel)})" if annees_sel else "1=1"
filtre_cat   = f"CATEGORY_TITLE IN ({','.join(repr(c) for c in cats_sel)})" if cats_sel else "1=1"
clause_where = f"WHERE {filtre_annee} AND {filtre_cat}"

# ── KPIs ───────────────────────────────────────────────────────────────────────
st.subheader("Indicateurs Clés de Performance")
df_kpi = requete(f"""
    SELECT
        SUM(MONTANT_LIGNE)   * {FCFA}    AS CHIFFRE_AFFAIRES,
        COUNT(DISTINCT VENTE_ID)         AS NB_VENTES,
        COUNT(DISTINCT FACTURE_ID)       AS NB_FACTURES,
        COUNT(DISTINCT CUSTOMER_CODE)    AS NB_CLIENTS_ACTIFS,
        SUM(QTE)                         AS TOTAL_LIVRES_VENDUS,
        AVG(MONTANT_LIGNE)   * {FCFA}    AS PANIER_MOYEN
    FROM OBT_SALES {clause_where}
""")

if not df_kpi.empty:
    r = df_kpi.iloc[0]
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Chiffre d'Affaires",   fmt(r['CHIFFRE_AFFAIRES']))
    c2.metric("Ventes",               f"{int(r['NB_VENTES'])}")
    c3.metric("Factures",             f"{int(r['NB_FACTURES'])}")
    c4.metric("Clients actifs",       f"{int(r['NB_CLIENTS_ACTIFS'])}")
    c5.metric("Livres vendus",        f"{int(r['TOTAL_LIVRES_VENDUS'])}")
    c6.metric("Panier moyen",         fmt(r['PANIER_MOYEN']))

st.divider()

# ── Évolution mensuelle + Répartition par catégorie ───────────────────────────
col_g, col_d = st.columns([3, 2])

with col_g:
    st.subheader("Évolution mensuelle du chiffre d'affaires")
    df_mensuel = requete(f"""
        SELECT ANNEES, MOIS,
               SUM(MONTANT_LIGNE) * {FCFA} AS CA,
               COUNT(VENTE_ID)             AS NB_VENTES
        FROM OBT_SALES {clause_where}
        GROUP BY ANNEES, MOIS
        ORDER BY ANNEES,
            CASE MOIS
                WHEN 'janvier'   THEN 1  WHEN 'fevrier'   THEN 2
                WHEN 'mars'      THEN 3  WHEN 'avril'     THEN 4
                WHEN 'mai'       THEN 5  WHEN 'juin'      THEN 6
                WHEN 'juillet'   THEN 7  WHEN 'aout'      THEN 8
                WHEN 'septembre' THEN 9  WHEN 'octobre'   THEN 10
                WHEN 'novembre'  THEN 11 WHEN 'decembre'  THEN 12
            END
    """)
    if not df_mensuel.empty:
        df_mensuel['CA'], u = echelle(df_mensuel['CA'])
        df_mensuel['PERIODE'] = df_mensuel['MOIS'].str[:3] + ' ' + df_mensuel['ANNEES'].astype(str)
        fig = px.line(df_mensuel, x='PERIODE', y='CA', color='ANNEES',
                      markers=True, line_shape='spline',
                      labels={'CA': f'CA ({u})', 'PERIODE': ''},
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=320, margin=dict(t=10, b=10), separators=',.')
        st.plotly_chart(fig, use_container_width=True)

with col_d:
    st.subheader("Répartition par catégorie")
    df_cat = requete(f"""
        SELECT CATEGORY_TITLE, SUM(MONTANT_LIGNE) * {FCFA} AS CA
        FROM OBT_SALES {clause_where}
        GROUP BY 1 ORDER BY 2 DESC
    """)
    if not df_cat.empty:
        df_cat['CA'], _ = echelle(df_cat['CA'])
        fig = px.pie(df_cat, values='CA', names='CATEGORY_TITLE', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(height=320, margin=dict(t=10, b=10), separators=',.')
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Top livres + Top clients ───────────────────────────────────────────────────
col_g2, col_d2 = st.columns(2)

with col_g2:
    st.subheader("Top 10 Livres par chiffre d'affaires")
    df_livres = requete(f"""
        SELECT BOOK_TITLE, CATEGORY_TITLE,
               SUM(MONTANT_LIGNE) * {FCFA} AS CA, SUM(QTE) AS QTE
        FROM OBT_SALES {clause_where}
        GROUP BY 1, 2 ORDER BY CA DESC LIMIT 10
    """)
    if not df_livres.empty:
        df_livres['CA'], u = echelle(df_livres['CA'])
        df_livres['CA_FMT'] = df_livres['CA'].apply(lambda v: fmt_col(v, u))
        fig = px.bar(df_livres, x='CA', y='BOOK_TITLE', orientation='h',
                     color='CATEGORY_TITLE', text='CA_FMT',
                     labels={'CA': f'CA ({u})', 'BOOK_TITLE': '', 'CATEGORY_TITLE': 'Catégorie'},
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(height=420, margin=dict(t=10, b=10),
                          yaxis=dict(autorange='reversed'), separators=',.',
                          legend=dict(orientation='h', yanchor='top', y=-0.15,
                                      xanchor='center', x=0.5, title=''))
        st.plotly_chart(fig, use_container_width=True)

with col_d2:
    st.subheader("Top 10 Clients par chiffre d'affaires")
    df_clients = requete(f"""
        WITH par_cat AS (
            SELECT CUSTOMER_NAME, CATEGORY_TITLE,
                   SUM(MONTANT_LIGNE) * {FCFA} AS CA_CAT
            FROM OBT_SALES {clause_where}
            GROUP BY CUSTOMER_NAME, CATEGORY_TITLE
        ),
        totaux AS (
            SELECT CUSTOMER_NAME, SUM(CA_CAT) AS CA
            FROM par_cat GROUP BY CUSTOMER_NAME
        )
        SELECT t.CUSTOMER_NAME, t.CA, p.CATEGORY_TITLE
        FROM totaux t
        JOIN par_cat p ON t.CUSTOMER_NAME = p.CUSTOMER_NAME
        QUALIFY ROW_NUMBER() OVER (PARTITION BY t.CUSTOMER_NAME ORDER BY p.CA_CAT DESC) = 1
        ORDER BY CA DESC LIMIT 10
    """)
    if not df_clients.empty:
        df_clients['CA'], u = echelle(df_clients['CA'])
        df_clients['CA_FMT'] = df_clients['CA'].apply(lambda v: fmt_col(v, u))
        fig = px.bar(df_clients, x='CUSTOMER_NAME', y='CA',
                     color='CATEGORY_TITLE', text='CA_FMT',
                     labels={'CA': f'CA ({u})', 'CUSTOMER_NAME': 'Client', 'CATEGORY_TITLE': 'Catégorie'},
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(height=420, margin=dict(t=10, b=10), separators=',.',
                          legend=dict(orientation='h', yanchor='top', y=-0.15,
                                      xanchor='center', x=0.5, title=''))
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Ventes par jour + Analyse des paiements ───────────────────────────────────
col_g3, col_d3 = st.columns(2)

with col_g3:
    st.subheader("Activité par jour de la semaine")
    df_jour = requete(f"""
        SELECT JOUR, CATEGORY_TITLE, COUNT(VENTE_ID) AS NB_VENTES
        FROM OBT_SALES {clause_where}
        GROUP BY 1, 2
        ORDER BY CASE JOUR
            WHEN 'lundi' THEN 1    WHEN 'mardi'    THEN 2
            WHEN 'mercredi' THEN 3 WHEN 'jeudi'    THEN 4
            WHEN 'vendredi' THEN 5 WHEN 'samedi'   THEN 6
            WHEN 'dimanche' THEN 7
        END
    """)
    if not df_jour.empty:
        fig = px.bar(df_jour, x='JOUR', y='NB_VENTES', color='CATEGORY_TITLE',
                     labels={'NB_VENTES': 'Nombre de ventes', 'JOUR': '',
                             'CATEGORY_TITLE': 'Catégorie'},
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=380, margin=dict(t=10, b=10), separators=',.',
                          legend=dict(orientation='h', yanchor='top', y=-0.15,
                                      xanchor='center', x=0.5, title=''))
        st.plotly_chart(fig, use_container_width=True)

with col_d3:
    st.subheader("Paiements encaissés vs impayés")
    df_paiement = requete(f"""
        SELECT ANNEES,
               SUM(TOTAL_AMOUNT) * {FCFA} AS MONTANT_FACTURE,
               SUM(TOTAL_PAID)   * {FCFA} AS MONTANT_ENCAISSE
        FROM OBT_SALES {clause_where}
        GROUP BY 1 ORDER BY 1
    """)
    if not df_paiement.empty:
        _, u = echelle(df_paiement['MONTANT_FACTURE'])
        if u == "M FCFA":
            df_paiement[['MONTANT_FACTURE', 'MONTANT_ENCAISSE']] /= 1_000_000
        elif u == "K FCFA":
            df_paiement[['MONTANT_FACTURE', 'MONTANT_ENCAISSE']] /= 1_000
        df_paiement['IMPAYE'] = df_paiement['MONTANT_FACTURE'] - df_paiement['MONTANT_ENCAISSE']
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Encaissé', x=df_paiement['ANNEES'],
                             y=df_paiement['MONTANT_ENCAISSE'], marker_color='#54A24B'))
        fig.add_trace(go.Bar(name='Impayé',   x=df_paiement['ANNEES'],
                             y=df_paiement['IMPAYE'],            marker_color='#E45756'))
        fig.update_layout(barmode='stack', height=320, margin=dict(t=10, b=10),
                          yaxis_title=f"Montant ({u})", separators=',.')
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Données brutes exportables ─────────────────────────────────────────────────
with st.expander("Données brutes — MARTS.OBT_SALES (200 premières lignes)"):
    df_brut = requete(f"SELECT * FROM OBT_SALES {clause_where} LIMIT 200")
    if not df_brut.empty:
        st.dataframe(df_brut, use_container_width=True, height=350)
        csv = df_brut.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger en CSV", csv, "obt_sales.csv", "text/csv")
