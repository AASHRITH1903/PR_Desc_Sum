import nltk
from nltk.tokenize import sent_tokenize
import re

def get_comments(comments: list):
    ''' 
        comments: List of comments
    '''
    # Removes the initial '+' and space
    comments = [comment[1:] for comment in comments]
    
    # Remove spaces
    comments = [comment.strip() for comment in comments]

    proc_comments = []
    
    flag = 0
    temp = ""
    for comm in comments:
        if comm.startswith('//'):
            proc_comments.append(comm[2:])
        
        if comm.startswith('/*'):
            flag = 1
            temp = ""
        
        elif comm.startswith('*/'):
            flag = 0
            proc_comments.append(temp)
            temp = ""

        elif comm.startswith('*'):
            if flag == 1:
                temp = temp + comm[1:] + " "
        

    return proc_comments

def preprocess_text(text:str):

    # can be used PR desc, commit message, commentsm - general preprocessing rules
     
    # split into sentences
    sent_list = sent_tokenize(text)
    proc_list = []

    # eliminate the sentences with the given patterns
    for sent in sent_list:
        url_pattern = r'https?://[-a-zA-Z0-9@:%._+~#?=/]+(?=($|[^-a-zA-Z0-9@:%._+~#?=/]))'
        structure_pattern = r'^#+'
        signature_pattern = r'^(signed-off-by|co-authored-by|also-by):'
        email_pattern = r'(^|\s)<[\w.-]+@(?=[a-z\d][^.]*\.)[a-z\d.-]*[^.]>'
        at_pattern = r'@\S+'
        reference_pattern = r'#[\d]+'

        pattern_list = [email_pattern, url_pattern, reference_pattern, signature_pattern, structure_pattern, at_pattern]
        
        # If we find a pattern, we don't add the sentence to the list
        flag = 0
        for pattern in pattern_list:
            if re.search(pattern, sent):
                flag = 1
                break
        
        if flag == 0:
            proc_list.append(sent)

    # concatenate all the sentences
    proc_text = ' '.join(proc_list)
    
    # Word tokenize
    proc_text = nltk.word_tokenize(proc_text)
    proc_list = []

    for word in proc_text:
        version_pattern = r'(^|\s|-)[\d]+(\.[\d]+){1,}' # Replace with 'version'
        sha_pattern = r'(^|\s)[\dA-Fa-f-]{7,}(?=(\s|$))' # Replace with 'sha'
        digit_pattern = r'(^|\s|-)[\d]+(?=(\s|$))' # Replace with 0

        pattern_list = [version_pattern, sha_pattern, digit_pattern]

        for pattern in pattern_list:
            if re.search(pattern, word):
                if pattern == version_pattern:
                    word = re.sub(pattern, ' version ', word)
                elif pattern == sha_pattern:
                    word = re.sub(pattern, ' sha ', word)
                elif pattern == digit_pattern:
                    word = re.sub(pattern, ' 0 ', word)
        
        proc_list.append(word)
    
    return ' '.join(proc_list)

if __name__ == "__main__":
    comments = [
            "+/*",
            "+ * Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one",
            "+ * or more contributor license agreements. Licensed under the Elastic License;",
            "+ * you may not use this file except in compliance with the Elastic License.",
            "+ */",
            "+/*",
            "+ * Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one",
            "+ * or more contributor license agreements. Licensed under the Elastic License;",
            "+ * you may not use this file except in compliance with the Elastic License.",
            "+ */",
            "+/*",
            "+ * Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one",
            "+ * or more contributor license agreements. Licensed under the Elastic License;",
            "+ * you may not use this file except in compliance with the Elastic License.",
            "+ */",
            "+        // Assert appropriate task state and assignment numbers",
            "+        // Set the upgrade mode setting",
            "+        // Assert state for tasks still exists and that the upgrade setting is set",
            "+        //Disable the setting",
            "+            // If we are waiting for an upgrade to complete, we should not assign to a node",
            "+/*",
            "+ * Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one",
            "+ * or more contributor license agreements. Licensed under the Elastic License;",
            "+ * you may not use this file except in compliance with the Elastic License.",
            "+ */",
            "+    /**",
            "+     * Fields used in a pattern to format a json log line:",
            "+     * <ul>",
            "+     * <li>type - the type of logs. These represent appenders and help docker distinguish log streams.</li>",
            "+     * <li>timestamp - ISO8601 with additional timezone ID</li>",
            "+     * <li>level - INFO, WARN etc</li>",
            "+     * <li>component - logger name, most of the times class name</li>",
            "+     * <li>cluster.name - taken from sys:es.logs.cluster_name system property because it is always set</li>",
            "+     * <li>node.name - taken from NodeNamePatternConverter, as it can be set in runtime as hostname when not set in elasticsearch.yml</li>",
            "+     * <li>node_and_cluster_id - in json as node.id and cluster.uuid - taken from NodeAndClusterIdConverter and present",
            "+     * once clusterStateUpdate is first received</li>",
            "+     * <li>message - a json escaped message. Multiline messages will be converted to single line with new line explicitly",
            "+     * replaced to \\",
            "+     * <li>exceptionAsJson - in json as a stacktrace field. Only present when throwable is passed as a parameter when using a logger.",
            "+     * Taken from JsonThrowablePatternConverter</li>",
            "+     * </ul>",
            "+     */",
            "+/*",
    ]

    proc = get_comments(comments)
    for comm in proc:
        print(preprocess_text(comm))