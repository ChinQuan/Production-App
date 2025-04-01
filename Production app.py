import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import openpyxl
from fpdf import FPDF
import io
import seaborn as sns


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


def save_users(users_df):
    with pd.ExcelWriter('users.xlsx', engine='openpyxl', mode='w') as writer:
        users_df.to_excel(writer, sheet_name='Users', index=False)


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


# Admin Panel
if st.session_state.user is not None and st.session_state.user['Role'] == 'Admin':
    st.sidebar.header("Admin Panel")

    with st.sidebar.form("Add User"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_role = st.selectbox("Role", ["Admin", "Manager", "Operator"])
        add_user = st.form_submit_button("Add User")

        if add_user:
            new_user = pd.DataFrame({
                'Username': [new_username],
                'Password': [new_password],
                'Role': [new_role]
            })
            users_df = pd.concat([users_df, new_user], ignore_index=True)
            save_users(users_df)
            st.sidebar.success("User added successfully!")

    # Display Users List
    st.header("Manage Users")
    st.dataframe(users_df)

    # Delete User
    delete_user = st.selectbox("Select User to Delete", users_df['Username'].tolist())
    if st.button("Delete User"):
        users_df = users_df[users_df['Username'] != delete_user]
        save_users(users_df)
        st.success(f"User {delete_user} deleted successfully!")


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
            # Load or create production data file
            try:
                df = pd.read_excel('production_data.xlsx', sheet_name='Daily Production Record')
            except FileNotFoundError:
                df = pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time (Minutes)', 'Downtime (Minutes)', 'Reason for Downtime'])

            # Add new entry
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

            # Save to Excel
            with pd.ExcelWriter('production_data.xlsx', engine='openpyxl', mode='w') as writer:
                df.to_excel(writer, sheet_name='Daily Production Record', index=False)

            st.sidebar.success("Entry saved successfully!")

else:
    st.write("Please log in to use the application.")
