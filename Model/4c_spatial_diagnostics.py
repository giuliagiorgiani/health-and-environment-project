import pandas as pd
import numpy as np
import geopandas as gpd
import statsmodels.api as sm
import libpysal
from esda.moran import Moran
import matplotlib.pyplot as plt

# --- Configurazioni ---
# Sostituisci con il file geografico che usi nello Step 6
SHAPEFILE_PATH = 'temperature_voronoi_ats.shp'

final_features = [
    'pm10_mean', 'o3_lag1', 'temp_lag1',
    'urban_pct', 'forest_pct',
    'elderly_pct', 'child_pct', 'female_pct'
]

# --- 1. Caricamento e Fit del Modello ---
print("Caricamento dataset e stima del modello sull'intero periodo...")
df = pd.read_csv('model_dataset.csv').dropna(subset=final_features + ['SindromiResp_Tot', 'population', 'IdSensore'])

X = sm.add_constant(df[final_features])
y = df['SindromiResp_Tot']
offset = np.log(df['population'])

# Riestimiamo il modello per estrarre i residui
poisson_model = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset)
results = poisson_model.fit()

# --- 2. Estrazione e Aggregazione dei Residui ---
print("Estrazione dei residui di Pearson...")
# I residui di Pearson sono standardizzati, ideali per la diagnostica
df['resid_pearson'] = results.resid_pearson

# Aggreghiamo i residui mediamente per ogni poligono
gdf_residuals = df.groupby('IdSensore')['resid_pearson'].mean().reset_index()

# --- 3. Unione con le Geometrie Spaziali ---
print("Caricamento geometrie spaziali...")
try:
    gdf_poly = gpd.read_file(SHAPEFILE_PATH)
except FileNotFoundError:
    print(f"ERRORE: Shapefile '{SHAPEFILE_PATH}' non trovato. Modifica SHAPEFILE_PATH nel codice.")
    exit()

# Unione (assicurati che i nomi delle colonne combacino)
gdf = gdf_poly.merge(gdf_residuals, on='IdSensore', how='inner')

if gdf.empty:
    print("ERRORE: Il merge tra shapefile e dataset dei residui è vuoto. Controlla la colonna 'IdSensore'.")
    exit()

# --- 4. Calcolo Indice di Moran ---
print("\nCalcolo della matrice dei pesi spaziali (Queen contiguity)...")
# Crea una matrice di adiacenza (poligoni che condividono un lato o un vertice)
w = libpysal.weights.Queen.from_dataframe(gdf)
w.transform = 'r'  # Normalizzazione per riga

print("Calcolo Indice di Moran Globale...")
moran = Moran(gdf['resid_pearson'], w)

print("\n--- Risultati Diagnostica Spaziale (Moran's I) ---")
print(f"Indice di Moran (I): {moran.I:.4f}")
print(f"P-value (simulazione): {moran.p_sim:.4f}")
print(f"Z-score: {moran.z_sim:.4f}")

# --- 5. Interpretazione Automatica ---
if moran.p_sim < 0.05:
    if moran.I > 0:
        print("\nCONCLUSIONE: Autocorrelazione spaziale POSITIVA significativa.")
        print("I residui simili tendono a raggrupparsi (cluster di errori). Il modello non cattura un fenomeno spaziale locale.")
    else:
        print("\nCONCLUSIONE: Autocorrelazione spaziale NEGATIVA significativa.")
        print("I residui dissimili tendono a raggrupparsi (pattern a scacchiera). Molto raro in epidemiologia.")
else:
    print("\nCONCLUSIONE: Nessuna autocorrelazione spaziale significativa.")
    print("I residui sono distribuiti in modo casuale nello spazio. Il modello ha un ottimo fit spaziale!")

# --- 6. Mappa dei Residui ---
print("\nGenerazione mappa dei residui...")
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
gdf.plot(column='resid_pearson', cmap='coolwarm', legend=True, ax=ax,
         edgecolor='black', linewidth=0.2)
ax.set_title("Residui Medi di Pearson per Poligono", fontsize=14)
ax.axis('off')
plt.savefig('spatial_residuals_map.png', dpi=300, bbox_inches='tight')
print("Mappa salvata come 'spatial_residuals_map.png'.")
