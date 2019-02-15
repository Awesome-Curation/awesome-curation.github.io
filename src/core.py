import api
import re
import json
import os.path
from helpers import write_emojis

def main():
    sandbox_links = get_root_path() + '/src/sandbox'
    with open(sandbox_links) as f:
        text = f.read()
    
    destroy_table()
    write_table(text)        

# Read emojis from json text file
def read_emojis():
    g_emojis = get_root_path() + '/data/emojis.txt'
    try:
        with open(g_emojis, 'r') as f:
            data = f.read()
    except IOError:
        print("Error reading emojis.txt"
              "Calling api rewrite file...")
        return write_emojis()
    except ValueError:
        print("Fatal error. Could not fetch emojis"
              "Reevaluate your life.")

    return json.loads(data)

# Get the root directory of the project
# (Just the parent directory. Probably a much better way)
def get_root_path(f=__file__):
    path = os.path.dirname(f)
    return os.path.abspath(os.path.join(path, os.pardir)) 

# Delete table from index.html
def destroy_table():
    site = get_root_path() + '/index.html'
    with open(site, 'r') as f:
        buffer = f.readlines()
    
    isTable = False
    with open(site, 'w') as html:
        for line in buffer:
            if 'Begin Table Insertion' in line:
                isTable = True
                html.write('<!-- Begin Table Insertion -->\n')  
            elif 'End Table Insertion' in line:
                isTable = False
            
            if not isTable:
                html.write(line)    

# Insert table into html webpage 
def write_table(data):
    site = get_root_path() + '/index.html'
    with open(site, 'r') as f:
        buffer = f.readlines()
    
    data = build_table(data)
    with open(site, 'w') as html:
        for line in buffer:
            if 'Begin Table Insertion' in line:
                line += data
            html.write(line)    

# Return a string with the html formatted table rows
def build_table(text):
    table = ""
    for link in api.get_links(text):
        (user, repo) = api.get_user_repo(link)
        data = api.get_repo_data(user, repo)
        tr = html_print(repo, link, data)
        table += tr

    return table

# Format description to include emoji images 
def format_description(text):
    formatted = text
    # Check if description has emojis
    if re.search(':[a-z_]{1,30}:', text):
        words = text.split()
        cat = ''
        for word in words:
            # Could not find UTF-8 emoji - Using GitHub image
            if re.search(':[a-z_]{1,30}:', word):
                r = re.sub(':', '', word)
                try:
                    # Put in an image html tag
                    g_emojis = read_emojis()
                    tag = "<img src='" + g_emojis[r] + "'> "
                except (KeyError, AttributeError):
                    print("Unable to get emoji")
                    tag = ''
                cat += tag
            else:
                # Concatenate words normally
                cat += word + ' '
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
               "    <td> <a href='" + url + "'target='_blank'>" + name +"</a></td>\n"
               "    <td>"+ description +"</td>\n"
               "    <td>"+ str(stars)  +"</td>\n"
               "    <td>"+ str(forks)  +"</td>\n"
               "    <td>"+ lang  +"</td>\n"
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

    return row.encode('utf-8')

if __name__ == '__main__':
    main()