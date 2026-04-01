# Librerías
import pandas as pd
import os

'''
Script to check how many countries are shared between all the files. Works
under the assumption that a country appearing in a file is enought 
(pressumes that all the data for that country in that file is pressent)
'''

# Loading initial parameters
current_path = os.path.dirname(__file__)
clean_data_path = current_path[:-4] + "Data/Clean-data"
iso_path = current_path[:-4] + "Data/countries-ISO-3166.csv"
# Load the ISO 3166-1 reference data and build a dictionary
countries_iso = pd.read_csv(iso_path)
countries_dic = countries_iso.set_index("alpha-3")["name"].to_dict()

# Dictionary to store the sets.
sets_alpha3 = {}

for file in os.listdir(clean_data_path):
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join(clean_data_path, file))
        sets_alpha3[file] = set((df["alpha3"]).dropna())
        print(f"{file}: {len(sets_alpha3[file])} valores únicos")

# Compute intersection
common = set.intersection(*sets_alpha3.values())
total = set.union(*sets_alpha3.values())

output_file = os.path.join(clean_data_path[:-11], "comparacion-cruzada.txt")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Los archivos comparten {len(common)} países.\n")
    for file, countries in sets_alpha3.items():
        f.write(f"\n{file}: {len(countries)} países. ")
        missing = total - countries
        if missing:
            f.write(f"Faltan {len(sorted(missing))} países.\n")
            for c in missing:
                f.write(f"- {c}: {countries_dic[c]}\n")
        else:
            f.write(f"{file}: contiene todos los países.")

