import re

with open('data.diff', 'r') as f:
    diffs = re.split('@@[\s][-][0-9]+[\,][0-9]*[\s][+][0-9]+[\,][0-9]*[\s]@@', f.read())

    print(diffs)