import re
import subprocess
import javalang

MODIFIERS = ['abstract', 'default', 'final', 'native', 'private',
                  'protected', 'public', 'static', 'strictfp', 
                  'transient', 'volatile'] 

def process_bracket(tokens):
    if tokens[0] == '}':
        tokens.pop(0)
    stack = []
    for token in tokens:
        if token == '{':
            stack.append('{')
        elif token == '}':
            if stack and stack[-1] == '{':
                stack.pop()
            else:
                stack.append('}')
    l_num = stack.count('{')
    r_num = stack.count('}')
    tokens = ['{'] * r_num + tokens + ['}'] * l_num
    return tokens

def extract_segments(chunk):

    diff_lines = chunk.split('\n')
 
    deleted_code = ""
    added_code = ""

    for line in diff_lines:

        if not line:
            continue

        if line[0] == '-':
            line = line[1:].strip()
            deleted_code += line

        elif line[0] == '+':
            line = line[1:].strip()
            added_code += line
        
    return deleted_code, added_code

def get_complete_text(codes_ori):

    if len(codes_ori) == 0:  
        return None, -1
    
    if 'implement' in codes_ori:
        codes_ori.remove('implement')
    if codes_ori[-1] == 'implements':
        codes_ori.remove('implements')
    if len(codes_ori) == 0:
        return None, -1
    
    
    if len(codes_ori) >= 4 and 'class' in codes_ori and codes_ori[-2] == '<' and codes_ori[-1] != '>':
        codes_ori += '>' 
    
    codes_ori = process_bracket(codes_ori)
    
    if len(codes_ori) == 0:
        return None, -1
    
    ori_start_token = ' '.join(codes_ori)
    
    if codes_ori[0] == 'import':
        pass
    elif codes_ori[0] == 'package':
        pass
    elif codes_ori[0] == '@':
        if 'class' in codes_ori:  # definition of class
            pass
        else:  # definition of method
            codes_ori = ['class', 'pad_pad_class', '{'] + codes_ori + ['}']
            # gumtree can only parse class, so a padding class needs to be inserted
    elif codes_ori[0] in MODIFIERS:
        
        if 'class' in codes_ori:  # definition of class
            if codes_ori[-1] == '}':
                pass
            elif codes_ori[-1] == '{':
                raise
            else:
                codes_ori +=  ['{', '}'] 
        elif '(' in codes_ori and ')' in codes_ori and ('=' not in codes_ori or ('='  in codes_ori and codes_ori.index('(') < codes_ori.index('=') and codes_ori.index(')') < codes_ori.index('='))):  # definition of method
            if codes_ori[-1] == '}':
                pass
            elif codes_ori[-1] == '{':
                raise
            elif codes_ori[-1] != ';':
                codes_ori +=  ['{', '}'] 
                
            codes_ori = ['class', 'pad_pad_class', '{'] + codes_ori + ['}']
        else:  # definition of field
            codes_ori = ['class', 'pad_pad_class', '{', '{'] + codes_ori + ['}', '}']
    elif codes_ori[0] == '{':
        codes_ori = ['class', 'pad_pad_class', '{'] + codes_ori + ['}']
    else:
        if codes_ori[0] == 'if':
            if codes_ori[-1] == '}':
                pass
            elif codes_ori[-1] == '{':
                
                raise
            elif codes_ori[-1] == ')':
                codes_ori +=  ['{', '}']
        codes_ori = ['class', 'pad_pad_class', '{', '{'] + codes_ori + ['}', '}']

  
    text = ' '.join(codes_ori)
    start_code_pos = text.index(ori_start_token)
    assert start_code_pos != -1

    return text


if __name__=='__main__':

    diff_text = open('../data.diff').read()

    # divide them into chunks
    chunks = re.split("@@[\s][-][0-9]+[\,][0-9]+[\s][+][0-9]+[\,][0-9]+[\s]@@", diff_text)

    for chunk in chunks[1:]:

        deleted_code, added_code = extract_segments(chunk)

        del_tokens = list(javalang.tokenizer.tokenize(deleted_code))
        del_tokens = [x.value for x in del_tokens]
        del_text = get_complete_text(del_tokens)

        add_tokens = list(javalang.tokenizer.tokenize(added_code))
        add_tokens = [x.value for x in add_tokens]
        add_text = get_complete_text(add_tokens)

        print(' '.join(del_text))
        print(' '.join(add_text))

        open('del.java', 'w+').write(del_text)           
        open('add.java', 'w+').write(add_text)

        subprocess.run('../lib/gumtree/gumtree/bin/gumtree parse del.java > del.ast.json', shell=True)
        subprocess.run('../lib/gumtree/gumtree/bin/gumtree parse add.java > add.ast.json', shell=True)




        exit(0)




