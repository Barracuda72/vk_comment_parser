from comment_collector import CommentCollector
import config
import credentials
import json
import sys

if (len(sys.argv) < 2):
    print ("Usage: {} <file_with_ids> [<file_with_proxies>]".format(sys.argv[0]))
    sys.exit(1)

filename = sys.argv[1]

proxies = None

if (len(sys.argv) > 2):
    proxies = [x.strip() for x in open(sys.argv[2]).readlines()]

comment_collector = CommentCollector(credentials.login, credentials.password, proxies)

with open(filename, "r") as f:
    for user_id in f:
        print(f"current_user: {user_id}")
        user_id = user_id.strip()
        result = comment_collector.get_comments_recursive(user_id, max_depth=1)
        with open(config.datadir + "/{user_id}.json", 'w+') as res_f:
            json.dump(result, res_f, ensure_ascii=False, indent=2)
