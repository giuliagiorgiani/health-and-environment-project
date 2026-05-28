import requests
import pandas as pd

# -----------------------------------
# READ TEMPERATURE SENSOR IDS
# -----------------------------------

temp_weights = pd.read_csv(
    r"C:\Users\Mariam Saad\Desktop\hUMAN hEALTH\PYTHON\temperature_weights.csv"
)

sensor_ids = temp_weights["IdSensore"].dropna().astype(int).unique()

sensor_ids = ",".join(
    [f"'{x}'" for x in sensor_ids]
)

# -----------------------------------
# DOWNLOAD DATA
# -----------------------------------

all_data = []

for offset in range(0, 4000000, 500000):

    url = (
        "https://www.dati.lombardia.it/resource/w9wd-u6jh.json?"
        "$where=data >= '2026-01-12T00:00:00' "
        "AND data <= '2026-04-19T23:59:59' "
        f"AND idsensore IN({sensor_ids}) "
        f"&$limit=500000&$offset={offset}"
    )

    response = requests.get(url)

    chunk = pd.DataFrame(response.json())

    print(offset, len(chunk))

    all_data.append(chunk)

    if len(chunk) < 500000:
        break

# -----------------------------------
# MERGE ALL CHUNKS
# -----------------------------------

temp_2026 = pd.concat(all_data, ignore_index=True)

print(len(temp_2026))
print(temp_2026.head())

# -----------------------------------
# SAVE CSV
# -----------------------------------

temp_2026.to_csv(
    "temperature_2026.csv",
    index=False
)

print(temp_2026["data"].min())
print(temp_2026["data"].max())