import pandas as pd
import streamlit as st

# --- SECURITATE ---
parola_introdusa = st.text_input("Introdu parola de acces:", type="password")

if parola_introdusa != "Draghici1!":
  st.warning("Introdu parola pentru a vedea calculatorul.")
  st.stop()

st.title("Dashboard Financiar - Elareducere")

# --- SELECTIE ENTITATE SI PERIOADA ---
col1, col2, col3 = st.columns(3)
with col1:
  entitate = st.selectbox("Selecteaza Entitatea", ["Draghici", "Claudiu"])
with col2:
  luna = st.selectbox(
      "Luna",
      [
          "Ianuarie",
          "Februarie",
          "Martie",
          "Aprilie",
          "Mai",
          "Iunie",
          "Iulie",
          "August",
          "Septembrie",
          "Octombrie",
          "Noiembrie",
          "Decembrie",
      ],
  )
with col3:
  an = st.selectbox("Anul", [2026, 2027, 2028])

st.divider()

# --- INTRODUCERE DATE LUNARE ---
st.subheader(f"Date financiare pentru: {entitate} ({luna} {an})")

vanzari_lunare = st.number_input(
    "Valoare vanzari fara transport (lei)",
    min_value=0.0,
    max_value=100000.0,
    value=5000.0,
    step=50.0,
)
buget_reclama_lunar = st.number_input(
    "Publicitate lunara (lei)",
    min_value=0.0,
    max_value=10000.0,
    value=1500.0,
    step=50.0,
)

# --- CALCULE ---
cost_marfa = vanzari_lunare / 2.1
comision_platforma = vanzari_lunare * 0.254
profit_net = (
    vanzari_lunare - (cost_marfa + comision_platforma + buget_reclama_lunar)
)
marja_neta = (
    (profit_net / vanzari_lunare) * 100 if vanzari_lunare > 0 else 0
)

# --- AFISARE REZULTATE CURENTE ---
st.markdown("### Rezultate Luna Curenta")
c1, c2 = st.columns(2)
with c1:
  st.metric(label="Profit Net Lunar", value=f"{profit_net:.2f} lei")
with c2:
  st.metric(label="Marja Neta", value=f"{marja_neta:.1f}%")

# --- SIMULARE / GRAFIC DE EVOLUTIE ---
st.divider()
st.subheader("Simulare Evolutie Profit in functie de Vanzari")
date_grafic = []
for v in range(0, 15001, 500):
  p = v - (v / 2.1) - (v * 0.254) - buget_reclama_lunar
  date_grafic.append({"Vanzari": v, "Profit Net": p})

df = pd.DataFrame(date_grafic)
st.line_chart(df.set_index("Vanzari"))
