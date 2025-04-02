import streamlit as st
import pandas as pd
import datetime
import bcrypt
import os
import plotly.express as px
import plotly.graph_objs as go

# Initialize the application
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Load users data from Excel with hashed passwords
def load_users():
    try:
        users = pd.read_excel('users.xlsx', sheet_name='Users')
        return users
    except FileNotFoundError:
        # Create default admin user if file not found
        users = pd.DataFrame({'Username': ['admin'], 'Password': [bcrypt.hashpw('admin'.encode(), bcrypt.gensalt()).decode()], 'Role': ['Admin']})
        users.to_excel('users.xlsx', sheet_name='Users', index=False)
        return users

# Verify password using bcrypt
def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode(), stored_password.encode())

# Login logic
def login(username, password, users_df):
    user = users_df[users_df['Username'] == username]
    if not user.empty and verify_password(user.iloc[0]['Password'], password):
        return user.iloc[0]
    return None

# Load production data from CSV
def load_data():
    try:
        return pd.read_csv('production_data.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Company', 'Seal Count', 'Operator', 'Seal Type', 'Production Time', 'Downtime', 'Reason for Downtime'])

def save_data(df):
    df.to_csv('production_data.csv', index=False)

# Load users and production data
users_df = load_users()
df = load_data()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

# Login panel
if st.session_state.user is None:
    st.sidebar.title("🔑 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user = login(username, password, users_df)
        if user is not None:
            st.session_state.user = user
            st.sidebar.success(f"Logged in as {user['Username']}")
        else:
            st.sidebar.error("Invalid username or password")
else:
    st.sidebar.write(f"✅ Logged in as {st.session_state.user['Username']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None

    menu = st.sidebar.selectbox("Navigate", ['Home', 'Production Charts', 'Add Entry'])

    if menu == 'Home':
        st.header("📊 Production Data Overview")
        if not df.empty:
            st.dataframe(df)

    if menu == 'Add Entry':
        st.header("➕ Add New Production Entry")
        with st.form("production_form"):
            date = st.date_input("Production Date", value=datetime.date.today())
            company = st.text_input("Company Name")
            operator = st.text_input("Operator", value=st.session_state.user['Username'])
            seal_type = st.selectbox("Seal Type", ['Standard Soft', 'Standard Hard', 'Custom Soft', 'Custom Hard', 'V-Rings'])
            seals_count = st.number_input("Number of Seals", min_value=0, step=1)
            production_time = st.number_input("Production Time (Minutes)", min_value=0.0, step=0.1)
            downtime = st.number_input("Downtime (Minutes)", min_value=0.0, step=0.1)
            downtime_reason = st.text_input("Reason for Downtime")
            submitted = st.form_submit_button("Save Entry")

            if submitted:
                if company and seals_count > 0 and production_time > 0:
                    new_entry = {
                        'Date': date,
                        'Company': company,
                        'Seal Count': seals_count,
                        'Operator': operator,
                        'Seal Type': seal_type,
                        'Production Time': production_time,
                        'Downtime': downtime,
                        'Reason for Downtime': downtime_reason
                    }
                    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                    save_data(df)
                    st.success("Production entry saved successfully.")
                else:
                    st.error("Please fill all required fields correctly.")

    if menu == 'Production Charts':
        st.header("📈 Production Charts")

        if not df.empty:
            date_range = st.sidebar.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])
            selected_operators = st.sidebar.multiselect("Select Operators", options=sorted(df['Operator'].unique().tolist()), default=[])
            selected_companies = st.sidebar.multiselect("Select Companies", options=sorted(df['Company'].unique().tolist()), default=[])
            selected_seal_types = st.sidebar.multiselect("Select Seal Types", options=sorted(df['Seal Type'].unique().tolist()), default=[])

            filtered_df = df.copy()

            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = filtered_df[(filtered_df['Date'] >= str(start_date)) & (filtered_df['Date'] <= str(end_date))]

            if selected_operators:
                filtered_df = filtered_df[filtered_df['Operator'].isin(selected_operators)]

            if selected_companies:
                filtered_df = filtered_df[filtered_df['Company'].isin(selected_companies)]

            if selected_seal_types:
                filtered_df = filtered_df[filtered_df['Seal Type'].isin(selected_seal_types)]

            st.write("Filtered Data", filtered_df)

            fig = px.line(filtered_df, x='Date', y='Seal Count', title='Daily Production Trend')
            st.plotly_chart(fig)

            fig = px.bar(filtered_df, x='Company', y='Seal Count', title='Production by Company')
            st.plotly_chart(fig)

            fig = px.bar(filtered_df, x='Seal Type', y='Seal Count', title='Production by Seal Type')
            st.plotly_chart(fig)

            fig = px.bar(filtered_df, x='Operator', y='Seal Count', title='Production by Operator')
            st.plotly_chart(fig)

