# Librerías
import pandas as pd
import os

'''
Script to clean databases downloaded from the WHO database.

All the data extracted from the WHO archive shares the same variables. We are
only interested in the next ones:

- Indicator: explains the units of the data
- SpatialDimValueCode: 3 letter country ID (equal to alpha3 in ISO 3166)
- Location: Name of the country
- Period: Year 
- Dim1 type: how is the data clasified (mostly by sex)
- Dim1: the dimension itself
- Value: the value of the data. It can have Confidence Intervals or not.

The files must be contained in folders matching their names (case sensitive)
inside the "Data/Raw-Data/Risk-factors/from-WHO" folder.
'''
# Loading initial parameters
current_path = os.path.dirname(__file__)
raw_data_path = current_path[:-4] + "Data/Raw-data/Risk-factors/from-WHO"
clean_data_path = current_path[:-4] + "Data/Clean-data"
iso_path = current_path[:-4] + "Data/countries-ISO-3166.csv"

################## Declaring main functions #############################
def extract_variables(df):
    '''
    Description: function to extract the wanted variables.
    '''
    # Selection of the variables
    df_selected = df[[
        "Indicator", 
        "SpatialDimValueCode", 
        "Location", 
        "Period", 
        "Dim1 type",
        "Dim1", 
        "Value"]]
    
    # Renaming some of them
    df_selected = df_selected.rename(columns={
    "SpatialDimValueCode": "alpha3",
    "Period": "Time period"})

    return df_selected

def select_near_2012(df, year=2012):
    '''
    Description: Select the closest data point to a reference year for each 
    country and subdivision.

    For each combination of country (alpha3) and subdivision (Dim1)
    (sex, residence type), this function selects the observation whose 
    year is nearest to the specified target year. In case of ties, the earliest 
    observation is chosen.'''

    # Compute absolute distance from the target year
    df["absolute-dist"] = (df["Time period"] - year).abs()

    # Sort by: country, distance to target year and year
    df_sorted = df.sort_values(by=["alpha3", "absolute-dist", "Time period"])

    # Keep the first occurrence for each country-subdivision combination
    df_circa_year = df_sorted.groupby(
        ["alpha3", "Dim1"], dropna=False).first().reset_index()

    # Remove the auxiliary distance column before returning
    df_circa_year = df_circa_year.drop(columns="absolute-dist")

    return df_circa_year

def insert_alpha3(df):
    '''
    Description: Add a numeric country code column based 
    on ISO 3166-1 alpha-3 codes. This function maps three-letter 
    country codes (alpha-3) to their corresponding numeric country codes 
    sing a reference file.
    '''
    # Load the ISO 3166-1 reference data and build a dictionary
    countries_iso = pd.read_csv(iso_path)
    countries_dic = countries_iso.set_index("alpha-3")["country-code"].to_dict()

    # Map alpha-3 codes to numeric country codes using the dictionary
    df["country-code"] = df["alpha3"].map(countries_dic)

    return df

def binary_sex(df):
    '''
    If the subdivision (Dim1) is the parameter sex, a new binary variable
    is created (Male = 1, Female = 0)'''

    if (df["Dim1 type"] == "Sex").all():
        df["sex_dichotomic"] = (df["Dim1"] == "Male").astype(int)

    return df

def manage_CI(df):
    '''
    If the Confidence Interval is present, it gets separated in two new 
    variables (upper and lower bound)
    '''

    # Value without spaces
    df["Value"] = df["Value"].astype(str)
    raw_value = df["Value"].str.replace(" ", "", regex=False)

    # Extraction of the value and the intervals
    parts = raw_value.str.split("[", expand=True)
    
    if parts.shape[1] > 1:
        intervals = parts[1].str.strip("]")
        intervals = intervals.str.split("-", expand=True)

        df["Value2"] = parts[0].astype(float)
        df["CI95_low"] = intervals[0].astype(float)
        df["CI95_high"] = intervals[1].astype(float)

    return df

########################### Main execution #####################################

# We iterate the folders with data from the WHO, parsing the files
for item in os.listdir(raw_data_path):
    item_path = os.path.join(raw_data_path, item)

    if os.path.isdir(item_path):
        raw_file_path = os.path.join(item_path, item + ".csv")
        clean_file_path = os.path.join(item_path, item + ".csv")
        
        # Loading the raw data
        raw_data = pd.read_csv(raw_file_path)
        
        # Select the wanted variables
        df_selected = extract_variables(raw_data)

        # Take the closest data to target year (2012)
        df_selected = select_near_2012(df_selected)

        # Add the country-code to be ISO3166 compliant
        df_selected = insert_alpha3(df_selected)

        # Add binary coding for sex if present
        df_selected = binary_sex(df_selected)

        # Manage Confidence Intervals if present
        df_selected = manage_CI(df_selected)

        # Save the new data into a .csv file
        df_selected.to_csv(os.path.join(clean_data_path, item + "-clean.csv"))

        # Control print for the amount of missing values on each category.
        print(f"Registro de valores faltantes para datos de {item}: ")
        print(df_selected.isnull().sum())
