import os
import json
from datetime import datetime

def get_post_stats(posts_dir):
    # 获取发布文章数量和最近更新日期的逻辑
    post_files = [f for f in os.listdir(posts_dir) if f.endswith('.md')]  # 假设你的文章是 Markdown 文件
    post_count = len(post_files)
    
    # 找到最新的文章
    latest_post = max(
        [os.path.join(posts_dir, f) for f in post_files],
        key=os.path.getmtime,
    )
    latest_post_time = datetime.fromtimestamp(os.path.getmtime(latest_post)).isoformat()

    return post_count, latest_post_time

def main():
    posts_dir = '_posts'  # 文章文件夹路径
    post_count, latest_post_time = get_post_stats(posts_dir)

    # 更新你的统计数据
    stats = {
        'last_updated': datetime.now().isoformat(),
        'post_count': post_count,
        'latest_post_time': latest_post_time,
    }

    with open('stats.json', 'w') as f:
        json.dump(stats, f, indent=4)

if __name__ == '__main__':
    main()
