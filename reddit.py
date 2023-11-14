import sys
import argparse
import requests
import json
from flask import jsonify
from prettytable import PrettyTable

# Open/Load the JSON file/data into a Python dictionary object
def load_secrets():
    with open('client_secrets.json', 'r') as file:
        json_data = json.load(file)
    return json_data

# Initialize headers or add token to header object
def set_headers(token=None):
    headers = {"User-Agent": "saved-links app by djrhernandez"}
    if token:
        headers['Authorization'] = "bearer %s" % (token)
    return headers

# Helper function to word wrap text
def word_wrap(text, width):
    return [text[i:i + width] for i in range(0, len(text), width)]

# Parse data into a formatted table with PrettyTable
def prettify_json(data, wrap_width=50):
    # Create a PrettyTable instance
    table = PrettyTable()

    # Helper function to handle nested objects, strings, etc.
    def process_value(key, value):
        if isinstance(value, dict):
            # If the value is a dictionary, recursively process it
            table.add_row(["-" * wrap_width, "-" * wrap_width])
            for nested_key, nested_value in value.items():
                process_value(f"{key}.{nested_key}", nested_value)
            table.add_row(["-" * wrap_width, "-" * wrap_width])
        elif isinstance(value, list):
            # If the value is a list(array), join the elements into a string
            table.add_row(["[" + ("-" * wrap_width) + "]", "[" + ("-" * wrap_width) + "]"])
            joined_value = "\n".join(map(str, value))
            wrapped_value = "\n".join(word_wrap(joined_value, wrap_width))
            table.add_row([key, wrapped_value])
        elif isinstance(value, str):
            # Word wrap the value if it's a string
            wrapped_value = "\n".join(word_wrap(value, wrap_width))
            table.add_row([key, wrapped_value])
        else:
            table.add_row([key, value])

    # Process the JSON data
    for key, value in data.items():
        process_value(key, value)
    
    # Finally set the field names to "Field" and "Value"
    table.field_names = ["Field", "Value"]
    
    print(table)

''' API call to GET reddit info
    Possible endpoints:
        Links:
        - POST /api/save
        - POST /api/unsave
        Listings:
        - GET /best
        - GET /{subreddit}/hot
        - GET /{subreddit}/sort
            - /{subreddit}/controversial
            - /{subreddit}/top
        Search:
        - GET /{subreddit}/search
        Subreddits:
        - POST /api/search_subreddits
        - GET /subreddits/popular
        - GET /subreddits/search
        Widgets & Wiki:
        - POST /{subreddit}/api/widget
        - GET /{subreddit}/api/widgets
        - GET /{subreddit}/wiki/pages
'''
def get_reddit_data(endpoint="", headers=None, params=None):
    base_url = "https://oauth.reddit.com"
    url = f"{base_url}/{endpoint}"

    if params:
        response = requests.get(url, headers=headers, params=params)
    else:
        response = requests.get(url, headers=headers)
        
    print(f"[GET] - {response.url}")
    if response.status_code == 200:
        results = response.json()
        result_data = results['data']['children']

        payload = []
        for item in result_data:
            data = item['data']
            print(f"{data}\n\n")

            if data['over_18'] == False or data['thumbnail'] != 'nsfw':
                reddit_post = {
                    'author': data['author'],
                    'author_fullname': data['author_fullname'],
                    'created': data['created'],
                    'created_utc': data['created_utc'],
                    'id': data['id'],
                    'media': data['media'],
                    'name': data['name'],
                    'num_comments': data['num_comments'],
                    'permalink': data['permalink'],
                    'score': data['score'],
                    'subreddit': data['subreddit'],
                    'subreddit_id': data['subreddit_id'],
                    'subreddit_name_prefixed': data['subreddit_name_prefixed'],
                    'thumbnail': data['thumbnail'],
                    'title': data['title'],
                    'url': data['url'],
                }
                payload.append(reddit_post)

        print(f"Total Count: {len(payload)}")
        return payload
    else:
        return jsonify({'error': 'Failed to fetch data'}), response.status_code



def post_reddit_data(endpoint="api/search_subreddits", headers=None, params=None):
    base_url = "https://oauth.reddit.com"
    url = f"{base_url}/{endpoint}"

    if params:
        response = requests.post(url, headers=headers, params=params)
    else:
        response = requests.post(url, headers=headers)
        
    print(f"[POST] - {response.url}")
    if response.status_code == 200:
        results = response.json()
        print(f"{results}")
        return results
    else:
        return jsonify({'error': 'Failed to fetch data'}), response.status_code


# Fetch Karma from RedditAPI
def get_reddit_karma(headers):
    url = "https://oauth.reddit.com/api/v1/me/karma"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        results = response.json()
        prettify_json(results)
        print(f'GET {url} - {response.reason} [{response.status_code}]')
        return results
    else:
        return jsonify({'error': 'Failed to fetch data'}), response.status_code

def main():
    client_data = load_secrets()
    header_data = set_headers()    
    post_data = {"grant_type": "password", "username": "djrhernandez"}
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-at', "--access-token", nargs='?', const=True, help='Request a Reddit access token')
    parser.add_argument('-e', "--endpoint", nargs='?', const=True, help='Endpoint for Reddit\'s API')
    
    args = parser.parse_args()

    # Send a POST request for a new access token if the argument is provided
    if args.access_token:
        password = input('Enter password: ')
        post_data['password'] = password

        client_auth = requests.auth.HTTPBasicAuth(client_data['client_id'], client_data['client_secret'])
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=header_data)
        ''' Example: API response object
        {
            u'access_token': u'fhTdafZI-0ClEzzYORfBSCR7x3M',
            u'expires_in': 3600,
            u'scope': u'*',
            u'token_type': u'bearer'
        }
        '''

        print(f"Fetching new access token...")
        if response.status_code == 200:
            results = response.json()
            print(f"Received access token: {results['access_token']}")
            
            # Now you can make API requests with the access token
            header_data = set_headers(results['access_token'])
        else:
            print(f"Error fetching access token: {response.status_code}")
    else:
        header_data = set_headers(client_data['auth_token'])

    if args.endpoint:
        get_reddit_data(args.endpoint, header_data)
    else: 
        get_reddit_karma(header_data)

    return 0

if __name__ == "__main__":
    sys.exit(main())