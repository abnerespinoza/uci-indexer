from flask import Flask, request
from search import searchURLs
app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/search', methods=['GET'])

def urls():
    searchQuery = ""

    if 'searchQuery' in request.args:
       searchQuery = request.args['searchQuery'] 
    else:
        return "Error: No searchQuery field provided. Please specify an searchQuery."
    

    url_results = {}
    url_results = searchURLs(searchQuery)
    
    return url_results

app.run()