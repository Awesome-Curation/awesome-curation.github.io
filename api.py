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

def main():
    #f = open('/tmp/readme2', 'r+')
    #f.write(text)
    with open('/Users/ryanhennings/Developer/Python/GitHub-Collections-Filter/sandbox') as f:
        text = f.read()

    #for link in get_links(text):
    #    (user, repo) = get_user_repo(link)
    #    data = get_repo_data(user, repo)
    #    console_print(repo, link, data)

    #link = get_links(text)[0]
    #(user, repo) = get_user_repo(link)
    #data = get_repo_data(user, repo)
    #tr = html_print(repo, link, data)

    footer = "</table></body></html>"
    path = os.path.dirname(__file__)
    with open(path + "/table.html", "a") as f:
        for link in get_links(text):
            (user, repo) = get_user_repo(link)
            data = get_repo_data(user, repo)
            tr = html_print(repo, link, data)
            f.write(tr)
        f.write(footer)

# Format repo info to an html table row
def html_print(repo, url, data):
    stars = data['stargazers_count']
    forks = data['forks_count']
    lang = data['language']
    row = ("<tr>\n"
            "<td> <a href='" + url + "'target='_blank'>" + str(repo) +"</a></td>\n"
            "<td>"+ str(stars) +"</td>\n"
            "<td>"+ str(forks) +"</td>\n"
            "<td>"+ str(lang)  +"</td>\n"
            "</tr>\n")
    return row

# Extract username and repo name from github link
def get_user_repo(link):
    # ['https:', '', 'github.com', 'bayandin', 'awesome-awesomeness']
    parts = link.split("/")
    user = parts[3]
    repo = parts[4]
    return (user, repo)

# Print repo information to console
def console_print(repo, url, data):
    stars = data['stargazers_count']
    forks = data['forks_count']
    lang = data['language']
    print("="*60)
    print("Repo:     " + repo)
    print("Link:     " + url)
    print("Stars:    " + str(stars))
    print("Forks:    " + str(forks))
    print("Language: " + str(lang))    
    print("="*60+"\n")

# Get user token for github authentication
def get_token():
    try:
        path = os.path.dirname(__file__)
        with open(path + "/token") as f:
            return f.readline().strip()
    except IOError as err:
        print("Failed to get API token\nCreate a 'token' file in this directory")

# Get JSON repo data from github api
def get_repo_data(user, repo):
    h = {'Authorization':"token " + get_token(),
         'Accept':'application/vnd.github.v3+json'}
    try:
        url  = api + 'repos/' + user + '/' + repo
        r = requests.get(url, headers=h)
        # TODO: Handle status_code
        #print(json.dumps(r.json(), indent=4, sort_keys=True))
        return r.json()
    except requests.RequestException as err:
        print("Unable to get repo data")

# Get README.md raw data file to string
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

if __name__ == "__main__":
    main()

print("*" * 65)

# TODO items
#subscribers_count
#watchers_count
# Need to look at status codes for contributors
#+ /stats/contributors""