import requests
import pandas as pd

# pm10 sensor IDs
pm10_weights = pd.read_csv("pm10_weights.csv")

sensor_ids = pm10_weights["idSensore"].unique()

sensor_ids = ",".join(
    [f"'{x}'" for x in sensor_ids]
)

# download data
all_data = []

for offset in range(0, 2000000, 500000):

    url = (
        "https://www.dati.lombardia.it/resource/g2hp-ar79.json?"
        "$where=data >= '2022-01-12T00:00:00' "
        "AND data <= '2022-04-19T23:59:59' "
        f"AND idsensore IN({sensor_ids}) "
        f"&$limit=500000&$offset={offset}"
    )

    response = requests.get(url)

    chunk = pd.DataFrame(response.json())

    print(offset, len(chunk))

    all_data.append(chunk)

    if len(chunk) < 500000:
        break

pm10_2022 = pd.concat(all_data, ignore_index=True)

print(len(pm10_2022))
print(pm10_2022.head())
pm10_2022.to_csv(
    "pm10_2022.csv",
    index=False
)