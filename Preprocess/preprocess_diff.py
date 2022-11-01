from nltk import word_tokenize
import re
import json


def process_diff(diff_lines):
 
    diff_tokens = []
    diff_marks = []

    for line in diff_lines:

        if line.startswith('@@'):
            line = re.sub('@@.*@@', '', line)
            tokens = re.findall(r"[\w']+|[^\w\s']", line)
            diff_tokens.extend(['<nb>'] + tokens + ['<nl>'])
            diff_marks.extend([2]*(len(tokens)+2))
        elif line[0] == '-':
            line = line[1:].strip()
            tokens = re.findall(r"[\w']+|[^\w\s']", line)
            diff_tokens.extend(tokens)
            diff_tokens.append('<nl>')
            diff_marks.extend([1]*(len(tokens)+1))
        elif line[0] == '+':
            line = line[1:].strip()
            tokens = re.findall(r"[\w']+|[^\w\s']", line)
            diff_tokens.extend(tokens)
            diff_tokens.append('<nl>')
            diff_marks.extend([3]*(len(tokens)+1))
        else:
            line = line.strip()
            tokens = re.findall(r"[\w']+|[^\w\s']", line)
            diff_tokens.extend(tokens)
            diff_tokens.append('<nl>')
            diff_marks.extend([2]*(len(tokens)+1))
        

    return diff_tokens, diff_marks




if __name__ == '__main__':

    diff_lines = open('diff.code').readlines()

    diff_tokens, diff_marks = process_diff(diff_lines)

    # for t in zip(diff_tokens, diff_marks):
    #     print(t)

    with open('difftoken.json', 'w+') as f:
        json.dump([diff_tokens], f)

    with open('diffmark.json', 'w+') as f:
        json.dump([diff_marks], f)






