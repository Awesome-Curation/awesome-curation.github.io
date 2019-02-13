from api import *

g_emojis = get_emojis()

def main():
    with open('/Users/ryanhennings/Developer/Python/GitHub-Collections-Filter/s2') as f:
        text = f.read()

    #link = get_links(text)[0]
    #(user, repo) = get_user_repo(link)
    #data = get_repo_data(user, repo)
    #tr = html_print(repo, link, data)

    user = 'MaximAbramchuck'
    repo = 'awesome-interview-questions#ios'

    #j = get_repo_data(user,repo)
    #description = j['description']
    #print(description)
    #f = format_description(description)
    #print(f)

    footer = "</table></body></html>"
    path = os.path.dirname(__file__)
    with open(path + "/table.html", "a") as f:
        for link in get_links(text):
            (user, repo) = get_user_repo(link)
            data = get_repo_data(user, repo)
            tr = html_print(repo, link, data)
            f.write(tr)
        f.write(footer)

def format_description(text):
    formatted = text
    if re.search(':[a-z_]{1,30}:', text):
        s = text.split()
        cat = ''
        for w in s:
            # Could not find UTF-8 emoji - Using GitHub image
            if re.search(':[a-z_]{1,30}:', w):
                r = re.sub(':', '', w)
                try:
                    tag = "<img src='" + g_emojis[r] + "'> "
                except (KeyError, AttributeError):
                    print("Unable to get emoji")
                    tag = ''
                cat += tag
            else:
                cat += w + ' '
        formatted = cat
    return formatted

# Format repo info to an html table row
# Sometime api returns with values missing. Need to reload if so
def html_print(repo, url, data):
    stars = data['stargazers_count']
    forks = data['forks_count']
    name = data['name'] if data['name'] != None else "None" # None == NoneType i guess
    lang = data['language'] if data['language'] != None else "None"
    description = format_description(data['description'])   

    try:
        row = ("<tr>\n"
                "<td> <a href='" + url + "'target='_blank'>" + name +"</a></td>\n"
                "<td>"+ description +"</td>\n"
                "<td>"+ str(stars)  +"</td>\n"
                "<td>"+ str(forks)  +"</td>\n"
                "<td>"+ lang  +"</td>\n"
                "</tr>\n")
    except UnicodeDecodeError as err:
        print("============")
        print("unicode error")
        print(repo)
        print(lang)
        return ""
    except AttributeError as err:
        print("============")
        print("Attribute error")
        print(repo)
        return ""

    print(row)
    return row.encode('utf-8')

# Print repo information to console
def console_print(repo, url, data):
    stars = data['stargazers_count']
    forks = data['forks_count']
    lang = data['language']
    print('='*60)
    print('Repo:     ' + repo)
    print('Link:     ' + url)
    print('Stars:    ' + str(stars))
    print('Forks:    ' + str(forks))
    print('Language: ' + str(lang))    
    print('='*60+'\n')

if __name__ == '__main__':
    main()