#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mongodb import MongoAPI
import pymongo

def check_database():
    try:
        # 连接数据库
        mongo = MongoAPI()
        
        # 检查帖子数据
        posts_count = mongo.db.eastmoney_posts.count_documents({})
        print(f'帖子总数: {posts_count}')
        
        # 检查评论数据
        comments_count = mongo.db.eastmoney_comments.count_documents({})
        print(f'评论总数: {comments_count}')
        
        if posts_count > 0:
            print('\n最近的3条帖子:')
            recent_posts = list(mongo.db.eastmoney_posts.find({}).sort('_id', -1).limit(3))
            for i, post in enumerate(recent_posts, 1):
                print(f'{i}. 标题: {post.get("title", "无标题")}')
                print(f'   发布时间: {post.get("publish_time", "无时间")}')
                print(f'   阅读数: {post.get("read_count", 0)}')
                print(f'   评论数: {post.get("comment_count", 0)}')
                print(f'   帖子ID: {post.get("post_id", "无ID")}')
                print()
        
        if comments_count > 0:
            print('最近的3条评论:')
            recent_comments = list(mongo.db.eastmoney_comments.find({}).sort('_id', -1).limit(3))
            for i, comment in enumerate(recent_comments, 1):
                content = comment.get("content", "无内容")
                if len(content) > 50:
                    content = content[:50] + "..."
                print(f'{i}. 评论内容: {content}')
                print(f'   发布时间: {comment.get("publish_time", "无时间")}')
                print(f'   点赞数: {comment.get("like_count", 0)}')
                print()
        else:
            print('\n数据库中没有评论数据')
            
        # 检查有评论数大于0的帖子
        posts_with_comments = list(mongo.db.eastmoney_posts.find({"comment_count": {"$gt": 0}}).limit(5))
        if posts_with_comments:
            print(f'\n有评论的帖子数量: {len(posts_with_comments)}')
            for post in posts_with_comments:
                print(f'- {post.get("title", "无标题")} (评论数: {post.get("comment_count", 0)})')
        else:
            print('\n没有找到有评论的帖子')
            
    except Exception as e:
        print(f'检查数据库时出错: {e}')

if __name__ == "__main__":
    check_database()