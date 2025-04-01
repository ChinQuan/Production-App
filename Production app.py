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

    if menu == 'Home':
        st.header("Production Data Overview")
        if not df.empty:
            st.dataframe(df)

            # Display Statistics
            st.header("Production Statistics")
            daily_average = df['Seal Count'].mean()
            st.write(f"### Average Daily Production: {daily_average:.2f} seals")

            top_companies = df.groupby('Company')['Seal Count'].sum().sort_values(ascending=False).head(3)
            st.write("### Top 3 Companies by Production")
            st.write(top_companies)

            top_operators = df.groupby('Operator')['Seal Count'].sum().sort_values(ascending=False).head(3)
            st.write("### Top 3 Operators by Production")
            st.write(top_operators)

        # Data Entry Form
        st.sidebar.header("Add New Production Entry")

        with st.sidebar.form("production_form"):
            date = st.date_input("Production Date", datetime.date.today())
            company = st.text_input("Company Name")
            operator = st.session_state.user['Username']
            seal_type = st.selectbox("Seal Type", st.session_state.seal_types)
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
                    'Seal Type': [seal_type],
                    'Production Time (Minutes)': [production_time],
                    'Downtime (Minutes)': [downtime],
                    'Reason for Downtime': [downtime_reason]
                })

                df = pd.concat([df, new_entry], ignore_index=True)
                save_data(df)
                st.sidebar.success("Production entry saved successfully.")

