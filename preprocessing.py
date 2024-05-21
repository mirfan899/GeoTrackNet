import pandas as pd


df = pd.read_csv('data/csvs/sept_2023_mar_2024_fishing.csv')
# mean = df.mean()
# df.fillna(mean, inplace=True)
df["SOG"].ffill(inplace=True)
df["COG"].ffill(inplace=True)
df["HEADING"].bfill(inplace=True)
df["HEADING"].ffill(inplace=True)
df["ROT"].bfill(inplace=True)
df["ROT"].ffill(inplace=True)
df["NAV_STT"].ffill(inplace=True)
df.to_csv("data/csvs/clean_sept_2023_mar_2024_fishing.csv", index=False)
print(df.info())
