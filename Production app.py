import streamlit as st
import pandas as pd
import datetime
from data import load_data, save_data
from charts import show_charts
from filters import filter_data
from export import export_data


# Initialize the application
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

df = load_data()

# Sidebar Navigation
menu = st.sidebar.radio("Go to", ['Home', 'Production Charts', 'Export Data'])

if menu == 'Home':
    st.header("Production Data Overview")
    
    if not df.empty:
        st.dataframe(df)

        # 📊 **Dodajemy ogólne statystyki**
        st.header("Production Statistics")

        # Obliczanie średniej dziennej produkcji
        daily_average = df.groupby('Date')['Seal Count'].sum().mean()
        st.write(f"### Average Daily Production: {daily_average:.2f} seals")

        # Top 3 firmy
        top_companies = df.groupby('Company')['Seal Count'].sum().sort_values(ascending=False).head(3)
        st.write("### Top 3 Companies by Production")
        st.write(top_companies)

        # Top 3 operatorzy
        top_operators = df.groupby('Operator')['Seal Count'].sum().sort_values(ascending=False).head(3)
        st.write("### Top 3 Operators by Production")
        st.write(top_operators)

    st.sidebar.header("Add New Production Entry")
    with st.sidebar.form("production_form"):
        date = st.date_input("Production Date", datetime.date.today())
        company = st.text_input("Company Name")
        operator = st.text_input("Operator")
        seal_type = st.selectbox("Seal Type", ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings'])
        seals_count = st.number_input("Number of Seals", min_value=0, step=1)
        production_time = st.number_input("Production Time (Minutes)", min_value=0.0, step=0.1)
        downtime = st.number_input("Downtime (Minutes)", min_value=0.0, step=0.1)
        downtime_reason = st.text_input("Reason for Downtime")
        submitted = st.form_submit_button("Save Entry")

        if submitted:
            new_entry = pd.DataFrame({
                'Date': [date],
                'Company': [company],
                'Seal Count': [seals_count],
                'Operator': [operator],
                'Seal Type': [seal_type],
                'Production Time': [production_time],
                'Downtime': [downtime],
                'Reason for Downtime': [downtime_reason]
            })

            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)
            st.sidebar.success("Production entry saved successfully.")

if menu == 'Production Charts':
    show_charts(df)

if menu == 'Export Data':
    export_data(df)
