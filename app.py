import streamlit as st
import requests
import PyPDF2
import json
import time

st.set_page_config(page_title="Agent IA pour appel à projet", page_icon="📄")

st.title("📄 Agent IA - Rédaction d'appel à projet")
st.write("Déposez un appel à projet (PDF) et le profil de votre association (JSON). L'IA génère une proposition adaptée.")

# Interface utilisateur
hf_token = st.text_input("🔑 Token Hugging Face", type="password")
uploaded_file = st.file_uploader("📎 Appel à projet (PDF)", type="pdf")


# Lire un fichier PDF
def lire_pdf(fichier):
    lecteur = PyPDF2.PdfReader(fichier)
    texte = ""
    for page in lecteur.pages:
        texte += page.extract_text()
    return texte
    
# Chargement du profil associatif
try:
    with open("profil_association.json", "r", encoding="utf-8") as f:
        profil = json.load(f)
except FileNotFoundError:
    st.error("Fichier 'profil_association.json' manquant.")
    st.stop()

# Appeler le modèle Hugging Face
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
            st.warning("⏳ Le modèle se réveille, réessai dans 10 secondes...")
            time.sleep(10)
            response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            resultat = response.json()
            if isinstance(resultat, list):
                return resultat[0].get("generated_text", "⚠️ Réponse vide.")
            else:
                return f"Réponse inattendue : {resultat}"
        else:
            return f"❌ Erreur Hugging Face : code {response.status_code}"

    except Exception as e:
        return f"❌ Erreur système : {str(e)}"

# Nettoyer la réponse IA pour n'afficher que le projet
def extraire_reponse(text):
    index = text.find("Titre du projet")
    if index != -1:
        return text[index:]
    return text

# Traitement principal
if uploaded_file and hf_token :
    texte_pdf = lire_pdf(uploaded_file)

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

    with st.spinner("✍️ Génération de la réponse..."):
        resultat = interroger_modele_hf(prompt, hf_token)
        st.subheader("📄 Proposition de projet générée")
        st.markdown(resultat)
