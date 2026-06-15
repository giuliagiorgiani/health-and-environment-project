import requests
import pandas as pd
# --------------------------------------------------
# USER SETTINGS
# --------------------------------------------------
#
# To download a different pollutant or year:
#
# 1. Change the weights file:
#    O3   -> o3_weights.csv
#    PM10 -> pm10_weights.csv
#
# 2. Change the API dataset URL:
#    O3   -> g2hp-ar79
#    PM10 -> nicp-bhqi
#
# 3. Change the date range:
#    Example:
#    2025 -> 2024-12-29 to 2025-05-24
#    2024 -> 2023-12-26 to 2024-05-22
#
# 4. Change the output file name:
#    o3_2025.csv
#    pm10_2025.csv
#    etc.
#
# 5. Change the dataframe name:
#    o3_2025
#    pm10_2025
#    etc.
#
# --------------------------------------------------
# o3 sensor IDs
o3_weights = pd.read_csv("o3_weights.csv")

sensor_ids = o3_weights["idSensore"].unique()

sensor_ids = ",".join(
    [f"'{x}'" for x in sensor_ids]
)

# download data
all_data = []

for offset in range(0, 2000000, 500000):

    url = (
        "https://www.dati.lombardia.it/resource/g2hp-ar79.json?"
        "$where=data >= '2024-12-29T00:00:00' "
        "AND data <= '2025-05-24T23:59:59' "
        f"AND idsensore IN({sensor_ids}) "
        f"&$limit=500000&$offset={offset}"
    )
#nicp-bhqi for recent data
    response = requests.get(url)

    chunk = pd.DataFrame(response.json())

    print(offset, len(chunk))

    all_data.append(chunk)

    if len(chunk) < 500000:
        break

o3_2025 = pd.concat(all_data, ignore_index=True)

print(len(o3_2025))
print(o3_2025.head())
o3_2025.to_csv(
    "o3_2025.csv",
    index=False
)
print(o3_2025["data"].min())
print(o3_2025["data"].max())