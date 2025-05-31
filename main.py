import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"
import read_data
import read_pandas
from PIL import Image


tab1, tab2 = st.tabs(["EKG Daten", "Leistungstest"])

with tab1:
    st.write("# EKG APP")
    st.write("## Versuchsperson auswählen")

    # Liste der Namen laden
    person_names = read_data.get_person_list()
    DEFAULT_IMAGE_PATH = "data/pictures/none.jpg"

    # Auswahlbox für Versuchsperson
    selected_name = st.selectbox("Versuchsperson", options=person_names, key="sbVersuchsperson")

    # Personendaten finden
    person = read_data.find_person_data_by_name(selected_name)
    picture_path = person.get("picture_path", DEFAULT_IMAGE_PATH)

    # Name anzeigen
    st.write("Der Name ist:", selected_name)

    # Bild anzeigen
    try:
        image = Image.open(picture_path)
        st.image(image, caption=selected_name)
    except FileNotFoundError:
        st.warning("Bilddatei nicht gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Laden des Bilds: {e}")


    st.write("Bildpfad:", picture_path)
    st.write("Personendaten:", person["date_of_birth"])

with tab2:
    st.write("# Leistungstest")
    max_hr_input = st.number_input("Maximale Herzfrequenz", min_value=0, max_value=250, step=1)
    
    if st.button("Absenden"):
        df = read_pandas.read_my_csv()
        zones = read_pandas.get_zone_limit(max_hr_input)
        
        # Assign zones to each heart rate value
        df['Zone'] = df['HeartRate'].apply(lambda x: read_pandas.assign_zone(x, zones))
        
        fig = read_pandas.make_plot(df, zones)
        st.plotly_chart(fig)


    



