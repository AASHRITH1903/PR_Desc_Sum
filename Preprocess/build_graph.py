import os
from os import path
import json
import time
from github import Github
import requests
import shlex
import subprocess
import whatthepatch
from dotenv import load_dotenv

load_dotenv()
github = Github(os.environ['TOKEN'])

TS_ROOT = path.join('..', 'tree-sitter-codeviews')
INPUT_PATH = path.join(TS_ROOT, 'code_test_files', 'java', 'input.java')
OUTPUT_PATH = path.join(TS_ROOT, 'output_json', 'AST_output.json')

MAX_ASTS = 1

def parse_key(d_key):

    '''
        Parses the dataset key which is in the form
        <user>/<repo>_<pull_number>
    '''

    username = d_key.split('/')[0]
    repo_name = d_key.split('/')[1].split('_')[0]
    pull_number = int(d_key.split('/')[1].split('_')[1])

    return username, repo_name, pull_number

def get_obj(username, repo_name, pull_number, user, repo):

    '''
        Calls the Github api to fetch the user, repo, and pull objects
    '''

    if not user or not user.name == username:
        user = github.get_user(username)
        repo = user.get_repo(repo_name)
    elif not repo or not repo.name == repo_name:
        repo = user.get_repo(repo_name)

    pull_req = repo.get_pull(pull_number)

    return user, repo, pull_req


# def clone_repo(username, repo_name):

#         '''
#             Clones the repo if it doesn't exist already
#         '''

#         repo_path = path.join('repos', username, repo_name)
#         if not path.isdir(repo_path):
#             os.makedirs(repo_path)
#             command = shlex.split(f'git clone https://github.com/{username}/{repo_name}.git {repo_path}')
#             subprocess.run(command)

#         print("repo check.")

# def get_entity_names(patch: str):

#     '''
#         Parses the git diff patch of a file and returns the 
#         entities (method, class, etc.) names where the changes 
#         occurred. These entity names are used to identify the 
#         ASTs.
#     '''

#     lines = patch.split('\n')
#     lines = list(filter(lambda x: x[0]=='@', lines))
#     entity_names = [x.split('@@')[-1].split('(')[0].split(' ')[-1] for x in lines]
#     return entity_names

# def get_cur_version(repo_path, file_sha):
#     '''
#         Retrieves the version of the file after modifcation 
#         using the file sha
#     '''
#     proc = subprocess.run(f'git show {file_sha}', shell=True, cwd=repo_path, stdout=subprocess.PIPE, text=True)
#     cur_text = proc.stdout

#     return cur_text

# def get_prev_version(cur_text, file_patch):

#     '''
#         Applies the patch backwards to retrieve the version of the
#         file before modification.
#     '''

#     diff_obj = [x for x in whatthepatch.parse_patch(file_patch)][0]
#     old_text = whatthepatch.apply_diff(diff_obj, cur_text, reverse=True)
#     old_text = '\n'.join(old_text)

#     return old_text


# def get_custom_ast(ast):

#     '''
#         custom represenation :-
#         {
#             <node_id> : { "label": <label>, "children": [<child_id>, <child_id>, ...] },
#         }
#     '''

#     custom_ast = {}

#     for node in ast['nodes']:

#         node_id = node['id']
#         node_type = node['node_type']
#         node_label = node['label']

#         custom_ast[node_id] = {'label': f'{node_type}_{node_label}', 'children': []}

#     for edge in ast['links']:

#         custom_ast[edge['source']]['children'].append(edge['target'])

#     return custom_ast
    

# def get_ast(text):

#     with open(INPUT_PATH, 'w+') as f:
#         f.write(text)

#     st = time.time()
#     subprocess.run('python main.py', shell=True, cwd=TS_ROOT, stdout=subprocess.PIPE)
#     ed = time.time()
#     print(f'Time taken by tree sitter: {ed - st}')

#     with open(OUTPUT_PATH, 'r') as f:
#         ast = json.load(f)

#     ast = get_custom_ast(ast)

#     return ast

class TreeNode:
    def __init__(self, id, label, node_type):
        self.id = id
        self.label = label
        self.node_type = node_type
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)

def Gra

# For tree-sitter-codeview format
def get_custom_ast(ast_json):
    edges = ast_json['links']
    nodes = ast_json['nodes']
    node_dict = {}

    for node in nodes:
        node_dict[node['id']] = TreeNode(node['id'], node['label'], node['node_type'])

    for edge in edges:
        node_dict[edge['source']].add_child(node_dict[edge['target']])

    root_node = min(list(node_dict.keys()))

    return node_dict[root_node]

def extract_changes(patch):
    patch_lines = patch.split('\n')
    changes = []
    plus_lines = ""
    minus_lines = ""
    flag = False
    for line in patch_lines:
        if line.startswith('-'):
            minus_lines += line[1:] + '\n'
            flag = True
        elif line.startswith('+'):
            plus_lines += line[1:] + '\n'
            flag = True
        else:
            if flag:
                changes.append((minus_lines, plus_lines))
                minus_lines = ""
                plus_lines = ""
                flag = False

    if flag:
        changes.append((minus_lines, plus_lines))
        minus_lines = ""
        plus_lines = ""
        flag = False

    return changes
 

if __name__=='__main__':

    st_g = time.time()
    q = 0

    if not path.isdir('repos'):
        os.makedirs('repos')

    with open(path.join('..', 'Data', 'dataset.json')) as f:
        dataset = json.load(f)
    
    user, repo = [None]*2

    i = 1

    for d_key in dataset:

        # print(f'\n--- datapoint {i} -------------------\n')
        i += 1

        username, repo_name, pull_number = parse_key(d_key)

        user, repo, pull_req = get_obj(username, repo_name, pull_number, user, repo)

        # try:
        #     issue_res = requests.get(pull_req.issue_url)
        #     dataset[d_key]['issue_title'] = issue_res.json()['title']
        # except:
        #     print("No issue associated.")
        #     dataset[d_key]['issue_title'] = ''

        # print("issue title check.")

        # ---------------- ASTs ---------------------------------------

        # clone_repo(username, repo_name)
        # repo_path = path.join('repos', username, repo_name)

        # print(f'Commits: {len(pull_req.get_commits())}')

        for commit in pull_req.get_commits():

            # dataset[d_key]['commits'][f"'{commit.sha}'"]['cur_asts'] = []
            # dataset[d_key]['commits'][f"'{commit.sha}'"]['old_asts'] = []

            print(f'Files: {len(commit.files)}')

            for file in commit.files:

                # if len(dataset[d_key]['commits'][f"'{commit.sha}'"]['cur_asts']) >= MAX_ASTS:
                    # break

                # Considering only the changes in JAVA files.
                if not file.filename.endswith('.java'):
                    continue

                code_changes = extract_changes(file.patch)

                for code_change in code_changes:
                    
                    text_del, text_add = code_change

                    with open(INPUT_PATH, 'w+') as f:
                        f.write(text_del)

                    subprocess.run('python main.py', shell=True, cwd=TS_ROOT, stdout=subprocess.PIPE)

                    ast_del = json.load(open(OUTPUT_PATH, 'r'))
                    ast_del = get_custom_ast(ast_del)


                    with open(INPUT_PATH, 'w+') as f:
                        f.write(text_add)

                    subprocess.run('python main.py', shell=True, cwd=TS_ROOT, stdout=subprocess.PIPE)

                    ast_add = json.load(open(OUTPUT_PATH, 'r'))
                    ast_add = get_custom_ast(ast_add)



                    exit(0)
                    





                print('--------------------------------------------------')
                q += 1

                if q >= 5:
                    exit(0)



                # cur_text = get_cur_version(repo_path, file.sha)
                # old_text = get_prev_version(cur_text, file.patch)

                # cur_ast = get_ast(cur_text)
                # old_ast = get_ast(old_text)

                # dataset[d_key]['commits'][f"'{commit.sha}'"]['cur_asts'].append(cur_ast)
                # dataset[d_key]['commits'][f"'{commit.sha}'"]['old_asts'].append(old_ast)

        
    with open(path.join('..', 'Data', 'dataset_aug.json'), 'w+') as f:
        json.dump(dataset, f)
    
    ed_g = time.time()
    # TIME
    print(f'Time taken overall : {ed_g - st_g}')
            

