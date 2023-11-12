from flask import Flask
app = Flask(__name__)
from reddit_get_me import load_secrets, set_headers, get_reddit_saved, prettify_json

client_data = load_secrets()
headers = set_headers(client_data['auth_token'])

@app.route("/")
def sanity():
    return {"health": "OK"}

@app.route("/all_links")
def all_saved_links():
    data = get_reddit_saved(headers)
    results = data['data']['children']

    print(f"--- BIG DOSH RESULTS ---")
    
    for item in results:
        prettify_json(item['data'])

    print(f"Length: {len(results)}")
    return results

@app.route("/saved")
def saved_links():
    return {"health": "OK"}

if __name__ == "__main__":
    app.run(debug=True)