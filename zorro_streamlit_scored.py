import pandas as pd
import streamlit as st
import io

st.set_page_config(page_title="Zorro BI - Match avec Score", layout="wide")
st.title("Zorro BI – Moteur de Recommandation Scoré")

st.sidebar.header("📁 Fichiers d'entrée")

# Upload fichiers utilisateurs et catalogue
file_users = st.sidebar.file_uploader("Données utilisateurs (CSV, Excel ou JSON)", type=['csv', 'xlsx', 'xls', 'json'])
file_recos = st.sidebar.file_uploader("Catalogue de recommandations (CSV ou Excel)", type=['csv', 'xlsx', 'xls'])

def read_file(f):
    if f is None:
        return None
    if f.name.endswith('.csv'):
        return pd.read_csv(f)
    elif f.name.endswith('.json'):
        return pd.read_json(f)
    else:
        return pd.read_excel(f)

df_users = read_file(file_users)
df_recos = read_file(file_recos)

# --- Nettoyage des doublons dès l'import
if df_users is not None:
    df_users = df_users.drop_duplicates()
if df_recos is not None:
    df_recos = df_recos.drop_duplicates()

def gravite_str(score):
    if score <= 0.3:
        return "faible"
    elif score <= 0.7:
        return "modéré"
    else:
        return "élevé"

def get_user_emotions(user):
    # Récupère les émotions > 0.5
    emotions = []
    # user peut être une série Pandas : on accède par [] pas .get
    for e in ["tristesse","honte","colère","peur","angoisse","dégoût"]:
        val = user.get(f"emotion_{e}", 0) if isinstance(user, dict) else user[f"emotion_{e}"] if f"emotion_{e}" in user else 0
        if val > 0.5:
            emotions.append(e)
    return emotions

def match_score(user, reco):
    score = 0
    # Type harcèlement exact = +4
    if str(user['type_harcelement']).strip().lower() == str(reco['type_harcelement']).strip().lower():
        score += 4

    # Contexte exact = +3
    if str(user['contexte']).strip().lower() == str(reco['contexte']).strip().lower():
        score += 3

    # Gravité match = +1
    grav_user = gravite_str(user['gravité_estimée'])
    if grav_user == reco['gravité']:
        score += 1

    # Âge dans le range = +1
    try:
        age_min, age_max = map(int, str(reco['rang_age']).split('-'))
        if age_min <= int(user['âge_estimé']) <= age_max:
            score += 1
    except:
        pass

    # Matching émotion : +2 par émotion du user présente dans reco
    user_emotions = get_user_emotions(user)
    if str(reco['emotion']) in user_emotions:
        score += 2

    return score

if (df_users is not None) and (df_recos is not None):
    # Préparer colonnes émotion si absentes
    for col in ["emotion_tristesse","emotion_honte","emotion_colère","emotion_peur","emotion_angoisse","emotion_dégoût"]:
        if col not in df_users.columns:
            df_users[col] = 0

    # Sélection utilisateur
    user_id = st.selectbox("Choisir un utilisateur :", df_users["utilisateur_id"].unique())
    selected_user = df_users[df_users["utilisateur_id"] == user_id].iloc[0]
    st.subheader("Profil sélectionné")
    st.json(selected_user.to_dict())

    # Score pour chaque reco (on travaille sur une COPIE pour ne pas polluer df_recos global)
    df_recos_scored = df_recos.copy()
    df_recos_scored["score"] = df_recos_scored.apply(lambda r: match_score(selected_user, r), axis=1)
    df_scored = df_recos_scored[df_recos_scored["score"] > 6].sort_values(by="score", ascending=False)

    st.markdown("### Recommandations trouvées")
    if df_scored.empty:
        st.warning("Aucune recommandation exacte. Voici des suggestions globales.")
        st.dataframe(df_recos_scored.head(5))
    else:
        st.success(f"{len(df_scored)} recommandations trouvées avec score.")
        st.dataframe(df_scored[["recommandation_id", "type_harcelement", "contexte", "emotion", "gravité", "rang_age", "lien", "contact", "lieu", "score"]])

    # Export recommandations utilisateur sélectionné
    st.markdown("---")
    if st.button("💾 Exporter recommandations (utilisateur sélectionné)"):
        to_export = df_scored
        file_buffer = io.BytesIO()
        to_export.to_excel(file_buffer, index=False)
        st.download_button(
            label="Télécharger en Excel",
            data=file_buffer.getvalue(),
            file_name=f"recommandations_{user_id}.xlsx"
        )
        # CSV
        st.download_button(
            label="Télécharger en CSV",
            data=to_export.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"recommandations_{user_id}.csv"
        )
        # JSON
        st.download_button(
            label="Télécharger en JSON",
            data=to_export.to_json(orient="records", force_ascii=False, indent=2),
            file_name=f"recommandations_{user_id}.json"
        )
        st.success("Export réalisé avec succès.")

    # --- Export global
    st.markdown("## 📦 Export global pour tous les utilisateurs")
    if st.button("Exporter toutes les recommandations scorées pour tous les utilisateurs"):
        rows = []
        # TRAVAILLER SUR UNE COPIE NON MODIFIÉE
        df_recos_global = df_recos.copy()
        for idx_user, user in df_users.iterrows():
            for idx_reco, reco in df_recos_global.iterrows():
                score = match_score(user, reco)
                row = {
                    "utilisateur_id": user["utilisateur_id"],
                    "recommandation_id": reco["recommandation_id"],
                    "score": score,
                    "type_harcelement_user": user["type_harcelement"],
                    "type_harcelement_reco": reco["type_harcelement"],
                    "contexte_user": user["contexte"],
                    "contexte_reco": reco["contexte"],
                    "gravité_user": gravite_str(user['gravité_estimée']),
                    "gravité_reco": reco["gravité"],
                    "age_user": user["âge_estimé"],
                    "rang_age_reco": reco["rang_age"],
                    "emotion_reco": reco["emotion"],
                    "emotions_user": get_user_emotions(user),
                    "lien": reco["lien"],
                    "contact": reco["contact"],
                    "lieu": reco["lieu"],
                }
                rows.append(row)
        df_global = pd.DataFrame(rows)

        # CSV
        csv_buffer = io.StringIO()
        df_global.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        csv_bytes = csv_buffer.getvalue().encode('utf-8-sig')
        st.download_button(
            label="📥 Télécharger le fichier global (CSV)",
            data=csv_bytes,
            file_name="scoring_recommendations_global.csv",
            mime="text/csv"
        )

        # Excel
        excel_buffer = io.BytesIO()
        df_global.to_excel(excel_buffer, index=False)
        st.download_button(
            label="📥 Télécharger le fichier global (Excel)",
            data=excel_buffer.getvalue(),
            file_name="scoring_recommendations_global.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # JSON
        st.download_button(
            label="📥 Télécharger le fichier global (JSON)",
            data=df_global.to_json(orient="records", force_ascii=False, indent=2),
            file_name="scoring_recommendations_global.json",
            mime="application/json"
        )

else:
    st.info("🡐 Merci d'importer les deux fichiers pour démarrer.")
