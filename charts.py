import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data import load_data


def show_charts():
    df = load_data()

    if df.empty:
        st.write("No data available to display charts.")
        return

    st.header("Production Charts")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig, ax = plt.subplots(figsize=(5, 3))
        daily_trend = df.groupby('Date')['Seal Count'].sum()
        ax.bar(daily_trend.index, daily_trend.values, color='skyblue')
        st.pyplot(fig)

    with col1:
        fig, ax = plt.subplots(figsize=(5, 3))
        company_trend = df.groupby('Company')['Seal Count'].sum()
        ax.bar(company_trend.index, company_trend.values, color='lightgreen')
        st.pyplot(fig)

    with col1:
        fig, ax = plt.subplots(figsize=(5, 3))
        seal_type_trend = df.groupby('Seal Type')['Seal Count'].sum()
        ax.bar(seal_type_trend.index, seal_type_trend.values, color='coral')
        st.pyplot(fig)
