import streamlit as st
import pandas as pd
import numpy as np
import requests

st.title("Prêt à dépenser - Scoring client")

DATA_URL= ("/data/test_data_cleaned.csv")

# Load the csv data and put it in cache
@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL)
    return data

# Once customer selected, get its main infos from loaded data
def get_customer_data(data, customer_id):
    customer_data = data.loc[
        data["SK_ID_CURR"]==customer_id,
        [
            "CODE_GENDER", 
            "DAYS_BIRTH",
            "CNT_CHILDREN",
            "AMT_INCOME_TOTAL",
            "DAYS_EMPLOYED",
            "FLAG_OWN_CAR",
            "FLAG_OWN_REALTY"
        ]
    ]
    customer_data["AGE"] = np.round(-customer_data["DAYS_BIRTH"] / 365, 2)
    customer_data["TIME_EMPLOYED"] = np.round(-customer_data["DAYS_EMPLOYED"] / 365, 2)
    customer_data = customer_data.drop(["DAYS_BIRTH", "DAYS_EMPLOYED"], axis=1)
    return customer_data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load data into the dataframe.
data = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

# Create the from where the user have to select the customer ID
with st.form("form"):
    st.write("Selection of the customer")
    customer_id = st.selectbox("Pick a customer", data["SK_ID_CURR"])
    submit = st.form_submit_button("Get score for this customer")
 
if submit:
    # Get customer data
    customer_data = get_customer_data(data, customer_id)
    # Arrange customer data to display it
    if customer_data["CODE_GENDER"][0] == 0 :
        gender = " - is a **man**."
        pronoun = "He"
    else :
        gender = " - is a **woman**."
        pronoun = "She"
    age = f" - {pronoun} is **{customer_data["AGE"][0]}** years old."
    childrens = f" - {pronoun} have **{customer_data["CNT_CHILDREN"][0]}** childrens."
    employed = f" - {pronoun} have been employed for **{customer_data["TIME_EMPLOYED"][0]}** years."
    income = f" - {pronoun} have an income of **{customer_data["AMT_INCOME_TOTAL"][0]}**$."
    if customer_data["FLAG_OWN_CAR"][0] == 0 :
        car = f" - {pronoun} **does not own** a car."
    else :
        car = f" - {pronoun} **owns** a car."
    if customer_data["FLAG_OWN_REALTY"][0] == 0 :
        realty = f" - {pronoun} **does not own** real estate."
    else :
        realty = f" - {pronoun} **owns** real estate."

    # Get data from the API
    response = requests.get(f"http://api:5001/api/v1/customer?id={customer_id}")
    
    if response.status_code == 200:
        response_data = response.json()
        tab1, tab2, tab3 = st.tabs(["Customer data", "Credit response", "Score explanations"])

        with tab1:
            st.header("Customer data")
            st.write(f"Customer ID {customer_id}")
            st.write(gender)
            st.write(age)
            st.write(childrens)
            st.write(employed)
            st.write(income)
            st.write(car)
            st.write(realty)
        with tab2:
            st.header("Credit response")
        with tab3:
            st.header("Score explanations")
    else :
        st.error("Invalid customer ID or error from API")
