import pandas as pd
import streamlit as st

# User si parola
parola_introdusa = st.text_input("Introdu parola de acces:", type="password")

if parola_introdusa != "Draghici1!":
  st.warning("Te rog să introduci parola corecta pentru a vedea calculatorul.")
  st.stop()  # Opreste executia aplicatiei daca parola este gresita

# De aici în colo vine codul tău normal de calculator (st.title, slidere, etc.)
st.title("Calculator Profit Parteneriat Elareducere")

# Sliders interactive
vanzari_saptamanale = st.slider(
    "Vânzări săptămânale (lei)", min_value=3000, max_value=15000, value=5000, step=250
)
buget_reclama_lunar = st.slider(
    "Publicitate lunară (lei)", min_value=500, max_value=3000, value=1500, step=100
)

# Calcule
reclama_saptamanala = buget_reclama_lunar / 4
cost_marfa = vanzari_saptamanale / 2.1
comision_platforma = vanzari_saptamanale * 0.254
profit_net = (
    vanzari_saptamanale
    - (cost_marfa + comision_platforma + reclama_saptamanala)
)
marja_neta = (
    (profit_net / vanzari_saptamanale) * 100 if vanzari_saptamanale > 0 else 0
)

# Afișare rezultate
st.metric(label="Profit Net Săptămânal", value=f"{profit_net:.2f} lei")
st.metric(label="Marja Netă", value=f"{marja_neta:.1f}%")

# Generare date pentru grafic
date_grafic = []
for v in range(3000, 15001, 500):
  p = v - (v / 2.1) - (v * 0.254) - reclama_saptamanala
  date_grafic.append({"Vânzări": v, "Profit Net": p})

df = pd.DataFrame(date_grafic)

st.subheader("Evoluția profitului net în funcție de volumul vânzărilor")
st.line_chart(df.set_index("Vânzări"))