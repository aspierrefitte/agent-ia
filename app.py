import streamlit as st
import requests
import json
import PyPDF2

# 🔧 URL du modèle Hugging Face (modifiable si tu veux tester un autre modèle)
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

# 📥 Lire le PDF
def lire_pdf(fichier_pdf):
    reader = PyPDF2.PdfReader(fichier_pdf)
    texte = ""
    for page in reader.pages:
        texte += page.extract_text()
    return texte

# 💬 Fonction pour interroger le modèle Hugging Face
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

# 🌐 Interface Streamlit
st.set_page_config(page_title="🧠 Agent IA pour Appels à Projets", layout="centered")
st.title("🏓 Agent IA pour Répondre à un Appel à Projet")

hf_token = st.text_input("🔑 Clé Hugging Face", type="password")

uploaded_file = st.file_uploader("📄 Charger un appel à projet (PDF)", type=["pdf"])
profil_json = st.text_area("🧾 Profil de l'association (JSON)", height=200)

idee = st.text_area("💡 Optionnel : une idée de projet à proposer ? (facultatif)", height=150)

if st.button("🚀 Générer la réponse") and uploaded_file and profil_json and hf_token:
    try:
        texte_pdf = lire_pdf(uploaded_file)
        profil = json.loads(profil_json)

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

    except Exception as e:
        st.error(f"Erreur : {str(e)}")
