import os
from os import path
import json
import time
from github import Github, GithubException
import requests
import shlex
import subprocess
import whatthepatch
from dotenv import load_dotenv
import datetime
import time
from filter import preprocess_text


load_dotenv()
github = Github(os.environ['TOKEN'])

def parse_key(d_key):

    '''
        Parses the dataset key which is in the form
        <user>/<repo>_<pull_number>
    '''
    username = d_key.split('/')[0]
    repo_name = d_key.split('/')[1].split('_')[0]
    pull_number = int(d_key.split('/')[1].split('_')[1])

    return username, repo_name, pull_number

def wait_to_reset():

        if github.rate_limiting[0] <= 0:
            now_unix = time.mktime(datetime.datetime.now().timetuple())
            wait_time = github.rate_limiting_resettime - now_unix + 60 # secs
            print(f"Remaining Requests: {github.rate_limiting[0]}, wait time: {wait_time/60} mins.", )
            time.sleep(wait_time)

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


if __name__=='__main__':

    # load the dataset
    # fix one graph for each commit
    # get diffs for each commit - take the first diff
    # make the graph for the diff

    # for each datapoint
    # delete the unnecessary stuff
    # PR desc
    # issue title - preprocess it
    # commits
        # for each commit
        # cm
        # comments para
        # graph
            # get the first diff for the first file
            # make the graph
    # save the data point in a json file with a filename
    # save the filename in a .txt file

    dataset = json.load(open('dataset_filtered.json', 'r'))

    user, repo = [None]*2

    if not path.exists('data'):
        os.mkdir('data')
    
    if not path.isfile('data.txt'):
        open('data.txt', 'w+')

    i = 0
    for d_key in dataset:

        print(f'---------- datapoint {i} -----------')
        i += 1

        del dataset[d_key]['id']
        del dataset[d_key]['cms']

        username, repo_name, pull_number = parse_key(d_key)

        try:
            user, repo, pull_req = get_obj(username, repo_name, pull_number, user, repo)
        except GithubException as e:
            print(e.data)
            wait_to_reset()
            user, repo, pull_req = get_obj(username, repo_name, pull_number, user, repo)
        except Exception as e:
            time.sleep(5)
            user, repo, pull_req = get_obj(username, repo_name, pull_number, user, repo)

        issue_res = requests.get(pull_req.issue_url)
        issue_title = issue_res.json()['title']
        issue_title = preprocess_text(issue_title)

        try:
            issue_res = requests.get(pull_req.issue_url)
            issue_title = issue_res.json()['title']
            dataset[d_key]['issue_title'] = preprocess_text(issue_title)
        except:
            print("No issue associated.")
            dataset[d_key]['issue_title'] = ''

        commit_shas = list(dataset[d_key]['commits'].keys())

        for commit_sha in commit_shas:
            dataset[d_key]['commits'][commit_sha]['graphs'] = []

        try:
            commits = pull_req.get_commits()
        except:
            wait_to_reset()
            commits = pull_req.get_commits()
            print(username, repo_name, pull_number)
        
        
        for commit in commits:

            if f"'{commit.sha}'" not in commit_shas:
                continue

            print(f'COMMIT {commit.sha}: {len(commit.files)} files.')

            for file in commit.files:

                # Considering only the changes in JAVA files.
                if not file.filename.endswith('.java'):
                    continue
            
                open('diff.txt', 'w+').write(file.patch)
                subprocess.run('python make_graph.py', shell=True)
                subprocess.run('python process_graph.py', shell=True)
                try:
                    graph = json.load(open('graph_processed.json'))
                except:
                    # if the graph is not successfully generated
                    # continue to the next file
                    continue
                dataset[d_key]['commits'][f"'{commit.sha}'"]['graphs'].append(graph)
                # only one graph
                break
        
        filename = f'{username}_{repo_name}_{pull_number}'
        json.dump(dataset[d_key], open(f'data/{filename}.json', 'w+'))
        open('data.txt', 'a').write(filename + '\n')
        



    



                



    


