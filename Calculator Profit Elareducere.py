import pandas as pd
import streamlit as st

# User si parola
parola_introdusa = st.text_input("Introdu parola de acces:", type="password")

if parola_introdusa != "Draghici1!":
  st.warning("Introdu parola pentru a vedea calculatorul.")
  st.stop()  # Opreste executia aplicatiei daca parola este gresita

# Titlu aplicatie
st.title("Calculator Profit pentru Elareducere")

# Sliders interactive
vanzari_lunare = st.slider(
    "Valoare vanzari fara transport (lei)",
    min_value=0,
    max_value=15000,
    value=5000,
    step=50,
)
buget_reclama_lunar = st.slider(
    "Publicitate lunara (lei)",
    min_value=0,
    max_value=2000,
    value=1500,
    step=50,
)

# Calcule
cost_marfa = vanzari_lunare / 2.1
comision_platforma = vanzari_lunare * 0.254
profit_net = (
    vanzari_lunare - (cost_marfa + comision_platforma + buget_reclama_lunar)
)
marja_neta = (
    (profit_net / vanzari_lunare) * 100 if vanzari_lunare > 0 else 0
)

# Afisare rezultate
st.metric(label="Profit Net Lunar", value=f"{profit_net:.2f} lei")
st.metric(label="Marja Neta", value=f"{marja_neta:.1f}%")

# Generare date pentru grafic
date_grafic = []
for v in range(0, 15001, 500):
  p = v - (v / 2.1) - (v * 0.254) - buget_reclama_lunar
  date_grafic.append({"Vanzari": v, "Profit Net": p})

df = pd.DataFrame(date_grafic)

st.subheader("Evolutia profitului net in functie de volumul vanzarilor")
st.line_chart(df.set_index("Vanzari"))
