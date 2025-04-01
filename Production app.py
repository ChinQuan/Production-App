import streamlit as st
import pandas as pd
import datetime
import os
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

# Wyczyść cache Streamlit
if hasattr(st, 'cache_data'):
    st.cache_data.clear()
if hasattr(st, 'cache_resource'):
    st.cache_resource.clear()

# Usuń katalog cache Streamlit jeśli istnieje
if os.path.exists(".streamlit"):
    shutil.rmtree(".streamlit")

# Initialize the application
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Load users data from users.xlsx
def load_users():
    try:
        return pd.read_excel('users.xlsx', sheet_name='Users')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Username', 'Password', 'Role'])

users_df = load_users()

# User session management
if 'user' not in st.session_state:
    st.session_state.user = None

# Function to authenticate user
def login(username, password):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    else:
        return None

# Function to log out
def logout():
    st.session_state.user = None

# Load production data from CSV
def load_data():
    try:
        return pd.read_csv('production_data.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time', 'Downtime', 'Reason for Downtime'])

df = load_data()

# Save Data
def save_data():
    df.to_csv('production_data.csv', index=False)

# Login Panel
if st.session_state.user is None:
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user = login(username, password)
        if user is not None:
            st.session_state.user = user
            st.sidebar.success(f"Logged in as {user['Username']}")
        else:
            st.sidebar.error("Invalid username or password")

else:
    st.sidebar.write(f"Logged in as {st.session_state.user['Username']}")
    if st.sidebar.button("Logout"):
        logout()

# Sidebar Navigation
if st.session_state.user is not None:
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Go to", ['Home', 'Production Charts', 'Export Data'])

    if menu == 'Home':
        st.header("Production Data Overview")

        if not df.empty:
            st.dataframe(df)

            st.sidebar.header("Add New Production Entry")
            with st.sidebar.form("production_form"):
                date = st.date_input("Production Date", datetime.date.today())
                company = st.text_input("Company Name")
                operator = st.session_state.user['Username']
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
                    save_data()
                    st.sidebar.success("Production entry saved successfully.")

    if menu == 'Production Charts':
        st.header("Production Charts")

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

    if menu == 'Export Data':
        st.header("Export Data")

        if st.button("Download as Excel"):
            df.to_excel('production_data_export.xlsx', index=False)
            with open('production_data_export.xlsx', 'rb') as f:
                st.download_button(label="Download Excel file", data=f, file_name="production_data_export.xlsx")

        if st.button("Download as PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Production Data Report", ln=True, align='C')
            pdf.output("production_data_report.pdf")
            with open("production_data_report.pdf", "rb") as f:
                st.download_button(label="Download PDF file", data=f, file_name="production_data_report.pdf")
