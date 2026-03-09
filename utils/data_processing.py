import pandas as pd
import os

# Get directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build path to CSV
csv_path = os.path.join(BASE_DIR, "..", "CoW.csv")

data = pd.read_csv(csv_path, sep=";")

data = data.drop(columns=["Column1"])

data["Population"] = pd.to_numeric(data["Population"], errors="coerce")
data["Year"] = pd.to_numeric(data["Year"], errors="coerce")

data = data.dropna(subset=["Year"])

data["Year"] = data["Year"].astype(int)
