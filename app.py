# ==============================
# Bank Customer Churn Dashboard
# ==============================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# ------------------------------
# Page Configuration
# ------------------------------
st.set_page_config(
    page_title="Bank Customer Churn Analysis Dashboard",
    layout="wide"
)

st.title("📊 Bank Customer Churn Analysis Dashboard")
st.markdown("Professional interactive dashboard for customer churn analysis")

# ------------------------------
# Load Data
# ------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Churn_Modelling.csv")
    return df

df = load_data()

# ------------------------------
# Handle Missing Values
# ------------------------------
df = df.dropna()

# ------------------------------
# Feature Engineering
# ------------------------------
df["AgeGroup"] = pd.cut(
    df["Age"],
    bins=[18, 25, 35, 45, 55, 100],
    labels=["18-25", "26-35", "36-45", "46-55", "56+"]
)

df["BalanceBucket"] = pd.cut(
    df["Balance"],
    bins=[-1, 0, 50000, 100000, 200000, df["Balance"].max()],
    labels=["Zero", "Low", "Medium", "High", "Very High"]
)

# Churn Label
df["ChurnStatus"] = df["Exited"].map({1: "Churned", 0: "Retained"})

# ------------------------------
# Sidebar Filters
# ------------------------------
st.sidebar.header("🔍 Filter Customers")

geo_filter = st.sidebar.multiselect(
    "Geography",
    options=df["Geography"].unique(),
    default=df["Geography"].unique()
)

gender_filter = st.sidebar.multiselect(
    "Gender",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

age_filter = st.sidebar.slider(
    "Age Range",
    int(df["Age"].min()),
    int(df["Age"].max()),
    (18, 60)
)

active_filter = st.sidebar.multiselect(
    "Is Active Member",
    options=df["IsActiveMember"].unique(),
    default=df["IsActiveMember"].unique()
)

product_filter = st.sidebar.multiselect(
    "Number of Products",
    options=df["NumOfProducts"].unique(),
    default=df["NumOfProducts"].unique()
)

# ------------------------------
# Apply Filters
# ------------------------------
filtered_df = df[
    (df["Geography"].isin(geo_filter)) &
    (df["Gender"].isin(gender_filter)) &
    (df["Age"].between(age_filter[0], age_filter[1])) &
    (df["IsActiveMember"].isin(active_filter)) &
    (df["NumOfProducts"].isin(product_filter))
]

# ------------------------------
# KPI Metrics
# ------------------------------
total_customers = len(filtered_df)
churned_customers = filtered_df["Exited"].sum()
churn_rate = (churned_customers / total_customers * 100) if total_customers > 0 else 0
avg_balance = filtered_df["Balance"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", total_customers)
col2.metric("Churned Customers", churned_customers)
col3.metric("Churn Rate (%)", f"{churn_rate:.2f}%")
col4.metric("Avg Account Balance", f"{avg_balance:,.2f}")

st.markdown("---")

# ------------------------------
# Visualizations
# ------------------------------
col1, col2 = st.columns(2)

# Churn Rate by Geography
geo_churn = filtered_df.groupby("Geography")["Exited"].mean().reset_index()
geo_churn["Exited"] = geo_churn["Exited"] * 100

fig_geo = px.bar(
    geo_churn,
    x="Geography",
    y="Exited",
    title="Churn Rate by Geography (%)",
    labels={"Exited": "Churn Rate (%)"}
)
col1.plotly_chart(fig_geo, use_container_width=True)

# Churn by Gender
gender_churn = filtered_df.groupby("Gender")["Exited"].mean().reset_index()
gender_churn["Exited"] = gender_churn["Exited"] * 100

fig_gender = px.pie(
    gender_churn,
    names="Gender",
    values="Exited",
    title="Churn by Gender (%)"
)
col2.plotly_chart(fig_gender, use_container_width=True)

# Age vs Churn
fig_age = px.histogram(
    filtered_df,
    x="Age",
    color="ChurnStatus",
    nbins=20,
    title="Age vs Churn Distribution"
)
st.plotly_chart(fig_age, use_container_width=True)

# Balance vs Churn
fig_balance = px.box(
    filtered_df,
    x="ChurnStatus",
    y="Balance",
    title="Balance vs Churn"
)
st.plotly_chart(fig_balance, use_container_width=True)

# Active vs Inactive Members
active_churn = filtered_df.groupby("IsActiveMember")["Exited"].mean().reset_index()
active_churn["Exited"] = active_churn["Exited"] * 100
active_churn["IsActiveMember"] = active_churn["IsActiveMember"].map({1: "Active", 0: "Inactive"})

fig_active = px.bar(
    active_churn,
    x="IsActiveMember",
    y="Exited",
    title="Churn: Active vs Inactive Members",
    labels={"Exited": "Churn Rate (%)"}
)
st.plotly_chart(fig_active, use_container_width=True)

# ------------------------------
# Bonus: Churn Risk Segmentation
# ------------------------------
def churn_risk(row):
    if row["IsActiveMember"] == 0 and row["Age"] > 40 and row["Balance"] > 100000:
        return "High Risk"
    elif row["IsActiveMember"] == 0:
        return "Medium Risk"
    else:
        return "Low Risk"

filtered_df["ChurnRisk"] = filtered_df.apply(churn_risk, axis=1)

risk_fig = px.bar(
    filtered_df["ChurnRisk"].value_counts().reset_index(),
    x="index",
    y="ChurnRisk",
    title="Customer Churn Risk Segmentation",
    labels={"index": "Risk Level", "ChurnRisk": "Customers"}
)
st.plotly_chart(risk_fig, use_container_width=True)

# ------------------------------
# Insights Section
# ------------------------------
st.markdown("## 🧠 Key Business Insights")

st.write(f"""
- **Overall churn rate** is **{churn_rate:.2f}%**
- **Inactive customers** show significantly higher churn
- Customers aged **40+** contribute more to churn
- High-balance but inactive customers are **high-risk**
- Customers with **multiple products** are more likely to stay
""")

# ------------------------------
# CSV Download
# ------------------------------
st.markdown("## ⬇ Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_churn_data.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("📌 Portfolio-ready Streamlit dashboard | Bank Customer Churn Analysis")
