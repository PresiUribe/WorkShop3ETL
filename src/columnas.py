import pandas as pd
for year in [2015, 2016, 2017, 2018, 2019]:
    df = pd.read_csv(f'data/raw/{year}.csv')
    print(f"\n=== {year}.csv ===")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")