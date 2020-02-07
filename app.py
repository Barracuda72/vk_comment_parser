from comment_collector import CommentCollector
import config
import json

comment_collector = CommentCollector(config.login,config.password)

with open("<filename>", "r") as f:
    for user_id in f:
        print(f"current_user: {user_id}")
        user_id = user_id.strip()
        result = comment_collector.get_comments_recursive(user_id, max_depth=1)
        with open(f"data_2/{user_id}.json", 'w+') as res_f:
            json.dump(result, res_f, ensure_ascii=False, indent=2)