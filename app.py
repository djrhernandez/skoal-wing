from flask import Flask
app = Flask(__name__)
from reddit import get_reddit_data, load_secrets, set_headers

client_data = load_secrets()
headers = set_headers(client_data['auth_token'])


@app.route("/health_check")
def sanity():
    return {"health": "OK"}


@app.route("/", methods=['GET'])
def fetch_saved_links():
    params = {'limit': '10'}

    response = get_reddit_data('user/djrhernandez/saved', headers, params)
    return response


@app.route('/best', methods=['GET'])
def fetch_best_posts():
    params = {
        'count': '0',
        'limit': '10',
        'show': 'all',
    }

    response = get_reddit_data('best', headers, params)
    return response

@app.route('/<subreddit>/', defaults={'where': 'hot'})
@app.route('/<subreddit>/<where>', methods=['GET'])
def fetch_subreddit_hot(subreddit, where):
    params = {
        'count': '0',
        'limit': '10',
        'show': 'all',
    }

    if where == 'top':
        params['t'] = 'week'

    response = get_reddit_data(f"r/{subreddit}/{where}", headers, params)
    return response


if __name__ == "__main__":
    app.run(debug=True)