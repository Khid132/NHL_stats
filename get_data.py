from nhlpy import NHLClient
from pathlib import Path
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import re

def get_player_df(player_id):
    dfs = []

    for season in SEASONS:
        stats = client.stats.player_game_log(
            player_id=player_id,
            season_id=season,
            game_type=GAME_TYPE
        )

        if stats:  
            df_season = pd.DataFrame(stats)
            df_season["season"] = int(season[:4])
            dfs.append(df_season)

    if not dfs:
        return None

    df = pd.concat(dfs, ignore_index=True)

    df["gameDate"] = pd.to_datetime(df["gameDate"])
    df = df.sort_values("gameDate", ascending=False).reset_index(drop=True)

    return df

def process_player(player_id: int, player_name: str) -> None:
    df = get_player_df(player_id)

    if df is None:
        return

    path = CSV_DIR / f"{player_name}.csv"
    df.to_csv(path, index=False)


# Configuration
DATA_DIR = Path("data")
CSV_DIR = Path("players_csv")
CSV_DIR.mkdir(exist_ok=True)

SEASONS = ["20222023", "20232024", "20242025", "20252026"]
GAME_TYPE = 2  
MAX_WORKERS = 8

# NHL Client
client = NHLClient()

# Data Loading
df_players = pd.read_excel(DATA_DIR / "skaters.xlsx")
player_ids = df_players["playerId"].dropna().astype(int).tolist()
player_names = df_players["name"].dropna().tolist()

# Parallel execution 
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [
        executor.submit(process_player, pid, name)
        for pid, name in zip(player_ids, player_names)
    ]

    for _ in tqdm(
        as_completed(futures),
        total=len(futures),
        desc="Téléchargement des joueurs"
    ):
        pass

