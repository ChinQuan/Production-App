import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Initialize the application
st.set_page_config(page_title="Production Manager App", layout="wide")
st.title("Production Manager App")

# Load users data from Excel
def load_users():
    try:
        return pd.read_excel('users.xlsx', sheet_name='Users')
    except FileNotFoundError:
        return pd.DataFrame({'Username': ['admin'], 'Password': ['admin'], 'Role': ['Admin']})

# Login logic
def login(username, password, users_df):
    user = users_df[(users_df['Username'] == username) & (users_df['Password'] == password)]
    if not user.empty:
        return user.iloc[0]  # Return user info if valid login
    else:
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
    st.sidebar.title("Login")
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
    st.sidebar.write(f"Logged in as {st.session_state.user['Username']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None

    # Sidebar Navigation
    menu = st.sidebar.radio("Go to", ['Home', 'Production Charts'])

    if menu == 'Home':
        st.header("Production Data Overview")
        if not df.empty:
            st.dataframe(df)

        # 📊 **Ogólne statystyki**
        st.header("Production Statistics")
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

        # Formularz dodawania nowych zleceń w bocznej kolumnie
        st.sidebar.header("Add New Production Entry")
        with st.sidebar.form("production_form"):
            date = st.date_input("Production Date")
            company = st.text_input("Company Name")
            operator = st.text_input("Operator", value=st.session_state.user['Username'])
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
    
    # Zamiast df.append(), używamy pd.concat()
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
