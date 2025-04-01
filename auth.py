import streamlit as st
import pandas as pd


def authenticate_user():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    try:
        users_df = pd.read_excel('users.xlsx', sheet_name='Users')
    except FileNotFoundError:
        users_df = pd.DataFrame({'Username': ['admin'], 'Password': ['admin'], 'Role': ['Admin']})
        users_df.to_excel('users.xlsx', sheet_name='Users', index=False)

    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]
    else:
        if st.sidebar.button("Login"):
            st.sidebar.error("Invalid username or password")
        return None


def logout():
    st.session_state.user = None
