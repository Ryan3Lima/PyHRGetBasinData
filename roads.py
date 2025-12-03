# PyHRGetBasinData/roads.py

# roads.py

import osmnx as ox
import geopandas as gpd
from config import CRS_GEO, CRS_UTM


def get_roads_for_geometry(geometry, geometry_crs: int = CRS_GEO) -> gpd.GeoDataFrame:
    """
    Get OpenStreetMap roads within a basin geometry using OSMnx.

    Parameters
    ----------
    geometry : shapely geometry
        Basin polygon.
    geometry_crs : int
        EPSG code of the input geometry.

    Returns
    -------
    roads_utm : GeoDataFrame
        Road segments within the basin, in CRS_UTM.
    """
    # OSMnx expects polygon in EPSG:4326
    if geometry_crs != CRS_GEO:
        geom_ll = gpd.GeoSeries([geometry], crs=geometry_crs).to_crs(CRS_GEO).iloc[0]
    else:
        geom_ll = geometry

    # Download street network
    G = ox.graph_from_polygon(
        geom_ll,
        network_type="all_public",  # or "drive", "all", etc.
    )

    # Convert to GeoDataFrames (we only need edges for roads)
    _, edges = ox.graph_to_gdfs(G, nodes=True, edges=True)

    # Reproject roads to UTM 12N
    roads_utm = edges.to_crs(CRS_UTM)
    return roads_utm


if __name__ == "__main__":
    from huc10_index import get_huc10_geometry
    import matplotlib.pyplot as plt

    test_huc10 = "1502001602"  # change if you want
    print(f"Testing roads for HUC10 {test_huc10}...")

    # Basin geometry in 4326
    geom_4326 = get_huc10_geometry(test_huc10, crs=CRS_GEO)

    # Fetch roads in UTM
    roads_utm = get_roads_for_geometry(geom_4326, geometry_crs=CRS_GEO)

    print("Number of road segments:", len(roads_utm))
    print("Roads CRS:", roads_utm.crs)
    print(roads_utm.head())

    # HUC boundary in UTM
    huc_gdf_utm = gpd.GeoDataFrame(geometry=[geom_4326], crs=CRS_GEO).to_crs(CRS_UTM)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))

    huc_gdf_utm.boundary.plot(ax=ax, edgecolor="black", linewidth=2)
    roads_utm.plot(ax=ax, color="gray", linewidth=0.4)

    ax.set_title(f"OSM Roads for HUC10 {test_huc10}")
    ax.set_axis_off()

    plt.tight_layout()
    plt.show()
