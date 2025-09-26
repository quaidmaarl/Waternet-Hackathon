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
tab1, tab2, tab3, tab4 = st.tabs(["Rivierkreeften", "Grafiek per maand", "Kaart van locaties", "Aankomend jaar"])

# -------- Grafiek --------
with tab1:
    # text
    st.markdown("""
    De rivierkreeft is een exotische, invasieve soort die zijn weg naar Nederland heeft gevonden. Hoewel de rivierkreeft al sinds 2003 wordt waargenomen, is de populatie in de afgelopen vijftien jaar enorm toegenomen. Dit vormt een probleem, omdat de rivierkreeft schade toebrengt aan het lokale milieu. Hij ondermijnt de oevers en veroorzaakt daardoor erosie. Bovendien planten ze zich zeer snel voort en hebben ze nauwelijks natuurlijke vijanden. Met dit dashboard willen we niet alleen bewustwording creëren, maar ook een overzicht geven van hoe en wanneer je rivierkreeften kunt vangen en bereiden. Door ze te vangen en te eten help je actief de lokale ecosystemen in Nederland.
    """)

    st.markdown("***")

    # How to prepare a crayfish
    st.header("Hoe bereid je een rivierkreeft om te eten")
    st.markdown("""
    Zodra je een rivierkreeft hebt gevangen, moet je hem klaarmaken voor je maaltijd. Volg hiervoor deze stappen:
    1. Zorg dat de rivierkreeft in een grote kom met water zit. Het is belangrijk dat hij actief en nog in leven is.
    2. Laat hem daar 30 minuten in staan. Ververs daarna het water. Herhaal dit tot het water helder blijft.
    3. Wanneer het water schoon is, kun je de rivierkreeft koken. Zorg dat het kookwater gezouten is. Je kunt dille, laurier en citrus toevoegen om extra smaak te geven.
    4. Kook de rivierkreeft 3 tot 5 minuten, tot hij naar het wateroppervlak komt drijven.
    5. Leg de kreeft vervolgens in koud water zodat hij niet verder gaart.
    """)

    # add picture
    st.image("Picture1.jpg")

             
with tab2:
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
with tab3:
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

with tab4:
    # add a graph using matplotlib 
    import matplotlib.pyplot as plt
    import pandas as pd
    data = pd.read_csv('data/RivierkreeftWaarnemingen_Cleaned.csv', index_col=False)

    # format
    data['Datum'] = pd.to_datetime(data['Datum'])
    ai_data = data.copy()
    ai_data.drop(columns=['Locatie', 'Longitude', 'Latitude'], inplace=True)

    # simplify to Aantal per month
    ai_data = ai_data.set_index('Datum')['Aantal'].resample('M').sum().reset_index()

    # take data from 2023 - 2025
    recent_data = ai_data.loc[(ai_data['Datum'] >= '2023-01-01') & (ai_data['Datum'] <= '2025-09-30')]

    # reformat Datum to YYYY-MM
    recent_data['Datum'] = recent_data['Datum'].dt.to_period('M').astype(str)

    # remove index
    recent_data.reset_index(drop=True, inplace=True)

    from prophet import Prophet
    # Requires columns 'ds' (dates) and 'y' (values)

    recent_data.rename(columns={'Datum': 'ds', 'Aantal': 'y'}, inplace=True)
    recent_data['ds'] = pd.to_datetime(recent_data['ds'])
    model = Prophet()
    model.fit(recent_data)

    future = model.make_future_dataframe(periods=12, freq='M')
    forecast = model.predict(future)

    fig = model.plot(forecast)
    plt.show()
    import pandas as pd
    import matplotlib.pyplot as plt
    from prophet import Prophet
    from datetime import datetime

    # Your existing code
    recent_data.rename(columns={'Datum': 'ds', 'Aantal': 'y'}, inplace=True)
    recent_data['ds'] = pd.to_datetime(recent_data['ds'])
    model = Prophet()
    model.fit(recent_data)

    future = model.make_future_dataframe(periods=12, freq='M')
    forecast = model.predict(future)

    # Custom plotting with your requirements
    fig, ax = plt.subplots(figsize=(12, 6))

    # Get today's date
    today = datetime.now()

    # start of last month
    today = today.replace(day=1) - pd.DateOffset(days=1)


    # Split forecast into historical and future
    historical_mask = forecast['ds'] <= today
    future_mask = forecast['ds'] > today

    # Alternative: More customized version with better styling
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plot with different colors for past and future
    historical_forecast = forecast[forecast['ds'] <= today]
    future_forecast = forecast[forecast['ds'] > today]

    # Historical line (blue)
    ax.plot(historical_forecast['ds'], historical_forecast['yhat'], 
            color='#1f77b4', linewidth=2.5, label='Historical Forecast')

    # Future line (red/orange)
    ax.plot(future_forecast['ds'], future_forecast['yhat'], 
            color='#ff7f0e', linewidth=2.5, label='Future Forecast')

    # # Actual data points
    # ax.scatter(recent_data['ds'], recent_data['y'], 
    #            color='black', s=40, zorder=5, alpha=0.8, label='Actual Data')

    # # Confidence intervals with different colors
    # ax.fill_between(historical_forecast['ds'], 
    #                 historical_forecast['yhat_lower'],
    #                 historical_forecast['yhat_upper'],
    #                 alpha=0.2, color='#1f77b4', label='Historical Confidence')

    ax.fill_between(future_forecast['ds'], 
                    future_forecast['yhat_lower'],
                    future_forecast['yhat_upper'],
                    alpha=0.2, color='#ff7f0e', label='Future Confidence')

    # Today line
    ax.axvline(x=today, color='red', linestyle='--', linewidth=2, alpha=0.8, label='Today')

    # Set limits with no margins
    ax.set_xlim(recent_data['ds'].min(), forecast['ds'].max())
    y_min = min(forecast['yhat_lower'].min(), recent_data['y'].min())
    y_max = max(forecast['yhat_upper'].max(), recent_data['y'].max())
    ax.set_ylim(y_min - 2, y_max + 2)  # Small buffer for readability

    # Styling
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Amount of Crayfish ', fontsize=12)
    ax.set_title('Prophet Forecast: Historical (Blue) vs Future (Orange)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)

    # Remove margins completely
    plt.margins(0)
    plt.tight_layout()
    st.pyplot(fig)

    # Print future predictions
    print("\nFuture Predictions:")
    future_predictions = forecast[forecast['ds'] > today][['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head(12)
    print(future_predictions.to_string(index=False, float_format='%.1f'))



