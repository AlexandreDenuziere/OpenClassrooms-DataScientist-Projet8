import streamlit as st
import pandas as pd
import numpy as np
import requests
import pickle
import shap

# Page config
st.set_page_config(page_title="Customer dashboard", layout="wide")

### ACCESSIBILITY OPTIONS ###
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
### ACCESSIBILITY OPTIONS ###

# Print the title of the page
st.title("Prêt à dépenser - Customer dashboard")

### UTILITY FUNCTIONS ###
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

# Load the model
@st.cache_resource
def load_model():
    pkl_model = pickle.load(open(MODEL_PATH, "rb"))
    return pkl_model

# Extract scaler and model  from the pkl model
@st.cache_resource
def load_scaler_model(pkl_model):
    scaler = pkl_model.named_steps["scaler"]
    model = pkl_model.named_steps["model"]
    return scaler, model

# Compute feature importance
@st.cache_data
def get_shap_values(model, scaler):
    # Scale the data
    data_transformed = scaler.transform(data)
    # Calculate the shap values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(data)
    return shap_values

# Compute global feature importance
@st.cache_data
def get_global_feature_importance(shap_values):
    # First we get all values in absolute
    shap_values_abs = np.abs(shap_values)
    # Then when calculate the mean for each features
    global_feature_importance = np.mean(shap_values_abs, axis=0)
    global_feature_importance = pd.DataFrame(
        global_feature_importance,
        columns=["Global Importance"],
        index=data.columns
    ).reset_index(names="Feature")
    return global_feature_importance

# Return the local feature importance for a customer
def get_local_feature_importance(shap_values, customer_index):
    local_feature_importance = shap_values[customer_index]
    local_feature_importance = pd.DataFrame(
        local_feature_importance,
        columns=["Local Importance"],
        index=data.columns
    ).reset_index(names="Feature")
    return local_feature_importance

@st.cache_data
def arrange_customer_data(customer_data):
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
    return gender, age, childrens, employed, income, car, realty

@st.cache_data
def get_main_important_features(local_feature_importance, global_feature_importance):
    # Get 10 most important positive features
    positive_important_features = local_feature_importance.loc[
         local_feature_importance["Local Importance"] > 0, :
    ].sort_values(by="Local Importance", ascending=False, key=abs).head(10)
    # Get 10 most important negative features
    negative_important_features = local_feature_importance.loc[
         local_feature_importance["Local Importance"] < 0, :
    ].sort_values(by="Local Importance", ascending=False, key=abs).head(10)

    # Add global importance
    positive_important_features = positive_important_features.merge(global_feature_importance)
    negative_important_features = negative_important_features.merge(global_feature_importance)

    # Put everything in absolute value
    positive_important_features["Local Importance"] = np.abs(positive_important_features["Local Importance"])
    negative_important_features["Local Importance"] = np.abs(negative_important_features["Local Importance"])

    return positive_important_features, negative_important_features

@st.cache_data
def get_scoring_data(customer_id):
    response = requests.get(f"http://api:5001/api/v1/customer?id={customer_id}")
    # Check that we got a valide answer from the API
    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else :
        st.error("Invalid customer ID or error from API")
### UTILITY FUNCTIONS ###

### DATA LOADING ###
# Set data path
DATA_URL = ("/data/cleaned_data/test_data_cleaned.csv")
# Set model path
MODEL_PATH = ("/data/model/model.pkl")

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load data into the dataframe.
data = load_data()
# Load the model
pkl_model = load_model()
# Extract scaler and model
scaler, model = load_scaler_model(pkl_model)
# Get shap values
shap_values = get_shap_values(model, scaler)
# Get the global feature importance
global_feature_importance = get_global_feature_importance(shap_values)

# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')
### DATA LOADING ###

# Create the from where the user have to select the customer ID
with st.form("form"):
    st.write("Selection of the customer")
    customer_id = st.selectbox("Pick a customer", data["SK_ID_CURR"])
    submit = st.form_submit_button("Get score for this customer")

# When submit is pressed
if submit:
    # Get customer data
    customer_data = get_customer_data(data, customer_id)
    customer_index = data.loc[data["SK_ID_CURR"] == customer_id, :].index[0]
    local_feature_importance = get_local_feature_importance(shap_values, customer_index)
    # Arrange customer data to display it
    gender, age, childrens, employed, income, car, realty = arrange_customer_data(customer_data)
    
    # Get main features by importance
    positive_important_features, negative_important_features = get_main_important_features(
        local_feature_importance, global_feature_importance
    )
    
    # Get data from the API
    response_data = get_scoring_data(customer_id)

	# Create different tabs to organize the application
    tab1, tab2, tab3, tab4 = st.tabs(["Customer data", "Credit response", "Analyze a feature", "Analyze two features"])

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
        st.markdown("######")

        with st.expander("See score explanations"):
            st.subheader("Most positive features")
            st.dataframe(
               positive_important_features,
               hide_index=True
            )
            st.subheader("Most negative features")
            st.dataframe(
                negative_important_features,
                hide_index=True
            )

            # Add explanations about table displayed
            st.markdown("""
            **Notes :**
            - The above tables are displaying which features of the customer are the most impacting its score.
            - **Local importance** are the score obtained by the customer.
            - It is compared to the **global importance** which is the mean of the score of every customers.
            """)
	# In the third tab, we display univariate analysis of a feature
    with tab3:
        st.header("Analyze a feature")
        selected_feature = st.selectbox("Select a feature to analyze", data.columns)
        st.write(selected_feature)
    # For the fourth tab, we display bivariate analysis of features
    with tab4:
        st.header("Analyze two features")

