import streamlit as st
import pandas as pd
import plotly.express as px
from data import load_data


def show_charts():
    df = load_data()

    if df.empty:
        st.write("No data available to display charts.")
        return

    st.header("Production Charts")

    # Filtry
    st.sidebar.header("Filter Data")
    selected_operator = st.sidebar.selectbox("Select Operator", options=['All'] + sorted(df['Operator'].unique().tolist()))
    selected_company = st.sidebar.selectbox("Select Company", options=['All'] + sorted(df['Company'].unique().tolist()))
    selected_seal_type = st.sidebar.selectbox("Select Seal Type", options=['All'] + sorted(df['Seal Type'].unique().tolist()))

    # Filtracja danych
    filtered_df = df.copy()
    if selected_operator != 'All':
        filtered_df = filtered_df[filtered_df['Operator'] == selected_operator]
    if selected_company != 'All':
        filtered_df = filtered_df[filtered_df['Company'] == selected_company]
    if selected_seal_type != 'All':
        filtered_df = filtered_df[filtered_df['Seal Type'] == selected_seal_type]

    # Daily Production Trend
    daily_trend = filtered_df.groupby('Date')['Seal Count'].sum().reset_index()
    fig1 = px.bar(daily_trend, x='Date', y='Seal Count', title="Daily Production Trend",
                  labels={'Seal Count': 'Number of Seals', 'Date': 'Production Date'},
                  text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)

    # Production by Company
    company_trend = filtered_df.groupby('Company')['Seal Count'].sum().reset_index()
    fig2 = px.bar(company_trend, x='Company', y='Seal Count', title="Production by Company",
                  labels={'Seal Count': 'Number of Seals', 'Company': 'Company Name'},
                  text_auto=True)
    st.plotly_chart(fig2, use_container_width=True)

    # Production by Seal Type
    seal_type_trend = filtered_df.groupby('Seal Type')['Seal Count'].sum().reset_index()
    fig3 = px.bar(seal_type_trend, x='Seal Type', y='Seal Count', title="Production by Seal Type",
                  labels={'Seal Count': 'Number of Seals', 'Seal Type': 'Seal Type'},
                  text_auto=True)
    st.plotly_chart(fig3, use_container_width=True)

    # Production by Operator
    operator_trend = filtered_df.groupby('Operator')['Seal Count'].sum().reset_index()
    fig4 = px.bar(operator_trend, x='Operator', y='Seal Count', title="Production by Operator",
                  labels={'Seal Count': 'Number of Seals', 'Operator': 'Operator'},
                  text_auto=True)
    st.plotly_chart(fig4, use_container_width=True)
