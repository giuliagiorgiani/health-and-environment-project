import requests
import pandas as pd

# -----------------------------------
# READ TEMPERATURE SENSOR IDS
# -----------------------------------

temp_weights = pd.read_csv(
    "temperature_weights.csv"
)

sensor_ids = temp_weights["IdSensore"].dropna().astype(int).unique()

sensor_ids = ",".join(
    [f"'{x}'" for x in sensor_ids]
)

# -----------------------------------
# DOWNLOAD DATA
# -----------------------------------
# Modify the dates below to match the
# study period of interest.
#
# Example:
# 2022:
# data >= '2021-12-28T00:00:00'
# data <= '2022-05-25T23:59:59'

all_data = []

for offset in range(0, 5000000, 500000):

    url = (
        "https://www.dati.lombardia.it/resource/w9wd-u6jh.json?"
        "$where=data >= '2021-12-28T00:00:00' "
        "AND data <= '2022-05-25T23:59:59' "
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

temp_2022 = pd.concat(all_data, ignore_index=True)

print(len(temp_2022))
print(temp_2022.head())

# -----------------------------------
# SAVE CSV
# -----------------------------------
# -----------------------------------
# SAVE CSV
# -----------------------------------
#
# Update filename to match the year
# being downloaded.
temp_2022.to_csv(
    "temperature_2022.csv",
    index=False
)

print(temp_2022["data"].min())
print(temp_2022["data"].max())
