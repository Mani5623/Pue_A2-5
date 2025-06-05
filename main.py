import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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

    st.write("Geburtsdatum:", person_dict.get("date_of_birth", "Unbekannt"))
    st.write("Geschlecht:", person_dict.get("gender", "Unbekannt"))

with tab2:
    st.header("🫀 EKG-Datenanalyse")

    if person_dict and person_dict.get("ekg_tests"):
        ekg_dict = person_dict["ekg_tests"][0]
        ekg = EKGdata(ekg_dict)

        # Maximalpuls und Alter berechnen
        person_obj = Person(person_dict)
        max_hr = person_obj.calc_max_heart_rate(gender=person_dict.get("gender", "male"))
        age = person_obj.calc_age()
        person_id = person_obj.id

        # EKG-Peaks berechnen
        ekg.find_peaks(max_puls=max_hr)
        estimated_hr = ekg.estimate_hr()

        st.write(f"ID: **{person_id}**")
        st.write(f"Alter: **{age} Jahre**")
        st.write(f"Geschätzte Herzfrequenz: **{estimated_hr:.1f} bpm**")
        st.write(f"Geschätzte maximale Herzfrequenz: **{max_hr} bpm**")

        # EKG Zeitreihe anzeigen mit Peaks
        fig = ekg.plot_with_peaks()
        st.plotly_chart(fig, use_container_width=True)

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


