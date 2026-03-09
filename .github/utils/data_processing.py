import pandas as pd

data = pd.read_csv("CoW.csv", sep=";")

data = data.drop(columns=["Column1"])

data["Population"] = pd.to_numeric(data["Population"], errors="coerce")
data["Year"] = pd.to_numeric(data["Year"], errors="coerce")

data = data.dropna(subset=["Year"])

data["Year"] = data["Year"].astype(int)

print(data.info())
