
from pathlib import Path
import pandas as pd
import requests
import io
from tqdm import tqdm

# Dossiers relatifs
DATA_DIR = Path("data")
CSV_DIR = Path("players_csv")
CSV_DIR.mkdir(exist_ok=True)

# Charger les joueurs
df_players = pd.read_excel(DATA_DIR / "skaters.xlsx")
player_ids = df_players['playerId'].dropna().astype(int).tolist()
player_names = df_players['name'].dropna().tolist()

# Fonction pour filtrer les situations
def filter_df(df):
    return df[df["situation"] == "all"]

# Télécharger et sauvegarder les CSV des joueurs
for idx, ids in enumerate(tqdm(player_ids, desc="Téléchargement + filtrage")):
    url = f"http://moneypuck.com/moneypuck/playerData/careers/gameByGame/regular/skaters/{ids}.csv"
    response = requests.get(url)
    df = pd.read_csv(io.BytesIO(response.content))

    if "situation" in df.columns:
        df = filter_df(df)

    save_path = CSV_DIR / f"{player_names[idx]}.csv"
    df.to_csv(save_path, index=False)
