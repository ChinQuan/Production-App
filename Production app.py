import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from io import BytesIO
from fpdf import FPDF

# Uwierzytelnianie użytkownika na podstawie pliku users.xlsx
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Logowanie do aplikacji")
    username_input = st.text_input("Nazwa użytkownika")
    password_input = st.text_input("Hasło", type="password")
    if st.button("Zaloguj"):
        try:
            users_df = pd.read_excel("users.xlsx")
        except Exception as e:
            st.error("Nie znaleziono pliku users.xlsx z danymi użytkowników!")
        else:
            # Sprawdzenie danych logowania
            row = users_df[users_df["Username"] == username_input]
            if not row.empty and str(row.iloc[0]["Password"]) == str(password_input):
                # Ustawienie stanu sesji po poprawnym zalogowaniu
                st.session_state.authenticated = True
                st.session_state.username = str(row.iloc[0]["Username"])
                st.session_state.role = str(row.iloc[0]["Role"])
                st.experimental_rerun()
            else:
                st.error("Błędna nazwa użytkownika lub hasło. Spróbuj ponownie.")
    st.stop()

# Główna część aplikacji po zalogowaniu
username = st.session_state.username
role = st.session_state.role

st.title("Rejestr produkcji uszczelek")
st.sidebar.markdown(f"**Zalogowano jako:** {username} ({role})")
logout = st.sidebar.button("Wyloguj")
if logout:
    st.session_state.authenticated = False
    st.experimental_rerun()

# Wczytanie danych produkcyjnych z CSV (lub utworzenie pustego pliku)
csv_file = "production_data.csv"
if not os.path.isfile(csv_file):
    # Tworzenie pustego pliku CSV z nagłówkami
    cols = ["Date", "Company", "Operator", "SealType", "Quantity", "ProductionTime", "Downtime", "DowntimeReason"]
    pd.DataFrame(columns=cols).to_csv(csv_file, index=False)
# Wczytanie danych do DataFrame
df = pd.read_csv(csv_file, parse_dates=["Date"])
# Zamiana NaN na pusty tekst w kolumnie powodu przestoju (jeśli występuje)
if "DowntimeReason" in df.columns:
    df["DowntimeReason"] = df["DowntimeReason"].fillna("")

# Sekcja dodawania nowego zlecenia produkcyjnego
st.subheader("Dodaj nowe zlecenie produkcyjne")
with st.form("add_production_form", clear_on_submit=True):
    # Ułożenie pól formularza w układzie kolumn dla czytelności
    col1, col2 = st.columns(2)
    with col1:
        date_val = st.date_input("Data", value=pd.Timestamp.today())
        company_val = st.text_input("Firma")
    with col2:
        st.text_input("Operator", value=username, disabled=True)
        # Lista typów uszczelek (można dostosować/rozszerzyć)
        seal_types = ["RS09A", "RS10B", "TypC"]  # przykładowe typy
        seal_type_val = st.selectbox("Typ uszczelki", seal_types)
    col3, col4, col5 = st.columns(3)
    with col3:
        quantity_val = st.number_input("Liczba uszczelek", min_value=0, value=0, step=1)
    with col4:
        prod_time_val = st.number_input("Czas produkcji (minuty)", min_value=0, value=0, step=1)
    with col5:
        downtime_val = st.number_input("Czas przestoju (minuty)", min_value=0, value=0, step=1)
    reason_val = st.text_input("Powód przestoju")
    submitted = st.form_submit_button("Dodaj")
    
if submitted:
    # Przygotowanie nowego wpisu
    new_entry = {
        "Date": pd.to_datetime(date_val),
        "Company": company_val,
        "Operator": username,
        "SealType": seal_type_val,
        "Quantity": int(quantity_val),
        "ProductionTime": int(prod_time_val),
        "Downtime": int(downtime_val),
        "DowntimeReason": str(reason_val) if reason_val else ""
    }
    # Dopisanie do DataFrame i zapis do CSV
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(csv_file, index=False, date_format="%Y-%m-%d")
    st.success("✅ Pomyślnie dodano zlecenie produkcyjne.")

# Filtrowanie danych według operatora, firmy, typu uszczelki
df_filtered = df.copy()
# Filtruj po operatorze (dla operatorów nie-admin ogranicz dane do własnych)
if role.lower() != "admin":
    df_filtered = df_filtered[df_filtered["Operator"] == username]
    # Nie pokazujemy filtra operatora dla zwykłego użytkownika
    ops_list = [username]
else:
    ops_list = sorted(df["Operator"].unique().tolist())
    selected_ops = st.sidebar.multiselect("Filtruj operatorów", ops_list, default=ops_list)
    if selected_ops:
        # Jeśli wybrano podzbiór operatorów, filtruj
        df_filtered = df_filtered[df_filtered["Operator"].isin(selected_ops)]
# Filtruj po firmie
company_list = sorted(df_filtered["Company"].unique().tolist())
selected_companies = st.sidebar.multiselect("Filtruj firmy", company_list, default=company_list)
if selected_companies:
    df_filtered = df_filtered[df_filtered["Company"].isin(selected_companies)]
# Filtruj po typie uszczelki
type_list = sorted(df_filtered["SealType"].unique().tolist())
selected_types = st.sidebar.multiselect("Filtruj typy uszczelek", type_list, default=type_list)
if selected_types:
    df_filtered = df_filtered[df_filtered["SealType"].isin(selected_types)]

# Sprawdzenie, czy po filtrach są dane
if df_filtered.empty:
    st.warning("Brak danych dla wybranych filtrów.")
else:
    # Przygotowanie danych do wykresów (agregacje)
    # Dzienne trendy produkcji (suma dzienna)
    daily_counts = df_filtered.groupby(df_filtered["Date"].dt.date)["Quantity"].sum()
    # Produkcja tygodniowa (suma na tydzień ISO)
    iso_calendar = df_filtered["Date"].dt.isocalendar()
    week_labels = iso_calendar.year.astype(str) + "-W" + iso_calendar.week.astype(str).str.zfill(2)
    weekly_counts = df_filtered.groupby(week_labels)["Quantity"].sum().sort_index()
    # Produkcja miesięczna (suma na miesiąc)
    month_labels = df_filtered["Date"].dt.strftime("%Y-%m")
    monthly_counts = df_filtered.groupby(month_labels)["Quantity"].sum().sort_index()
    # Produkcja według firm
    company_counts = df_filtered.groupby("Company")["Quantity"].sum().sort_values(ascending=False)
    # Produkcja według typów uszczelek
    type_counts = df_filtered.groupby("SealType")["Quantity"].sum().sort_values(ascending=False)
    # Produkcja według operatorów
    operator_counts = df_filtered.groupby("Operator")["Quantity"].sum().sort_values(ascending=False)
    
    # Ustawienie układu kolumn dla wykresów
    col_left, col_right = st.columns(2)
    # Wykres 1: Dzienne trendy produkcji
    with col_left:
        st.subheader("Trendy dzienne produkcji")
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        x_dates = [str(d) for d in daily_counts.index]
        y_values = daily_counts.values
        bars = ax1.bar(x_dates, y_values, color="#4c78a8")
        ax1.bar_label(bars)
        ax1.set_xlabel("Data")
        ax1.set_ylabel("Liczba uszczelek")
        # Obrót etykiet dat dla czytelności
        plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig1)
    # Wykres 2: Produkcja tygodniowa
    with col_left:
        st.subheader("Produkcja tygodniowa")
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        x_weeks = weekly_counts.index.tolist()
        y_weeks = weekly_counts.values
        bars = ax2.bar(x_weeks, y_weeks, color="#4c78a8")
        ax2.bar_label(bars)
        ax2.set_xlabel("Tydzień")
        ax2.set_ylabel("Liczba uszczelek")
        plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig2)
    # Wykres 3: Produkcja miesięczna
    with col_left:
        st.subheader("Produkcja miesięczna")
        fig3, ax3 = plt.subplots(figsize=(5, 3))
        x_months = monthly_counts.index.tolist()
        y_months = monthly_counts.values
        bars = ax3.bar(x_months, y_months, color="#4c78a8")
        ax3.bar_label(bars)
        ax3.set_xlabel("Miesiąc")
        ax3.set_ylabel("Liczba uszczelek")
        plt.setp(ax3.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig3)
    # Wykres 4: Produkcja według firm
    with col_right:
        st.subheader("Produkcja według firm")
        fig4, ax4 = plt.subplots(figsize=(5, 3))
        x_comp = company_counts.index.tolist()
        y_comp = company_counts.values
        bars = ax4.bar(x_comp, y_comp, color="#f58518")
        ax4.bar_label(bars)
        ax4.set_xlabel("Firma")
        ax4.set_ylabel("Liczba uszczelek")
        plt.setp(ax4.get_xticklabels(), rotation=0, ha="center")
        st.pyplot(fig4)
    # Wykres 5: Produkcja według typów uszczelek
    with col_right:
        st.subheader("Produkcja według typów uszczelek")
        fig5, ax5 = plt.subplots(figsize=(5, 3))
        x_types = type_counts.index.tolist()
        y_types = type_counts.values
        bars = ax5.bar(x_types, y_types, color="#f58518")
        ax5.bar_label(bars)
        ax5.set_xlabel("Typ uszczelki")
        ax5.set_ylabel("Liczba uszczelek")
        plt.setp(ax5.get_xticklabels(), rotation=0, ha="center")
        st.pyplot(fig5)
    # Wykres 6: Produkcja według operatorów
    with col_right:
        st.subheader("Produkcja według operatorów")
        fig6, ax6 = plt.subplots(figsize=(5, 3))
        x_ops = operator_counts.index.tolist()
        y_ops = operator_counts.values
        bars = ax6.bar(x_ops, y_ops, color="#f58518")
        ax6.bar_label(bars)
        ax6.set_xlabel("Operator")
        ax6.set_ylabel("Liczba uszczelek")
        plt.setp(ax6.get_xticklabels(), rotation=0, ha="center")
        st.pyplot(fig6)
    
    # Sekcja eksportu danych
    st.subheader("Eksport danych")
    # Przygotowanie danych do eksportu (aktualny df_filtered)
    # Eksport do Excel
    output_xlsx = BytesIO()
    with pd.ExcelWriter(output_xlsx, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="ProductionData")
    excel_data = output_xlsx.getvalue()
    st.download_button(label="📥 Pobierz dane (Excel)",
                       data=excel_data,
                       file_name="production_data_export.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    # Eksport do PDF (podsumowanie)
    # Obliczenie podstawowych statystyk
    total_seals = int(df_filtered["Quantity"].sum())
    total_prod_time = int(df_filtered["ProductionTime"].sum())
    total_downtime = int(df_filtered["Downtime"].sum())
    unique_days = df_filtered["Date"].dt.date.nunique()
    avg_per_day = total_seals / unique_days if unique_days else 0
    # Opis filtrów dla raportu
    filters_info = []
    if role.lower() == "admin":
        if 'selected_ops' in locals() and selected_ops and set(selected_ops) != set(ops_list):
            filters_info.append(f"Operator = {', '.join(selected_ops)}")
    if selected_companies and set(selected_companies) != set(company_list):
        filters_info.append(f"Firma = {', '.join(selected_companies)}")
    if selected_types and set(selected_types) != set(type_list):
        filters_info.append(f"Typ = {', '.join(selected_types)}")
    if filters_info:
        filters_text = "; ".join(filters_info)
    else:
        filters_text = "Brak (uwzględniono wszystkie dane)"
    # Tworzenie PDF w pamięci
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Production Data Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Łączna liczba uszczelek: {total_seals}", ln=True)
    pdf.cell(0, 8, f"Sumaryczny czas produkcji (min): {total_prod_time}", ln=True)
    pdf.cell(0, 8, f"Sumaryczny czas przestoju (min): {total_downtime}", ln=True)
    pdf.cell(0, 8, f"Średnia uszczelek na dzień: {avg_per_day:.2f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 11)
    pdf.cell(0, 8, f"Filtry: {filters_text}", ln=True)
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    st.download_button(label="📄 Pobierz raport (PDF)",
                       data=pdf_bytes,
                       file_name="production_data_report.pdf",
                       mime="application/pdf")
