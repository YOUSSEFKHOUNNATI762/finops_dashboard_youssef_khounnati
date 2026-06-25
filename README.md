# 💹 FinOps Dashboard — Fintech Monitoring

> **Dashboard de Haute Disponibilité et de Monitoring FinOps pour infrastructures Fintech Asynchrones**

---

## 📌 Informations du Projet

| Champ            | Valeur                                                                 |
|------------------|------------------------------------------------------------------------|
| **Étudiant**     | Youssef Khounnati                                                      |
| **Professeur**   | TAOUSSI Jamal                                                          |
| **Formation**    | Data Visualisation — Projet Dashboard Python                           |
| **Version**      | 1.0 — 2026                                                             |
| **Données**      | `Youssef_Khounnati_Dashboard_FinOps_Fintech_Monitoring.csv` (3225 lignes) |

---

## 🚀 Démarrage Rapide

### 1. Pré-requis

- Python **3.10+** installé
- pip à jour : `pip install --upgrade pip`

### 2. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 3. Placement du fichier CSV

Placer le fichier CSV **dans le même dossier que `app.py`** :

```
dashboard/
├── app.py
├── requirements.txt
├── README.md
└── Youssef_Khounnati_Dashboard_FinOps_Fintech_Monitoring.csv
```

### 4. Lancement de l'application

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur à l'adresse :  
`http://localhost:8501`

---

## 🔐 Authentification

| Champ          | Valeur          |
|----------------|-----------------|
| **Login**      | `youssef.finops` |
| **Mot de passe** | `FinOps@2026`  |

---

## 🗂️ Architecture du Projet

```
app.py
│
├── inject_css()                  → Styles CSS personnalisés (thème sombre)
├── show_login()                  → Page de login avec validation
├── load_and_clean()              → Pipeline de nettoyage (cached)
│   ├── Lecture CSV (utf-8-sig)
│   ├── Suppression des doublons
│   ├── Conversion datetime
│   ├── Traitement valeurs manquantes (médiane/mode)
│   ├── Détection outliers IQR×3
│   └── Création colonnes dérivées (date, month, week, hour)
│
├── build_sidebar()               → Filtres dynamiques interconnectés
│   ├── Plage de dates
│   ├── Fournisseur Cloud
│   ├── Service
│   ├── Environnement
│   ├── Région
│   ├── Mode de traitement
│   └── Conformité SLA
│
├── section_vue_globale()         → KPI Cards + jauges
├── section_analyse_detaillee()   → 8 graphiques analytiques
├── section_qualite()             → Rapport qualité données
├── section_tableau()             → Table filtrable + export CSV
└── section_conclusion()          → Recommandations auto-générées
```

---

## 📊 Fonctionnalités du Dashboard

### 🔒 Page Login
- Formulaire sécurisé avec validation identifiant + mot de passe
- Session Streamlit persistante
- Bouton de déconnexion accessible depuis toutes les pages

### 📊 Vue Globale — KPI Essentiels
| KPI | Description |
|-----|-------------|
| Coût Cloud Total | Somme de `cout_total_usd` |
| Uptime Moyen | Moyenne de `uptime_pct` avec jauge visuelle |
| Latence p95 / p99 | Moyennes des percentiles de latence |
| Error Rate Moyen | Taux d'erreurs moyen |
| Nombre d'Incidents | Total des incidents |
| MTTR Moyen | Mean Time To Resolution en minutes |
| Conformité SLA | Pourcentage de SLA respectés |
| Service le plus coûteux | Service avec le coût total maximum |

### 📈 Analyse Détaillée
1. **Évolution temporelle** (journalier / hebdomadaire / mensuel) : 4 métriques clés
2. **Top 10 services par coût** : Bar chart horizontal
3. **Top 10 services par incidents** : Bar chart horizontal
4. **Répartition coûts par fournisseur** : Donut chart
5. **Coût par région & fournisseur** : Grouped bar chart
6. **Scatter plot Coût vs Uptime** : Taille = nb incidents
7. **Heatmap de corrélation** : 13 variables numériques
8. **Latence p95/p99 par mode** : Grouped bar chart
9. **Heatmap heure × jour** : Patterns temporels de latence

### 🧹 Qualité des Données
- Métriques de nettoyage (doublons, NaN, outliers)
- Graphique valeurs manquantes
- Distribution des types de colonnes
- Statistiques descriptives avec gradient
- Box plots avec détection d'outliers par fournisseur

### 📋 Tableau Détaillé & Export
- Table interactive avec toutes les colonnes filtrées
- Pagination et tri natifs Streamlit
- Bouton d'export CSV des données filtrées

### 💡 Conclusion & Recommandations
Analyse automatique basée sur les seuils métier :
- 🟢 Uptime ≥ 99.5% / 🟡 ≥ 98% / 🔴 < 98%
- 🟢 Error Rate ≤ 1% / 🟡 ≤ 3% / 🔴 > 3%
- Alertes MTTR, latence p99, SLA
- Recommandations d'optimisation de coûts
- Identification du service prioritaire

---

## 🛠️ Stack Technique

| Bibliothèque | Usage |
|--------------|-------|
| `streamlit`  | Interface web interactive |
| `pandas`     | Manipulation et nettoyage des données |
| `numpy`      | Calculs numériques |
| `plotly`     | Visualisations interactives (Express + Graph Objects) |

---

## 📁 Données — Colonnes du CSV

| Colonne | Type | Description |
|---------|------|-------------|
| `metric_id` | str | Identifiant unique |
| `timestamp` | datetime | Horodatage de la mesure |
| `cloud_provider` | str | AWS / GCP / Azure / Private Cloud |
| `service` | str | Nom du microservice |
| `environment` | str | prod / staging / dev |
| `region_cloud` | str | Région de déploiement |
| `requests_count` | float | Nombre de requêtes |
| `latence_p95_ms` | float | Latence 95e percentile (ms) |
| `latence_p99_ms` | float | Latence 99e percentile (ms) |
| `error_rate_pct` | float | Taux d'erreurs (%) |
| `uptime_pct` | float | Disponibilité (%) |
| `cpu_pct` | float | Utilisation CPU (%) |
| `ram_pct` | float | Utilisation RAM (%) |
| `cout_compute_usd` | float | Coût calcul ($) |
| `cout_storage_usd` | float | Coût stockage ($) |
| `cout_network_usd` | float | Coût réseau ($) |
| `nb_incidents` | int | Nombre d'incidents |
| `mttr_minutes` | float | MTTR en minutes |
| `sla_respecte` | bool | Conformité SLA |
| `mode_traitement` | str | asynchrone / batch / streaming / synchrone |
| `cout_total_usd` | float | Coût total ($) |

---

## ⚠️ Notes Importantes

1. **Le fichier CSV original n'est jamais modifié** — tout le nettoyage est effectué en mémoire.
2. **Si aucun résultat** après filtrage, un message d'alerte s'affiche.
3. **Cache Streamlit** : les données sont chargées une seule fois grâce à `@st.cache_data`.

---

*Formation Data Visualisation · Prof: TAOUSSI Jamal · 2026*
