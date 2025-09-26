import pandas as pd
import streamlit as st
import altair as alt
import pydeck as pdk

st.set_page_config(layout="wide")
st.title("Waternet Crayfish Dashboard")

# ----------------- Data inladen -----------------
cray_csv = "data/RivierkreeftWaarnemingen_Cleaned.csv"
wq_csv = "data/FYCHEM_Location_OverallStatus.csv"

# ----- Crayfish -----
dfc = pd.read_csv(cray_csv, engine="python")
dfc.columns = [c.strip().lower() for c in dfc.columns]
dfc = dfc.rename(columns={"lat": "latitude", "lon": "longitude", "lng": "longitude"})
for col in ["aantal", "latitude", "longitude"]:
    dfc[col] = pd.to_numeric(dfc[col], errors="coerce")
dfc = dfc.dropna(subset=["latitude", "longitude"])
dfc['datum'] = pd.to_datetime(dfc['datum'], errors='coerce')
dfc['jaar'] = dfc['datum'].dt.year
dfc['maand'] = dfc['datum'].dt.month

# Aggregate near-duplicates
dfc["lat_round"] = dfc["latitude"].round(5)
dfc["lon_round"] = dfc["longitude"].round(5)
cray_agg = (
    dfc.groupby(["locatie", "lat_round", "lon_round"], as_index=False)["aantal"]
    .sum()
    .rename(columns={"lat_round": "latitude", "lon_round": "longitude"})
)
cray_agg["type"] = "Crayfish"

# ----- Water quality -----
try:
    dfw = pd.read_csv(wq_csv, engine="python")
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

# Status -> color
def status_to_color(s):
    s = str(s).strip().lower()
    if s in {"ok", "good"}:
        return [0, 170, 0, 220]
    if s == "potential stress":
        return [255, 205, 0, 220]
    if s in {"in danger", "danger", "at risk", "poor"} or "danger" in s:
        return [200, 0, 0, 220]
    return [160, 160, 160, 200]

wq["color"] = wq["status"].apply(status_to_color)

# ----------------- Sidebar -----------------
max_year = int(dfc['jaar'].max())
selected_year = st.sidebar.slider("Selecteer jaar", 2010, max_year, max_year)
filtered_data = dfc[dfc['jaar'] == selected_year]

# ----------------- KPI’s -----------------
monthly_counts = filtered_data.groupby("maand")['aantal'].sum().reset_index()
total_crayfish = monthly_counts['aantal'].sum()
avg_crayfish = monthly_counts['aantal'].mean()

location_counts = filtered_data.groupby("locatie")['aantal'].sum().reset_index()
best_location = location_counts.sort_values("aantal", ascending=False).iloc[0]
location_name = best_location['locatie']
display_name = location_name if len(location_name) <= 25 else location_name[:22] + "..."

col1, col2, col3 = st.columns([1, 1, 5])
with col1:
    st.metric(label=f"Totaal aantal in {selected_year}", value=f"{total_crayfish}")
with col2:
    st.metric(label=f"Gemiddeld per maand in {selected_year}", value=f"{avg_crayfish:.2f}")
with col3:
    st.metric(label=f"Beste locatie in {selected_year}", value=display_name,
              delta=f"{best_location['aantal']} Gespot")

# ----------------- Tabs: Grafiek & Kaart -----------------
tab1, tab2 = st.tabs(["Grafiek per maand", "Kaart van locaties"])

# -------- Grafiek --------
with tab1:
    month_map = {1:"Jan",2:"Feb",3:"Mrt",4:"Apr",5:"Mei",6:"Jun",
                 7:"Jul",8:"Aug",9:"Sep",10:"Okt",11:"Nov",12:"Dec"}
    monthly_counts['maandnaam'] = monthly_counts['maand'].map(month_map)

    line_chart = alt.Chart(monthly_counts).mark_line(point=True, color='teal').encode(
        x=alt.X("maandnaam:O", title="Maand"),
        y=alt.Y("aantal", title="Aantal Crayfish"),
        tooltip=["maandnaam", "aantal"]
    ).properties(
        width=700,
        height=400,
        title=f"Aantal Crayfish per Maand in {selected_year}"
    ).interactive()

    st.altair_chart(line_chart, use_container_width=True)

# -------- Kaart --------
with tab2:
    # Combineer view center
    latitudes = list(cray_agg["latitude"]) + list(wq["latitude"])
    longitudes = list(cray_agg["longitude"]) + list(wq["longitude"])
    if latitudes and longitudes:
        view = pdk.ViewState(latitude=sum(latitudes)/len(latitudes),
                             longitude=sum(longitudes)/len(longitudes),
                             zoom=10, pitch=0)
    else:
        view = pdk.ViewState(latitude=52.37, longitude=4.90, zoom=10, pitch=0)

    # Layers
    cray_heat = pdk.Layer(
        "HeatmapLayer",
        data=cray_agg,
        get_position='[longitude, latitude]',
        get_weight='aantal',
        radiusPixels=50,
        pickable=False
    )
    cray_points = pdk.Layer(
        "ScatterplotLayer",
        data=cray_agg,
        get_position='[longitude, latitude]',
        get_radius=30,
        get_fill_color=[200, 30, 0, 120],
        pickable=True,
        auto_highlight=True
    )
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

    deck = pdk.Deck(
        layers=[cray_heat, cray_points, cray_hover_hit, wq_points],
        initial_view_state=view,
        tooltip={"text": "Locatie: {locatie}\nStatus: {status}"}
    )

    st.pydeck_chart(deck)
    st.caption("Legend — Water quality: OK = green, Potential stress = yellow, In danger = red")
