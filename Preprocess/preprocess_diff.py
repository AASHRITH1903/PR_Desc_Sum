from nltk import word_tokenize
import re
import json


def process_diff(diff_lines):
 
    diff_token = []
    diff_mark = []
    diff_att = []

    for line in diff_lines:

        if line.startswith('@@'):
            line = re.sub('@@.*@@', '', line)
            tokens = re.findall(r"[\w']+|[^\w\s']", line)
            diff_token.extend(['<nb>'] + tokens + ['<nl>'])
            diff_mark.extend([2]*(len(tokens)+2))
            diff_att.extend([[]]*(len(tokens)+2))

        elif line[0] == '-':
            line = line[1:].strip()
            tokens = re.findall(r"[\w']+|[^\w\s']", line)
            diff_token.extend(tokens)
            diff_token.append('<nl>')
            diff_mark.extend([1]*(len(tokens)+1))
            diff_att.extend([[]]*(len(tokens)+1))

        elif line[0] == '+':
            line = line[1:].strip()
            tokens = re.findall(r"[\w']+|[^\w\s']", line)
            diff_token.extend(tokens)
            diff_token.append('<nl>')
            diff_mark.extend([3]*(len(tokens)+1))
            diff_att.extend([[]]*(len(tokens)+1))

        else:
            line = line.strip()
            tokens = re.findall(r"[\w']+|[^\w\s']", line)
            diff_token.extend(tokens)
            diff_token.append('<nl>')
            diff_mark.extend([2]*(len(tokens)+1))
            diff_att.extend([[]]*(len(tokens)+1))
        

    return diff_token, diff_mark, diff_att




if __name__ == '__main__':

    diff_lines = open('../diff.code').readlines()

    diff_token, diff_mark, diff_att = process_diff(diff_lines)

    # for t in zip(diff_token, diff_mark):
    #     print(t)


    json.dump([diff_token], open('difftoken.json', 'w+'))
    json.dump([diff_mark], open('diffmark.json', 'w+'))
    json.dump([diff_att], open('diffatt.json', 'w+'))






