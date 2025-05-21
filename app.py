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

def interroger_modele_hf(prompt, token):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]['generated_text']
    else:
        return f"❌ Erreur : {response.status_code} - {response.json()}"

if uploaded_file and hf_token:
    texte_pdf = lire_pdf(uploaded_file)

    with st.spinner("🔍 Analyse en cours..."):
        prompt = f"""
Tu es un expert des appels à projets pour les associations sportives.

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

        resultat = interroger_modele_hf(prompt, hf_token)
        st.subheader("📌 Résultat de l'analyse")
        st.markdown(resultat)
