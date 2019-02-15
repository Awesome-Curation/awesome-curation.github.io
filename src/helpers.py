import api

# Write data/emojis.txt file with GitHub assets links
# Return the dictionary to caller if needed
def write_emojis():
    path = get_root_path()
    g_emojis = api.get_emojis()

    # Pretty print to file
    style = json.dumps(g_emojis, indent=4, sort_keys=True)
    with open(path + '/data/emojis.txt', 'w') as f:
        f.write(style)

    return g_emojis

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

