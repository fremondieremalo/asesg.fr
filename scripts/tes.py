import requests
from bs4 import BeautifulSoup
import json
import os
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURATION ---
# ⚠️ REMETS TA CLÉ ICI POUR TESTER EN LOCAL (mais ne l'envoie pas sur GitHub)
GEMINI_API_KEY = "AIzaSyBqZ_XgPqtRd8hB1ffkDYzBmisiKejpg8M" 

# Sur GitHub, utilise :
# GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# URL Agenda (District)
URL = "https://foot79.fff.fr/competitions?tab=agenda&id=436830&phase=1&poule=2&type=ch"

def ask_gemini():
    if not GEMINI_API_KEY:
        print("❌ Erreur : Pas de clé API Gemini trouvée.")
        return None

    # --- ÉTAPE 1 : ON TÉLÉCHARGE LE VRAI CALENDRIER (C'est obligatoire !) ---
    print(f"1. Téléchargement de la page : {URL}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    clean_text = ""
    try:
        r = requests.get(URL, headers=headers)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, 'html.parser')
        # On extrait tout le texte de la page
        text_content = soup.get_text(separator="\n")
        
        # On nettoie pour ne garder que les lignes utiles (dates, équipes)
        lines = [line.strip() for line in text_content.splitlines() if line.strip()]
        # On garde les 500 premières lignes (suffisant pour le prochain match)
        clean_text = "\n".join(lines[:500])

    except Exception as e:
        print(f"❌ Erreur téléchargement : {e}")
        return None

    # --- ÉTAPE 2 : ON PRÉPARE L'INTELLIGENCE ARTIFICIELLE ---
    print("2. Analyse par Gemini (Modèle 2.0 Flash)...")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')

        # On récupère la date d'aujourd'hui pour aider l'IA
        aujourdhui = datetime.now().strftime("%d/%m/%Y")

        # LE PROMPT MAGIQUE : On lui donne le texte qu'on vient de télécharger
        prompt = f"""
        NOUS SOMMES LE : {aujourdhui}
        
        TACHE : Trouve le prochain match de chaque équipe sénior du club de football : Echire St Gelais AS.
        La date doit être supérieure ou égale à celle d'aujourd'hui. Fais des recherches sur le site de la Ligue de Football Nouvelle-Aquitaine et sur le site du District Football des Deux-Sèvres.
        
        Règles :
        1. Ignore les matchs passés (ceux avant {aujourdhui}).
        2. Si tu vois un score (ex: 3-0), c'est passé -> Ignore.
        3. Si tu vois une heure (ex: 15H00) sans score -> C'est le match que je veux.
        
        Réponds UNIQUEMENT avec ce JSON pour chaque équipe, je veux ces détails dans 1 seul JSON :
        {{
            "date": "JJ/MM/AAAA",
            "heure": "HHhMM",
            "equipe_domicile": "Nom Exact 1",
            "equipe_exterieur": "Nom Exact 2",
            "lieu": "Stade Municipal" (si ECHIRE/ASESG à domicile) ou "Extérieur"
        }}
        """

        response = model.generate_content(prompt)
        
        # Nettoyage
        text_rep = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text_rep)
        return data

    except Exception as e:
        print(f"❌ Erreur Gemini : {e}")
        return None

if __name__ == "__main__":
    prochain_match_info = ask_gemini()
    
    os.makedirs("assets/data", exist_ok=True)
    fichier = "assets/data/prochains_matchs_seniors.json"
    
    # Structure finale
    final_data = {
        "prochain": prochain_match_info
    }

    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
        
    print(f"💾 Résultat sauvegardé : {final_data}")