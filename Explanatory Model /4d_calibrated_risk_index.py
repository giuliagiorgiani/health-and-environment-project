import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import MinMaxScaler

# --- 1. Configurazioni ---
final_features = [
    'pm10_mean', 'o3_lag1', 'temp_lag1',
    'urban_pct', 'forest_pct',
    'elderly_pct', 'child_pct', 'female_pct'
]

print("Caricamento dataset...")
df = pd.read_csv('model_dataset.csv').dropna(subset=final_features + ['SindromiResp_Tot', 'population', 'IdSensore'])

# --- 2. Ricalcolo dei Coefficienti (Training) ---
print("Estrazione dei coefficienti pesati dai dati storici...")
X = sm.add_constant(df[final_features])
y = df['SindromiResp_Tot']
offset = np.log(df['population'])

# Fit del modello per ottenere i beta (i pesi reali)
results = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset).fit()

# I coefficienti stimati (escludiamo la costante per l'indice relativo)
betas = results.params.drop('const')

# --- 3. Calcolo del Rischio Assoluto (Lineare) ---
print("Calcolo dell'Indice di Rischio grezzo...")
# Moltiplichiamo ogni variabile (X) per il suo coefficiente (beta) e sommiamo tutto
# linear_predictor = beta1*X1 + beta2*X2 + ... + betaK*XK
df['linear_predictor'] = df[final_features].dot(betas)

# L'esponenziale del predittore lineare ci dà il "Moltiplicatore di Rischio"
df['risk_multiplier'] = np.exp(df['linear_predictor'])

# --- 4. Normalizzazione (Scala 0 - 100) ---
print("Normalizzazione dell'Indice su scala 0-100...")
scaler = MinMaxScaler(feature_range=(0, 100))
# Reshape necessario per scikit-learn
risk_array = df['risk_multiplier'].values.reshape(-1, 1)
df['risk_index_100'] = scaler.fit_transform(risk_array).round(2)

# --- 5. Salvataggio ed Esportazione ---
columns_to_export = ['IdSensore', 'Anno', 'study_week'] + final_features + ['risk_multiplier', 'risk_index_100']
df_export = df[columns_to_export]

output_file = 'calibrated_risk_index.csv'
df_export.to_csv(output_file, index=False)

print(f"\nOperazione completata con successo!")
print(f"L'indice è stato salvato in '{output_file}'.")
print("\nStatistiche dell'Indice di Rischio (0-100):")
print(df['risk_index_100'].describe())