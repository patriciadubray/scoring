import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request, send_file
import joblib
import pandas as pd
import pickle

app = Flask(__name__)

# Load the model
model = joblib.load('model.pkl')

# Load the MinMaxScaler from mms.pkl
mms = joblib.load('mms.pkl')

# Load the SHAP explainer from shap.pkl
explainer = joblib.load('shap.pkl')

# Define the route for making predictions
@app.route('/predict', methods=['POST'])
def predict():
    # Retrieve the data sent as JSON
    data = request.get_json()

    # Create a DataFrame from the data
    df = pd.DataFrame([data], index=[0])

    # Normalize the input data using MinMaxScaler
    df_normalized = pd.DataFrame(mms.transform(df), columns=df.columns)

    # Make predictions
    proba = model.predict_proba(df_normalized)
    class_0_proba = proba[0][0]
    class_1_proba = proba[0][1]

    class_0_percentage = round(class_0_proba * 100, 1)
    class_1_percentage = round(class_1_proba * 100, 1)

    class_0 = f"Classe 0 : {class_0_percentage}% de probabilité que le remboursement soit ok"
    class_1 = f"Classe 1 : {class_1_percentage}% de probabilité d'avoir des problèmes de remboursement"

    result = {
        "class_0": class_0,
        "class_1": class_1
    }

    # Generate SHAP visualization for the observation
    shap_values = explainer.shap_values(df_normalized.iloc[[0]])
    
    # Summary plot
    shap.summary_plot(shap_values, df_normalized.iloc[[0]], plot_type="bar")

    # Save the summary plot to a file
    summary_plot_path = 'summary_plot.png'
    plt.savefig(summary_plot_path)
    plt.clf()  # Clear the plot

    # Return the predictions and file path as JSON
    result["summary_plot_path"] = summary_plot_path
    return jsonify(result)


# Route for downloading the summary plot
@app.route('/download/summary_plot')
def download_summary_plot():
    return send_file('summary_plot.png', as_attachment=True)


# Route for the home page
@app.route('/')
def home():
    return "API dashboard prêt à dépenser"


if __name__ == '__main__':
    # Display a message when the URL is launched
    print("API dashboard prêt à dépenser")
    app.run(debug=True, port=0, use_reloader=False)