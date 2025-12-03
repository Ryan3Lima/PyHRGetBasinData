# PyHRGetBasinData/io_utils.py

from pathlib import Path
import geopandas as gpd
from config import DATA_DIR

def make_huc_output_dir(huc10_id: str) -> Path:
    base = Path(DATA_DIR) / f"huc10_{huc10_id}"
    base.mkdir(parents=True, exist_ok=True)
    return base

def save_roads(roads_gdf: gpd.GeoDataFrame, out_dir: Path):
    roads_path = out_dir / "roads.gpkg"
    roads_gdf.to_file(roads_path, driver="GPKG", layer="roads")
    return roads_path

def save_flowlines(flow_gdf: gpd.GeoDataFrame, out_dir: Path):
    flow_path = out_dir / "flowlines.gpkg"
    flow_gdf.to_file(flow_path, driver="GPKG", layer="flowlines")
    return flow_path

def save_dem(dem_da, out_dir: Path):
    dem_path = out_dir / "dem_30m.tif"
    dem_da.rio.to_raster(dem_path)
    return dem_path
