import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os

# --- Configurazioni ---
# Modifica con le variabili del tuo 'Final Model' (Full o Reduced)
final_features = [
    'pm10_mean', 'o3_lag1', 'temp_lag1',
    'urban_pct', 'forest_pct',
    'elderly_pct', 'child_pct', 'female_pct'
]

# --- 1. Caricamento Dati ---
print("Caricamento del dataset...")
try:
    df = pd.read_csv('model_dataset.csv')
except FileNotFoundError:
    print("Errore: model_dataset.csv non trovato. Esegui prima lo Step 1.")
    exit()

# Assicuriamoci che 'Anno' e 'population' ci siano
required_cols = final_features + ['Anno', 'SindromiResp_Tot', 'population']
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Colonna mancante nel dataset: {col}")

# --- 2. Split Temporale ---
print("Suddivisione in Training Set (2022-2024) e Test Set (2025-2026)...")
train_mask = df['Anno'].isin([2022, 2023, 2024])
test_mask = df['Anno'].isin([2025, 2026])

df_train = df[train_mask].dropna(subset=required_cols)
df_test = df[test_mask].dropna(subset=required_cols)

print(f"Dimensioni Training Set: {len(df_train)} osservazioni")
print(f"Dimensioni Test Set: {len(df_test)} osservazioni")

# Preparazione variabili (con costanti per statsmodels)
X_train = sm.add_constant(df_train[final_features])
y_train = df_train['SindromiResp_Tot']
offset_train = np.log(df_train['population'])

X_test = sm.add_constant(df_test[final_features])
y_test = df_test['SindromiResp_Tot']
offset_test = np.log(df_test['population'])

# --- 3. Fit del Modello sul Training Set ---
print("\nAddestramento del modello di Poisson sul Training Set...")
poisson_model = sm.GLM(
    y_train,
    X_train,
    family=sm.families.Poisson(),
    offset=offset_train
)
train_results = poisson_model.fit()

# --- 4. Predizioni sul Test Set ---
print("Generazione delle predizioni sul Test Set...")
# statsmodels GLM predict() richiede sia esog che l'offset se usato nel fit originale
y_pred = train_results.predict(exog=X_test, offset=offset_test)

# --- 5. Calcolo Metriche di Errore ---
print("\n--- Risultati Validazione Out-of-Sample ---")

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)

# Calcolo di un R2 di base (spesso nei modelli di conteggio si usano pseudo-R2,
# ma qui ci interessa la correlazione lineare tra predetto e osservato)
r_squared = np.corrcoef(y_test, y_pred)[0, 1]**2

print(f"RMSE (Root Mean Square Error): {rmse:.4f}")
print(f"MAE (Mean Absolute Error): {mae:.4f}")
print(f"R-quadro (correlazione al quadrato): {r_squared:.4f}")

# Esportazione risultati
results_df = pd.DataFrame({
    'Metric': ['RMSE', 'MAE', 'R-Squared'],
    'Value': [rmse, mae, r_squared]
})
results_df.to_csv('temporal_validation_metrics.csv', index=False)
print("\nMetriche salvate in 'temporal_validation_metrics.csv'.")
