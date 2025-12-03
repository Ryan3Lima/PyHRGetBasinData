# PyHRGetBasinData/flowlines.py

# flowlines.py

from pynhd import NHDPlusHR
import geopandas as gpd
from config import CRS_GEO, CRS_UTM


def get_flowlines_for_geometry(geometry, geometry_crs: int = CRS_GEO) -> gpd.GeoDataFrame:
    """
    Get NHDPlus High-Resolution flowlines within a basin geometry.

    Parameters
    ----------
    geometry : shapely geometry
        Basin polygon.
    geometry_crs : int
        EPSG code of the input geometry.

    Returns
    -------
    flowlines_utm : GeoDataFrame
        Flowlines intersecting the geometry, in CRS_UTM.
    """
    # Ensure geometry is in 4326 for the web service
    if geometry_crs != CRS_GEO:
        geom_ll = gpd.GeoSeries([geometry], crs=geometry_crs).to_crs(CRS_GEO).iloc[0]
    else:
        geom_ll = geometry

    # Access NHDPlus HR "flowline" layer, output in 4326
    nhdhr = NHDPlusHR("flowline", crs=CRS_GEO)

    # Spatial query: all flowlines that intersect the basin polygon
    fl = nhdhr.bygeom(geom=geom_ll, geo_crs=CRS_GEO)

    # Reproject to UTM 12N for analysis
    fl_utm = fl.to_crs(CRS_UTM)
    return fl_utm


if __name__ == "__main__":
    # Smoke test: get flowlines for a test HUC10 and plot them
    from huc10_index import get_huc10_geometry
    import matplotlib.pyplot as plt

    test_huc10 = "1502001602"  # change to a known AZ HUC10 if needed
    print(f"Testing flowlines for HUC10 {test_huc10}...")

    # Get basin geometry in 4326
    geom_4326 = get_huc10_geometry(test_huc10, crs=CRS_GEO)

    # Fetch flowlines in UTM
    flowlines_utm = get_flowlines_for_geometry(geom_4326, geometry_crs=CRS_GEO)

    print("Number of flowlines:", len(flowlines_utm))
    print("Flowlines CRS:", flowlines_utm.crs)
    print(flowlines_utm.head())

    # Rebuild basin boundary in UTM to overlay correctly
    huc_gdf_utm = gpd.GeoDataFrame(geometry=[geom_4326], crs=CRS_GEO).to_crs(CRS_UTM)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    huc_gdf_utm.boundary.plot(ax=ax, edgecolor="black", linewidth=2)
    flowlines_utm.plot(ax=ax, color="steelblue", linewidth=0.7)

    ax.set_title(f"NHDPlus HR Flowlines for HUC10 {test_huc10}")
    ax.set_axis_off()

    plt.tight_layout()
    plt.show()
