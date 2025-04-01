import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Initialize the application
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Load production data from CSV
def load_data():
    try:
        return pd.read_csv('production_data.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time', 'Downtime', 'Reason for Downtime'])

def save_data(df):
    df.to_csv('production_data.csv', index=False)

df = load_data()

# Sidebar Navigation
menu = st.sidebar.radio("Go to", ['Home', 'Production Charts'])

if menu == 'Home':
    st.header("Production Data Overview")

    if not df.empty:
        st.dataframe(df)

        # 📊 **Ogólne statystyki**
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
    st.header("Production Charts")

    if not df.empty:
        # Filtracja danych
        selected_operator = st.sidebar.selectbox("Select Operator", options=['All'] + sorted(df['Operator'].unique().tolist()))
        selected_company = st.sidebar.selectbox("Select Company", options=['All'] + sorted(df['Company'].unique().tolist()))
        selected_seal_type = st.sidebar.selectbox("Select Seal Type", options=['All'] + sorted(df['Seal Type'].unique().tolist()))

        filtered_df = df.copy()
        
        if selected_operator != 'All':
            filtered_df = filtered_df[filtered_df['Operator'] == selected_operator]
        if selected_company != 'All':
            filtered_df = filtered_df[filtered_df['Company'] == selected_company]
        if selected_seal_type != 'All':
            filtered_df = filtered_df[filtered_df['Seal Type'] == selected_seal_type]

        st.write("Filtered Data", filtered_df)

        # Wykresy
        col1, col2 = st.columns([2, 1])

        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            daily_trend = filtered_df.groupby('Date')['Seal Count'].sum().reset_index()
            sns.lineplot(x='Date', y='Seal Count', data=daily_trend, ax=ax)
            ax.set_title("Daily Production Trend")
            st.pyplot(fig)

        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            company_trend = filtered_df.groupby('Company')['Seal Count'].sum().reset_index()
            sns.barplot(x='Company', y='Seal Count', data=company_trend, ax=ax)
            ax.set_title("Production by Company")
            st.pyplot(fig)

        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            seal_type_trend = filtered_df.groupby('Seal Type')['Seal Count'].sum().reset_index()
            sns.barplot(x='Seal Type', y='Seal Count', data=seal_type_trend, ax=ax)
            ax.set_title("Production by Seal Type")
            st.pyplot(fig)

        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            operator_trend = filtered_df.groupby('Operator')['Seal Count'].sum().reset_index()
            sns.barplot(x='Operator', y='Seal Count', data=operator_trend, ax=ax)
            ax.set_title("Production by Operator")
            st.pyplot(fig)
