import streamlit as st
import fitz  # PyMuPDF
import json
from openai import OpenAI

st.set_page_config(page_title="Agent IA - Appel à projet", layout="centered")

st.title("📄 Agent IA - Analyse d'un appel à projet")

# Chargement du profil associatif
try:
    with open("profil_association.json", "r", encoding="utf-8") as f:
        profil = json.load(f)
except FileNotFoundError:
    st.error("Fichier 'profil_association.json' manquant. Ajoutez-le au dépôt GitHub.")
    st.stop()

# Entrée de la clé OpenAI
openai_api_key = st.text_input("🔑 Clé API OpenAI (ne sera pas stockée)", type="password")

# Téléversement du fichier PDF
uploaded_file = st.file_uploader("📎 Téléverser un appel à projet (PDF)", type="pdf")

def lire_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    texte = ""
    for page in doc:
        texte += page.get_text()
    return texte

if uploaded_file and openai_api_key:
    texte_pdf = lire_pdf(uploaded_file)

    with st.spinner("🔍 Analyse en cours..."):
        prompt = f"""
Tu es un expert en appels à projets pour les associations sportives.

Voici un appel à projet :
-------------------------
{texte_pdf}

Voici le profil de l'association :
-------------------------
{json.dumps(profil, indent=2)}

Analyse l'appel à projet et :
1. Résume les objectifs, critères d’éligibilité, éléments demandés, dates importantes.
2. Évalue si l'association semble éligible.
3. Propose un plan de réponse en 3 à 5 points.
        """

        try:
            client = OpenAI(api_key=openai_api_key)

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )

            resultat = response.choices[0].message.content
            st.subheader("📌 Résultat de l'analyse")
            st.markdown(resultat)

        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API OpenAI : {str(e)}")
