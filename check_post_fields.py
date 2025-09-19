#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mongodb import MongoAPI
import pymongo

def check_post_fields():
    try:
        # 连接数据库
        mongo = MongoAPI()
        
        # 检查帖子数据
        posts_count = mongo.db.eastmoney_posts.count_documents({})
        print(f'帖子总数: {posts_count}')
        
        if posts_count > 0:
            # 获取一条帖子数据来查看字段结构
            sample_post = mongo.db.eastmoney_posts.find_one({})
            print('\n帖子数据字段:')
            for key, value in sample_post.items():
                print(f'  {key}: {value} (类型: {type(value).__name__})')
            
            # 检查有评论数大于0的帖子
            posts_with_comments = list(mongo.db.eastmoney_posts.find({"comment_count": {"$gt": 0}}).limit(3))
            print(f'\n有评论的帖子数量: {len(posts_with_comments)}')
            
            if len(posts_with_comments) == 0:
                # 尝试其他可能的字段名
                posts_with_comments = list(mongo.db.eastmoney_posts.find({"comment_num": {"$gt": 0}}).limit(3))
                print(f'使用comment_num字段找到的有评论帖子数量: {len(posts_with_comments)}')
            
            if len(posts_with_comments) == 0:
                # 查看所有帖子的评论数字段
                all_posts = list(mongo.db.eastmoney_posts.find({}).limit(5))
                print('\n前5条帖子的评论相关字段:')
                for i, post in enumerate(all_posts, 1):
                    print(f'帖子{i}:')
                    for key, value in post.items():
                        if 'comment' in key.lower() or 'reply' in key.lower():
                            print(f'  {key}: {value}')
            else:
                print('\n有评论的帖子示例:')
                for i, post in enumerate(posts_with_comments, 1):
                    print(f'帖子{i}: {post.get("title", "无标题")} (评论数: {post.get("comment_count", post.get("comment_num", 0))})')
            
            # 检查日期字段
            print('\n日期相关字段:')
            sample_post = mongo.db.eastmoney_posts.find_one({})
            for key, value in sample_post.items():
                if 'date' in key.lower() or 'time' in key.lower():
                    print(f'  {key}: {value} (类型: {type(value).__name__})')
                    
    except Exception as e:
        print(f'检查数据库时出错: {e}')

if __name__ == "__main__":
    check_post_fields()