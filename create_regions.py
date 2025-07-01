
"""
Order of operations:
1) Load libraries
2) Load GEOCORR file as base file
    - This includes 2020 census tract GEOIDs and census place GEOIDs
    - Filter to identify the portion of the tract that is most within a place or not-a-place
3) Create a new column called TRACT22 that has the census tract GEOID or the swapped census tract GEOIDs for Connecticut
4) Add in CBSA values from the latest CBSA delineation available 2023
5) Identify census tracts in principal cities using latest principal cities delineations available
6) Identify "most" principal city using principal cities + city hall lat/lon: https://www.census.gov/library/publications/2012/dec/c2010sr-01.html
7) Join in GIS SQ MI, 2020 tract population, and distance to CBSA center defined as central city's city hall
8) Add in Census Bureau regions and subdivisions https://www2.census.gov/geo/pdfs/maps-data/maps/reference/us_regdiv.pdf

To do in the future:
 - Add in RUCA 2020 data

The output product is a dataframe called df
"""

# %%
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables from a .env file
env_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path=env_path)

# 
geocorr        = os.getenv("geocorr")
chapter1       = os.getenv("chapter1")
acres_distance = os.getenv("acres_distance")
regions        = os.getenv("regions")

# %%
# Load GEOCORR file
# Format tract
def format_tract(val):
    try:
        val = float(val)
        whole = int(val)
        frac = int(round((val - whole) * 100))
        return f"{whole:04d}{frac:02d}"
    except:
        return ""

df_geocorr                = pd.read_csv(geocorr, skiprows=1, encoding="latin1",low_memory=False)
df_geocorr.columns        = [str(h).upper().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "") for h in list(df_geocorr)]
df_geocorr["PLACE_CODE"]  = df_geocorr["PLACE_CODE"].astype(str).apply(lambda x: (str(x)).replace(".0", "").zfill(5))
df_geocorr["COUNTY_CODE"] = df_geocorr["COUNTY_CODE"].astype(str).apply(lambda x: (str(x)).replace(".0", "").zfill(5))
df_geocorr["TRACT"]       = df_geocorr["TRACT"].apply(format_tract)
df_geocorr["TRACT20"]     = df_geocorr["COUNTY_CODE"] + df_geocorr["TRACT"]
df_geocorr["PLACE"]       = df_geocorr["COUNTY_CODE"].astype(str).str[:2] + df_geocorr["PLACE_CODE"].astype(str).str.zfill(5)


# Display first record
print(df_geocorr.iloc[0].to_frame().T)
print(df_geocorr.head(5))
# %%
def majority_type (value):
    if isinstance(value, (int, pd.Int64Dtype().type, float)):
        try:
            val = float(value)
        except:
            return None
        if val == 1.0:
            return "COMPLETE"
        elif val > 0.66:
            return "SUPERMAJORITY"
        elif val > 0.5:
            return "MAJORITY"
        else:
            return "PLURALITY"
    else:
        return None
    

# Keep only the largest allocation factor values
# There are tracts that could be partially within not-a-place (99999) and some place but coded as not-a-place because not-a-place is the majority population allocation factor 
df_geocorr                  = df_geocorr.sort_values("TRACT_TO_PLACE_ALLOCATION_FACTOR", ascending=False).drop_duplicates(subset="TRACT20", keep="first")
df_geocorr["MAJORITY_TYPE"] = df_geocorr.apply(lambda x: majority_type(x["TRACT_TO_PLACE_ALLOCATION_FACTOR"]), axis=1) 

print(df_geocorr.head(5))
# %%
# Fix Connecticut issue by creating a new column called TRACT22 that is equal to TRACT20 unless it's Connecticut then swap with the correct value using the Connecticut census tract crosswalk
def convert_tract20(val):
    val_str = str(val)
    if val_str.startswith("09"):
        return ct_dict.get(val_str, val_str)  # Try to replace, fall back to original
    return val_str  # Not CT — leave unchanged


# Connecticut census tract swap crosswalk
ct                       = r"https://raw.githubusercontent.com/CT-Data-Collaborative/2022-tract-crosswalk/refs/heads/main/2022tractcrosswalk.csv"
df_ct                    = pd.read_csv(ct, usecols=["tract_fips_2020", "Tract_fips_2022"])
df_ct.columns            = [str(h).upper() for h in list(df_ct)]
df_ct["TRACT_FIPS_2020"] = df_ct["TRACT_FIPS_2020"].astype(str).apply(lambda x: (str(x).replace(".0", "")).zfill(11))
df_ct["TRACT_FIPS_2022"] = df_ct["TRACT_FIPS_2022"].astype(str).apply(lambda x: (str(x).replace(".0", "")).zfill(11))
ct_dict                  = dict(zip(df_ct["TRACT_FIPS_2020"], df_ct["TRACT_FIPS_2022"]))

# Create the new column with the updated crosswalk
df_geocorr["TRACT22"] = df_geocorr["TRACT20"].apply(convert_tract20)

# %%
# Get the CBSA info
# Skip the first two rows and delete the last three rows because they're junk 
cbsas            = r"https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx"
df_cbsas         = pd.read_excel(cbsas, skiprows=2)
df_cbsas.columns = [str(h).upper().replace(" ", "_").replace("/", "_") for h in list(df_cbsas)]
df_cbsas         = df_cbsas.iloc[:-3]

df_cbsas["CBSA_CODE"]                  = df_cbsas["CBSA_CODE"].astype(str).apply(lambda x: (str(x).replace(".0", "")).zfill(5))
df_cbsas["METROPOLITAN_DIVISION_CODE"] = df_cbsas["METROPOLITAN_DIVISION_CODE"].astype(str).apply(lambda x: (str(x).replace(".0", "")).zfill(5))
df_cbsas["CSA_CODE"]                   = df_cbsas["CSA_CODE"].astype(str).apply(lambda x: (str(x).replace(".0", "")).zfill(5))
df_cbsas["FIPS_STATE_CODE"]            = df_cbsas["FIPS_STATE_CODE"].astype(str).apply(lambda x: (str(x).replace(".0", "")).zfill(2))
df_cbsas["FIPS_COUNTY_CODE"]           = df_cbsas["FIPS_COUNTY_CODE"].astype(str).apply(lambda x: (str(x).replace(".0", "")).zfill(3))
df_cbsas["STCNTY22"]                   = df_cbsas["FIPS_STATE_CODE"] + df_cbsas["FIPS_COUNTY_CODE"]

# Perform actual join
df_geocorr["STCNTY22"] = df_geocorr["TRACT22"].astype(str).apply(lambda x: x[:5])
df                     = pd.merge(df_geocorr, df_cbsas[['CBSA_CODE', 'METROPOLITAN_DIVISION_CODE', 'CSA_CODE', 'CBSA_TITLE', 'METROPOLITAN_MICROPOLITAN_STATISTICAL_AREA', 'METROPOLITAN_DIVISION_TITLE', 'CSA_TITLE', 'COUNTY_COUNTY_EQUIVALENT',  'CENTRAL_OUTLYING_COUNTY', 'STCNTY22']], how = "left", on = "STCNTY22")


# %%
# Identify tracts within the principal city
pc                       = r"https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list2_2023.xlsx"
df_pc                    = pd.read_excel(pc, skiprows=2)
df_pc.columns            = [str(h).upper().replace(" ", "_").replace("/", "_") for h in list(df_pc)]
df_pc["CBSA_CODE"]       = df_pc["CBSA_CODE"].astype(str).apply(lambda x: (str(x).replace(".0", "")).zfill(5))
df_pc["FIPS_STATE_CODE"] = df_pc["FIPS_STATE_CODE"].astype(str).apply(lambda x: (str(x).replace(".0", "")).zfill(2))
df_pc["FIPS_PLACE_CODE"] = df_pc["FIPS_PLACE_CODE"].astype(str).apply(lambda x: (str(x).replace(".0", "")).zfill(5))
df_pc["PLACE"]           = df_pc["FIPS_STATE_CODE"] + df_pc["FIPS_PLACE_CODE"]
df["PRINCIPAL_CITY"]     = df["PLACE"].isin(df_pc["PLACE"]).astype(int)

# %%
# Identify tracts that are within *the* central city (e.g. only Washington, DC not all of the principal cities in the DC CBSA)




chp1          = pd.read_excel(chapter1, sheet_name="Principal Cities", skiprows=2)
chp1.columns  = ["CBSA_CODE", "PLACE", "METRO_AREA", "POP_10", "POP_00", "LAT", "LON"]
chp1          = chp1.iloc[2:].reset_index(drop=True)
chp1["PLACE"] = chp1["PLACE"].astype(str).apply(lambda x: (str(x).replace(".", "")).zfill(7))
chp1["PLACE"] = chp1["PLACE"].astype(str).apply(lambda x: x[:7])
chp1          = chp1[chp1["LAT"].notnull()]

print(chp1.head(10))

df["CENTRAL_CITY"]     = df["PLACE"].isin(chp1["PLACE"]).astype(int)
df.loc[(df["CENTRAL_CITY"] == 1) & (df["PRINCIPAL_CITY"] == 0), "CENTRAL_CITY"] = 0 # This is for 35 census tracts

# %%
# Add in GIS SQ MI and Distance

# Load, format, and filter the dataframe
df_ad                 = pd.read_csv(acres_distance)
df_ad["TRACT20"]      = df_ad["FIPS"].astype(str).apply(lambda x: (str(x).replace(".", "")).zfill(11))
df_ad["TRACT_POP_20"] = df_ad["POPULATION"]
df_ad                 = df_ad[["TRACT20", "TRACT_POP_20", "SQMI", "POP_SQMI", "CBSA_DISTANCE", "CBSA_PERCENTILE"]]

# Join in data
if "TRACT_POP_20" not in list(df):
    print("Performing join")
    df = pd.merge(df, df_ad, how = "left", on = "TRACT20")
else:
    print("GIS SQ MI and CBSA distance already exists in df")

# %%
# Add in Census Bureau regions and subdivisions
df_r                = pd.read_csv(regions)
df_r.columns        = [str(h).upper() for h in list(df_r)]
df_r["STATE_ABBR."] = df_r["STATE ABBREVIATION"]
df_r                = df_r[["STATE_ABBR.", "REGION", "DIVISION"]]

# Inspect the dataframe
count     = 0
dataframe = regions
m         = max([len(x) for x in list(dataframe)])
for item in list(dataframe):
    print("{0} | {1} | {2} | {3} | {4}".format(str(count).zfill(2), str(dataframe[item].dtype).ljust(7), str(item).ljust(m), str(dataframe[item].isna().sum()).ljust(5) , dataframe[item].iloc[0]))
# %%
# Save file as CSV
df_sorted = df.sort_values(by="TRACT22", ascending=True).reset_index(drop=True)
df_sorted = df_sorted.drop(["COUNTY_CODE", "TRACT", "STATE_CODE"], axis=1)
df_sorted.to_csv("Tract_Where_File.csv", index=False)
# %%
# Walk the first record of the dataframe
dataframe = df_sorted
print(f"\nRecords in datafrae: {len(dataframe):,}\n")
count = 0
m     = max([len(x) for x in list(dataframe)])
for item in list(dataframe):
    print("{0} | {1} | {2} | {3}".format(str(count).zfill(2), str(dataframe[item].dtype).ljust(7), str(item).ljust(m), dataframe[item].iloc[0]))
    count = count + 1

# %%



# %%
