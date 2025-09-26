import pandas as pd
import streamlit as st
import pydeck as pdk

st.title("Waternet Map: Crayfish + Water Quality")

# ---------- Load crawfish ----------
cray_csv = "data/RivierkreeftWaarnemingen_Cleaned.csv"
dfc = pd.read_csv(cray_csv, sep=None, engine="python")
dfc.columns = [c.strip().lower() for c in dfc.columns]
dfc = dfc.rename(columns={"lat": "latitude", "lon": "longitude", "lng": "longitude"})

# Ensure numeric
for col in ["aantal", "latitude", "longitude"]:
    dfc[col] = pd.to_numeric(dfc[col], errors="coerce")

# Keep valid coords
cray = dfc.dropna(subset=["latitude", "longitude"]).copy()

# Aggregate near-duplicates
cray["lat_round"] = cray["latitude"].round(5)
cray["lon_round"] = cray["longitude"].round(5)
cray_agg = (
    cray.groupby(["locatie", "lat_round", "lon_round"], as_index=False)["aantal"]
    .sum()
    .rename(columns={"lat_round": "latitude", "lon_round": "longitude"})
)
cray_agg["type"] = "Crayfish"

# ---------- Load water quality ----------
wq_csv = "data/FYCHEM_Location_OverallStatus.csv"
try:
    dfw = pd.read_csv(wq_csv, sep=None, engine="python")
except Exception:
    dfw = pd.read_csv(wq_csv, sep=";")
dfw.columns = [c.strip().lower() for c in dfw.columns]
dfw = dfw.rename(columns={
    "wgs84_lat": "latitude",
    "wgs84_lon": "longitude",
    "overall_status_weighted": "status",
})

dfw["latitude"] = pd.to_numeric(dfw["latitude"], errors="coerce")
dfw["longitude"] = pd.to_numeric(dfw["longitude"], errors="coerce")
wq = dfw.dropna(subset=["latitude", "longitude"]).copy()
wq["type"] = "Water quality"

# Status -> color (OK=green, Potential stress=yellow, In danger=red)
def status_to_color(s):
    s = str(s).strip().lower()
    if s in {"ok", "good"}:
        return [0, 170, 0, 220]      # green
    if s == "potential stress":
        return [255, 205, 0, 220]    # yellow
    if s in {"in danger", "danger", "at risk", "poor"} or "danger" in s:
        return [200, 0, 0, 220]      # red
    return [160, 160, 160, 200]      # grey fallback

wq["color"] = wq["status"].apply(status_to_color)

# ---------- View ----------
# Use combined center from whichever datasets have points
latitudes = []
longitudes = []
if not cray_agg.empty:
    latitudes.extend(cray_agg["latitude"].tolist())
    longitudes.extend(cray_agg["longitude"].tolist())
if not wq.empty:
    latitudes.extend(wq["latitude"].tolist())
    longitudes.extend(wq["longitude"].tolist())

if latitudes and longitudes:
    view = pdk.ViewState(latitude=sum(latitudes)/len(latitudes),
                         longitude=sum(longitudes)/len(longitudes),
                         zoom=10, pitch=0)
else:
    # Fallback: Amsterdam area
    view = pdk.ViewState(latitude=52.37, longitude=4.90, zoom=10, pitch=0)

# ---------- Layers ----------
# Crayfish heatmap
cray_heat = pdk.Layer(
    "HeatmapLayer",
    data=cray_agg,
    get_position='[longitude, latitude]',
    get_weight='aantal',
    radiusPixels=50,
    pickable=False
)

# Crayfish visible points
cray_points = pdk.Layer(
    "ScatterplotLayer",
    data=cray_agg,
    get_position='[longitude, latitude]',
    get_radius=30,
    get_fill_color=[200, 30, 0, 120],
    pickable=True,
    auto_highlight=True
)

# Crayfish invisible hover-hit layer with slightly larger radius
cray_hover_hit = pdk.Layer(
    "ScatterplotLayer",
    data=cray_agg,
    get_position='[longitude, latitude]',
    radius_units="pixels",
    get_radius=25,
    filled=True,
    stroked=False,
    get_fill_color=[0, 0, 0, 1],
    opacity=0.01,
    pickable=True
)

# Water quality points on top, colored by status
wq_points = pdk.Layer(
    "ScatterplotLayer",
    data=wq,
    get_position='[longitude, latitude]',
    radius_units="pixels",
    get_radius=12,
    radius_min_pixels=2.5,
    radius_max_pixels=3,
    filled=True,
    stroked=True,
    get_fill_color="color",
    get_line_color=[255, 255, 255],
    line_width_min_pixels=1,
    pickable=True,
    auto_highlight=True
)

# Order: heat (bottom) -> crayfish points -> crayfish hit -> water-quality points (top)
deck = pdk.Deck(
    layers=[cray_heat, cray_points, cray_hover_hit, wq_points],
    initial_view_state=view,
    tooltip={"text":
        "Locatie: {locatiecode}\n"
        "Status: {status}"
    }
)

st.pydeck_chart(deck)

# Optional simple legend for water quality
st.caption("Legend — Water quality: OK = green, Potential stress = yellow, In danger = red")