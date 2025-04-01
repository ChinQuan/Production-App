import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import openpyxl
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

if 'seal_types' not in st.session_state:
    st.session_state.seal_types = [
        'Standard Soft Seals', 'Standard Hard Seals', 'Custom Soft Seals', 'Custom Hard Seals', 'V-Rings (Soft Material)'
    ]


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


if st.session_state.user is not None:
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Go to", ['Home', 'Production Charts'])

    if menu == 'Production Charts':
        st.header("Production Charts")
        if not df.empty():
            col1, col2 = st.columns([2, 1])  # Adjusted column ratio to make charts smaller

            with col1:
                fig, ax = plt.subplots(figsize=(5, 3))
                daily_trend = df.groupby('Date')['Seal Count'].sum()
                bars = ax.bar(daily_trend.index, daily_trend.values, color='skyblue')
                for bar in bars:
                    ax.annotate(str(int(bar.get_height())), xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                                xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=8)
                st.pyplot(fig, use_container_width=False)

            with col1:
                fig, ax = plt.subplots(figsize=(5, 3))
                company_trend = df.groupby('Company')['Seal Count'].sum()
                bars = ax.bar(company_trend.index, company_trend.values, color='lightgreen')
                for bar in bars:
                    ax.annotate(str(int(bar.get_height())), xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                                xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=8)
                st.pyplot(fig, use_container_width=False)

            with col1:
                fig, ax = plt.subplots(figsize=(5, 3))
                seal_type_trend = df.groupby('Seal Type')['Seal Count'].sum()
                bars = ax.bar(seal_type_trend.index, seal_type_trend.values, color='coral')
                for bar in bars:
                    ax.annotate(str(int(bar.get_height())), xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                                xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=8)
                st.pyplot(fig, use_container_width=False)
