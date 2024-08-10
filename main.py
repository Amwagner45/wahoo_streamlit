import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
from datetime import datetime, timedelta

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

df["starts_at"] = pd.to_datetime(df["starts_at"])
df_this_week = df[df["starts_at"] >= seven_days_ago & df["starts_at"] <= today]

st.title("Wahoo Analytics")

all_columns = df.columns.tolist()
metric_columns = [
    "calories",
    "avg_cadence",
    "distance",
    "active_duration",
    "total_duration",
    "avg_power",
    "np",
    "tss",
    "avg_speed",
]

metric_dropdown = st.selectbox("Select metric", metric_columns)
# y_column = st.selectbox("Select y-axis column", all_columns)

st.subheader("Performance Day of Week")
st.bar_chart(df, x="weeday", y=metric_dropdown)

# if st.button("Generate Plot"):
#     st.line_chart(df.set_index(x_column)[y_column])
