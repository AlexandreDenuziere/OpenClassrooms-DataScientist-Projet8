# Import libraries
# Flask
import flask
from flask import request, jsonify

# Pickle
import pickle

# Pandas
import pandas as pd

# Create Flask objects
app = flask.Flask(__name__)

# Load the model
model = pickle.load(open("./model/model.pkl", "rb"))
# Load the data
df = pd.read_csv("/data/test_data_cleaned.csv").drop("TARGET", axis=1)

@app.route("/api/v1/customer", methods=["GET"])
def api_id():
    if "id" in request.args:
        try:
            customer_id=int(request.args["id"])
        except ValueError:
            return "Error: Are you sure you typed the customer ID correctly ? Please try again !"
    else:
        return """Error: No id provided. Please provide a customer ID. <br>The request should look like /api/v1/customer?id=12456"""
    # Select the customer in the dataframe
    customer = df.loc[df["SK_ID_CURR"]==customer_id, :]
    if customer.shape[0] != 1:
        return "Error: Bad customer ID provided. Please try again !"
    # Make the predictions
    results = model.predict_proba(customer)
    result = model.predict(customer)
    # Get the good customer proba
    good_customer_proba = results[0][0]
    # Get the bad customer proba
    bad_customer_proba = results[0][1]
    # Put the prediction into text
    if result == 0:
        translated_result = "Good customer, offer him his credit !"
    else:
        translated_result = "Bad customer, offer him a coffee !"
        
    # Create the response before convert it to JSON format
    response = {
        "Probability of the customer being a good one": good_customer_proba,
        "Probability of the customer being a bad one": bad_customer_proba,
        "Result of the analysis": translated_result,
    }
    return jsonify(response)

app.run(host="0.0.0.0", port=5001)
