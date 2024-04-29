import json
import flask
from flask import Flask,redirect, render_template, request, jsonify
from flask_cors import CORS
from app import process_query
app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['POST','GET'])
def search():
    print("Received a POST request")
    if request.method == "POST":
        search_query = request.form.get('query')
        # print(f"Received query: {search_query}")
        if  not search_query:
            return render_template("error.html", message = "No results found")
        
        search_data = {'search_query':search_query}
    #         search_data = {'query': search_query}
    #         # jsonified_data = jsonify(search_data)
        with open ('./search_data.json', 'w') as f:
            json.dump(search_data, f, indent=4)
        results = process_query()
        if not results:
            return render_template('error.html', message="No results found.")
        
        return render_template('results.html', documents = results, search_query = search_query)

@app.route('/home')
def home():
    # Add any logic here for rendering the home page
    return render_template('home.html')  # Replace 'home.html' with the actual template filename


@app.route('/')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)