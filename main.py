import streamlit as st
import read_data
from PIL import Image

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

