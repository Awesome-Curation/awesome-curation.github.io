import requests
import json
import re
import os

_API = 'https://api.github.com/'
_TOKEN = os.environ['TOKEN']

# Get JSON repo data from github api
def get_api_data(url):
    h = {'Authorization':"token " + _TOKEN,
         'Accept':'application/vnd.github.v3+json'}
    try:
        r = requests.get(_API + url, headers=h)
        # TODO: Handle status_code
        #print(json.dumps(r.json(), indent=4, sort_keys=True))
        return r.json()
    except requests.RequestException as err:
        print("Unable to get repo data")

# Extract username and repo name from github link
def get_user_repo(link):
    # ['https:', '', 'github.com', 'bayandin', 'awesome-awesomeness']
    parts = link.split("/")
    user = parts[3]
    repo = parts[4]
    return (user, repo)

# Get user token for github authentication
# Put token in a file instead of an environment variable 
def get_token():
    try:
        path = os.path.dirname(__file__)
        with open(path + "/token") as f:
            return f.readline().strip()
    except IOError as err:
        print("Failed to get API token\nCreate a 'token' file in this directory")

# Get links to GitHub emoji assets
# Returns dictionary of URLs
def get_emojis():
    return get_api_data("emojis")

def get_repo_data(user, repo):
    return get_api_data('repos/' + user + '/' + repo)

# Get README.md raw data file to string
def get_readme(user, repo):
    h = {"Accept":"application/vnd.github.VERSION.raw"}
    url = _API + 'repos/' + user + "/" + repo + "/readme"
    r = requests.get(url, headers=h)
    return r.text.encode('utf-8') 
 
 # Extract github link from a string
def get_url(text):
    try:
        if 'https://github.com/' in text:
            url = re.search("(?P<url>https?://[^\s]+)", text)  
            return url.group("url").replace(")","") 
    except IndexError:
        print("ERROR: Unable to extract URL")
    return ""

# Get all links from a file/string (\n separated)
# Return 'list' of links
def get_links(text):
    links=[]
    for line in text.splitlines():
        link = get_url(line)
        if link:
            links.append(get_url(line)) #+ "\n"
    return links #[:-1]
