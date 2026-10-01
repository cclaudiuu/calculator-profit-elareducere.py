from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# Configurare pagină Streamlit
st.set_page_config(
    page_title="Calculator Profit Elareducere", page_icon="💰", layout="wide"
)

# --- CONFIGURARE CONEXIUNE GOOGLE SHEETS ---


def incarca_date_din_cloud():
  try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    # Preluare credențiale din secrets de pe Streamlit Cloud
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # Numele foii tale Google
    sheet_name = "Baza_Date_Elareducere"
    sheet = client.open(sheet_name).sheet1

    # Citire date în DataFrame
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df, sheet
  except Exception as e:
    st.error(
        f"Eroare la conectarea cu baza de date din cloud: {e}. Asigură-te că"
        " ai configurat corect secțiunea Secrets în Streamlit."
    )
    return pd.DataFrame(), None


# --- INTERFAȚA APLICAȚIEI ---
st.title("📊 Calculator Profit - Elareducere")
st.write(
    "Aplicație partajată în timp real pentru introducerea și urmărirea"
    " datelor financiare."
)

# Încărcare date
df, sheet_connection = incarca_date_din_cloud()

if not df.empty:
  st.success("Datele au fost încărcate cu succes din cloud!")

  # Afișare tabel curent
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
        noua_linie = [str(data_intrare), client_furnizor, valoare, status]

        if sheet_connection:
          sheet_connection.append_row(noua_linie)
          st.success("Datele au fost salvate cu succes în cloud!")
          st.rerun()
      else:
        st.warning("Te rog să completezi cel puțin Numele Clientului/Furnizorului.")
else:
  st.info(
      "Se așteaptă configurarea bazei de date Google Sheets sau fișierul este"
      " gol."
  )
