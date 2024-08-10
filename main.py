import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)


# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache_data to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows


data = run_query(
    """
    SELECT *
    FROM `learngcp-408315.prod.wahoo_analysis` order by starts_at desc
    """
)
df = pd.DataFrame(data)

today = datetime.now().date()
seven_days_ago = today - timedelta(days=7)

df["start_date"] = pd.to_datetime(df["starts_at"]).dt.date
df["weekday"] = pd.Categorical(
    df["starts_at"].dt.day_name(),
    categories=[
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ],
    ordered=True,
)
# df_this_week = df[(df["start_date"] >= seven_days_ago) and (df["start_date"] <= today)]
df_this_week = df[(df["start_date"] >= seven_days_ago) & (df["start_date"] <= today)]

st.title("Wahoo Analytics")

all_columns = df.columns.tolist()
metric_columns = [
    "calories",
    "avg_cadence",
    "distance",
    "minutes",
    "active_duration",
    "total_duration",
    "avg_power",
    "avg_speed",
    "np",
    "tss",
]

with st.sidebar:
    metric_dropdown = st.selectbox("Select metric", metric_columns)
# y_column = st.selectbox("Select y-axis column", all_columns)


tab1, tab2 = st.tabs(["📈 Charts", "🗃 Data"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Performance Day of Week")
        df_weekday_avg = (
            df.groupby("weekday")[metric_dropdown]
            .mean()
            .reset_index()
            .sort_values("weekday")
        )
        st.bar_chart(df_weekday_avg, x="weekday", y=metric_dropdown)

    with col2:
        st.subheader("Performance over Time")
        df_avg = (
            df.groupby("start_date")[metric_dropdown]
            .mean()
            .reset_index()
            .sort_values("start_date")
        )
        st.line_chart(df_avg, x="start_date", y=metric_dropdown)

with tab2:
    st.write(df)
# if st.button("Generate Plot"):
#     st.line_chart(df.set_index(x_column)[y_column])
