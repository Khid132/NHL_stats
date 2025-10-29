import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os
from tqdm import tqdm

CSV_DIR = Path("players_csv")
PDF_DIR = Path("goals_distribution")
PDF_DIR.mkdir(exist_ok=True)

YEARS = [2022, 2023, 2024, 2025]
SEASON_COL = 'season'
GOALS_COL = 'I_F_goals'

def zeros_from_csv(csv_path, years, season_col=SEASON_COL, goals_col=GOALS_COL):
    if not csv_path.exists():
        print(f"Fichier introuvable : {csv_path}")
        return None

    df = pd.read_csv(csv_path)
    if df.empty:
        return None

    list_list_zeros = []

    for year in years:
        filtered = df[df[season_col].isin([year])]
        list_zeros = []
        list_goal = []

        if not filtered.empty:
            list_goal = filtered[goals_col].astype(float).tolist()[::-1]

        for index, goal in enumerate(list_goal):
            if goal != 0:
                counter = 0
                next_index = index + 1
                while next_index < len(list_goal) and list_goal[next_index] == 0:
                    counter += 1
                    next_index += 1
                list_zeros.append(counter)

        if list_zeros:
            list_zeros.pop()
        if list_zeros:
            list_list_zeros.append(list_zeros)

    return list_list_zeros

def figure_from_csv(csv_path, years, output_dir=PDF_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    player_name = csv_path.stem
    list_list_zeros = zeros_from_csv(csv_path, years)
    if list_list_zeros is None:
        print(f"Aucun résultat pour {player_name}")
        return

    n_years = len(years)
    fig, axs = plt.subplots(1, n_years, figsize=(5 * n_years, 5))
    if n_years == 1:
        axs = [axs]

    for i, year in enumerate(years):
        per_year_res = zeros_from_csv(csv_path, [year])
        if per_year_res is None:
            axs[i].text(0.5, 0.5, "No data", ha='center')
            axs[i].set_title(f"Année {year}")
            continue

        all_zeros = [z for sub in per_year_res for z in sub]
        occurrences = [all_zeros.count(k) for k in range(21)]
        axs[i].bar(range(21), occurrences)
        axs[i].set_xlabel('Nombre de zéros')
        axs[i].set_ylabel('Occurrences')
        axs[i].set_title(f"Année {year}")
        for j, value in enumerate(occurrences):
            if value > 0:
                axs[i].text(j, value + 0.1, str(value), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(output_dir / f"{player_name}.pdf", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Graphique sauvegardé : {player_name}.pdf")

# Exécution
if __name__ == "__main__":
    csv_files = list(CSV_DIR.glob("*.csv"))
    for file in tqdm(csv_files, desc="Génération PDFs"):
        try:
            figure_from_csv(file, YEARS)
        except Exception as e:
            print(f"❌ Erreur avec {file.stem} : {e}")
