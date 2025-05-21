import streamlit as st
import fitz  # PyMuPDF
import json
import requests

st.set_page_config(page_title="Agent IA - Appel à projet", layout="centered")

st.title("📄 Agent IA - Analyse d'un appel à projet (version gratuite)")

# Chargement du profil associatif
try:
    with open("profil_association.json", "r", encoding="utf-8") as f:
        profil = json.load(f)
except FileNotFoundError:
    st.error("Fichier 'profil_association.json' manquant.")
    st.stop()

# Entrée du token Hugging Face
hf_token = st.text_input("🔑 Token Hugging Face (ne sera pas stocké)", type="password")

# Téléversement du PDF
uploaded_file = st.file_uploader("📎 Téléverser un appel à projet (PDF)", type="pdf")

def lire_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    texte = ""
    for page in doc:
        texte += page.get_text()
    return texte

import time

def interroger_modele_hf(prompt, token):
    API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 503:
            # Modèle en train de se charger
            st.warning("⏳ Le modèle se réveille, réessai dans 10 secondes...")
            time.sleep(10)
            response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            resultat = response.json()
            if isinstance(resultat, list) and "generated_text" in resultat[0]:
                return resultat[0]["generated_text"]
            else:
                return "⚠️ Réponse inattendue du modèle."
        else:
            return f"❌ Erreur Hugging Face : code {response.status_code}"

    except Exception as e:
        return f"❌ Erreur système : {str(e)}"


if uploaded_file and hf_token:
    texte_pdf = lire_pdf(uploaded_file)

    with st.spinner("🔍 Analyse en cours..."):
       prompt = f"""
    Tu es un assistant expert en rédaction d'appels à projets associatifs.

    Voici un appel à projet :
    -------------------------
    {texte_pdf}

    Voici le profil de l'association :
    -------------------------
    {json.dumps(profil, indent=2)}

    Ta tâche : 
    Propose une **réponse structurée** à cet appel à projet au nom de l'association. Ne fais **aucune analyse**, ne donne pas d'avis, ne fais pas de résumé.

    Contenu attendu :
    - Titre du projet
    - Objectifs du projet
    - Public visé
    - Activités prévues
    - Partenaires éventuels
    - Budget estimé (si possible)
    - Résultats attendus

    Rédige de façon professionnelle, claire et concise.
"""



resultat = interroger_modele_hf(prompt, hf_token)
st.subheader("📌 Résultat de l'analyse")
st.markdown(resultat)
