# app_streamlit.py

import io
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt

import folium
import streamlit.components.v1 as components

from huc10_index import load_or_build_az_huc10_index, get_huc10_geometry
from dem import get_dem_for_geometry
from flowlines import get_flowlines_for_geometry
from roads import get_roads_for_geometry
from io_utils import make_huc_output_dir, save_roads, save_flowlines, save_dem
from config import CRS_GEO, CRS_UTM


def make_huc_boundary_map(geometry_4326):
    """Build a Folium map showing just the selected HUC10 boundary."""
    geom_geojson = geometry_4326.__geo_interface__
    centroid = geometry_4326.centroid
    center = [centroid.y, centroid.x]

    m = folium.Map(location=center, zoom_start=9, tiles="CartoDB positron")

    folium.GeoJson(
        geom_geojson,
        name="HUC10 boundary",
        style_function=lambda feature: {
            "color": "red",
            "weight": 3,
            "fill": False,
        },
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


def main():
    st.title("Arizona HUC10 Basin Data Downloader")

    st.markdown(
        """
        1. Select an **Arizona HUC10** from the list.  
        2. Verify the boundary on the map.  
        3. Click **Download data for this basin** to get:
           - 30 m DEM (3DEP),
           - NHDPlusHR flowlines,
           - OpenStreetMap roads.
        """
    )

    # 1) Load AZ HUC10 index
    with st.spinner("Loading Arizona HUC10 index..."):
        huc_gdf = load_or_build_az_huc10_index()

    huc_gdf = huc_gdf.sort_values("name")
    huc_gdf["label"] = huc_gdf["name"] + " (" + huc_gdf["huc10"] + ")"
    huc_options = {row["huc10"]: row["label"] for _, row in huc_gdf.iterrows()}

    selected_huc10 = st.selectbox(
        "Choose a HUC10:",
        options=list(huc_options.keys()),
        format_func=lambda h: huc_options[h],
    )

    if selected_huc10:
        # Basin geometry in 4326
        geometry_4326 = get_huc10_geometry(selected_huc10, crs=CRS_GEO)

        st.subheader("Step 2 – Confirm basin boundary")

        # Folium preview of boundary only
        m = make_huc_boundary_map(geometry_4326)
        map_html = m._repr_html_()
        components.html(map_html, height=600)

        st.markdown(
            f"Currently selected: **{huc_options[selected_huc10]}**. "
            "If this looks correct, click the button below to download data."
        )

        if st.button("Download DEM, flowlines, and roads for this basin"):
            with st.spinner(f"Downloading data for HUC10 {selected_huc10}..."):
                # 2) Fetch data
                dem_utm = get_dem_for_geometry(geometry_4326, geometry_crs=CRS_GEO)
                flow_utm = get_flowlines_for_geometry(geometry_4326, geometry_crs=CRS_GEO)
                roads_utm = get_roads_for_geometry(geometry_4326, geometry_crs=CRS_GEO)

                # 3) Save to disk (for persistence)
                out_dir = make_huc_output_dir(selected_huc10)
                dem_path = save_dem(dem_utm, out_dir)
                flow_path = save_flowlines(flow_utm, out_dir)
                roads_path = save_roads(roads_utm, out_dir)

            st.success("Download complete!")

            st.write("Files saved locally to:")
            st.code(str(out_dir))

            # 4) Expose files as downloadable links/buttons
            st.subheader("Download files")

            # DEM
            with open(dem_path, "rb") as f:
                dem_bytes = f.read()
            st.download_button(
                label="Download DEM (GeoTIFF)",
                data=dem_bytes,
                file_name=dem_path.name,
                mime="image/tiff",  # or "application/x-geotiff"
            )

            # Flowlines
            with open(flow_path, "rb") as f:
                flow_bytes = f.read()
            st.download_button(
                label="Download flowlines (GeoPackage)",
                data=flow_bytes,
                file_name=flow_path.name,
                mime="application/octet-stream",
            )

            # Roads
            with open(roads_path, "rb") as f:
                roads_bytes = f.read()
            st.download_button(
                label="Download roads (GeoPackage)",
                data=roads_bytes,
                file_name=roads_path.name,
                mime="application/octet-stream",
            )

            # 5) In-app preview: DEM and vector layers shown separately
            st.subheader("Preview of downloaded data")

            # Basin boundary in UTM to match DEM / flowlines / roads
            huc_utm = gpd.GeoDataFrame(geometry=[geometry_4326], crs=CRS_GEO).to_crs(CRS_UTM)

            # --- Figure 1: DEM only ---
            fig1, ax1 = plt.subplots(figsize=(6, 6))

            dem_utm.plot(
                ax=ax1,
                cmap="terrain",
                cbar_kwargs={"label": "elevation [m]"},
            )

            huc_utm.boundary.plot(ax=ax1, edgecolor="red", linewidth=2)

            ax1.set_title(f"DEM – {huc_options[selected_huc10]}")
            ax1.set_axis_off()

            st.pyplot(fig1)

            # --- Figure 2: Vector layers only (roads + flowlines + boundary) ---
            fig2, ax2 = plt.subplots(figsize=(6, 6))

            # Plot order: boundary first, then roads, then flowlines
            huc_utm.boundary.plot(ax=ax2, edgecolor="red", linewidth=2)
            roads_utm.plot(ax=ax2, color="gray", linewidth=0.4)
            flow_utm.plot(ax=ax2, color="steelblue", linewidth=0.7)

            ax2.set_title(f"Vector layers – {huc_options[selected_huc10]}")
            ax2.set_axis_off()

            from matplotlib.lines import Line2D
            legend_elems = [
                Line2D([0], [0], color="red", lw=2, label="HUC10 boundary"),
                Line2D([0], [0], color="gray", lw=2, label="Roads"),
                Line2D([0], [0], color="steelblue", lw=2, label="Flowlines"),
            ]

            ax2.legend(
                handles=legend_elems,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.05),
                ncol=3,
                frameon=True,
            )

            fig2.subplots_adjust(bottom=0.18)

            st.pyplot(fig2)


if __name__ == "__main__":
    main()
