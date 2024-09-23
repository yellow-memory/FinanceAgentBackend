import os
from dotenv import load_dotenv
import openai
import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO, StringIO
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import io

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
CORS(app)

def clean_code(code: str) -> str:
    # Remove ```python and ``` from the start and end of the response
    code = code.replace('```python', '').replace('```', '').strip()
    return code

def call_openai(prompt):# Add your OpenAI API key here
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Chat model
        messages=[
            {"role": "system", "content": "You are a helpful assistant for providing insights."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.5,
    )

    return response['choices'][0]['message']['content'].strip()

@app.route('/merge-excel', methods=['POST'])
def merge_excel():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "Please upload two files"}), 400

    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1.filename == '' or file2.filename == '':
        return jsonify({"error": "One of the files is missing a filename"}), 400

    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    prompt = (
        f"I have two Excel files containing the following data:\n\nFile 1:\n\n{df1}\n\nFile 2:\n\n{df2}\n\nPlease merge these datasets side by side, aligning the rows horizontally, and filling missing values with NaN. Return only the merged result in a structured format without any code or explanation."
    )

    openai_response = call_openai(prompt)
    print(openai_response)

    return jsonify({"merge_result": openai_response})

@app.route('/cohort-analysis', methods=['POST'])
def cohort_analysis():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    print(file)
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        df = pd.read_excel(file)
        prompt = (
            f"I have the following customer data in an Excel file:\n\n{df}\n\n"
            "The dataset includes columns like 'Date', 'Customer ID', 'Purchase Amount', and 'Customer Type'. "
            "Please perform a cohort analysis, grouping customers by the month of their first purchase. Calculate the monthly retention rate for each cohort over time. "
            "Return only the analysis results, including retention rates, churn rates, and key insights, in a structured format without any code or explanation."
        )
        openai_response = call_openai(prompt)
        print(openai_response)
        return jsonify({"cohort_result": openai_response})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sales-insights', methods=['POST'])
def sales_insights():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    try:
        file = request.files['file']
        
        df = pd.read_excel(file)
        data_sample = df.to_string()
        
        prompt = f"I have the following customer purchase data:\n\n{data_sample}\n\nProvide insights on frequent purchase behaviors like common categories, customer types, and trends in sales."
        openai_response = call_openai(prompt)

        return jsonify({"insights": openai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/sales-kpis', methods=['POST'])
def sales_kpis():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    try:
        file = request.files['file']
        
        df = pd.read_excel(file)
        data_sample = df.to_string()
        
        prompt = f"I have the following sales data:\n\n{data_sample}\n\nBased on this, what are the top KPIs I should focus on?"
        openai_response = call_openai(prompt)

        return jsonify({"kpis": openai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/sales-keydrivers', methods=['POST'])
def sales_keydrivers():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    try:
        file = request.files['file']
        
        df = pd.read_excel(file)        
        data_sample = df.to_string()
        
        prompt = f"I have the following recent sales data:\n\n{data_sample}\n\nIdentify the key drivers behind my company's revenue growth in the past quarter."
        openai_response = call_openai(prompt)

        return jsonify({"key_drivers": openai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/clean-dataset', methods=['POST'])
def clean_dataset_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    if not file.filename.endswith(('.xls', '.xlsx')):
        return jsonify({"error": "Invalid file format, only Excel files are allowed"}), 400

    try:
        df = pd.read_excel(file)
        print(df)

        data_json = df.to_string()
        prompt = f"""
            Please clean this sales dataset by performing the following actions:
            1. Remove any duplicate entries.
            2. Handle missing values by removing rows with missing critical data (e.g., Transaction ID, Customer Name, Transaction Date, Amount).
            3. Standardize all date formats to 'YYYY-MM-DD'.
            4. Ensure consistent string formatting by:
            - Trimming leading and trailing spaces.
            - Converting all text fields (e.g., Customer Name, Email, Country) to title case or proper case where appropriate.
            5. Return the cleaned dataset as a table, with no additional comments or explanations.
            The dataset is: {data_json}
            """

        openai_response = call_openai(prompt)
        print("openai connection is succeed\n")
        print(openai_response)

        return jsonify({"cleaned_data": openai_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/identify-outliers', methods=['POST'])
def identify_outliers():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    if not file.filename.endswith(('.xls', '.xlsx')):
        return jsonify({"error": "Invalid file format, only Excel files are allowed"}), 400

    try:
        df = pd.read_excel(file)
        print(df)

        data_json = df.to_string()
        prompt = f"""
            Please analyze this sales dataset and identify the outliers based on the following criteria:
            1. Unusually high or low transaction amounts compared to the rest of the dataset.
            2. Transactions that occur at abnormal times or dates.
            3. Repeated transactions or unusually high frequency of transactions for the same customer.
            
            Return only the rows of the dataset that are flagged as outliers, with an additional column 'Outlier Reason' explaining why each row was flagged. Do not return any Python code or additional explanations.
            The dataset is: {data_json}
        """
        openai_response = call_openai(prompt)
        print("openai connection is succeed\n")
        print(openai_response)
        # lines = openai_response.strip().split('\n')

        # data = []
        # for line in lines[0:]:
        #     values = [value.strip() for value in line.split('|')[1:-1]] 
        #     if any(values):  
        #         data.append(values)

        return jsonify({"outliers": openai_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
