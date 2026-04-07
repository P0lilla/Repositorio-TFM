import pandas as pd
import os

# Loading initial parameters
current_path = os.path.dirname(__file__)
raw_file_path = (
    current_path[:-4] + "Data/Raw-data/clave-país-región-continente.txt")
clean_file_path = (
    current_path[:-4] + "Data/clave-país-region-continente-limpia.csv")


df = pd.read_csv(raw_file_path, sep = '\t')
for fila in df:
    print(fila)



'''
# Load raw data with UTF-8 encoding
with open(raw_file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    for line in content:
        print(line, "\n")
'''