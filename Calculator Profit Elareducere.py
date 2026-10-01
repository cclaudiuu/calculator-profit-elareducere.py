import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# --- SECURITATE ---
parola_introdusa = st.text_input("Introdu parola de acces:", type="password")

if parola_introdusa != "Draghici1!":
  st.warning("Introdu parola pentru a vedea calculatorul.")
  st.stop()

st.title("Calcul Rapid - Elareducere")


# --- CONEXIUNEA LA GOOGLE SHEETS ---
@st.cache_resource
def init_connection():
  scope = [
      "https://spreadsheets.google.com/feeds",
      "https://www.googleapis.com/auth/drive",
  ]
  creds_dict = dict(st.secrets["gcp_service_account"])
  creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
  client = gspread.authorize(creds)
  sheet = client.open("Baza_Date_Elareducere").sheet1
  return sheet


def incarca_date_din_sheet():
  try:
    sheet = init_connection()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if df.empty:
      df = pd.DataFrame(
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
    return df
  except Exception as e:
    return pd.DataFrame(
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


def salveaza_in_sheet(df):
  try:
    sheet = init_connection()
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
  except Exception as e:
    st.error(f"Erore la salvarea în Google Sheets: {e}")


# --- INCARCARE INITIALA IN SESIUNE ---
if "istoric" not in st.session_state:
  st.session_state.istoric = incarca_date_din_sheet()

# Ordinea lunilor pentru sortare cronologica corecta
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


# --- PANOU LATERAL: RAPORT LA ZI (GLOBAL + DEFALCAT) ---
st.sidebar.header("📊 Indicatori la Zi")

if not st.session_state.istoric.empty:
  df_hist = st.session_state.istoric

  # 1. TOTAL GENERAL
  t_vanzari = df_hist["Vanzari"].sum()
  t_pub = df_hist["Publicitate"].sum()
  t_profit = df_hist["Profit Net"].sum()
  t_marja = (t_profit / t_vanzari) * 100 if t_vanzari > 0 else 0

  st.sidebar.subheader("🌟 Total General")
  st.sidebar.metric("Vanzari Acumulate", f"{t_vanzari:,.2f} lei")
  st.sidebar.metric("Profit Net Total", f"{t_profit:,.2f} lei")
  st.sidebar.metric("Marja Medie", f"{t_marja:.1f}%")

  st.sidebar.divider()

  # 2. DEFALCARE PE ENTITATI (DRAGHICI / CLAUDIU)
  st.sidebar.subheader("👥 Defalcare Entitati")

  for ent in ["Draghici", "Claudiu"]:
    df_ent_sub = df_hist[df_hist["Entitate"] == ent]
    if not df_ent_sub.empty:
      v_ent = df_ent_sub["Vanzari"].sum()
      p_ent = df_ent_sub["Profit Net"].sum()
      m_ent = (p_ent / v_ent) * 100 if v_ent > 0 else 0

      st.sidebar.markdown(f"**🔹 {ent}**")
      st.sidebar.text(
          f" • Vanzari: {v_ent:,.2f} lei\n • Profit: {p_ent:,.2f}"
          f" lei\n • Marja: {m_ent:.1f}%"
      )
    else:
      st.sidebar.markdown(f"**🔹 {ent}**: Fără date")
else:
  st.sidebar.info(
      "Nicio data inregistrata momentan pentru rapoartele la zi."
  )

st.sidebar.divider()

# --- MENIU LATERAL (NAVIGARE) ---
meniu = st.sidebar.radio(
    "Navigare", ["Simulator Rapid", "Jurnal Lunar & Istoric (Draghici / Claudiu)"]
)

# --- 1. SIMULATORUL RAPID ---
if meniu == "Simulator Rapid":
  st.subheader("Simulator Rapid (Slidere)")

  vanzari_lunare = st.slider(
      "Valoare vanzari fara transport (lei)",
      min_value=1000,
      max_value=50000,
      value=5000,
      step=50,
  )
  buget_reclama_lunar = st.slider(
      "Publicitate lunara (lei)",
      min_value=100,
      max_value=5000,
      value=1500,
      step=50,
  )

  cost_marfa = vanzari_lunare / 2.1
  comision_platforma = vanzari_lunare * 0.254
  profit_net = (
      vanzari_lunare - (cost_marfa + comision_platforma + buget_reclama_lunar)
  )
  marja_neta = (
      (profit_net / vanzari_lunare) * 100 if vanzari_lunare > 0 else 0
  )

  col_m1, col_m2 = st.columns(2)
  with col_m1:
    st.metric(label="Profit Net Lunar", value=f"{profit_net:.2f} lei")
  with col_m2:
    st.metric(label="Marja Neta", value=f"{marja_neta:.1f}%")

  date_grafic = []
  for v in range(0, 50001, 500):
    p = v - (v / 2.1) - (v * 0.254) - buget_reclama_lunar
    date_grafic.append({"Vanzari": v, "Profit Net": p})

  df_sim = pd.DataFrame(date_grafic)
  st.subheader("Evolutia profitului net in functie de volumul vanzarilor")
  st.line_chart(df_sim.set_index("Vanzari"))

# --- 2. JURNAL LUNAR & ISTORIC ---
elif meniu == "Jurnal Lunar & Istoric (Draghici / Claudiu)":
  st.subheader("Jurnal Financiar pe Luni")

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

      # Sincronizare cu Google Sheets la salvare
      salveaza_in_sheet(st.session_state.istoric)

      st.success(
          f"Datele pentru {entitate} ({luna} {an}) au fost salvate și"
          " sincronizate cu succes!"
      )

  st.divider()
  st.subheader("📋 Istoric & Vizualizare Detaliata")

  if not st.session_state.istoric.empty:
    st.dataframe(st.session_state.istoric, use_container_width=True)

    # --- SELECTIE SPECIFICA LUNA / ENTITATE ---
    st.markdown("### 🔍 Vizualizare rapida pe o luna anume")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
      ent_select = st.selectbox(
          "Filtreaza Entitate", ["Draghici", "Claudiu"], key="f_ent"
      )
    with col_f2:
      ani_disponibili = sorted(
          st.session_state.istoric["An"].unique().tolist()
      )
      an_select = st.selectbox(
          "Filtreaza An",
          ani_disponibili if ani_disponibili else [2026],
          key="f_an",
      )
    with col_f3:
      luni_disponibile = st.session_state.istoric[
          (st.session_state.istoric["Entitate"] == ent_select)
          & (st.session_state.istoric["An"] == an_select)
      ]["Luna"].tolist()
      luna_select = st.selectbox(
          "Filtreaza Luna",
          luni_disponibile if luni_disponibile else ["Niciuna disponibila"],
          key="f_luna",
      )

    if luna_select != "Niciuna disponibila":
      rand_luna = st.session_state.istoric[
          (st.session_state.istoric["Entitate"] == ent_select)
          & (st.session_state.istoric["An"] == an_select)
          & (st.session_state.istoric["Luna"] == luna_select)
      ]
      if not rand_luna.empty:
        r = rand_luna.iloc[0]
        st.markdown(
            f"Valori pentru **{ent_select}** ({luna_select} {an_select}):"
        )
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Vanzari", f"{r['Vanzari']} lei")
        m2.metric("Publicitate", f"{r['Publicitate']} lei")
        m3.metric("Profit Net", f"{r['Profit Net']} lei")
        m4.metric("Marja Neta", f"{r['Marja Neta (%)']}%")

    # --- STERGERE INREGISTRARE ---
    with st.expander("⚙️ Optiuni de stergere inregistrare gresita"):
      optiuni_stergere = [
          f"{row.Index}: {row.Entitate} - {row.Luna} {row.An} (Vanzari:"
          f" {row.Vanzari} lei)"
          for row in st.session_state.istoric.itertuples()
      ]
      selectie_de_sters = st.selectbox(
          "Alege randul de sters:", ["Niciuna"] + optiuni_stergere
      )
      if selectie_de_sters != "Niciuna":
        if st.button("Sterge randul selectat"):
          idx = int(selectie_de_sters.split(":")[0])
          st.session_state.istoric = (
              st.session_state.istoric.drop(idx).reset_index(drop=True)
          )

          # Sincronizare cu Google Sheets la stergere
          salveaza_in_sheet(st.session_state.istoric)

          st.success("Inregistrarea a fost stearsa și sincronizată!")
          st.rerun()

    # --- GRAFICE INTUITIVE PE ENTITATI ---
    st.divider()
    st.subheader("📈 Evolutia financiara in timp")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
      entitate_grafic = st.selectbox(
          "Alege entitatea pentru grafice", ["Draghici", "Claudiu"], key="g_ent"
      )

    df_ent = st.session_state.istoric[
        st.session_state.istoric["Entitate"] == entitate_grafic
    ].copy()

    if not df_ent.empty:
      df_ent["Luna_Numar"] = df_ent.Luna.map(ordinea_luni)
      df_ent = df_ent.sort_values(by=["An", "Luna_Numar"])
      df_ent["Perioada"] = df_ent["Luna"] + " " + df_ent.An.astype(str)

      st.markdown(
          f"**1. Comparatie Valori Totale (Lei) pentru {entitate_grafic}**"
      )
      st.bar_chart(
          df_ent.set_index("Perioada")[
              ["Vanzari", "Profit Net", "Publicitate"]
          ]
      )

      st.markdown(f"**2. Evolutia Marjei Nete (%) pentru {entitate_grafic}**")
      st.line_chart(df_ent.set_index("Perioada")[["Marja Neta (%)"]])
    else:
      st.info("Nu exista date inregistrate pentru aceasta entitate.")
  else:
    st.info("Inca nu ai salvat nicio inregistrare în jurnal.")
