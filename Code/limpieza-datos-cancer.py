# Librerías
import pandas as pd
import os
from collections import defaultdict


# Loading initial paths
current_folder = os.path.dirname(__file__)
incidence_folder = current_folder[:-4] + "Data/Raw-data/Cancer/incidence"
mortality_folder = current_folder[:-4] + "Data/Raw-data/Cancer/mortality"
clean_data_folder = current_folder[:-4] + "Data/Clean-data"
renamed_folder = current_folder[:-4] + "Data/Raw-data/Cancer/renamed"
iso_path = current_folder[:-4] + "Data/countries-ISO-3166.csv"

def file_name_standaricer(folder, eliminate_motive=False):
    '''
    Checks if there is two files per country. It also can remove a motive
    present in the name of some of the files.
    '''
    # Counter to store number of files for each countrie.
    countries = defaultdict(int)

    for file_name in os.listdir(folder):
        # Remove .csv motive
        new_name = file_name[:-4]
        # Elimination of main motive
        new_name = new_name.replace("absolute-numbers-", "")
        # Rearrangement of the final filename
        parts = new_name.split("-", 5)
        country_name = parts[5]
        final_name = (
            parts[5] + "-" + parts[0] + "-" + parts[1] + "-" +
            parts[2] + "-" + parts[3] + "-" + parts[4] + ".csv")
        
        # Update de counter
        countries[country_name] += 1

        if eliminate_motive:
            os.rename((os.path.join(folder, file_name)), 
                      (os.path.join(renamed_folder, final_name)))
            
    # Print the countries with more or less than two files.
    ok = True
    for key, value in countries.items():
        if value != 2:
            print(f"Hay {value} archivos para el país {key}")
            ok = False
    if ok:
        print("Todos los países tienen dos archivos.")

    print(f"Se han contabilizado {len(countries)} paises")

def merge_files(folder):
    '''
    Merges all the files from the selected folder (incidence or mortality).
    '''
    file_list = []

    for file in os.listdir(folder):
        if file.endswith(".csv"):
            file_path = os.path.join(folder, file)
            df = pd.read_csv(file_path)
            file_list.append(df)

    # Merge dataframes
    df_final = pd.concat(file_list, ignore_index=True)

    return df_final

def insert_alpha3(df):
    '''
    Description: Add the three-letter country code (alpha3) corresponding to
    the numeric country-code from ISO 3166.
    '''
    # Load the ISO 3166-1 reference data and build a dictionary
    countries_iso = pd.read_csv(iso_path)
    countries_dic = countries_iso.set_index("country-code")["alpha-3"].to_dict()

    # Rename the country variable to match the variable in risk factors data
    df = df.rename(columns={"Country": "country-code"})

    # Map alpha-3 codes to numeric country codes using the dictionary
    df["alpha3"] = df["country-code"].map(countries_dic)

    return df


# Merging and cleaning the files for incidence data.
df = merge_files(incidence_folder)
# Changing sex variable from male = 1, female = 2 to male = 1, female = 0
df['Sex'] = df['Sex'].replace(2, 0)
df = insert_alpha3(df)
df.to_csv(
    os.path.join(clean_data_folder, "cancer-incidence-clean.csv"))