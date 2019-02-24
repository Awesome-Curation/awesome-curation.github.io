#!/usr/bin/env python
# -*- coding: utf-8 -*

import os.path
import api

def get_root_path(f=__file__):
    """ Get the root path of the project

    - TODO:
        * Probably a much better way

    Args:
        f (str): filename
    Returns:
        str: absolute root path of the project

    """
    path = os.path.dirname(f)
    return os.path.abspath(os.path.join(path, os.pardir))

# Write data/emojis.txt file with GitHub assets links
# Return the dictionary to caller if needed
def write_emojis():
    """ Write GitHub emoji image assets to file

    This functions retrieves the asset links from the API
    as a json dictionary and pretty print them a file. Ideally
    this should only be called once and the file is used for
    all retrieval after. Can be called again in the event of
    a file reading failure.

    Returns:
        dict (optional): json emoji names & asset links

    """
    path = get_root_path()
    g_emojis = api.get_emojis()

    # Pretty print to file
    style = json.dumps(g_emojis, indent=4, sort_keys=True)
    with open(path + '/data/emojis.txt', 'w') as f:
        f.write(style)

    return g_emojis

def console_print(repo, url, data):
    """ Print repository data to console

    - TODO:
        * Use a logging function instead to catch all
          exceptions 

    Args:
        repo (str): repository name
        urls (str): repository link
        data (dict): json repository response data

    """
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

