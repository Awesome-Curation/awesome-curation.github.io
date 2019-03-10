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

# HTML page markers for inserting text - depreciated
MARKERS   = ["Dropdown", "Table"]
CORE_LOG  = add_logger('core')
ROOT_PATH = get_root_path()

def main():
    setup_logging()

    # Testing - contains a sample readme file
    sandbox_readme = os.path.join(ROOT_PATH, 'data/sandbox_readme')
    with open(sandbox_readme) as f:
        text = f.read()
        CORE_LOG.debug('read file')

    repos = build_links_dict(text)
    #links = repos['GIF'] # Random sections (contains the most URLs)
    #links = repos['PickerView'] # erroneous '-' appended to repo url

    #print(build_table(links))
    name = get_valid_filename('GIF')
    links = repos['GIF']
    table = build_table(links)
    write_table_file('awesome-ios', name, table)
    # Write all html tables to files
    #build_database(repos, 'awesome-ios')

    api.get_rate_limit('Remaining')

    # HTML table insert depreciated
    #destroy_section('Table')
    #destroy_section('Dropdown')
    # Should move logs into build_ functions
    #write_section(build_categories(repos), 'Dropdown')
    #write_section(build_table(links), 'Table')        

    CORE_LOG.info(FINISHED + SCRIPT)

##############################################
# Build Core Data Section
##############################################

def build_database(repos, list_name):
    """ Save all categories & repos to data files as an html table

    This function loops all categories in an awesome list and builds
    html tables that are saved to files in 'data/awesome-list/category',
    which will be added and deleted to the table in index.html 
    dynamically through js. A dict ('info') is used to store & print
    logging information.

    Args:
        repos (dict): Category keys and list of repo links as values
        list_name (str): Awesome List to traverse

    """
    CORE_LOG.info(CATEGORY + FULL_LIST, {'Awesome List': list_name})

    total_repos = 0
    total_categories = 0
    for category in repos:
        info = {'Awesome List': list_name, 'Category': category}
        CORE_LOG.info(WRITING + CATEGORY, info)

        name = get_valid_filename(category)
        links = repos[category]
        table = build_table(links)
        write_table_file(list_name, name, table)

        repo_count = len(links)
        total_repos += repo_count
        total_categories += 1
        info['Repo Count'] = repo_count
        info['File Name'] = name
        CORE_LOG.info(FINISHED + CATEGORY, info)
    
    info = {
        'Awesome List': list_name,
        'Category Count': total_categories,
        'Repo Count': total_repos
    }
    CORE_LOG.info(FINISHED + FULL_LIST, info)


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
            re.search('\[.*\(.*\)', line)

            # Simplify logging text
            try:
                repo = re.search('\[.*\(.*\)', line).group(0) 
            except:
                repo = line
            CORE_LOG.debug('%s - %s', section, repo)
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

    site = os.path.join(ROOT_PATH, 'index.html')
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
    site = os.path.join(ROOT_PATH, 'index.html')
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
    """ Setup and json formatted table with GitHub repo data

    This function will request ALL data for repositories in a
    given markdown string. Requests take about 0.5s so EXPECT A 
    SIGNIFICANT DELAY for large arguments. The data will be 
    returned in an json object to be loaded into the table displayed
    in the webpage. All of the links found in the argument will be 
    added the to object returned. Only markdown bulleted, new line 
    separated strings should be passed to this function. Ex:
        * [repo_name](https://github.com/user/repo) - Description
    
        - TODO:
            * Handle get_repo_data requests exception
    
    Args:
        text (str): markdown bullets with GitHub repo links
    Returns:
        str: json object formatted to a string to be printed

    """
    table = {
        "data" : []
    }   
    CORE_LOG.debug('**** Building HTML Table ****')
    for link in repo_links(text):
        try:
            # TODO: need to log bad links
            (user, repo) = api.get_user_repo(link)
            data = api.get_repo_data(user, repo)
            tr = json_table(repo, link, data)
            table["data"].append(tr)
        except ValueError:
            CORE_LOG.warning('Skipping failed link: %s', link)

    CORE_LOG.debug('**** Finished HTML Table ****')
    return json.dumps(table, indent=4, sort_keys=True) 

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
        # TODO: Need error raised for bad links
        link = api.get_url(line)
        if link:
            links.append(link) #+ "\n"
            
    CORE_LOG.debug('Retrieved all GitHub links from text')
    return links #[:-1]

def json_table(repo, url, data):
    """ Format repository data into dictionary used for a single table row

    This function accepts a json dictionary containing the repository
    data and filters only the needed attributes for the table to a new json 
    object used by DataTables (datatables.js)
        - TODO:
            * Handle bad repo arguments (raise & call a reload)
            * Handle exceptions (& add one for KeyError 'data' access)
            * Repo & url arguments are unnecessary & can be removed
            * Add more table rows (as options to be shown by DataTables lib)
    
    Args:
        repo (str): used to print during exceptions. Should be removed
        url (str): GitHub URL. Should be available from 'data'
        data (dict): GitHub json response dictionary
    Returns:
        dict: column name keys with GitHub repo data values
    """
    CORE_LOG.debug('Building table row for repo: %s', repo)

    try:
        name = data['name'] if data['name'] != None else "None" # None == NoneType i guess
        description = format_description(data['description'])   
        stars = data['stargazers_count']
        forks = data['forks_count']
        lang = data['language'] if data['language'] != None else "None"

        row = {
            "Repo" : "<a href='" + url + "'target='_blank'>" + name +"</a>",
            "Description": description,
            "Stars": stars,
            "Forks": forks,
            "Language": lang
        }
    except KeyError:
        CORE_LOG.error('Unable to get data from API request.\nRepo: %s\nURL: %s', repo, url)
        raise ValueError
    except UnicodeDecodeError:
        CORE_LOG.error('HTML Table Unicode decoding.\nRepo: %s\nURL: %s', repo, url)
        raise ValueError
    except AttributeError:
        CORE_LOG.error('HTML Table Attribute.\nRepo: %s\nURL: %s', repo, url)
        raise ValueError

    return row

# DEPRECIATED - may be removed
# Using JSON for datatables ajax seems better
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
    g_emojis = os.path.join(ROOT_PATH, 'data/emojis.txt')
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

def write_table_file(list_name, category, table):
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
        list_name (str): awesome list name (directory to save tables)
        category (str): file name to write table
        table (str): html formatted table data
    """
    path = os.path.join(ROOT_PATH, 'data', list_name, category)

    try:
        with open(path, 'w') as f:
            f.write(table)
    except IOError:
        CORE_LOG.error('Unable to write date to table file')
        return
    
    CORE_LOG.info('Successfully wrote html table to: %s', 'data/' + list_name + '/' + category)

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