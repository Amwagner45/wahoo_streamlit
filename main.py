import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

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
    "SELECT * FROM `learngcp-408315.prod.wahoo_mage` order by starts desc LIMIT 10"
)
df = pd.DataFrame(data)


st.title("Wahoo Analytics")

st.subheader("Preview Data")
st.write(df.head(10))
