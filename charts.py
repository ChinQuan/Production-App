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

    # Daily Production Trend
    daily_trend = df.groupby('Date')['Seal Count'].sum().reset_index()
    fig1 = px.bar(daily_trend, x='Date', y='Seal Count', title="Daily Production Trend",
                  labels={'Seal Count': 'Number of Seals', 'Date': 'Production Date'})
    st.plotly_chart(fig1, use_container_width=True)

    # Production by Company
    company_trend = df.groupby('Company')['Seal Count'].sum().reset_index()
    fig2 = px.bar(company_trend, x='Company', y='Seal Count', title="Production by Company",
                  labels={'Seal Count': 'Number of Seals', 'Company': 'Company Name'})
    st.plotly_chart(fig2, use_container_width=True)

    # Production by Seal Type
    seal_type_trend = df.groupby('Seal Type')['Seal Count'].sum().reset_index()
    fig3 = px.bar(seal_type_trend, x='Seal Type', y='Seal Count', title="Production by Seal Type",
                  labels={'Seal Count': 'Number of Seals', 'Seal Type': 'Seal Type'})
    st.plotly_chart(fig3, use_container_width=True)
