# PyHRGetBasinData/config.py

AZ_STATE_FIPS = "04"             # if you ever need it
AZ_STATE_ABBR = "AZ"

CRS_GEO = 4326                   # WGS84
CRS_UTM = 32612                  # UTM Zone 12N
DEM_RES_M = 30                   # 30m DEM

DATA_DIR = "data"                # root data folder (you can make subfolders)

if __name__ == "__main__":
    print("Config OK")
    print("State Abbreviation: ", AZ_STATE_ABBR)
    print("State FIPS Code: ", AZ_STATE_FIPS)
    print("CRS_GEO:", CRS_GEO)
    print("CRS_UTM:", CRS_UTM)
    print("DATA_DIR:", DATA_DIR)