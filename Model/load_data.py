import os
import json
import numpy as np
import copy

join = os.path.join

N_GRAPHS = 1
N_COMMITS = 10
N_PRDESC = Constants.MAX_LEN

# write code for generating batches

default_graph = {
    'node_features': [[1, 1, 1]],
    'edge_index': []
}

default_commit =  {
    'cm': [1],
    'comments': [1],
    'old_asts': [default_ast]*N_ASTS,
    'cur_asts': [default_ast]*N_ASTS
}

def pad_body(body: list):
    
    '''Fixes the size of body'''
    if len(body) >= N_PRDESC:
        body = body[:N_PRDESC-1] + [2]
    elif len(body) < N_PRDESC:
        body.append(2)
        body.extend([1]*(N_PRDESC - len(body)))

    return body

def pad_commits(commits: dict):

    n = len(commits)

    if n < N_COMMITS:
        for i in range(1, N_COMMITS-n+1):
            commits[f'key{i}'] = copy.deepcopy(default_commit)
    elif n > N_COMMITS:
        keys = list(commits.keys())
        keys = keys[N_COMMITS:]
        for k in keys:
            del commits[k]

    return commits


def generate_batch(batch_size):
    # read the Dataset/data.txt -> this contains the filename
    # take "batch_size" PRs at once and process them
    # processing
        # padding
        # convert to tensors
        # make a batch
        # return it -> yield() function
    
    data = open('Dataset/data.txt', 'r')
    filenames = data.readlines()
    
    for i in range(len(filenames)):
        batch_pr = []
        batch_prdesc = []
        batch_prdesc_shift = []

        for j in batch_size:
            pr = json.load(open(join('Dataset', 'data', filenames[i+j]+'.json'), 'r'))

            # Processing
            pr['body'] = np.array(pad_body(pr['body']))
            pr['issue_title'] = np.array(pr['issue_title'] if len(pr['issue_title']) > 0 else [1])

            commits = pr['commits']
            commits = pad

    pass

