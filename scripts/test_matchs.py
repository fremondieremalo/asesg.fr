import requests
from bs4 import BeautifulSoup
import json
import os
import re

# ON CHANGE L'URL POUR LA VERSION LISIBLE PAR PYTHON
# C'est la page "Résultats et Calendrier" de ton équipe spécifique sur le site vitrine
URL = "https://www.fff.fr/competition/club/515733-echire-st-gelais-as-2/equipe/2025_4873_SEM_5/resultats-et-calendrier.html"

def get_matchs_data():
    print(f"📡 Connexion à : {URL}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        r = requests.get(URL, headers=headers)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Sur ce site, chaque match est dans un bloc "confrontation"
        matchs_blocs = soup.find_all('div', class_='confrontation')
        
        if not matchs_blocs:
            print("❌ Aucun bloc match trouvé. L'URL a peut-être changé.")
            return None

        print(f"📊 Analyse de {len(matchs_blocs)} matchs...")

        matchs_joues = []
        matchs_a_venir = []

        for match in matchs_blocs:
            # --- 1. RECUPERATION DES INFOS ---
            
            # Date (souvent dans un titre H3 juste avant)
            date_bloc = match.find_previous('h3', class_='title_date')
            date_str = date_bloc.get_text(strip=True) if date_bloc else "Date inconnue"
            
            # Heure
            heure_bloc = match.find('span', class_='confrontation__time')
            heure_str = heure_bloc.get_text(strip=True).replace(' - ', '') if heure_bloc else ""
            
            # Équipes
            equipes = match.find_all('span', class_='confrontation__team_name')
            if len(equipes) < 2: continue
            
            domicile = equipes[0].get_text(strip=True)
            exterieur = equipes[1].get_text(strip=True)
            
            # Score (C'est ici qu'on voit si le match est fini)
            score_bloc = match.find('span', class_='confrontation__score_value')
            score = None
            if score_bloc:
                text_score = score_bloc.get_text(strip=True)
                # Si le score contient des chiffres (ex: "3 - 0"), c'est joué
                # Si c'est "-" ou vide, ce n'est pas joué
                if any(char.isdigit() for char in text_score):
                    score = text_score

            # Lieu (Déduction simple pour l'affichage)
            lieu = "Extérieur"
            if "ECHIRE" in domicile.upper() or "ASESG" in domicile.upper():
                lieu = "Stade Municipal"

            match_info = {
                "date": date_str,
                "heure": heure_str,
                "domicile": domicile,
                "exterieur": exterieur,
                "score": score,
                "lieu": lieu
            }

            # --- 2. CLASSEMENT (Passé ou Futur ?) ---
            if score:
                matchs_joues.append(match_info)
            else:
                matchs_a_venir.append(match_info)

        # --- 3. SELECTION DES MEILLEURS CANDIDATS ---
        
        # Le dernier match joué est le dernier de la liste 'joués'
        dernier = matchs_joues[-1] if matchs_joues else None
        
        # Le prochain match est le premier de la liste 'à venir'
        prochain = matchs_a_venir[0] if matchs_a_venir else None

        return {
            "dernier": dernier,
            "prochain": prochain
        }

    except Exception as e:
        print(f"❌ Erreur : {e}")
        return None

if __name__ == "__main__":
    data = get_matchs_data()
    
    os.makedirs("assets/data", exist_ok=True)
    fichier = "assets/data/matchs_d2.json"
    
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"💾 Fichier généré : {fichier}")
    
    if data:
        if data['dernier']:
            print(f"✅ DERNIER : {data['dernier']['domicile']} {data['dernier']['score']} {data['dernier']['exterieur']}")
        else:
            print("⚠️ Pas de dernier match trouvé.")
            
        if data['prochain']:
            print(f"✅ PROCHAIN : {data['prochain']['domicile']} vs {data['prochain']['exterieur']}")
        else:
            print("⚠️ Pas de prochain match trouvé.")