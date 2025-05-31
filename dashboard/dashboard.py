import streamlit as st
import pandas as pd
import numpy as np
import requests

st.title("Prêt à dépenser - Scoring client")

DATA_URL= ("/data/test_data_cleaned.csv")

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL)
    return data

def show_row_data(data, nrows):
    return data.iloc[:nrows]
    
# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load data into the dataframe.
data = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

with st.form("form"):
    st.write("Selection of the customer")
    customer_id = st.selectbox("Pick a customer", data["SK_ID_CURR"])
    submit = st.form_submit_button("Get score for this customer")

if submit:
    response = requests.get(f"http://api:5001/api/v1/customer?id={customer_id}")
    if response.status_code == 200:
        response_data = response.json()
        st.write(response_data)
    else :
        st.error("Invalid customer ID or error from API")
