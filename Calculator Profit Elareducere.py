from datetime import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configurare pagină Streamlit
st.set_page_config(
    page_title="Calculator Profit Elareducere", page_icon="💰", layout="wide"
)

st.title("📊 Calculator Profit - Elareducere")
st.write(
    "Aplicație partajată în timp real pentru introducerea și urmărirea"
    " datelor financiare."
)

try:
  # Conexiune la Google Sheets folosind pachetul dedicat
  conn = st.connection("gsheets", type=GSheetsConnection)
  df = conn.read(ttl=0)

  if df is not None:
    st.success("Datele au fost încărcate cu succes din cloud!")
    st.subheader("Date financiare existente:")
    st.dataframe(df, use_container_width=True)

    # Secțiune pentru adăugare date noi
    st.subheader("Adaugă o înregistrare nouă")

    with st.form("formular_date"):
      data_intrare = st.date_input("Data", datetime.today())
      client_furnizor = st.text_input("Client / Furnizor")
      valoare = st.number_input("Valoare (RON)", min_value=0.0, step=0.01)
      status = st.selectbox("Status", ["În curs", "Finalizat", "Anulat"])

      submit_button = st.form_submit_button(
          label="Salvează în Baza de Date Online"
      )

      if submit_button:
        if client_furnizor:
          noua_linie = pd.DataFrame([{
              "Data": str(data_intrare),
              "Client / Furnizor": client_furnizor,
              "Valoare": valoare,
              "Status": status,
          }])

          updated_df = pd.concat([df, noua_linie], ignore_index=True)
          conn.update(data=updated_df)

          st.success("Datele au fost salvate cu succes în cloud!")
          st.rerun()
        else:
          st.warning(
              "Te rog să completezi cel puțin Numele Clientului/Furnizorului."
          )
  else:
    st.info("Tabelul este gol sau se așteaptă date.")

except Exception as e:
  st.error(f"Eroare la conectarea cu Google Sheets: {e}")
