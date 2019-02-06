import requests
import json
import re

awesome = 'awesome-ios'
user = 'vsouza'
api = 'https://api.github.com/'
debug = False

print("\n\n\n")
print("$" * 65)
print("$" * 65)

def get_repo(user, repo):
    url  = api + 'repos/' + user + '/' + repo
    r = requests.get(url)
    parsed = json.loads(r.text)
    #print(json.dumps(parsed, indent=4, sort_keys=True))
    return parsed

def get_readme(user, repo):
    url = api + 'repos/' + user + "/" + repo + "/readme"
    r = requests.get(url, headers={"Accept":"application/vnd.github.VERSION.raw"})
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

#f = open('/tmp/readme2', 'r+')
#f.write(text)
with open('/Users/ryanhennings/Developer/Python/GitHub-Collections-Filter/sample') as f:
    text = f.read()

print(loop_file(text))


#print("Full Count: " + str(text.count('\n')))
#print("Link Count: " + str(links.count('\n')))
#print("Link Count: " + str(count))


print("*" * 65)
print("*" * 65)

