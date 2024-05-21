import pandas as pd


# vessel = pd.read_csv('data/csvs/vessels_type_30.csv')
vessel = pd.read_csv('data/ais-gis-3/vessels_type_70_or_80.csv')
names = [f"./data/ais-gis-3/output_{i}.csv" for i in range(1, 13)]

new_column_names = {'id': 'MMSI'}

vessel = vessel.rename(columns=new_column_names)
cols = vessel.columns.tolist()
cols.remove("MMSI")
cols.remove("vessel_type")
dfs = [pd.read_csv(name) for name in names]


total = pd.concat(dfs, axis=0)
print(vessel.__len__())

filtered_df = pd.merge(total, vessel, on=['MMSI'], how='left')

filtered_df.drop(cols, axis=1, inplace=True)

filtered_df.to_csv('data/ais-gis-3/vessel-ais-gis-3.csv', index=False)