# PyHRGetBasinData/dem.py

# PyHRGetBasinData/dem.py

import geopandas as gpd
import py3dep
import rioxarray  # noqa: F401
from config import CRS_GEO, CRS_UTM, DEM_RES_M


def get_dem_for_geometry(geometry, geometry_crs: int = CRS_GEO):
    """
    Get a DEM for the given basin geometry.

    Steps:
    1. Reproject geometry to CRS_GEO (4326) for py3dep.get_dem.
    2. Call py3dep.get_dem (default behavior), which returns a DEM
       in the service's native CRS.
    3. Reproject DEM to UTM 12N for analysis.

    Returns
    -------
    dem_utm : xarray.DataArray
        DEM at DEM_RES_M resolution, in CRS_UTM (UTM Zone 12N).
    """
    # 1) Ensure geometry is in 4326 for py3dep
    if geometry_crs != CRS_GEO:
        geom_ll = gpd.GeoSeries([geometry], crs=geometry_crs).to_crs(CRS_GEO).iloc[0]
    else:
        geom_ll = geometry

    # 2) Get DEM using py3dep default behavior (like the tutorial)
    dem = py3dep.get_dem(
        geometry=geom_ll,
        resolution=DEM_RES_M,
    )
    # At this point, dem.rio.crs is whatever the service uses natively

    # 3) Reproject DEM to UTM 12N for analysis
    dem_utm = dem.rio.reproject(CRS_UTM)

    return dem_utm

if __name__ == "__main__":
    from huc10_index import get_huc10_geometry
    import matplotlib.pyplot as plt

    test_huc10 = "1502001602"  # example; change if needed
    print(f"Testing DEM download for HUC10 {test_huc10}...")

    # 1) Get basin geometry in 4326
    geom_4326 = get_huc10_geometry(test_huc10, crs=CRS_GEO)

    # 2) Get DEM in UTM using your function
    dem_utm = get_dem_for_geometry(geom_4326, geometry_crs=CRS_GEO)

    print("DEM (UTM) summary:")
    print(dem_utm)
    print("DEM shape:", dem_utm.shape)
    print("DEM CRS:", dem_utm.rio.crs)

    # Quick sanity check: are there any non-NaN values?
    print("DEM min/max:", float(dem_utm.min()), float(dem_utm.max()))

    # 3) Reproject DEM to 4326 to match the polygon for plotting
    dem_ll = dem_utm.rio.reproject(CRS_GEO)
    print("DEM CRS (for plot):", dem_ll.rio.crs)

    # 4) Build a GeoDataFrame for the HUC10 boundary in 4326
    import geopandas as gpd
    huc_gdf = gpd.GeoDataFrame(geometry=[geom_4326], crs=CRS_GEO)

    # 5) Plot DEM + HUC10 boundary
    fig, ax = plt.subplots(figsize=(8, 6))

    dem_ll.plot(ax=ax, cmap="terrain")        # raster DEM
    huc_gdf.boundary.plot(ax=ax, edgecolor="red", linewidth=2)

    ax.set_title(f"DEM for HUC10 {test_huc10}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    plt.tight_layout()
    plt.show()
