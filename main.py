import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"
import read_data
import read_pandas
from PIL import Image
from person import Person
from ekgdata import EKGdata

# Tabs: Person, EKG, Leistungstest
tab1, tab2, tab3 = st.tabs(["👤 Versuchsperson", "🫀 EKG-Daten", "🚴 Leistungstest"])

# Gemeinsame Daten
person_names = read_data.get_person_list()
DEFAULT_IMAGE_PATH = "data/pictures/none.jpg"

with tab1:
    st.header("Versuchsperson auswählen")
    selected_name = st.selectbox("Name der Versuchsperson", options=person_names)

    person_dict = read_data.find_person_data_by_name(selected_name)
    picture_path = person_dict.get("picture_path", DEFAULT_IMAGE_PATH)

    # Bild anzeigen
    try:
        image = Image.open(picture_path)
        st.image(image, caption=selected_name, width=250)
    except FileNotFoundError:
        st.warning("Bilddatei nicht gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Laden des Bilds: {e}")

    st.write("Personen-ID:", person_dict.get("id", "Unbekannt"))

    gender = person_dict.get("gender", None)
    if gender is None or gender == "":
        gender = "Unbekannt"
    st.write("Geschlecht:", gender)


with tab2:
    st.header("🫀 EKG-Datenanalyse")

    if person_dict and person_dict.get("ekg_tests"):
        ekg_tests = person_dict["ekg_tests"]
        ekg_options = [f"ID {test['id']} - {test['date']}" for test in ekg_tests]
        selected_ekg_str = st.selectbox("EKG-Test auswählen", options=ekg_options)

        selected_index = ekg_options.index(selected_ekg_str)
        selected_ekg_dict = ekg_tests[selected_index]

        ekg = EKGdata(selected_ekg_dict)
        gender = person_dict.get("gender", "male")
        person_obj = Person(person_dict)
        max_hr = person_obj.calc_max_heart_rate(gender=gender)
        ekg.find_peaks(max_puls=max_hr)
        estimated_hr = ekg.estimate_hr()
        age = person_obj.calc_age()

        st.write("Personen-ID:", person_dict.get("id", "Unbekannt"))
        st.write(f"Alter: {age} Jahre")
        st.write(f"EKG-ID: {selected_ekg_dict['id']}")
        st.write(f"Geschätzte Herzfrequenz: {estimated_hr:.1f} bpm")
        st.write(f"Geschätzter Maximalpuls: {max_hr} bpm")

        df = ekg.df

        # Hier legen wir nur **ein** Platzhalter-Element an, das wir mit Plot füllen
        plot_placeholder = st.empty()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Zeit in ms"], y=df["Messwerte in mV"], mode='lines', name='EKG Signal'))
        peaks_df = df[df["Peak"] == 1]
        fig.add_trace(go.Scatter(x=peaks_df["Zeit in ms"], y=peaks_df["Messwerte in mV"], mode='markers', name='Peaks'))

        start = df["Zeit in ms"].min()
        fig.update_layout(
            title="EKG mit Peaks",
            xaxis=dict(
                range=[start, start + 5000],
                rangeslider=dict(visible=True),
                type="linear",
                autorange=False
            ),
            yaxis_title="Messwerte in mV",
            xaxis_title="Zeit in ms",
            height=400
        )

        # Rendern in den Platzhalter - damit wird der alte Plot überschrieben!
        plot_placeholder.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Keine EKG-Daten für diese Person vorhanden.")



with tab3:
    st.header("🚴 Leistungstest-Auswertung")

    max_hr_input = st.number_input("Manuelle Eingabe: Max. Herzfrequenz (für Zonenanalyse)", min_value=0, max_value=250, step=1)

    if st.button("Absenden"):
        df = read_pandas.read_my_csv()
        zones = read_pandas.get_zone_limit(max_hr_input)

        # Zonen zuweisen
        df['Zone'] = df['HeartRate'].apply(lambda x: read_pandas.assign_zone(x, zones))

        fig = read_pandas.make_plot(df, zones)
        st.plotly_chart(fig)

        zone_counts = df['Zone'].value_counts().sort_index()
        zone_minutes = zone_counts / 60  # Sekunden → Minuten

        st.subheader("🕒 Verweildauer in Herzfrequenzzonen")
        for zone, minutes in zone_minutes.items():
            st.write(f"{zone}: {minutes:.1f} Minuten")

        avg_power_per_zone = df.groupby('Zone')['PowerOriginal'].mean()

        st.subheader("⚡ Durchschnittliche Leistung je Zone")
        for zone, avg_power in avg_power_per_zone.items():
            st.write(f"{zone}: {avg_power:.1f} Watt")