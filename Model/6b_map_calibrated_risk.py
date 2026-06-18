import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# --- Configurazioni ---
# Ricordati di avere i file .shp, .shx e .dbf nella stessa cartella!
SHAPEFILE_PATH = 'temperature_voronoi_ats.shp'

print("Caricamento dell'Indice di Rischio Calibrato...")
df_risk = pd.read_csv('calibrated_risk_index.csv')

# --- 1. Aggregazione Spaziale ---
print("Calcolo del Rischio Medio per ogni poligono...")
# Calcoliamo la media dell'indice di rischio per ogni zona (su tutti gli anni/settimane)
df_mean_risk = df_risk.groupby('IdSensore')['risk_index_100'].mean().reset_index()

# --- 2. Unione con le Geometrie ---
print("Caricamento dello shapefile ed esecuzione del merge...")
try:
    gdf = gpd.read_file(SHAPEFILE_PATH)
except FileNotFoundError:
    print(f"ERRORE: Impossibile trovare '{SHAPEFILE_PATH}'.")
    exit()

# Merge dei dati tabellari con le geometrie spaziali
gdf_map = gdf.merge(df_mean_risk, on='IdSensore', how='inner')

if gdf_map.empty:
    print("ERRORE: Nessun IdSensore corrispondente tra lo shapefile e i dati del rischio.")
    exit()

# --- 3. Generazione della Mappa ---
print("Generazione della mappa in corso...")
fig, ax = plt.subplots(1, 1, figsize=(12, 10))

# Creiamo una mappa coropletica (Choropleth) usando una palette dal Giallo (basso) al Rosso scuro (alto)
gdf_map.plot(
    column='risk_index_100',
    cmap='YlOrRd',          # Palette intuitiva per il rischio (Giallo -> Arancio -> Rosso)
    linewidth=0.5,
    edgecolor='black',
    legend=True,
    legend_kwds={
        'label': "Indice di Rischio Medio (0-100)",
        'orientation': "vertical",
        'shrink': 0.7
    },
    ax=ax
)

ax.set_title("Mappa dell'Indice di Rischio Respiratorio Calibrato", fontsize=16, fontweight='bold', pad=15)
ax.axis('off')  # Rimuove le coordinate degli assi per un look più pulito

plt.tight_layout()
output_image = 'Calibrated_Risk_Map.png'
plt.savefig(output_image, dpi=300, bbox_inches='tight')

print(f"\nFinito! Mappa salvata con successo come '{output_image}'.")
