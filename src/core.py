import api
import re
import json
import os.path
from helpers import write_emojis

# HTML page markers for inserting text
MARKERS = ["Dropdown", "Table"]

def main():
    sandbox_readme = get_root_path() + '/data/sandbox_readme'
    #sandbox_links = get_root_path() + '/src/sandbox'
    with open(sandbox_readme) as f:
        text = f.read()
    
    
    repos = build_links_dict(text)
    links = repos['Bluetooth']

    destroy_section('Table')
    write_section(links, 'Table')        


# Write categories to html
# Accepts dictionary (with categories key) or list
def build_categories(items):
    sections = []
    if isinstance(items, dict):
        for key in items:
            sections.append(key)
    elif isinstance(text, list):
        sections = items
    else:
        print("Unsupported text argument. Requires dictionary or list")
        return []
    return sections

# Format categories to html for dropdown button
def html_categories(sections):
    try:
        for item in sections:
            rows += "<option>" + item + "</option>\n"
    except AttributeError as err:
        print("============")
        print("Categories attribute error")
        print(sections)
        return ""

    return rows.encode('utf-8')

# Create dictionary for links with category
# Keys - Categories
# Values - List of repo links
def build_links_dict(text):
    section = 'unknown'
    items = []
    repos = {}
    for line in text.splitlines():
        if re.search('^#{2,5}', line):
            items = []
            h = re.sub('^#{2,5} {1,5}','',line)        
            if len(h) > 0:
                section = h 
        if re.search('\* \[.*]\(http[s]?:\/\/.*\)', line):
            items.append(line)
            repos[section] = items    
    return repos

# Get all links from a file/string (\n separated)
# Return 'list' of links
def repo_links(text):
    links=[]
    lines = []
    if isinstance(text, str):
        lines = text.splitlines()
    elif isinstance(text, list):
        lines = text
    else:
        print("Unsupported text argument. Requires string or list")

    for line in lines:
        link = api.get_url(line)
        if link:
            links.append(link) #+ "\n"
            
    return links #[:-1]


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

# Delete section from index.html
# section - marker to look for (ex: Dropdown)
def destroy_section(section):
    if section not in MARKERS:
        print("Unable to find html marker to destroy")
        return

    site = get_root_path() + '/index.html'
    with open(site, 'r') as f:
        buffer = f.readlines()
    
    marker = section + ' Insertion'
    isSection = False
    with open(site, 'w') as html:
        for line in buffer:
            if 'Begin ' + marker in line:
                isSection = True
                html.write('<!-- Begin ' + marker + ' -->\n')  
                start_success = True
            elif 'End ' + marker in line:
                isSection = False
                end_success = True
            
            if not isSection:
                html.write(line)    

        if not start_success:
            print("Unable to find '" + section + "' Begin marker")
        if not end_success:
            print("Unable to find '" + section + "' End marker")

# Insert section into html webpage 
# date - text to write
# section - marker to look for (ex: Dropdown)
def write_section(data, section):
    if section not in MARKERS:
        print("Unable to find html marker to insert")
        return

    marker = 'Begin ' + section + ' Insertion'
    site = get_root_path() + '/index.html'
    with open(site, 'r') as f:
        buffer = f.readlines()
    
    info = build_table(data)
    with open(site, 'w') as html:
        for line in buffer:
            if marker in line:
                line += info
                success = True
            html.write(line)    
        if not success:
            print("Unable to insert '" + section + "' into html page")

# Return a string with the html formatted table rows
def build_table(text):
    table = ""
    for link in repo_links(text):
        (user, repo) = api.get_user_repo(link)
        data = api.get_repo_data(user, repo)
        tr = html_table(repo, link, data)
        table += tr

    return table

# Format description to include emoji images 
def format_description(text):
    if not text:
        return ''
    
    formatted = text
    emojis = re.findall(':[a-z_]{1,30}:', text)
    for emoji in emojis:
        name = re.sub(':', '', emoji)
        try:
             # Put in an image html tag
             g_emojis = read_emojis()
             tag = "<img src='" + g_emojis[name] + "'> "
        except (KeyError, AttributeError):
            print("Unable to get emoji")
            print("Full description: " + text)
            tag = ''
        formatted = re.sub(emoji, tag, formatted)
    
    return formatted

# Format repo info to an html table row
# Sometime api returns with values missing. Need to reload if so
def html_table(repo, url, data):
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
        print("Table unicode error")
        print(repo)
        print(lang)
        return ""
    except AttributeError as err:
        print("Table attribute error")
        print(repo)
        return ""

    return row.encode('utf-8')

if __name__ == '__main__':
    main()