#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO:
    * Exception handling
    * HTTP error code handling
    * Tests
"""

# Standard libs
import os
import re
import sys
import json
import requests

# Custom
from logs import add_logger

_API = 'https://api.github.com/'
try:
    _TOKEN = os.environ['TOKEN']
    _USER = os.environ['GITHUB_NAME']
except KeyError:
    msg = ("Unable to fetch environment variables.\n"
           "Please set your api token and username.\n"
           "Ex:\n"
           "export TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n"
           "export GITHUB_NAME=ryans-git")
    sys.exit(msg)

API_LOG = add_logger('api')

def get_api_data(url, format=True, display=False):
    """ Get data response from GitHub api

    Send a request to GitHub with specified URL. Use this
    function to retrieve REST API json data. Contains default
    headers of token & json formatting. Can maybe be expanded
    to using a an argument

    Args:
        url (str): endpoint suffix link to send 
        format (bool, optional): return data in a json dictionary
            defaults to True
        display (bool, optional): pretty print json data to console
            defaults to False
    Returns:
        dict: json response if format is True
        obj: requests module object
    Raises:
        requests.exceptions.RequestException: IOError from requests
        requests.exceptions.HTTPError: response code from github
    """

    h = {'Authorization':"token " + _TOKEN,
         'Accept':'application/vnd.github.v3+json'}
    try:
        r = requests.get(_API + url, headers=h)
        # TODO: Handle status_code
        if display:
            print(json.dumps(r.json(), indent=4, sort_keys=True))
        if format:
            return r.json()
        else:
            return r
    except requests.RequestException as err:
        print("Unable to fetch api data")

def get_user_repo(url):
    """ Extract username and repository name from GitHub URL
    
    Args:
        url (str): Full GitHub URL
            ex: https://github.com/user/repo
    Returns:
        tuple: username and repository
            - Empty if error to continue to next
    """
    try:
        # ['https:', '', 'github.com', 'user', 'repo']
        if (
            not re.search('http[s]?://github.com', url) or 
            len(url.split('/')) != 5 
           ): # v sad
           API_LOG.error('Invalid GitHub link: %s', url)
           raise ValueError

        (_,_,_,user,repo) = url.split('/')

        # Remove html jump link (breaks api call)
        if '#' in repo:
            repo = repo.split('#', 1)[0]
        
        # TODO: regex validate names
        #regex = '/^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$/i'
        #if not re.search(regex, user) or not re.search(regex, repo):
    except IndexError:
        API_LOG.error('Failed to access split parts: %s', url)
        raise ValueError

    return (user, repo)

def get_token():
    """ Get API token key from a file

    Optional method of setting the GitHub API token.
    Create a file in cwd named 'token' with a single line
    containing the key.
    
    Returns:
        str: token value
    Raises:
        IOError: couldn't get it; error reading file
    """
    try:
        path = os.path.dirname(__file__)
        with open(path + "/token", 'r') as f:
            return f.readline().strip()
    except IOError:
        API_LOG.critical("Failed to get API token\nCreate a 'token' file in this directory")

def get_emojis():
    """ Get the GitHub emoji assets links

    Use the function to get image links when the emojis
    cannot be found/printed in html UTF-8. Avoid calling 
    every time an emoji is needed. Store in text file or
    variable.
    
    Returns:
        dict: json formatted with name & links
    """
    return get_api_data("emojis")

def get_repo_data(user, repo):
    """ Get the GitHub repository data

    Use the function to get entire repository data
    response from GitHub API. Only used for single level
    depth items {str:str} (ex: stars, lang, forks). Others
    may be easer to get from just crawling the actual
    repository GitHub page (ex: latest commit date)
    
    Returns:
        dict: json formatted with name & links
    """    
    return get_api_data('repos/' + user + '/' + repo)

def get_rate_limit(option=''):
    """ Get GitHub API rate limit data

    Use this function to monitor how many API request
    are left in the hour to fetch data accordingly.

    Args:
        option (str, optional): X-RateLimit option
            - `Limit`: max number of queries per hour
            - `Remaining`: number of queries left in the hour
            - 'Reset': UTC time until limit reset 
    Returns:
        tuple: all 3 option if no argument given
        int: number for given argument
    
    Raises:
        KeyError: problem getting number from the response header

    """
    req = get_api_data('users/' + _USER, format=False)
    try:
        limit = req.headers['X-RateLimit-Limit'] 
        remaining = req.headers['X-RateLimit-Remaining']
        reset = req.headers['X-RateLimit-Reset']
    except KeyError:
        API_LOG.error('Unable to get RateLimit data')
        return ''

    if not option:
        API_LOG.info('Retrieved all RateLimit data: %s', (limit, remaining, reset))
        return (limit, remaining, reset)
    
    opts = ['Limit', 'Remaining', 'Reset']
    if option not in opts:
        API_LOG.error("Unable to get RateLimit data")
        API_LOG.info("Options: Limit, Remaining, Reset")
    else:
        data = req.headers['X-RateLimit-' + option]
        API_LOG.info('Retrieved RateLimit: %s = %s', option, data)
        return data

# Get README.md raw data file to string
def get_readme(user, repo):
    """ Get README raw text data

    Use for getting finding the GitHub links in the 'awesome list'
    README file. Current architecture should call this seperatley
    for each list to store in data/repo.txt file.

    Args:
        user (str): username
        repo (str): repository name
    Returns:
        str: raw text
    """
    h = {"Accept":"application/vnd.github.VERSION.raw"}
    url = _API + 'repos/' + user + "/" + repo + "/readme"
    r = requests.get(url, headers=h)
    return r.text.encode('utf-8') 
 
 # Extract github link from a string
def get_url(text):
    """ Extract URL from a markdown bullet

    Use this function to get GitHub link found between
    parentheses an a markdown bullet point.
    * [repo_name](https://github.com/user/repo) - Description

    Args:
        text (str): single like to extract from
    Returns:
        str: GitHub URL
    """
    try:
        if 'https://github.com/' in text:
            url = re.search("(?P<url>https?://[^\s]+)", text)  
            return url.group("url").replace(")","") 
    except IndexError:
        API_LOG.error('Unable to extract URL')
    return ""
