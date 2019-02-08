import requests
import json
import re
import os
import emoji

awesome = 'awesome-ios'
user = 'vsouza'
u2 = 'JohnEstropia' 
r2 = 'GCDKit'
API = 'https://api.github.com/'
TOKEN = os.environ['TOKEN']

print("\n\n\n")
print("$" * 65)

def main():
    emojis = get_emojis()

    with open('/Users/ryanhennings/Developer/Python/GitHub-Collections-Filter/sandbox') as f:
        text = f.read()

    #rgx = re.compile(':[a-z_]{1,30}:')
    for x in text.splitlines():
        if re.search(':[a-z_]{1,30}:', x):
            print(x)
        else:
            print(x)

    #link = get_links(text)[0]
    #(user, repo) = get_user_repo(link)
    #data = get_repo_data(user, repo)
    #tr = html_print(repo, link, data)

    #footer = "</table></body></html>"
    #path = os.path.dirname(__file__)
    #with open(path + "/table.html", "a") as f:
    #    for link in get_links(text):
    #        (user, repo) = get_user_repo(link)
    #        data = get_repo_data(user, repo)
    #        tr = html_print(repo, link, data)
    #        f.write(tr)
    #        break
    #    f.write(footer)

def formatted_description(text):

    return ""

# Format repo info to an html table row
def html_print(repo, url, data):
    stars = data['stargazers_count']
    name = data['name']
    forks = data['forks_count']
    lang = data['language']

    description = formatted_description(data['description'])   

    row = ("<tr>\n"
            "<td> <a href='" + url + "'target='_blank'>" + name +"</a></td>\n"
            "<td>"+ description +"</td>\n"
            "<td>"+ str(stars)  +"</td>\n"
            "<td>"+ str(forks)  +"</td>\n"
            "<td>"+ str(lang)   +"</td>\n"
            "</tr>\n")
    return row.encode('utf-8')

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

def get_emojis():
    return get_api_data("emojis")

def get_repo_data(user, repo):
    return get_api_data('repos/' + user + '/' + repo)

# Get JSON repo data from github api
def get_api_data(url):
    h = {'Authorization':"token " + TOKEN,
         'Accept':'application/vnd.github.v3+json'}
    try:
        r = requests.get(API + url, headers=h)
        # TODO: Handle status_code
        #print(json.dumps(r.json(), indent=4, sort_keys=True))
        return r.json()
    except requests.RequestException as err:
        print("Unable to get repo data")

# Get README.md raw data file to string
def get_readme(user, repo):
    h = {"Accept":"application/vnd.github.VERSION.raw"}
    url = API + 'repos/' + user + "/" + repo + "/readme"
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