import requests
import json
import re
import os

awesome = 'awesome-ios'
user = 'vsouza'
u2 = 'JohnEstropia' 
r2 = 'GCDKit'
api = 'https://api.github.com/'

print("\n\n\n")
print("$" * 65)
print("$" * 65)
def main():
    #f = open('/tmp/readme2', 'r+')
    #f.write(text)
    with open('/Users/ryanhennings/Developer/Python/GitHub-Collections-Filter/sandbox') as f:
        text = f.read()

    #print(loop_file(text))
    #print(get_token())
    get_repo(u2, r2)

def get_token():
    try:
        path = os.path.dirname(__file__)
        with open(path + "/token") as f:
            return f.readline().strip()
    except IOError as err:
        print("Failed to get API token\nCreate a 'token' file in this directory")

def get_repo(user, repo):
    h = {'Authorization':"token " + get_token(),
         'Accept':'application/vnd.github.v3+json'}
    try:
        url  = api + 'repos/' + user + '/' + repo 
        r = requests.get(url, headers=h)
        #print(json.dumps(r.json(), indent=4, sort_keys=True))
        return r.json()
    except requests.RequestException as err:
        print("Unable to get repo data")

def get_readme(user, repo):
    h = {"Accept":"application/vnd.github.VERSION.raw"}
    url = api + 'repos/' + user + "/" + repo + "/readme"
    r = requests.get(url, headers=h)
    return r.text.encode('utf-8') 
 
 # Extract github link from a string
def get_url(text):
    try:
        if 'https://github.com/' in text:
            url = re.search("(?P<url>https?://[^\s]+)", text)  
            return url.group("url").replace(")","") 
    except IndexError:
        print("Unable to extract URL")
    return ""

# Get all links from a file/string (\n separated)
def loop_file(text):
    links=""
    for line in text.splitlines():
        link = get_url(line)
        if link:
            links += get_url(line) + "\n"
    return links[:-1]

if __name__ == "__main__":
    main()

print("*" * 65)
print("*" * 65)

# TODO items
#forks_count
#language
#stargazers_count
#subscribers_count
#watchers_count
# Need to look at status codes for contributors
#+ /stats/contributors""