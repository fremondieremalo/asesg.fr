import requests
import pandas as pd
import json
import os
from io import StringIO

# L'URL de la poule D3
URL_FFF = "https://epreuves.fff.fr/competition/engagement/436831-seniors-departemental-3/phase/1/3/classement"

def get_classement():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        r = requests.get(URL_FFF, headers=headers)
        r.raise_for_status()

        # On cherche le tableau contenant "Pts"
        dfs = pd.read_html(StringIO(r.text), match="Pts")
        
        if not dfs:
            print("Aucun tableau trouvé.")
            return []

        df = dfs[0]

        # --- C'EST ICI QUE LA MAGIE OPÈRE ---
        
        # 1. On met tous les noms de colonnes en minuscules pour éviter les erreurs
        df.columns = [str(c).lower().strip() for c in df.columns]

        # 2. Dictionnaire de traduction (Ce qu'on reçoit -> Ce qu'on veut)
        mapping = {
            "unnamed: 0": "pos",   # "unnamed: 0" devient "pos"
            "pl": "pos",
            "rang": "pos",
            "equipe": "equipe",
            "club": "equipe",
            "pts": "pts",
            "points": "pts",
            "j.": "joues",         # "j." devient "joues"
            "jo": "joues",
            "dif": "dif",
            "diff": "dif"
        }

        # 3. On applique le renommage
        df = df.rename(columns=mapping)

        # 5. On ne garde que les colonnes utiles pour le JSON
        colonnes_a_garder = ["pos", "equipe", "pts", "joues"]
        # On filtre pour ne garder que celles qui existent vraiment
        cols_finales = [c for c in colonnes_a_garder if c in df.columns]
        df = df[cols_finales]

        # Nettoyage du nom de l'équipe (enlève les espaces inutiles)
        df['equipe'] = df['equipe'].astype(str).str.strip()
        
        return df.to_dict(orient="records")

    except Exception as e:
        print(f"Erreur lors du scraping : {e}")
        return []

if __name__ == "__main__":
    data = get_classement()
    
    if data:
        os.makedirs("assets/data", exist_ok=True)
        output_path = "assets/data/classement_d3.json"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"✅ JSON corrigé généré avec succès dans : {output_path}")
        # Petit aperçu pour vérifier
        print(json.dumps(data[0], indent=2)) 
    else:
        print("❌ Échec.")