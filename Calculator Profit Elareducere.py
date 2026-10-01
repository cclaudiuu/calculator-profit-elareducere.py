import pandas as pd
import streamlit as st

# --- SECURITATE ---
parola_introdusa = st.text_input("Introdu parola de acces:", type="password")

if parola_introdusa != "Draghici1!":
  st.warning("Introdu parola pentru a vedea calculatorul.")
  st.stop()

st.title("Calcul rapid - Elareducere")

# --- MENIU LATERAL (NAVIGARE) ---
meniu = st.sidebar.radio(
    "Navigare", ["Simulator Rapid", "Jurnal Lunar & Istoric (Draghici / Claudiu)"]
)

# Ordinea lunilor pentru sortare corecta in grafice
ordinea_luni = {
    "Ianuarie": 1,
    "Februarie": 2,
    "Martie": 3,
    "Aprilie": 4,
    "Mai": 5,
    "Iunie": 6,
    "Iulie": 7,
    "August": 8,
    "Septembrie": 9,
    "Octombrie": 10,
    "Noiembrie": 11,
    "Decembrie": 12,
}

# --- 1. SIMULATORUL RAPID (Varianta ta clasică) ---
if meniu == "Simulator Rapid":
  st.subheader("Simulator Rapid (Slidere)")

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

  df_sim = pd.DataFrame(date_grafic)
  st.subheader("Evolutia profitului net in functie de volumul vanzarilor")
  st.line_chart(df_sim.set_index("Vanzari"))

# --- 2. JURNAL LUNAR & ISTORIC ---
elif meniu == "Jurnal Lunar & Istoric (Draghici / Claudiu)":
  st.subheader("Jurnal Financiar pe Luni")

  # Initializare memorie pentru istoricul in sesiune
  if "istoric" not in st.session_state:
    st.session_state.istoric = pd.DataFrame(
        columns=[
            "Entitate",
            "An",
            "Luna",
            "Vanzari",
            "Publicitate",
            "Profit Net",
            "Marja Neta (%)",
        ]
    )

  with st.form("form_inregistrare"):
    col1, col2, col3 = st.columns(3)
    with col1:
      entitate = st.selectbox("Entitate", ["Draghici", "Claudiu"])
    with col2:
      an = st.selectbox("An", [2026, 2027, 2028])
    with col3:
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

    v_real = st.number_input(
        "Vanzari reale fara transport (lei)", min_value=0.0, value=5000.0, step=50.0
    )
    p_real = st.number_input(
        "Publicitate lunara reala (lei)", min_value=0.0, value=1500.0, step=50.0
    )

    buton_salvare = st.form_submit_button("Salveaza in istoric")

    if buton_salvare:
      c_marfa = v_real / 2.1
      c_plat = v_real * 0.254
      p_net = v_real - (c_marfa + c_plat + p_real)
      m_neta = (p_net / v_real) * 100 if v_real > 0 else 0

      noua_inregistrare = pd.DataFrame({
          "Entitate": [entitate],
          "An": [an],
          "Luna": [luna],
          "Vanzari": [v_real],
          "Publicitate": [p_real],
          "Profit Net": [round(p_net, 2)],
          "Marja Neta (%)": [round(m_neta, 1)],
      })

      st.session_state.istoric = pd.concat(
          [st.session_state.istoric, noua_inregistrare], ignore_index=True
      )
      st.success(
          f"Datele pentru {entitate} ({luna} {an}) au fost salvate cu succes!"
      )

  # --- GESTIONARE SI STERGERE INREGISTRARI ---
  st.divider()
  st.subheader("Istoric Inregistrari (Gestionare)")

  if not st.session_state.istoric.empty:
    # Afisam tabelul complet
    st.dataframe(st.session_state.istoric, use_container_width=True)

    # Optiune de stergere a unei inregistrari gresite
    st.markdown("### Sterge o inregistrare gresita")
    optiuni_stergere = [
        f"{row.Index}: {row.Entitate} - {row.Luna} {row.An} (Vanzari: {row.Vanzari} lei)"
        for row in st.session_state.istoric.itertuples()
    ]

    selectie_de_sters = st.selectbox(
        "Alege inregistrarea pe care doresti o stergi:", ["Niciuna"] + optiuni_stergere
    )

    if selectie_de_sters != "Niciuna":
      if st.button("Sterge randul selectat"):
        index_de_sters = int(selectie_de_sters.split(":")[0])
        st.session_state.istoric = (
            st.session_state.istoric.drop(index_de_sters)
            .reset_index(drop=True)
        )
        st.success("Înregistrarea a fost ștersă cu succes! Reîncarcă pagina.")
        st.rerun()

    # --- GRAFICE DE EVOLUTIE ---
    st.divider()
    entitate_selectata = st.selectbox(
        "Alege entitatea pentru graficul de evolutie", ["Draghici", "Claudiu"]
    )
    df_entitate = st.session_state.istoric[
        st.session_state.istoric["Entitate"] == entitate_selectata
    ].copy()

    if not df_entitate.empty:
      st.markdown(
          f"### Evolutie in timp pentru: **{entitate_selectata}**"
      )

      # Sortam corect cronologic dupa an si luna
      df_entitate["Luna_Numar"] = df_entitate["Luna"].map(ordinea_luni)
      df_entitate = df_entitate.sort_values(by=["An", "Luna_Numar"])

      df_entitate["Perioada"] = (
          df_entitate["Luna"] + " " + df_entitate["An"].astype(str)
      )

      # Grafic Vanzari vs Profit Net
      st.subheader("Evolutie Vanzari vs Profit Net vs Publicitate (lei)")
      st.line_chart(
          df_entitate.set_index("Perioada")[
              ["Vanzari", "Profit Net", "Publicitate"]
          ]
      )

      # Grafic Marja Neta
      st.subheader("Evolutie Marja Neta (%)")
      st.line_chart(df_entitate.set_index("Perioada")[["Marja Neta (%)"]])
    else:
      st.info(
          "Nu există încă date înregistrate pentru această entitate. Completează"
          " formularul de sus."
      )
  else:
    st.info("Încă nu ai salvat nicio înregistrare. Folosește formularul de sus.")
