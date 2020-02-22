#!/usr/bin/env python3

from comment_collector import CommentCollector
import config
import credentials
import json
import sys
import gzip
from multiprocessing import Pool

def worker_process(creds, user_ids, proxies):
    comment_collector = CommentCollector(creds[0], creds[1], proxies)

    for user_id in user_ids:
        print(f"current_user: {user_id}")
        result = comment_collector.get_comments_recursive(user_id, max_depth=1)
        with gzip.open(config.datadir + f"/{user_id}.json.gz", 'w+') as res_f:
            res_f.write(json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8'))

def chunker_list(seq, size):
    return list(seq[i::size] for i in range(size))

if (len(sys.argv) < 2):
    print ("Usage: {} <file_with_ids> [<file_with_proxies>]".format(sys.argv[0]))
    sys.exit(1)

filename = sys.argv[1]

proxies = None

if (len(sys.argv) > 2):
    proxies = [x.strip() for x in open(sys.argv[2]).readlines()]

user_ids = [x.strip() for x in open(filename, "r").readlines()]

try:
    creds = credentials.login_list
except:
    creds = [(credentials.login, credentials.password),]

pool_size = len(creds)
data = chunker_list(user_ids, pool_size)
data = [(creds[i], data[i], proxies) for i in range(pool_size)]

with Pool(len(creds)) as p:
    p.starmap(worker_process, data)
