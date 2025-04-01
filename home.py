import streamlit as st
import pandas as pd
from data import load_data, save_data


def show_home():
    df = load_data()

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
        date = st.date_input("Production Date")
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
                'Company': [company],
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
