import pandas as pd
import os
from flask import render_template, Flask
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/results', methods=['GET'])
def result():
    if not os.path.isfile('final.csv'):
        return "No result file found"
    df = pd.read_csv('final.csv')
    data = df.to_dict(orient='records')  # Convert DataFrame to list of dicts
    return render_template('results.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)