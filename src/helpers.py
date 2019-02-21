import api
import os.path

# Get the root directory of the project
# (Just the parent directory. Probably a much better way)
def get_root_path(f=__file__):
    path = os.path.dirname(f)
    return os.path.abspath(os.path.join(path, os.pardir))

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

