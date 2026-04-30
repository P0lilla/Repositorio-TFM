# Librerías
import pandas as pd
import os

'''
Este archivo tiene como función agrupar todas las variables en un mismo
dataframe con la siguiente estructura:

TIPO DE CANCER X PAIS X SEXO X FACTOR DE RIESGO 1 X ... X FACTOR DE RIESGO N.

1. Primero se cargan todos los archivos como panda dataframes.

2. Luego se eliminan de los dataframes de factores de riesgo los países que no
   aparecen en el dataframe de incidencia de cáncer.

3. Por último se fusionan los valores restantes en un dataframe que se exporta
   como .csv.

Si para un país determinado no se tienen valores de un factor de riesgo, se 
indica como NaN.
'''
# Loading relative folder paths.
current_path = os.path.dirname(__file__)
clean_data_path = os.path.join(current_path[:-4], "Test-data")
temp_output_path = current_path[:-4]

# Dictionary to store the dataframes
dataframes = {}

# Iterating the folder loading the dataframes
for archivo in os.listdir(clean_data_path):
    if archivo.endswith(".csv"):
        print(f"Cargando archivo {archivo}.")
        nombre_df = archivo.replace(".csv", "")
        dataframes[nombre_df] = pd.read_csv(os.path.join(clean_data_path, archivo))

######## Filtering by alpha3 values using cancer-incidence as reference ########

# Selecting cancer-incidence dataframe
df_incidencia = dataframes["cancer-incidence-clean"]

# Extracting alpha3 values
alpha3_validos = set(df_incidencia["alpha3"])

# Filtering the rest of the datasets
for nombre, df in dataframes.items():
    if nombre != "cancer-incidence-clean":
        dataframes[nombre] = df[df["alpha3"].isin(alpha3_validos)]


# Selecting wanted variables from cancer-incidence dataframe
wanted_variables = ['Label', 'sex_dichotomic', 'Crude rate', 'alpha3']
cancer_temporal = dataframes["cancer-incidence-clean"][wanted_variables]

# Removing rows for "Label: All cancers"
cancer_temporal = cancer_temporal[cancer_temporal["Label"] != "All cancers"]

# Updating the dataframe in the original dictionary
dataframes["cancer-incidence-clean"] = cancer_temporal

def merge_datasets(merged_datasets, factor_df, nombre_factor):
    # eliminamos el motivo "-clean" del nombre de la variable.
    nombre_factor = nombre_factor[:-6]

    # Si el factor está codificado por sexo:
    if "sex_dichotomic" in factor_df.columns:
        if "Value2" in factor_df.columns:
            variables_to_merge = factor_df[["alpha3", "Value2", "sex_dichotomic"]].copy()
            variables_to_merge = variables_to_merge.rename(columns={"Value2": nombre_factor})
        else:
            variables_to_merge = factor_df[["alpha3", "Value", "sex_dichotomic"]].copy()
            variables_to_merge = variables_to_merge.rename(columns={"Value": nombre_factor})

        merged = pd.merge(merged_datasets, variables_to_merge, 
                          on=["alpha3", "sex_dichotomic"], how="left")

    # Caso particular de AirPollution, que subdivide por Área de residencia:
    elif (factor_df["Dim1 type"] == "Residence Area Type").any():
        variables_to_merge = factor_df[["alpha3", "Dim1", "Value2"]].copy()
        variables_to_merge = variables_to_merge.rename(columns={"Value2": nombre_factor})
        # Seleccionamos solo las filas con Dim1 = Total
        variables_to_merge = variables_to_merge[variables_to_merge["Dim1"] == "Total"]
        # Eliminamos la variable Dim1
        variables_to_merge = variables_to_merge.drop(columns=["Dim1"])

        merged = pd.merge(merged_datasets, variables_to_merge, 
                          on=["alpha3"], how="left")
    
    # Si no hay codificación por sexo:
    else:
        if "Value2" in factor_df.columns:
            variables_to_merge = factor_df[["alpha3", "Value2"]].copy()
            variables_to_merge = variables_to_merge.rename(columns={"Value2": nombre_factor})
        else:
            variables_to_merge = factor_df[["alpha3", "Value"]].copy()
            variables_to_merge = variables_to_merge.rename(columns={"Value": nombre_factor})

        merged = pd.merge(merged_datasets, variables_to_merge, 
                          on=["alpha3"], how="left")

    return merged

merged_datasets = cancer_temporal.copy()

for nombre, df in dataframes.items():
    if nombre != "cancer-incidence-clean":
        merged_datasets = merge_datasets(merged_datasets, df, nombre)
        

print(merged_datasets.head())
merged_datasets.to_csv(os.path.join(temp_output_path, "test_merge.csv"))


df = merged_datasets.copy()