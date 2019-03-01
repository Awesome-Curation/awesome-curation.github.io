#!/usr/bin/env python
# -*- coding: utf-8 -*

# Standard libs
import os.path
import re
import time
import json

# Custom
import api
from helpers import *
from logs import *

# HTML page markers for inserting text
MARKERS = ["Dropdown", "Table"]
CORE_LOG = add_logger('core')

def main():
    start_time = time.time()

    # Testing - contains a sample readme file
    sandbox_readme = get_root_path() + '/data/sandbox_readme'
    with open(sandbox_readme) as f:
        text = f.read()
        CORE_LOG.debug('read file')

    repos = build_links_dict(text)
    links = repos['Bluetooth'] # Random sections (contains the most URLs)
    #links = repos['PickerView'] # erroneous '-' appended to repo url

    # Write all html tables to files
    '''
    for category in repos:
        print('='*60)
        print('Writing - ' + category)

        st = time.time()
        name = get_valid_filename(category)
        links = repos[category]
        table = build_table(links)
        write_table_file('awesome-ios', name, table)

        et = time.time() - st
        print('Done    - ' + category)
        print('Time elapsed: ' + str(float("%0.4f" % (et))))
        print('='*60)
        print()
    '''
        
    print(api.get_rate_limit('Remaining'))

    destroy_section('Table')
    destroy_section('Dropdown')
    write_section(build_categories(repos), 'Dropdown')
    write_section(build_table(links), 'Table')        

    elapsed_time = time.time() - start_time
    print("TOTAL TIME:")
    print('Time elapsed: ' + str(float("%0.4f" % (elapsed_time))))

##############################################
# Build Core Data Section
##############################################

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
                CORE_LOG.debug('Added section: %s', section)
        if re.search('\* \[.*]\(http[s]?:\/\/.*\)', line):
            items.append(line)
            repos[section] = items    
            CORE_LOG.debug('(%s) %s', section, line)
    return repos


##############################################
# HTML Modification Section
##############################################

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
        CORE_LOG.error("Unable to find markers for sections: %s", section)
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
            CORE_LOG.error("Unable to find '%s' Begin marker", section)
        if not end_success:
            CORE_LOG.error("Unable to find '%s' End marker", section)

    CORE_LOG.info('Deleted section: %s', section)

def write_section(data, section):
    """ Insert a section of text into an index.html page

    This function will insert content between two markers in 
    the home page with the format:
    <!-- Begin Section Inserstion -->
    Acceptable section arguments are explicitly defined in a 
    global list named MARKERS. The string must be in valid HTML
    format.
        - TODO: 
            * Validate acceptable html 

    Args:
        data (str): HTML content to insert
        section (str): marker to insert after
    """
    if section not in MARKERS:
        CORE_LOG.error("Unable to find html marker to insert")
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
            CORE_LOG.error("Unable to insert '%s' into html page", section)

    CORE_LOG.info('Inserted section: %s', section)


##############################################
# Table Section
##############################################

def build_table(text):
    """ Setup and HTML formatted table with GitHub repo data

    This function will request ALL data for repositories in a
    given markdown string. Requests take about 0.5s so EXPECT A 
    SIGNIFICANT DELAY for large arguments. The data will be 
    returned in an HTML formatted table for all of the links found 
    in the argument.Only markdown bulleted, new line separated 
    strings should be passed to this function. Ex:
        * [repo_name](https://github.com/user/repo) - Description
    
        - TODO:
            * Handle get_repo_data requests exception
    
    Args:
        text (str): markdown bullets with GitHub repo links
    Returns:
        str: HTML formatted table rows

    """
    table = ""
    CORE_LOG.debug('**** Building HTML Table ****')
    for link in repo_links(text):
        try:
            (user, repo) = api.get_user_repo(link)
            data = api.get_repo_data(user, repo)
            tr = html_table(repo, link, data)
            table += tr
        except ValueError:
            table += ''
            CORE_LOG.warning('Skipping failed link: %s', link)

    CORE_LOG.debug('**** Finished HTML Table ****')
    return table

def repo_links(text):
    """ Get a list of repository links

    This function will accept a list or newline separated
    string of markdown bullets containing GitHub repository
    links. The GitHub URLs contained in the bullets will be
    returned as a list of strings.

    Args:
        text (str, list): markdown bullets containing GitHub URLs
            - str: newline separated
            - list[str]: list of bullets
    Returns:
        list: GitHub URLs in the argument
    """
    links=[]
    lines = []
    if isinstance(text, str):
        lines = text.splitlines()
    elif isinstance(text, list):
        lines = text
    else:
        CORE_LOG.error('Unsupported text argument. Requires string or list')
        raise TypeError

    for line in lines:
        link = api.get_url(line)
        if link:
            links.append(link) #+ "\n"
            
    CORE_LOG.debug('Retrieved all GitHub links from text')
    return links #[:-1]

def html_table(repo, url, data):
    """ Format repository data into an HTML table row

    This function accepts a json dictionary containing the repository
    data and builds and HTML formatted table row. 
        - TODO:
            * Handle bad repo arguments (raise & call a reload)
            * Handle exceptions (& add one for KeyError 'data' access)
            * Repo & url arguments are unnecessary & can be removed
            * Add more table rows (as options to be shown by DataTables lib)
    
    Args:
        repo (str): used to print during exceptions. Should be removed
        url (str): GitHub URL. Should be available from 'data'
        data (dict): GitHub json response dictionary
    """
    CORE_LOG.debug('Building table row for repo: %s', repo)
    try:
        stars = data['stargazers_count']
        forks = data['forks_count']
        name = data['name'] if data['name'] != None else "None" # None == NoneType i guess
        lang = data['language'] if data['language'] != None else "None"
        description = format_description(data['description'])   
        row = ("<tr>\n"
               "    <td> <a href='" + url + "'target='_blank'>" + name +"</a></td>\n"
               "    <td>"+ description +"</td>\n"
               "    <td>"+ str(stars)  +"</td>\n"
               "    <td>"+ str(forks)  +"</td>\n"
               "    <td>"+ lang  +"</td>\n"
               "</tr>\n")
    except KeyError:
        CORE_LOG.error('Unable to get data from API request.\nRepo: %s\nURL: %s', repo, url)
        return ""
    except UnicodeDecodeError:
        CORE_LOG.error('HTML Table Unicode decoding.\nRepo: %s\nURL: %s', repo, url)
        return ""
    except AttributeError:
        CORE_LOG.error('HTML Table Attribute.\nRepo: %s\nURL: %s', repo, url)
        return ""

    return row.encode('utf-8')

def format_description(text):
    """ Format repository description to handle invalid UTF-8 strings

    This function modifies descriptions containing emojis (formatted in 
    API response as ':emoji_name:'). All descriptions should be passed 
    here to sanitize the input for a table row. For descriptions containing 
    emojis, an img html tag with a link to the corresponding GitHub asset
    will replace the ':emoji_name:' from the original string.
    
    Args:
        text (str): description retrieved from repository
    Returns:
        str: formatted string with img emojis if necessary 

    """
    if not text:
        CORE_LOG.warning('No text to format')
        return ''
    
    formatted = text
    emojis = re.findall(':[a-z_]{1,30}:', text)
    for emoji in emojis:
        name = re.sub(':', '', emoji)
        try:
             # Put in an image html tag
             g_emojis = read_emojis()
             tag = "<img src='" + g_emojis[name] + "'> "
             CORE_LOG.debug('Added image for emoji: %s', name)
        except (KeyError, AttributeError):
            CORE_LOG.error('Unable to get emoji asset.\nFull description: %s', text)
            tag = ''
        formatted = re.sub(emoji, tag, formatted)
    
    return formatted

def read_emojis():
    """ Get emoji dictionary with GitHub assets links

    This function retrieves the emojis from a file and returns
    the data as a json dictionary. In the event of an error reading
    the file, another API call will be made to fetch the emojis 
    again and will return that dictionary. A new file should be
    created in this case.

    Retruns:
        dict: emoji names with asset links
            - {'emoji_name':'https://github.githubassets.com/images/icons/emoji/emoji_name.png?v'}

    """
    g_emojis = get_root_path() + '/data/emojis.txt'
    try:
        with open(g_emojis, 'r') as f:
            data = f.read()
    except IOError:
        CORE_LOG.error('Unable to read emojis.txt')
        CORE_LOG.info('Calling api to rewrite file...')
        return write_emojis()
    except ValueError:
        CORE_LOG.critical('Fatal error. Could not fetch emojis.')

    return json.loads(data)

def write_table_file(a_list, category, table):
    """ Write html formatted table data to file

    This function writes table rows for a category to a file 
    that is later retrieved to be inserted into index.html when 
    the corresponding category button is selected. The file is
    created with the category name in the directory of the
    current awesome list (repository).
        data/awesome-list/category

        -TODO:
            * Validation & Error handling
    
    Args:
        a_list (str): awesome list name (directory to save tables)
        category (str): file name to write table
        table (str): html formatted table data
    """
    path = get_root_path() + '/data/' + a_list + '/' + category

    try:
        with open(path, 'w') as f:
            f.write(table)
    except IOError:
        CORE_LOG.error('Unable to write date to table file')
    
    CORE_LOG.info('Successfully wrote html table to: %s', path)

##############################################
# Categories Section
##############################################

def build_categories(items):
    """ Build an HTML list of categories

    This function is used to create and HTML formated list of
    categories to be used in a dropdown menu bar. 
        - TODO:
            * Probably not needed. Just returns a function value
    
    Args:
        items (dict, list): categories
            - dict: key containing categories
            - list: categories
    Returns:
        str: HTML formatted categories

    """
    sections = []
    if isinstance(items, dict):
        for key in items:
            sections.append(key)
    elif isinstance(items, list):
        sections = items
    else:
        CORE_LOG.error('Unsupported text argument. Requires dictionary or list')
        return ""
    
    dr = html_categories(sections)
    return dr

def html_categories(sections):
    """ Put categories into 'bootstrap-select' formatted dropdown list
    
    This function accepts a list of categories and formats them for
    bootstrap-select to handle in a dropdown menu. Categories are
    concatinated in the form:
        <option>Category</option>
    
    Args: 
        sections (list): categories to add in dropdown
    Returns:
        str: bootstrap-select formatted categories

    """
    rows = ''
    try:
        for item in sections:
            rows += "<option>" + item + "</option>\n"
    except AttributeError as err:
        CORE_LOG.critical('Unable to write categories: %s', sections)

    CORE_LOG.info('Successfully build html categories')
    return rows.encode('utf-8')

if __name__ == '__main__':
    CORE_LOG.debug('***** init *****')
    main()