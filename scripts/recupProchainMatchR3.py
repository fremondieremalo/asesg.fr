import requests
import pandas as pd
import json
import os
import re
from datetime import datetime
from io import StringIO

# URL du calendrier FFF
URL_CALENDRIER = "https://epreuves.fff.fr/competition/engagement/436830-seniors-departemental-2/phase/1/2/resultats-et-calendrier"

# Nom de ton équipe tel qu'il apparaît sur le site FFF (pour filtrer)
MON_EQUIPE = "ECHIRE"

def parse_french_date(date_str):
    """
    Transforme 'dimanche 05 octobre 2025 - 15:00' en objet datetime
    """
    # Dictionnaire pour traduire les mois français
    mois_fr = {
        "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
        "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12
    }
    
    try:
        # Nettoyage de la chaine (on enlève les espaces en trop)
        date_str = date_str.lower().strip()
        
        # On cherche le format : jour (chiffre) mois (texte) annee (chiffre)
        # Ex: "dimanche 5 octobre 2025"
        parts = date_str.replace('-', ' ').split()
        
        # On cherche où sont les chiffres et le mois
        jour = int([p for p in parts if p.isdigit() and int(p) <= 31][0])
        annee = int([p for p in parts if p.isdigit() and int(p) > 1000][0])
        mois = [m for m in parts if m in mois_fr][0]
        numero_mois = mois_fr[mois]
        
        # On extrait l'heure si elle existe (ex: 15:00)
        heure = 15 # Heure par défaut
        minute = 0
        match_heure = re.search(r'(\d{1,2}):(\d{2})', date_str)
        if match_heure:
            heure = int(match_heure.group(1))
            minute = int(match_heure.group(2))
            
        return datetime(annee, numero_mois, jour, heure, minute)
        
    except Exception as e:
        print(f"Erreur date sur : {date_str} -> {e}")
        return None

def get_next_match():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(URL_CALENDRIER, headers=headers)
        
        # On cherche tous les tableaux (souvent la FFF découpe par journée)
        # Mais sur la page calendrier, c'est souvent un gros tableau
        dfs = pd.read_html(StringIO(r.text))
        
        # On concatène tous les tableaux trouvés (au cas où il y en a plusieurs)
        if not dfs: return None
        df = pd.concat(dfs)

        # Nettoyage des colonnes
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # On renomme pour s'y retrouver
        # Colonnes typiques FFF : 'date', 'domicile', 'score', 'visiteur', 'lieu'
        # Parfois "Date" est la première colonne sans nom
        if 'date' not in df.columns:
            # On suppose que la 1ere est la date, la 2eme domicile, la 4eme visiteur
            df = df.rename(columns={df.columns[0]: 'date', df.columns[1]: 'domicile', df.columns[3]: 'visiteur'})

        # 1. On garde uniquement les matchs de NOTRE équipe
        df = df[df['domicile'].str.contains(MON_EQUIPE, case=False, na=False) | 
                df['visiteur'].str.contains(MON_EQUIPE, case=False, na=False)]

        # 2. On convertit les dates
        df['date_obj'] = df['date'].apply(parse_french_date)
        
        # 3. On enlève les lignes où la date a échoué
        df = df.dropna(subset=['date_obj'])
        
        # 4. On filtre : On veut une date >= Aujourd'hui
        maintenant = datetime.now()
        futur_matches = df[df['date_obj'] >= maintenant].sort_values(by='date_obj')

        if futur_matches.empty:
            return {"error": "Fin de saison"}

        # 5. On prend le TOUT PREMIER match de la liste (le plus proche)
        prochain = futur_matches.iloc[0]
        
        # Formatage propre pour le JSON
        match_info = {
            "date": prochain['date_obj'].strftime("%d/%m/%Y"), # Ex: 12/10/2025
            "heure": prochain['date_obj'].strftime("%Hh%M"),   # Ex: 15h00
            "equipe_domicile": prochain['domicile'].strip(),
            "equipe_exterieur": prochain['visiteur'].strip(),
            "lieu": "Voir FFF" # Parfois dispo dans une colonne 'terrain'
        }
        
        return match_info

    except Exception as e:
        print(f"Erreur globale : {e}")
        return None

if __name__ == "__main__":
    data = get_next_match()
    
    if data:
        os.makedirs("assets/data", exist_ok=True)
        with open("assets/data/prochain_match_r3.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ Prochain match trouvé et sauvegardé !")
        print(data)
    else:
        print("❌ Aucun match trouvé.")