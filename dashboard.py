import os
import json
import streamlit as st
import requests
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="E-Commerce Analytics", layout="wide")
st.title("📊 Enterprise Database & Multi-Category Transaction Dashboard")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/analytics/summary")

# comment: The code fetches payment data from the FastAPI backend and displays it in a Streamlit dashboard. It includes filtering options, key metrics, visualizations for revenue by category and payment mode distribution, and a table showing recent payments with dynamic item specifications.
try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        if not df.empty:
            # Sidebar Filter
            st.sidebar.header("Filter Options")
            selected_category = st.sidebar.multiselect(
                "Select Product Categories",
                options=df["category"].unique(),
                default=df["category"].unique()
            )

            filtered_df = df[df["category"].isin(selected_category)]

            # Key Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Revenue", f"${filtered_df['total_paid'].sum():,.2f}")
            col2.metric("Total Transactions", len(filtered_df))
            col3.metric("Avg Transaction Value", f"${filtered_df['total_paid'].mean():,.2f}")

            st.markdown("---")

            # Visualizations
            col_left, col_right = st.columns(2)

            with col_left:
                st.subheader("Revenue by Product Category")
                fig_cat = px.bar(
                    filtered_df.groupby("category")["total_paid"].sum().reset_index(),
                    x="category", y="total_paid", color="category"
                )
                st.plotly_chart(fig_cat, use_container_width=True)

            with col_right:
                st.subheader("Payment Mode Distribution")
                fig_mode = px.pie(filtered_df, names="payment_mode", values="total_paid", hole=0.4)
                st.plotly_chart(fig_mode, use_container_width=True)

            st.subheader("Recent Payments & Dynamic Item Specifications")
            
            # Format specifications column for clean display
            display_df = filtered_df.copy()
            display_df["specifications"] = display_df["specifications"].apply(lambda x: json.dumps(x, indent=2))
            
            st.dataframe(display_df[[
                "payment_id", "user_name", "city", "item_name", "category", 
                "specifications", "total_paid", "payment_mode", "created_at"
            ]])
        else:
            st.info("No payment records found. Run seed.py to insert mock data.")
    else:
        st.error("Failed to connect to backend API.")
except Exception as e:
    st.error(f"Make sure FastAPI is running! Error: {e}")

