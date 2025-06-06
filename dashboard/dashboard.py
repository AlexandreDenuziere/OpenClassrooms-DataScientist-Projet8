import streamlit as st
import pandas as pd
import numpy as np
import requests

# Page config
st.set_page_config(page_title="Customer dashboard", layout="wide")

# Initialize session_state values
if "show_accessibility" not in st.session_state:
    st.session_state.show_accessibility = False
if "font_size" not in st.session_state:
    st.session_state.font_size = "medium"
# Initialize temp variables for the form
if "temp_font_size" not in st.session_state:
    st.session_state.temp_font_size = st.session_state.font_size

if st.sidebar.button("🔧 Accessibility"):
    st.session_state.show_accessibility = not st.session_state.show_accessibility

# Show options if the menu is activated
if st.session_state.show_accessibility :
    st.sidebar.markdown("## Accessibility parameters")

    st.session_state.temp_font_size = st.sidebar.selectbox(
	"Text size",
	["small", "medium", "big"],
	index=["small", "medium", "big"].index(st.session_state.temp_font_size)
    )

    if st.sidebar.button("✅ Apply"):
        st.session_state.font_size = st.session_state.temp_font_size
        st.rerun()

# Define sizes to apply to the text
font_sizes = {
    "small": "14px",
    "medium": "18px",
    "big": "22px",
}

# Apply text style
st.markdown(f"""
    <style>
	html, body, [class*="css"] {{
	    font-size: {font_sizes[st.session_state.font_size]} !important;
	}}
    </style>
""", unsafe_allow_html=True)

# Print the title of the page
st.title("Prêt à dépenser - Customer dashboard")

# Set data path
DATA_URL= ("/data/cleaned_data/test_data_cleaned.csv")
# Set model path
MODEL_PATH = ("/data/model/model.pkl")

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
    return customer_data.iloc[0]

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

# When submit is pressed
if submit:
    # Get customer data
    customer_data = get_customer_data(data, customer_id)
    # Arrange customer data to display it
    if customer_data["CODE_GENDER"] == 0 :
        gender = " - is a **man**."
        pronoun = "He"
    else :
        gender = " - is a **woman**."
        pronoun = "She"
    age = f" - {pronoun} is **{customer_data["AGE"]}** years old."
    childrens = f" - {pronoun} have **{customer_data["CNT_CHILDREN"]}** childrens."
    employed = f" - {pronoun} have been employed for **{customer_data["TIME_EMPLOYED"]}** years."
    income = f" - {pronoun} have an income of **{customer_data["AMT_INCOME_TOTAL"]}**$."
    if customer_data["FLAG_OWN_CAR"] == 0 :
        car = f" - {pronoun} **does not own** a car."
    else :
        car = f" - {pronoun} **owns** a car."
    if customer_data["FLAG_OWN_REALTY"] == 0 :
        realty = f" - {pronoun} **does not own** real estate."
    else :
        realty = f" - {pronoun} **owns** real estate."

    # Get data from the API
    response = requests.get(f"http://api:5001/api/v1/customer?id={customer_id}")

    # Check that we got a valide answer from the API
    if response.status_code == 200:
        response_data = response.json()

	# Create different tabs to organize the application
        tab1, tab2, tab3, tab4 = st.tabs(["Customer data", "Credit response", "Score explanations", "Toto"])

	# In the first tab, we display the customer data
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
	# In the second tab we display the response of the model
        with tab2:
            st.header("Credit response")
            score = response_data["Probability of the customer being a good one"]
            st.progress(score, f"Probability of the customer being a good one : {np.round(score*100, 1)} %")

            
	# In the third tab 
        with tab3:
            st.header("Score explanations")
    else :
        st.error("Invalid customer ID or error from API")
