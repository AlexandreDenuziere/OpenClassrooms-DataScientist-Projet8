import streamlit as st
import pandas as pd
import numpy as np
import requests
import pickle
import shap
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Customer dashboard", layout="wide")

### ACCESSIBILITY OPTIONS ###
# Initialize session_state values
if "show_accessibility" not in st.session_state:
    st.session_state.show_accessibility = False
if "font_size" not in st.session_state:
    st.session_state.font_size = "medium"
if "customer_id" not in st.session_state:
    st.session_state.customer_id = "231433"
if "rerun" not in st.session_state:
    st.session_state.rerun = False

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
            "AMT_CREDIT",
            "AMT_ANNUITY",
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
def load_scaler_model(_pkl_model):
    scaler = _pkl_model.named_steps["scaler"]
    model = _pkl_model.named_steps["model"]
    return scaler, model

# Compute feature importance
@st.cache_data
def get_shap_values(_model, _scaler):
    # Scale the data
    data_transformed = _scaler.transform(data)
    # Calculate the shap values
    explainer = shap.TreeExplainer(_model)
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
    # Create a list of features to add to the returned dataframe
    general_attributes_list = [
        "Gender", "Age", "Number of children",
        "Time employed", "Owns a car", "Owns realty",
        "Credit amount"
    ]
    # Get the values of desired features
    if customer_data["CODE_GENDER"] == 0 :
        gender = "Man"
    else :
        gender = "Woman"
    age = f"{customer_data["AGE"]} years old."
    childrens = f"{customer_data["CNT_CHILDREN"]} childrens."
    employed = f"{customer_data["TIME_EMPLOYED"]} years."
    if customer_data["FLAG_OWN_CAR"] == 0 :
        car = f"Does not own a car."
    else :
        car = f"Owns a car."
    if customer_data["FLAG_OWN_REALTY"] == 0 :
        realty = f"Does not own real estate."
    else :
        realty = f"Owns real estate."
    credit = customer_data["AMT_CREDIT"]
    # Create a list with the values
    general_values_list = [gender, age, childrens, employed, car, realty, credit]
    # Create the dataframe
    general_data = pd.DataFrame.from_dict({
        "Attributes": general_attributes_list,
        "Values": general_values_list
    })

    # Create a list of features to add to the returned dataframe
    financial_attributes_list = ["Credit", "Income", "Annuity"]
    # Get the values of desired features
    income = customer_data["AMT_INCOME_TOTAL"]
    annuity = customer_data["AMT_ANNUITY"]
    # Create a list with the values
    financial_values_list = [credit, income, annuity]
    # Create the dataframe
    financial_data = pd.DataFrame.from_dict({
        "Attributes": financial_attributes_list,
        "Values": financial_values_list
    })

    return general_data, financial_data

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
    # Check that we got a valid answer from the API
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
# Set columns description path
COLUMNS_URL = ("/data/columns/HomeCredit_columns_description.csv")

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

# Create the form where the user have to select the customer ID
with st.form("customer_selection_form"):
    st.write("Selection of the customer")
    customer_id = st.selectbox("Pick a customer", data["SK_ID_CURR"])
    submit = st.form_submit_button("Get score for this customer")

# Initialize tabs if the customer has not changed
if st.session_state.customer_id == customer_id:
    st.write("Same customer")
    tab1, tab2, tab3, tab4 = st.tabs(["Customer data", "Credit response", "Analyze a feature", "Analyze two features"])

# When submit is pressed
if submit or st.session_state.rerun:
    if submit and st.session_state.rerun:
        st.rerun()
    # If customer have changed, initialize tabs and reset rerun
    if st.session_state.customer_id != customer_id:
        st.session_state.rerun = False
        tab1, tab2, tab3, tab4 = st.tabs(["Customer data", "Credit response", "Analyze a feature", "Analyze two features"])
        st.session_state.customer_id = customer_id

    # Get customer data
    customer_data = get_customer_data(data, st.session_state.customer_id)
    customer_index = data.loc[data["SK_ID_CURR"] == st.session_state.customer_id, :].index[0]
    local_feature_importance = get_local_feature_importance(shap_values, customer_index)
    # Arrange customer data to display it
    general_data, financial_data = arrange_customer_data(customer_data)

    # Get main features by importance
    positive_important_features, negative_important_features = get_main_important_features(
        local_feature_importance, global_feature_importance
    )

    # Get data from the API
    response_data = get_scoring_data(st.session_state.customer_id)

    # In the first tab, we display the customer data
    with tab1:
        st.header("Customer data")
        st.write(f"Customer ID {st.session_state.customer_id}")
        st.dataframe(general_data, hide_index=True)

        # Create a bar chart to display financial data versus max. debt ratio
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=financial_data["Values"],
            y=financial_data["Attributes"],
            orientation="h"
        ))
        fig.add_vline(
            x=financial_data.loc[
                financial_data["Attributes"] == "Income",
                "Values"
            ].iloc[0] * 0.33,
            line_color="red",
            annotation_text="Max. debt ratio"
        )
        st.plotly_chart(fig)
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

        # Create a session state variable to store the feature to analyze
        if "selected_feature" not in st.session_state:
            st.session_state.selected_feature = data.columns[1]
        if "selected_feature_tmp" not in st.session_state:
            st.session_state.selected_feature_tmp = st.session_state.selected_feature

        # Define a callback function to update the session_state variable
        def on_feature_change():
            st.session_state.selected_feature = st.session_state.selected_feature_tmp

        st.selectbox(
            "Which feature do you want to analyze ?",
            data.columns.tolist(),
            key="selected_feature_tmp",
            index=data.columns.get_loc(st.session_state.selected_feature),
            placeholder="Select the feature from the list above",
            on_change=on_feature_change
        )
        st.session_state.rerun = True

        # Plot the histogram
        st.write(f"Analysis of the {st.session_state.selected_feature} feature for our customer compared to the population")
        # Create the plotly figure
        fig = go.Figure()
        # Create the histogram for all the population
        fig.add_trace(
            go.Histogram(
                x=data[st.session_state.selected_feature]
            )
        )
        # Create a line for our customer
        client_value = data.loc[
            data["SK_ID_CURR"] == st.session_state.customer_id,
            st.session_state.selected_feature
        ].iloc[0]
        fig.add_vline(
            x=client_value,
            line_color="red",
            annotation_text=f"Customer {st.session_state.customer_id}"
        )
        # Decoration of the plot
        fig.update_layout(
            xaxis_title=f"{st.session_state.selected_feature}",
            yaxis_title="Number of customers"
        )
        # Plot everything in streamlit
        st.plotly_chart(fig)
    # For the fourth tab, we display bivariate analysis of features
    with tab4:
        st.header("Analyze two features")

        # Create a session state variable to store the feature to analyze
        if "selected_feature1" not in st.session_state:
            st.session_state.selected_feature1 = data.columns[1]
        if "selected_feature_tmp1" not in st.session_state:
            st.session_state.selected_feature_tmp1 = st.session_state.selected_feature1
        if "selected_feature2" not in st.session_state:
            st.session_state.selected_feature2 = data.columns[2]
        if "selected_feature_tmp2" not in st.session_state:
            st.session_state.selected_feature_tmp2 = st.session_state.selected_feature2

        # Define a callback function to update the session_state variable
        def on_feature1_change():
            st.session_state.selected_feature1 = st.session_state.selected_feature_tmp1
        def on_feature2_change():
            st.session_state.selected_feature2 = st.session_state.selected_feature_tmp2

        st.selectbox(
            "Which is the first feature you want to plot ?",
            data.columns.tolist(),
            key="selected_feature_tmp1",
            index=data.columns.get_loc(st.session_state.selected_feature1),
            placeholder="Select the feature from the list above",
            on_change=on_feature1_change
        )
        st.session_state.rerun = True

        st.selectbox(
            "Which is the second feature you want to plot ?",
            data.columns.tolist(),
            key="selected_feature_tmp2",
            index=data.columns.get_loc(st.session_state.selected_feature2),
            placeholder="Select the feature from the list above",
            on_change=on_feature2_change
        )
        st.session_state.rerun = True

        # Plot the histogram
        st.write(f"Analysis of the {st.session_state.selected_feature1} feature vs the {st.session_state.selected_feature2} feature comparing our customer and the population")
        # Create the plotly figure
        fig = go.Figure()
        # Create the histogram for all the population
        fig.add_trace(
            go.Scatter(
                x=data[st.session_state.selected_feature1],
                y=data[st.session_state.selected_feature2],
                mode="markers"
            )
        )
        # Create a point for our customer
        client_value1 = data.loc[
            data["SK_ID_CURR"] == st.session_state.customer_id,
            st.session_state.selected_feature1
        ].iloc[0]
        client_value2 = data.loc[
            data["SK_ID_CURR"] == st.session_state.customer_id,
            st.session_state.selected_feature2
        ].iloc[0]
        fig.add_trace(
            go.Scatter(
                x=[client_value1],
                y=[client_value2],
                mode="markers",
                fillcolor="red",
                text=f"Customer {st.session_state.customer_id}",
                marker={
                    "color": "red",
                    "size": 8
                }
            )
        )
        # Plot everything in streamlit
        st.plotly_chart(fig)
