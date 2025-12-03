#PyHRGetBasinData/huc10_index.py

from pathlib import Path
import geopandas as gpd
from pygeohydro import WBD
from config import AZ_STATE_ABBR, CRS_GEO, DATA_DIR


WBD_LAYER = "huc10"

def fetch_az_huc10_index() -> gpd.GeoDataFrame:
    """
    Download all HUC10 polygons in Arizona using WBD, then cache them locally.
    """
    wbd10 = WBD(WBD_LAYER, crs=CRS_GEO)

    # Filter by state = 'AZ' using the WBD attributes.
    # (This uses a SQL WHERE clause understood by the WBD service.)
    sql = f"States LIKE '%{AZ_STATE_ABBR}%'"

    gdf = wbd10.bysql(sql)
    # Sanity: keep only relevant columns and rename for clarity
    # Typical field names: 'HUC10', 'Name' or 'HU_10_NAME' – adjust once you inspect.
    gdf = gdf.rename(columns={
        "HUC10": "huc10",
        "Name": "name",         # or "HU_10_NAME": "name"
    })
    return gdf


def load_or_build_az_huc10_index() -> gpd.GeoDataFrame:
    """
    Load cached AZ HUC10 index if exists; otherwise fetch from WBD and save.
    """
    data_dir = Path(DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    index_path = data_dir / "az_huc10.gpkg"

    if index_path.exists():
        return gpd.read_file(index_path)

    gdf = fetch_az_huc10_index()
    gdf.to_file(index_path, driver="GPKG", layer="huc10")
    return gdf


def get_huc10_geometry(huc10_id: str, crs: int = CRS_GEO):
    gdf = load_or_build_az_huc10_index()
    row = gdf.loc[gdf["huc10"] == huc10_id]

    if row.empty:
        raise ValueError(f"HUC10 {huc10_id} not found in Arizona index")
    geom = row.geometry.iloc[0]
    if gdf.crs.to_epsg() != crs:
        geom = gpd.GeoSeries([geom], crs=gdf.crs).to_crs(crs).iloc[0]
    return geom

if __name__ == "__main__":
    # Simple smoke test: build or load the AZ HUC10 index and print the first few rows
    gdf = load_or_build_az_huc10_index()
    print("Loaded AZ HUC10 index with", len(gdf), "features")
    print(gdf[["huc10", "name"]].head())

    # Try getting the geometry for the first HUC10
    first_huc = gdf["huc10"].iloc[0]
    geom = get_huc10_geometry(first_huc)
    print("Geometry type for first HUC10:", geom.geom_type)
