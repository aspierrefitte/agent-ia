import streamlit as st
import requests
import json
import PyPDF2

API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

def lire_pdf(fichier_pdf):
    reader = PyPDF2.PdfReader(fichier_pdf)
    texte = ""
    for page in reader.pages:
        texte += page.extract_text()
    return texte

def interroger_modele_hf(prompt, token):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {"temperature": 0.7, "max_new_tokens": 800},
    }
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        output = response.json()
        if isinstance(output, list) and "generated_text" in output[0]:
            return output[0]["generated_text"]
        else:
            return "❌ Format de réponse inattendu."
    else:
        return f"❌ Erreur Hugging Face : code {response.status_code}"

st.set_page_config(page_title="🧠 Agent IA pour Appels à Projets", layout="centered")
st.title("🏓 Agent IA pour Répondre à un Appel à Projet")

hf_token = st.text_input("🔑 Clé Hugging Face", type="password")
github_url = st.text_input("🌐 URL brute GitHub du profil JSON", value="https://raw.githubusercontent.com/aspierrefitte/agent-ia/main/profil_association.json")
uploaded_file = st.file_uploader("📄 Charger un appel à projet (PDF)", type=["pdf"])
idee = st.text_area("💡 Optionnel : une idée de projet à proposer ? (facultatif)", height=150)

if st.button("🚀 Générer la réponse") and uploaded_file and hf_token and github_url:
    try:
        # Télécharger le profil JSON depuis GitHub
        r = requests.get(github_url)
        r.raise_for_status()
        profil = r.json()

        texte_pdf = lire_pdf(uploaded_file)

        try:
            prompt = f"""
            Tu es un assistant expert en rédaction d'appels à projets associatifs.

            Voici un appel à projet :
            -------------------------
            {texte_pdf}

            Voici le profil de l'association :
            -------------------------
            {json.dumps(profil, indent=2)}

            {"Voici une idée à intégrer : " + idee if idee else ""}

            Ta tâche : 
            Rédige une **proposition unique et complète** pour répondre à cet appel à projet au nom de l'association.

            La proposition doit contenir, clairement structurés :
            - Titre du projet
            - Objectifs du projet
            - Public visé
            - Activités prévues
            - Partenaires éventuels
            - Budget estimé (si possible)
            - Résultats attendus

            Ne donne aucune autre information, analyse, résumé, ou conseil.

            Rédige de façon professionnelle, claire, concise, et directement utilisable dans une réponse à l'appel à projet.
            """
        except Exception as e:
            st.error(f"Erreur lors de la création du prompt : {e}")

        with st.spinner("✍️ Génération de la réponse..."):
            resultat = interroger_modele_hf(prompt, hf_token)

        st.subheader("📄 Proposition de projet générée")
        st.markdown(resultat)

    except Exception as e:
        st.error(f"Erreur : {str(e)}")
