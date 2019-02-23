#!/usr/bin/env python
# -*- coding: utf-8 -*

import os.path
import re
import time
import json

import api
from helpers import write_emojis, get_root_path

# HTML page markers for inserting text
MARKERS = ["Dropdown", "Table"]

def main():
    start_time = time.time()

    sandbox_readme = get_root_path() + '/data/sandbox_readme'
    with open(sandbox_readme) as f:
        text = f.read()
    
    repos = build_links_dict(text)
    links = repos['UI']
    print(api.get_rate_limit('Reset'))

    destroy_section('Table')
    destroy_section('Dropdown')
    write_section(build_categories(repos), 'Dropdown')
    write_section(build_table(links), 'Table')        

    elapsed_time = time.time() - start_time
    print('Time elapsed: ' + str(float("%0.4f" % (elapsed_time))))

'''
MARK: Build Core Data Section
'''

# Create dictionary for links with category
# Keys - Categories
# Values - List of repo links
def build_links_dict(text):
    """ Get all repositories in each category

    This function traverses a markdown formatted string to get
    links to all repositories in each category. A dictionary is
    formed with a the category as the key and a list of GitHub 
    links (strings) as the value. Currently the lists of links are 
    only stored in the immediate parent markdown header (i.e. there 
    are no sub-sections iOS->UI->Animation->Transformation would 
    just have 'Transformation' as the category) 

    Args:
        text (str): A markdown formatted string (containing newlines)
    Returns:
        dict: Categories with repository links
            - {'Category':['https://github.com/user/repo', 'https://github.com/2user/2repo']}

    """
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

'''
MARK: HTML Modification Section
'''

# Delete section from index.html
# section - marker to look for (ex: Dropdown)
def destroy_section(section):
    """ Delete a section of index.html

    This function will remove all content between two markers
    in the home page with the format:
    <!-- Begin Section Inserstion -->
    <!-- End Section Insertion -->
    Acceptable section parameters are explicitly defined in a 
    global list named MARKERS.

    Args:
        section (str): section to search and destroy
    """
    if section not in MARKERS:
        print("Unable to find html marker to destroy")
        return

    site = get_root_path() + '/index.html'
    with open(site, 'r') as f:
        buffer = f.readlines()
    
    marker = section + ' Insertion'
    isSection, start_success, end_success = (False,)*3
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
    """ Insert a section of text into an index.html page

    This function will insert content between two markers in 
    the home page with the format:
    <!-- Begin Section Inserstion -->
    Acceptable section arguments are explicitly defined in a 
    global list named MARKERS. The string must be in valid HTML
    format.
        - TODO: Validate acceptable html 

    Args:
        data (str): HTML content to insert
        section (str): marker to insert after
    """
    if section not in MARKERS:
        print("Unable to find html marker to insert")
        return

    marker = 'Begin ' + section + ' Insertion'
    site = get_root_path() + '/index.html'
    with open(site, 'r') as f:
        buffer = f.readlines()
    
    with open(site, 'w') as html:
        for line in buffer:
            if marker in line:
                line += data
                success = True
            html.write(line)    
        if not success:
            print("Unable to insert '" + section + "' into html page")


'''
MARK: Table Section
'''

# Return a string with the html formatted table rows
def build_table(text):
    """ Setup and HTML formatted table with GitHub repo data

    This function will request all data for repositories in a
    given markdown string. The data will be returned in an HTML
    formatted table for all of the links found in the argument.
    
    

    """
    table = ""
    for link in repo_links(text):
        (user, repo) = api.get_user_repo(link)
        data = api.get_repo_data(user, repo)
        tr = html_table(repo, link, data)
        table += tr

    return table

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

'''
MARK: Categories Section
'''

# Write categories to html
# Accepts dictionary (with categories key) or list
def build_categories(items):
    sections = []
    if isinstance(items, dict):
        for key in items:
            sections.append(key)
    elif isinstance(items, list):
        sections = items
    else:
        print("Unsupported text argument. Requires dictionary or list")
        return ""
    
    dr = html_categories(sections)
    return dr

# Format categories to html for dropdown button
def html_categories(sections):
    rows = ''
    try:
        for item in sections:
            rows += "<option>" + item + "</option>\n"
    except AttributeError as err:
        print('============')
        print('Categories attribute error')
        print(sections)
        return ''

    return rows.encode('utf-8')

if __name__ == '__main__':
    main()