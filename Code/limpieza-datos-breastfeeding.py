# Librerías
import pandas as pd
import os

# Script para limpiar los datos de breastfeeding
current_path = os.path.dirname(__file__)

# Cargamos archivo original
breast_raw = pd.read_csv(os.path.join(
    current_path[:-4], "Data/Raw-data/Risk-factors/Breastfeeding/breastfeeding-all-years.csv"))

# Cargamos archivo con la codificación ISO por país
countries_iso = pd.read_csv(
    os.path.join(ruta_relativa, "countries-ISO-3166.csv"))

# Construir diccionario alpha-3 : country-code
countries_dic = {}
for index, row in countries_iso.iterrows():
    countries_dic[row["alpha-3"]] = row["country-code"]

# Selección de las variables de interés del archivo raw
breast_selected = breast_raw[[
    "INDICATOR:Indicator", "REF_AREA:Geographic area", 
    "TIME_PERIOD:Time period", "OBS_VALUE:Observation Value",
    "LOWER_BOUND:Lower Bound", "UPPER_BOUND:Upper Bound"]]

# Modificamos nombre de columnas para aumentar legibilidad
breast_renamed = breast_selected.rename(columns={
    "INDICATOR:Indicator": "Indicator", 
    "REF_AREA:Geographic area": "alpha3",
    "TIME_PERIOD:Time period": "Time period",
    "OBS_VALUE:Observation Value": "Percentage",
    "LOWER_BOUND:Lower Bound": "CI95_low",
    "UPPER_BOUND:Upper Bound": "CI95_high"})

# Eliminación de motivo recurrente en la variable "Indicator"
breast_renamed["Indicator"] = breast_renamed["Indicator"].str[16:]

# Modificamos la variable alpha3 para dejar únicamente el id. de 3 digitos
breast_renamed["alpha3"] = breast_renamed["alpha3"].str[:3]

# Añadimos una variable para el código del país comparando con el dict ISO
breast_renamed["country-code"] = breast_renamed["alpha3"].map(countries_dic)

# Seleccionamos solo los valores de 2012 o los más cercanos.
# Primero nos quedamos solo con el año, dropeando el mes cuando está presente
breast_renamed["Time period"] = (
    breast_renamed["Time period"].astype(str).str[:4].astype(int))

# Calculamos la distancia a 2012
breast_renamed["dist_2012"] = (breast_renamed["Time period"] - 2012).abs()

# Ordenamos por distancia a 2012
breast_sorted = breast_renamed.sort_values(by=[
    "alpha3", "dist_2012", "Time period"])

# Seleccionamos la primera fila de cada país (que será la más cercana a 2012)
breast_circa_2012 = breast_sorted.groupby("alpha3").first().reset_index()

# Eliminamos la columna auxiliar de distancias
breast_circa_2012 = breast_circa_2012.drop(columns="dist_2012")

print("Registro de valores faltantes: ")
print(breast_circa_2012.isnull().sum())

# Lo guardamos en un nuevo csv
breast_circa_2012.to_csv(os.path.join(
    ruta_relativa, "Breastfeeding/breastfeeding-clean-circa-2012.csv"), 
    index=False)

