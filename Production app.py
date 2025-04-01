import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import openpyxl
from fpdf import FPDF
import io
import seaborn as sns
import os
import requests
import base64


# Initialize the application
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")


# Initialize user session
if 'user' not in st.session_state:
    st.session_state.user = None


# Load users file
try:
    users_df = pd.read_excel('users.xlsx', sheet_name='Users')
except FileNotFoundError:
    users_df = pd.DataFrame({'Username': ['admin'], 'Password': ['admin'], 'Role': ['Admin']})
    with pd.ExcelWriter('users.xlsx', engine='openpyxl', mode='w') as writer:
        users_df.to_excel(writer, sheet_name='Users', index=False)


def login(username, password):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    else:
        return None


def logout():
    st.session_state.user = None


# GitHub Token and Repo Details
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = 'ChinQuan/Production-App'
FILE_PATH = 'production_data.csv'


def upload_to_github(content):
    url = f'https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json().get('sha')
    else:
        sha = None

    data = {
        'message': 'Updating production data',
        'content': base64.b64encode(content.encode()).decode('utf-8')
    }

    if sha:
        data['sha'] = sha

    response = requests.put(url, json=data, headers=headers)

    if response.status_code == 201 or response.status_code == 200:
        st.sidebar.success('Data saved successfully to GitHub!')
    else:
        st.sidebar.error('Failed to save data to GitHub. Error: ' + response.json().get('message', 'Unknown error'))


# Load production data from CSV
if os.path.exists('production_data.csv'):
    df = pd.read_csv('production_data.csv')
else:
    df = pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time (Minutes)', 'Downtime (Minutes)', 'Reason for Downtime'])


def save_data(df):
    df.to_csv('production_data.csv', index=False)
    upload_to_github(df.to_csv(index=False))


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


# Application available for all logged-in users
if st.session_state.user is not None:
    st.header(f"Welcome, {st.session_state.user['Username']}!")
    st.write("You are logged in.")

    # Data Entry Form
    st.sidebar.header("Add New Production Entry")

    with st.sidebar.form("production_form"):
        date = st.date_input("Production Date", datetime.date.today())
        company = st.text_input("Company Name")
        operator = st.session_state.user['Username']
        seal_type = st.text_input("Seal Type")
        seals_count = st.number_input("Number of Seals", min_value=0, step=1)
        production_time = st.number_input("Production Time (Minutes)", min_value=0.0, step=0.1)
        downtime = st.number_input("Downtime (Minutes)", min_value=0.0, step=0.1)
        downtime_reason = st.text_input("Reason for Downtime")

        submitted = st.form_submit_button("Save Entry")

        if submitted:
            new_entry = pd.DataFrame({
                'Date': [date],
                'Company': [company.title()],
                'Seal Count': [seals_count],
                'Operator': [operator],
                'Seal Type': [seal_type.title()],
                'Production Time (Minutes)': [production_time],
                'Downtime (Minutes)': [downtime],
                'Reason for Downtime': [downtime_reason]
            })

            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)

    st.header("Production Data Overview")
    st.dataframe(df)

    # Displaying Bar Charts
    if not df.empty:
        charts = ['Daily Production Trend', 'Production by Company', 'Production by Operator']
        for chart_name in charts:
            st.header(chart_name)
            fig, ax = plt.subplots(figsize=(2, 1), dpi=120)  # Ekstremalnie mały rozmiar z wysokim DPI
            if chart_name == 'Daily Production Trend':
                summary = df.groupby('Date')['Seal Count'].sum().reset_index()
                ax.bar(summary['Date'], summary['Seal Count'], width=0.4, color='skyblue')
            elif chart_name == 'Production by Company':
                summary = df.groupby('Company')['Seal Count'].sum().reset_index()
                ax.bar(summary['Company'], summary['Seal Count'], width=0.4, color='lightgreen')
            elif chart_name == 'Production by Operator':
                summary = df.groupby('Operator')['Seal Count'].sum().reset_index()
                ax.bar(summary['Operator'], summary['Seal Count'], width=0.4, color='orange')
            ax.set_title(chart_name, fontsize=8)
            ax.set_ylim(0)
            plt.xticks(rotation=45, fontsize=6)
            plt.yticks(fontsize=6)
            plt.tight_layout()
            st.pyplot(fig)
