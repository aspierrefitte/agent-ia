import streamlit as st
import requests
import PyPDF2
import json
import time
import openai

st.set_page_config(page_title="Agent IA pour appel à projet", page_icon="📄")

st.title("📄 Agent IA - Rédaction d'appel à projet")
st.write("Déposez un appel à projet (PDF) et le profil de votre association (JSON). L'IA génère une proposition adaptée.")

# Interface utilisateur
openai_api_key = st.text_input("🔑 Clé API OpenAI", type="password")
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

#briefing de l'ia
idee_projet = st.text_area(
    "💬 Débrief / idée de projet souhaitée",
    placeholder="Par exemple : un programme pour initier les jeunes filles au football dans les quartiers ruraux..."
)


# Appeler le modèle 
def interroger_modele_openai(prompt, openai_api_key):
    openai.api_key = openai_api_key

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # ou "gpt-4" si tu y as accès
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en appels à projets associatifs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Erreur OpenAI : {str(e)}"

# Nettoyer la réponse IA pour n'afficher que le projet
def extraire_reponse(text):
    index = text.find("Titre du projet")
    if index != -1:
        return text[index:]
    return text

# Traitement principal
if uploaded_file and openai_api_key :
    texte_pdf = lire_pdf(uploaded_file)





    prompt = f"""
Tu es un assistant expert en rédaction d'appels à projets associatifs.

Voici un appel à projet :
-------------------------
{texte_pdf}

Voici le profil de l'association :
-------------------------
{json.dumps(profil, indent=2)}


Voici l'idée de projet de l'association (optionnelle mais à suivre si possible) :
-------------------------
{idee_projet}

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
        resultat = interroger_modele_openai(prompt, openai_api_key)
        st.subheader("📄 Proposition de projet générée")
        st.markdown(resultat)
