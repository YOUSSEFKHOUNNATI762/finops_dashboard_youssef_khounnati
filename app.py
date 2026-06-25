# =============================================================================
# Dashboard FinOps - Haute Disponibilité & Monitoring Fintech Asynchrones
# Auteur  : Youssef Khounnati
# Prof    : TAOUSSI Jamal
# Version : 1.0 - 2026
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import warnings
warnings.filterwarnings("ignore")

# ─── Configuration globale de la page ────────────────────────────────────────
st.set_page_config(
    page_title="FinOps Dashboard – Fintech",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Palette de couleurs ──────────────────────────────────────────────────────
COLORS = {
    "primary":   "#1A73E8",
    "success":   "#0F9D58",
    "warning":   "#F4B400",
    "danger":    "#DB4437",
    "dark":      "#0D1117",
    "card_bg":   "#161B22",
    "text":      "#E6EDF3",
    "border":    "#30363D",
    "accent1":   "#58A6FF",
    "accent2":   "#3FB950",
    "accent3":   "#D29922",
    "accent4":   "#F85149",
}

PROVIDER_COLORS = {
    "AWS":           "#FF9900",
    "GCP":           "#4285F4",
    "Azure":         "#008AD7",
    "Private Cloud": "#6E40C9",
}

# ─── CSS personnalisé ─────────────────────────────────────────────────────────
def inject_css():
    st.markdown(f"""
    <style>
    /* Fond global */
    .stApp {{
        background-color: {COLORS['dark']};
        color: {COLORS['text']};
    }}
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #0D1117;
        border-right: 1px solid {COLORS['border']};
    }}
    /* KPI cards */
    .kpi-card {{
        background: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 18px 22px;
        text-align: center;
        margin: 4px;
    }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        margin: 6px 0;
    }}
    .kpi-label {{
        font-size: 0.82rem;
        color: #8B949E;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }}
    .kpi-delta {{
        font-size: 0.78rem;
        margin-top: 4px;
    }}
    /* Section headers */
    .section-title {{
        font-size: 1.3rem;
        font-weight: 700;
        color: {COLORS['accent1']};
        border-bottom: 2px solid {COLORS['primary']};
        padding-bottom: 6px;
        margin-bottom: 16px;
    }}
    /* Alert message */
    .alert-info {{
        background: #1C2128;
        border-left: 4px solid {COLORS['warning']};
        padding: 12px 16px;
        border-radius: 4px;
        color: {COLORS['warning']};
        margin: 8px 0;
    }}
    /* Badge */
    .badge {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    .badge-green {{ background:#0F3D2E; color:{COLORS['success']}; }}
    .badge-red   {{ background:#3D1A1A; color:{COLORS['danger']};  }}
    /* Login */
    .login-box {{
        max-width: 420px;
        margin: 8vh auto;
        background: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 40px 36px;
    }}
    .login-title {{
        text-align: center;
        font-size: 1.6rem;
        font-weight: 700;
        color: {COLORS['accent1']};
        margin-bottom: 6px;
    }}
    .login-subtitle {{
        text-align: center;
        font-size: 0.88rem;
        color: #8B949E;
        margin-bottom: 28px;
    }}
    /* Metric row */
    div[data-testid="metric-container"] {{
        background: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 12px;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# 1.  AUTHENTIFICATION
# ═════════════════════════════════════════════════════════════════════════════
VALID_USER = "youssef.finops"
VALID_PASS = "FinOps@2026"


def show_login():
    """Affiche le formulaire de connexion et gère l'authentification."""
    inject_css()
    st.markdown("""
    <div class="login-box">
      <div class="login-title">💹 FinOps Dashboard</div>
      <div class="login-subtitle">Monitoring Fintech · Haute Disponibilité</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            st.markdown("### 🔐 Connexion sécurisée")
            username = st.text_input("Identifiant", placeholder="youssef.finops")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••••")
            submitted = st.form_submit_button("Se connecter", use_container_width=True)

            if submitted:
                if username == VALID_USER and password == VALID_PASS:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ Identifiant ou mot de passe incorrect.")


# ═════════════════════════════════════════════════════════════════════════════
# 2.  CHARGEMENT & NETTOYAGE DES DONNÉES
# ═════════════════════════════════════════════════════════════════════════════
CSV_PATH = "Youssef_Khounnati_Dashboard_FinOps_Fintech_Monitoring.csv"


@st.cache_data(show_spinner="⏳ Chargement des données…")
def load_and_clean(path: str) -> tuple[pd.DataFrame, dict]:
    """
    Charge le CSV et applique un pipeline de nettoyage complet en mémoire.
    Retourne : (df_clean, rapport_qualite)
    Le fichier CSV original n'est JAMAIS modifié.
    """
    # ── Lecture ──────────────────────────────────────────────────────────────
    df_raw = pd.read_csv(path, encoding="utf-8-sig")
    rapport = {
        "lignes_initiales":    len(df_raw),
        "colonnes_initiales":  len(df_raw.columns),
        "doublons_supprimes":  0,
        "nan_traites":         0,
        "outliers_detectes":   0,
        "colonnes_converties": [],
    }

    df = df_raw.copy()

    # ── Doublons ─────────────────────────────────────────────────────────────
    nb_dup = df.duplicated().sum()
    df = df.drop_duplicates()
    rapport["doublons_supprimes"] = int(nb_dup)

    # ── Conversion datetime ───────────────────────────────────────────────────
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    rapport["colonnes_converties"].append("timestamp → datetime")

    # ── Valeurs manquantes ────────────────────────────────────────────────────
    nan_total_before = df.isnull().sum().sum()
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else "Inconnu")
    rapport["nan_traites"] = int(nan_total_before)

    # ── Outliers (IQR) – détection uniquement, pas de suppression ─────────────
    outlier_count = 0
    for col in ["latence_p95_ms", "latence_p99_ms", "cout_total_usd", "error_rate_pct"]:
        if col in df.columns:
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            mask = (df[col] < q1 - 3 * iqr) | (df[col] > q3 + 3 * iqr)
            outlier_count += mask.sum()
    rapport["outliers_detectes"] = int(outlier_count)

    # ── Colonnes dérivées ──────────────────────────────────────────────────────
    df["date"]    = df["timestamp"].dt.date
    df["month"]   = df["timestamp"].dt.to_period("M").astype(str)
    df["week"]    = df["timestamp"].dt.to_period("W").astype(str)
    df["hour"]    = df["timestamp"].dt.hour
    df["sla_ok"]  = df["sla_respecte"].astype(bool)

    # ── Garantie types ────────────────────────────────────────────────────────
    df["nb_incidents"] = df["nb_incidents"].astype(int)

    rapport["lignes_finales"] = len(df)
    return df, rapport


# ═════════════════════════════════════════════════════════════════════════════
# 3.  SIDEBAR – FILTRES DYNAMIQUES
# ═════════════════════════════════════════════════════════════════════════════
def build_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """Construit la sidebar de filtres et retourne le DataFrame filtré."""
    st.sidebar.image(
        "https://img.icons8.com/fluency/96/cloud-computing.png", width=56
    )
    st.sidebar.markdown("## 💹 FinOps · Filtres")
    st.sidebar.markdown("---")

    # Période
    st.sidebar.markdown("### 📅 Période")
    min_date = df["timestamp"].min().date()
    max_date = df["timestamp"].max().date()
    date_range = st.sidebar.date_input(
        "Plage de dates",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Cloud Provider
    st.sidebar.markdown("### ☁️ Fournisseur Cloud")
    providers = sorted(df["cloud_provider"].dropna().unique().tolist())
    sel_providers = st.sidebar.multiselect(
        "Cloud Provider", providers, default=providers,
        help="Filtrer par fournisseur cloud"
    )

    # Service
    st.sidebar.markdown("### ⚙️ Service")
    services = sorted(df["service"].dropna().unique().tolist())
    sel_services = st.sidebar.multiselect(
        "Service", services, default=services
    )

    # Environnement
    st.sidebar.markdown("### 🏗️ Environnement")
    envs = sorted(df["environment"].dropna().unique().tolist())
    sel_envs = st.sidebar.multiselect(
        "Environnement", envs, default=envs
    )

    # Région
    st.sidebar.markdown("### 🌍 Région")
    regions = sorted(df["region_cloud"].dropna().unique().tolist())
    sel_regions = st.sidebar.multiselect(
        "Région", regions, default=regions
    )

    # Mode traitement
    st.sidebar.markdown("### 🔄 Mode de traitement")
    modes = sorted(df["mode_traitement"].dropna().unique().tolist())
    sel_modes = st.sidebar.multiselect(
        "Mode", modes, default=modes
    )

    # SLA
    st.sidebar.markdown("### ✅ Conformité SLA")
    sla_filter = st.sidebar.radio(
        "SLA Respecté", ["Tous", "Oui", "Non"], index=0, horizontal=True
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("💡 Les filtres s'appliquent à toutes les sections.")

    # ── Application des filtres ───────────────────────────────────────────────
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_d, end_d = date_range
        mask = (
            (df["timestamp"].dt.date >= start_d)
            & (df["timestamp"].dt.date <= end_d)
        )
    else:
        mask = pd.Series(True, index=df.index)

    df_f = df[mask].copy()
    if sel_providers:
        df_f = df_f[df_f["cloud_provider"].isin(sel_providers)]
    if sel_services:
        df_f = df_f[df_f["service"].isin(sel_services)]
    if sel_envs:
        df_f = df_f[df_f["environment"].isin(sel_envs)]
    if sel_regions:
        df_f = df_f[df_f["region_cloud"].isin(sel_regions)]
    if sel_modes:
        df_f = df_f[df_f["mode_traitement"].isin(sel_modes)]
    if sla_filter == "Oui":
        df_f = df_f[df_f["sla_ok"] == True]
    elif sla_filter == "Non":
        df_f = df_f[df_f["sla_ok"] == False]

    return df_f


# ═════════════════════════════════════════════════════════════════════════════
# 4.  SECTION – VUE GLOBALE (KPI CARDS)
# ═════════════════════════════════════════════════════════════════════════════
def kpi_card(label: str, value: str, icon: str, color: str, delta: str = ""):
    """Génère une carte KPI HTML."""
    delta_html = f'<div class="kpi-delta" style="color:{color};">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{icon} {label}</div>
      <div class="kpi-value" style="color:{color};">{value}</div>
      {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_vue_globale(df: pd.DataFrame):
    """Vue globale : KPI cards principales."""
    st.markdown('<div class="section-title">📊 Vue Globale — KPI Essentiels</div>',
                unsafe_allow_html=True)

    # Calcul KPI
    cout_total    = df["cout_total_usd"].sum()
    uptime_moy    = df["uptime_pct"].mean()
    lat_p95_moy   = df["latence_p95_ms"].mean()
    lat_p99_moy   = df["latence_p99_ms"].mean()
    error_rate    = df["error_rate_pct"].mean()
    nb_incidents  = df["nb_incidents"].sum()
    mttr_moy      = df["mttr_minutes"].mean()
    sla_rate      = df["sla_ok"].mean() * 100
    nb_rows       = len(df)

    # Couleurs adaptatives
    c_uptime   = COLORS["success"]  if uptime_moy >= 99.5 else (COLORS["warning"] if uptime_moy >= 98 else COLORS["danger"])
    c_error    = COLORS["success"]  if error_rate <= 1     else (COLORS["warning"] if error_rate <= 3   else COLORS["danger"])
    c_sla      = COLORS["success"]  if sla_rate >= 80      else COLORS["danger"]

    # Rangée 1
    cols = st.columns(4)
    with cols[0]:
        kpi_card("Coût Cloud Total",    f"${cout_total:,.0f}",     "💰", COLORS["accent1"], f"{nb_rows:,} enregistrements")
    with cols[1]:
        kpi_card("Uptime Moyen",        f"{uptime_moy:.2f}%",      "⬆️",  c_uptime,  "Disponibilité globale")
    with cols[2]:
        kpi_card("Latence p95",         f"{lat_p95_moy:.0f} ms",   "⚡",  COLORS["accent3"], f"p99: {lat_p99_moy:.0f} ms")
    with cols[3]:
        kpi_card("Error Rate Moyen",    f"{error_rate:.2f}%",      "🚨",  c_error,   "Taux d'erreurs")

    st.markdown("<br>", unsafe_allow_html=True)

    # Rangée 2
    cols2 = st.columns(4)
    with cols2[0]:
        kpi_card("Nombre d'Incidents",  f"{nb_incidents:,}",       "🔥",  COLORS["accent4"], "Total incidents")
    with cols2[1]:
        kpi_card("MTTR Moyen",          f"{mttr_moy:.1f} min",     "🔧",  COLORS["warning"],  "Mean Time To Resolution")
    with cols2[2]:
        kpi_card("Conformité SLA",      f"{sla_rate:.1f}%",        "✅",  c_sla,      f"{df['sla_ok'].sum():,} / {nb_rows:,}")
    with cols2[3]:
        cout_par_service = df.groupby("service")["cout_total_usd"].sum().idxmax()
        kpi_card("Service + Coûteux",   cout_par_service,           "🏆",  COLORS["accent1"], "Par coût total")

    st.markdown("<br>", unsafe_allow_html=True)

    # Mini-résumé bar
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=uptime_moy,
            title={"text": "Uptime Global (%)", "font": {"color": COLORS["text"]}},
            gauge={
                "axis": {"range": [95, 100], "tickcolor": COLORS["text"]},
                "bar": {"color": c_uptime},
                "steps": [
                    {"range": [95, 98], "color": "#3D1A1A"},
                    {"range": [98, 99.5], "color": "#3D2B00"},
                    {"range": [99.5, 100], "color": "#0F3D2E"},
                ],
                "threshold": {"line": {"color": COLORS["danger"], "width": 3},
                              "thickness": 0.8, "value": 99.5},
            },
            number={"suffix": "%", "font": {"color": COLORS["text"]}},
        ))
        fig_gauge.update_layout(
            height=240, paper_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"],
            margin=dict(t=40, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_b:
        fig_gauge2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=error_rate,
            title={"text": "Error Rate Moyen (%)", "font": {"color": COLORS["text"]}},
            gauge={
                "axis": {"range": [0, 10], "tickcolor": COLORS["text"]},
                "bar": {"color": c_error},
                "steps": [
                    {"range": [0, 1],  "color": "#0F3D2E"},
                    {"range": [1, 3],  "color": "#3D2B00"},
                    {"range": [3, 10], "color": "#3D1A1A"},
                ],
            },
            number={"suffix": "%", "font": {"color": COLORS["text"]}},
        ))
        fig_gauge2.update_layout(
            height=240, paper_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"],
            margin=dict(t=40, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_gauge2, use_container_width=True)

    with col_c:
        # Distribution SLA par environnement
        sla_env = df.groupby("environment")["sla_ok"].mean().reset_index()
        sla_env["sla_pct"] = sla_env["sla_ok"] * 100
        fig_sla = px.bar(
            sla_env, x="environment", y="sla_pct",
            color="sla_pct",
            color_continuous_scale=["#DB4437", "#F4B400", "#0F9D58"],
            range_color=[0, 100],
            labels={"environment": "Environnement", "sla_pct": "SLA (%)"},
            title="SLA par Environnement (%)",
        )
        fig_sla.update_layout(
            height=240, paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"],
            coloraxis_showscale=False,
            margin=dict(t=40, b=10, l=10, r=10),
        )
        fig_sla.update_traces(marker_line_color=COLORS["border"], marker_line_width=1)
        st.plotly_chart(fig_sla, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# 5.  SECTION – ANALYSE DÉTAILLÉE
# ═════════════════════════════════════════════════════════════════════════════
def section_analyse_detaillee(df: pd.DataFrame):
    """Graphiques analytiques approfondis."""
    st.markdown('<div class="section-title">📈 Analyse Détaillée</div>',
                unsafe_allow_html=True)

    # ── 5.1  Évolution temporelle ─────────────────────────────────────────────
    st.markdown("#### 🕐 Évolution Temporelle des Performances")
    granularity = st.radio(
        "Granularité", ["Journalier", "Hebdomadaire", "Mensuel"],
        horizontal=True, key="gran"
    )
    grp_col = {"Journalier": "date", "Hebdomadaire": "week", "Mensuel": "month"}[granularity]
    ts = (
        df.groupby(grp_col)
        .agg(
            uptime=("uptime_pct", "mean"),
            error_rate=("error_rate_pct", "mean"),
            latence_p95=("latence_p95_ms", "mean"),
            cout=("cout_total_usd", "sum"),
            incidents=("nb_incidents", "sum"),
        )
        .reset_index()
        .rename(columns={grp_col: "periode"})
    )
    ts["periode"] = ts["periode"].astype(str)

    fig_ts = make_subplots(
        rows=2, cols=2, shared_xaxes=False,
        subplot_titles=("Uptime (%)", "Error Rate (%)", "Latence p95 (ms)", "Coût Total ($)"),
        vertical_spacing=0.14, horizontal_spacing=0.08,
    )
    common = dict(x=ts["periode"], mode="lines+markers", line_width=2, marker_size=4)
    fig_ts.add_trace(go.Scatter(**common, y=ts["uptime"],      line_color=COLORS["success"], name="Uptime"),    row=1, col=1)
    fig_ts.add_trace(go.Scatter(**common, y=ts["error_rate"],  line_color=COLORS["danger"],  name="Error Rate"), row=1, col=2)
    fig_ts.add_trace(go.Scatter(**common, y=ts["latence_p95"], line_color=COLORS["warning"], name="Latence p95"), row=2, col=1)
    fig_ts.add_trace(go.Scatter(**common, y=ts["cout"],        line_color=COLORS["accent1"], name="Coût",
                                fill="tozeroy", fillcolor="rgba(26,115,232,0.08)"), row=2, col=2)
    fig_ts.update_layout(
        height=480, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["text"], showlegend=False,
        margin=dict(t=50, b=20),
    )
    for ann in fig_ts.layout.annotations:
        ann.font.color = COLORS["accent1"]
    fig_ts.update_xaxes(gridcolor=COLORS["border"], tickfont_color="#8B949E")
    fig_ts.update_yaxes(gridcolor=COLORS["border"], tickfont_color="#8B949E")
    st.plotly_chart(fig_ts, use_container_width=True)

    st.markdown("---")

    # ── 5.2  Top 10 services par coût ─────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏆 Top Services par Coût Total")
        top_svc = (
            df.groupby("service")["cout_total_usd"]
            .sum()
            .nlargest(10)
            .reset_index()
            .sort_values("cout_total_usd")
        )
        fig_top = px.bar(
            top_svc, x="cout_total_usd", y="service", orientation="h",
            color="cout_total_usd",
            color_continuous_scale=["#1A73E8", "#F4B400", "#DB4437"],
            labels={"cout_total_usd": "Coût ($)", "service": "Service"},
        )
        fig_top.update_layout(
            height=360, paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"],
            coloraxis_showscale=False, showlegend=False,
            margin=dict(t=10, b=10, l=0, r=0),
        )
        fig_top.update_xaxes(gridcolor=COLORS["border"])
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.markdown("#### 📉 Top 10 Incidents par Service")
        top_inc = (
            df.groupby("service")["nb_incidents"]
            .sum()
            .nlargest(10)
            .reset_index()
            .sort_values("nb_incidents")
        )
        fig_inc = px.bar(
            top_inc, x="nb_incidents", y="service", orientation="h",
            color="nb_incidents",
            color_continuous_scale=["#0F9D58", "#F4B400", "#DB4437"],
            labels={"nb_incidents": "Incidents", "service": "Service"},
        )
        fig_inc.update_layout(
            height=360, paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"],
            coloraxis_showscale=False, showlegend=False,
            margin=dict(t=10, b=10, l=0, r=0),
        )
        fig_inc.update_xaxes(gridcolor=COLORS["border"])
        st.plotly_chart(fig_inc, use_container_width=True)

    st.markdown("---")

    # ── 5.3  Comparaison par catégorie ────────────────────────────────────────
    st.markdown("#### 🌐 Comparaison par Fournisseur Cloud & Région")
    col3, col4 = st.columns(2)

    with col3:
        # Donut fournisseur
        prov = df.groupby("cloud_provider")["cout_total_usd"].sum().reset_index()
        fig_donut = px.pie(
            prov, names="cloud_provider", values="cout_total_usd",
            hole=0.5,
            color="cloud_provider",
            color_discrete_map=PROVIDER_COLORS,
            title="Répartition des Coûts par Fournisseur",
        )
        fig_donut.update_traces(textfont_color=COLORS["text"])
        fig_donut.update_layout(
            height=360, paper_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"],
            legend=dict(font_color=COLORS["text"]),
            margin=dict(t=40, b=10),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col4:
        # Grouped bar région × provider
        reg_prov = (
            df.groupby(["region_cloud", "cloud_provider"])["cout_total_usd"]
            .sum()
            .reset_index()
        )
        fig_rprov = px.bar(
            reg_prov, x="region_cloud", y="cout_total_usd",
            color="cloud_provider",
            color_discrete_map=PROVIDER_COLORS,
            barmode="group",
            labels={"region_cloud": "Région", "cout_total_usd": "Coût ($)",
                    "cloud_provider": "Fournisseur"},
            title="Coût par Région & Fournisseur",
        )
        fig_rprov.update_layout(
            height=360, paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"],
            legend=dict(font_color=COLORS["text"]),
            margin=dict(t=40, b=10),
        )
        fig_rprov.update_xaxes(gridcolor=COLORS["border"])
        fig_rprov.update_yaxes(gridcolor=COLORS["border"])
        st.plotly_chart(fig_rprov, use_container_width=True)

    st.markdown("---")

    # ── 5.4  Scatter plot – Coût vs Uptime ────────────────────────────────────
    st.markdown("#### 🔴 Analyse Coût ↔ Rentabilité (Uptime vs Coût)")
    fig_scatter = px.scatter(
        df,
        x="cout_total_usd",
        y="uptime_pct",
        color="cloud_provider",
        size="nb_incidents",
        size_max=20,
        hover_data=["service", "environment", "region_cloud", "error_rate_pct"],
        color_discrete_map=PROVIDER_COLORS,
        labels={
            "cout_total_usd": "Coût Total ($)",
            "uptime_pct":     "Uptime (%)",
            "cloud_provider": "Fournisseur",
        },
        title="Coût vs Uptime — taille = nb incidents",
        opacity=0.75,
    )
    fig_scatter.update_layout(
        height=460, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"],
        legend=dict(font_color=COLORS["text"]),
    )
    fig_scatter.update_xaxes(gridcolor=COLORS["border"])
    fig_scatter.update_yaxes(gridcolor=COLORS["border"])
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # ── 5.5  Heatmap de corrélation ───────────────────────────────────────────
    st.markdown("#### 🧮 Heatmap de Corrélation entre Variables Numériques")
    num_cols_hm = [
        "latence_p95_ms", "latence_p99_ms", "error_rate_pct", "uptime_pct",
        "cpu_pct", "ram_pct", "cout_compute_usd", "cout_storage_usd",
        "cout_network_usd", "nb_incidents", "mttr_minutes", "cout_total_usd",
        "requests_count",
    ]
    corr = df[num_cols_hm].corr().round(2)
    fig_hm = px.imshow(
        corr,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        text_auto=True,
        aspect="auto",
        title="Matrice de Corrélation des Variables Clés",
    )
    fig_hm.update_traces(textfont_size=10)
    fig_hm.update_layout(
        height=560, paper_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["text"],
        coloraxis_colorbar=dict(tickfont_color=COLORS["text"], title_font_color=COLORS["text"]),
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown("---")

    # ── 5.6  Latence par mode de traitement & heure ───────────────────────────
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("#### ⏱️ Latence p95 par Mode de Traitement")
        lat_mode = (
            df.groupby("mode_traitement")[["latence_p95_ms", "latence_p99_ms"]]
            .mean()
            .reset_index()
        )
        fig_lat = go.Figure()
        fig_lat.add_bar(
            x=lat_mode["mode_traitement"], y=lat_mode["latence_p95_ms"],
            name="p95", marker_color=COLORS["accent3"]
        )
        fig_lat.add_bar(
            x=lat_mode["mode_traitement"], y=lat_mode["latence_p99_ms"],
            name="p99", marker_color=COLORS["danger"]
        )
        fig_lat.update_layout(
            barmode="group", height=300, paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"],
            legend=dict(font_color=COLORS["text"]),
            margin=dict(t=10, b=10),
        )
        fig_lat.update_xaxes(gridcolor=COLORS["border"])
        fig_lat.update_yaxes(gridcolor=COLORS["border"])
        st.plotly_chart(fig_lat, use_container_width=True)

    with col6:
        st.markdown("#### 🕐 Heatmap Heure × Jour (Latence p95)")
        df["dayofweek"] = df["timestamp"].dt.day_name()
        heat_df = (
            df.groupby(["dayofweek", "hour"])["latence_p95_ms"]
            .mean()
            .reset_index()
        )
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heat_pivot = heat_df.pivot(index="dayofweek", columns="hour", values="latence_p95_ms")
        heat_pivot = heat_pivot.reindex([d for d in day_order if d in heat_pivot.index])
        fig_htmap = px.imshow(
            heat_pivot,
            color_continuous_scale="YlOrRd",
            labels={"x": "Heure", "y": "Jour", "color": "Latence p95 (ms)"},
        )
        fig_htmap.update_layout(
            height=300, paper_bgcolor="rgba(0,0,0,0)",
            font_color=COLORS["text"],
            coloraxis_colorbar=dict(tickfont_color=COLORS["text"]),
            margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig_htmap, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# 6.  SECTION – QUALITÉ DES DONNÉES
# ═════════════════════════════════════════════════════════════════════════════
def section_qualite(df_raw_shape: tuple, rapport: dict, df: pd.DataFrame):
    """Résumé de la qualité des données."""
    st.markdown('<div class="section-title">🧹 Qualité des Données</div>',
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Lignes brutes",     f"{rapport['lignes_initiales']:,}")
    with col2:
        st.metric("Lignes après nettoyage", f"{rapport['lignes_finales']:,}",
                  delta=f"-{rapport['doublons_supprimes']} doublons")
    with col3:
        st.metric("Valeurs manquantes traitées", f"{rapport['nan_traites']:,}")
    with col4:
        st.metric("Outliers détectés (IQR×3)", f"{rapport['outliers_detectes']:,}")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 📋 Valeurs Manquantes par Colonne")
        missing = df.isnull().sum().reset_index()
        missing.columns = ["Colonne", "Manquantes"]
        missing = missing[missing["Manquantes"] > 0]
        if missing.empty:
            st.success("✅ Aucune valeur manquante après nettoyage !")
        else:
            fig_miss = px.bar(missing, x="Colonne", y="Manquantes",
                              color_discrete_sequence=[COLORS["warning"]])
            fig_miss.update_layout(
                height=280, paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"]
            )
            st.plotly_chart(fig_miss, use_container_width=True)

    with col_b:
        st.markdown("#### 📊 Distribution des Types de Colonnes")
        dtypes_count = df.dtypes.astype(str).value_counts().reset_index()
        dtypes_count.columns = ["Type", "Count"]
        fig_dt = px.pie(
            dtypes_count, names="Type", values="Count",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4,
        )
        fig_dt.update_layout(
            height=280, paper_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"],
            legend=dict(font_color=COLORS["text"])
        )
        st.plotly_chart(fig_dt, use_container_width=True)

    st.markdown("---")

    # Statistiques descriptives
    st.markdown("#### 📐 Statistiques Descriptives")
    num_cols = [
        "latence_p95_ms", "latence_p99_ms", "error_rate_pct", "uptime_pct",
        "cout_total_usd", "nb_incidents", "mttr_minutes", "cpu_pct", "ram_pct"
    ]
    desc = df[num_cols].describe().round(2).T
    desc.index.name = "Métrique"
    st.dataframe(desc, use_container_width=True)
        desc.style.background_gradient(cmap="Blues", axis=1).format("{:.2f}"),
        use_container_width=True
    )

    # Box plots outliers
    st.markdown("#### 📦 Détection d'Outliers (Box Plots)")
    sel_col = st.selectbox(
        "Choisir une variable", num_cols, index=num_cols.index("cout_total_usd")
    )
    fig_box = px.box(
        df, x="cloud_provider", y=sel_col,
        color="cloud_provider", color_discrete_map=PROVIDER_COLORS,
        points="outliers",
        labels={"cloud_provider": "Fournisseur"},
        title=f"Distribution de {sel_col} par Fournisseur",
    )
    fig_box.update_layout(
        height=380, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font_color=COLORS["text"],
        showlegend=False,
    )
    fig_box.update_xaxes(gridcolor=COLORS["border"])
    fig_box.update_yaxes(gridcolor=COLORS["border"])
    st.plotly_chart(fig_box, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# 7.  SECTION – TABLEAU DÉTAILLÉ + EXPORT
# ═════════════════════════════════════════════════════════════════════════════
def section_tableau(df: pd.DataFrame):
    """Tableau filtrable avec export CSV."""
    st.markdown('<div class="section-title">📋 Tableau Détaillé & Export</div>',
                unsafe_allow_html=True)

    st.markdown(f"**{len(df):,} enregistrements** correspondant aux filtres actifs.")

    # Colonnes à afficher
    display_cols = [
        "metric_id", "timestamp", "cloud_provider", "service",
        "environment", "region_cloud", "mode_traitement",
        "uptime_pct", "latence_p95_ms", "latence_p99_ms",
        "error_rate_pct", "nb_incidents", "mttr_minutes",
        "cout_total_usd", "sla_respecte",
    ]
    display_cols = [c for c in display_cols if c in df.columns]

    st.dataframe(
        df[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=420,
    )

    # Export CSV
    csv_bytes = df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Télécharger les données filtrées (.csv)",
        data=csv_bytes,
        file_name="finops_filtered_export.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ═════════════════════════════════════════════════════════════════════════════
# 8.  SECTION – CONCLUSION & RECOMMANDATIONS
# ═════════════════════════════════════════════════════════════════════════════
def section_conclusion(df: pd.DataFrame):
    """Recommandations métier générées automatiquement à partir des KPI."""
    st.markdown('<div class="section-title">💡 Conclusion & Recommandations Stratégiques</div>',
                unsafe_allow_html=True)

    # KPI de synthèse
    uptime_moy   = df["uptime_pct"].mean()
    error_rate   = df["error_rate_pct"].mean()
    sla_rate     = df["sla_ok"].mean() * 100
    mttr_moy     = df["mttr_minutes"].mean()
    lat_p99      = df["latence_p99_ms"].mean()
    cout_total   = df["cout_total_usd"].sum()

    prov_top = df.groupby("cloud_provider")["cout_total_usd"].sum().idxmax()
    svc_inc  = df.groupby("service")["nb_incidents"].sum().idxmax()
    svc_lat  = df.groupby("service")["latence_p99_ms"].mean().idxmax()

    recs = []

    # Uptime
    if uptime_moy < 99.5:
        recs.append(("🔴 Uptime Insuffisant",
                     f"L'uptime moyen est de **{uptime_moy:.2f}%**, en dessous du seuil SLA de 99.5%. "
                     "Renforcer la redondance des instances critiques et activer l'auto-scaling."))
    else:
        recs.append(("🟢 Uptime Satisfaisant",
                     f"L'uptime moyen de **{uptime_moy:.2f}%** est conforme aux objectifs. "
                     "Maintenir les pratiques actuelles de surveillance et d'alerting."))

    # Error rate
    if error_rate > 3:
        recs.append(("🔴 Taux d'Erreurs Élevé",
                     f"Le taux d'erreurs de **{error_rate:.2f}%** dépasse le seuil critique (3%). "
                     f"Investiguer en priorité le service **{svc_lat}** (latence p99 la plus élevée)."))
    elif error_rate > 1:
        recs.append(("🟡 Taux d'Erreurs Modéré",
                     f"Le taux d'erreurs de **{error_rate:.2f}%** est dans une zone de vigilance. "
                     "Mettre en place des circuit-breakers pour limiter l'impact des services dégradés."))
    else:
        recs.append(("🟢 Error Rate Maîtrisé",
                     f"Avec un taux d'erreurs de **{error_rate:.2f}%**, la plateforme est stable. "
                     "Continuer à monitorer les pics horaires identifiés dans la heatmap."))

    # SLA
    if sla_rate < 70:
        recs.append(("🔴 Conformité SLA Critique",
                     f"Seulement **{sla_rate:.1f}%** des SLA sont respectés. "
                     "Réviser les engagements contractuels ou accélérer les plans de remédiation."))
    elif sla_rate < 85:
        recs.append(("🟡 SLA à Améliorer",
                     f"Le taux de conformité SLA (**{sla_rate:.1f}%**) nécessite des actions ciblées. "
                     "Prioriser les services en échec SLA les plus fréquents."))

    # MTTR
    if mttr_moy > 60:
        recs.append(("⚠️ MTTR Trop Élevé",
                     f"Le MTTR moyen de **{mttr_moy:.0f} minutes** est trop long pour un contexte fintech. "
                     "Automatiser les runbooks d'incident et renforcer les playbooks on-call."))

    # Latence
    if lat_p99 > 500:
        recs.append(("⚠️ Latence p99 Critique",
                     f"La latence p99 moyenne (**{lat_p99:.0f} ms**) est élevée. "
                     f"Optimiser le service **{svc_lat}** et envisager du caching distribué (Redis/Memcached)."))

    # Coûts
    recs.append(("💰 Optimisation des Coûts",
                 f"Le fournisseur **{prov_top}** représente la plus grande part du budget cloud. "
                 "Analyser les reserved instances et les savings plans pour réduire les coûts de 15-25%. "
                 f"Coût total filtré : **${cout_total:,.0f} USD**."))

    recs.append(("🔧 Service Prioritaire",
                 f"Le service **{svc_inc}** accumule le plus d'incidents. "
                 "Un audit de code + revue d'architecture est recommandé en priorité."))

    # Affichage
    for title, text in recs:
        color = "#3D1A1A" if "🔴" in title else ("#3D2B00" if "🟡" in title or "⚠️" in title else "#0F3D2E")
        border = COLORS["danger"] if "🔴" in title else (COLORS["warning"] if "🟡" in title or "⚠️" in title else COLORS["success"])
        st.markdown(f"""
        <div style="background:{color}; border-left:4px solid {border};
                    padding:14px 18px; border-radius:6px; margin:10px 0;">
          <strong style="color:{border};">{title}</strong><br>
          <span style="color:{COLORS['text']}; font-size:0.9rem;">{text}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("📌 Ce rapport est généré automatiquement à partir des données filtrées. "
            "Pour une analyse approfondie, consultez les sections Analyse Détaillée et Qualité des Données.")


# ═════════════════════════════════════════════════════════════════════════════
# 9.  POINT D'ENTRÉE PRINCIPAL
# ═════════════════════════════════════════════════════════════════════════════
def main():
    inject_css()

    # ── Gestion de session ────────────────────────────────────────────────────
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        show_login()
        return

    # ── Chargement des données ────────────────────────────────────────────────
    try:
        df, rapport = load_and_clean(CSV_PATH)
    except FileNotFoundError:
        st.error(f"❌ Fichier CSV introuvable : `{CSV_PATH}`\n\n"
                 "Assurez-vous que le fichier est dans le même répertoire que `app.py`.")
        return

    # ── Header ────────────────────────────────────────────────────────────────
    col_logo, col_title, col_logout = st.columns([1, 10, 2])
    with col_logo:
        st.markdown("# 💹")
    with col_title:
        st.markdown(
            "<h1 style='color:#58A6FF; margin:0; padding:0;'>"
            "FinOps Dashboard — Fintech Monitoring</h1>"
            "<p style='color:#8B949E; margin:0;'>Haute Disponibilité · Infrastructures Asynchrones · 2026</p>",
            unsafe_allow_html=True,
        )
    with col_logout:
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

    st.markdown("---")

    # ── Filtres sidebar ───────────────────────────────────────────────────────
    df_filtered = build_sidebar(df)

    # ── Alerte si aucun résultat ──────────────────────────────────────────────
    if df_filtered.empty:
        st.markdown("""
        <div class="alert-info">
          ⚠️ <strong>Aucun résultat</strong> ne correspond à la combinaison de filtres sélectionnée.<br>
          Veuillez ajuster les filtres dans la barre latérale pour afficher les données.
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Navigation par onglets ────────────────────────────────────────────────
    tabs = st.tabs([
        "📊 Vue Globale",
        "📈 Analyse Détaillée",
        "🧹 Qualité des Données",
        "📋 Tableau & Export",
        "💡 Conclusion",
    ])

    with tabs[0]:
        section_vue_globale(df_filtered)

    with tabs[1]:
        section_analyse_detaillee(df_filtered)

    with tabs[2]:
        section_qualite(df.shape, rapport, df_filtered)

    with tabs[3]:
        section_tableau(df_filtered)

    with tabs[4]:
        section_conclusion(df_filtered)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#8B949E; font-size:0.8rem;'>"
        "💹 FinOps Dashboard v1.0 · Youssef Khounnati · Formation Data Visualisation · Prof: TAOUSSI Jamal"
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
