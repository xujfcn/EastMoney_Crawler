#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mongodb import MongoAPI
import pandas as pd

def test_comment_crawler():
    stock_symbol = "600438"
    
    print("=" * 50)
    print("测试评论爬虫数据库连接")
    print("=" * 50)
    
    # 连接帖子数据库
    postdb = MongoAPI('post_info', f'post_{stock_symbol}')
    
    # 检查数据库连接
    try:
        total_posts = postdb.count_documents()
        print(f"数据库 post_info.post_{stock_symbol} 中的帖子总数: {total_posts}")
        
        if total_posts == 0:
            print("❌ 数据库中没有帖子数据")
            return
        
        # 获取一个样本帖子来检查字段
        sample_post = postdb.find_one({}, {})
        if sample_post:
            print(f"\n✅ 找到样本帖子，字段如下:")
            for key, value in sample_post.items():
                print(f"  {key}: {value} (类型: {type(value).__name__})")
            
            # 检查日期字段
            date_fields = [k for k in sample_post.keys() if 'date' in k.lower() or 'time' in k.lower()]
            print(f"\n📅 日期相关字段: {date_fields}")
            
            # 检查评论数字段
            comment_fields = [k for k in sample_post.keys() if 'comment' in k.lower() or 'reply' in k.lower()]
            print(f"💬 评论相关字段: {comment_fields}")
            
            # 尝试查找有评论的帖子
            for comment_field in comment_fields:
                try:
                    posts_with_comments = list(postdb.find({comment_field: {"$ne": 0, "$ne": "0"}}, {}).limit(3))
                    if posts_with_comments:
                        print(f"\n✅ 使用字段 '{comment_field}' 找到 {len(posts_with_comments)} 条有评论的帖子:")
                        for i, post in enumerate(posts_with_comments, 1):
                            title = post.get('title', '无标题')[:30] + '...' if len(post.get('title', '')) > 30 else post.get('title', '无标题')
                            print(f"  {i}. {title} (评论数: {post.get(comment_field, 0)})")
                        break
                except Exception as e:
                    print(f"❌ 使用字段 '{comment_field}' 查询失败: {e}")
            
            # 测试日期范围查询
            for date_field in date_fields:
                try:
                    posts_in_range = list(postdb.find({date_field: {"$gte": "2025-08-01", "$lte": "2025-12-31"}}, {}).limit(3))
                    if posts_in_range:
                        print(f"\n✅ 使用日期字段 '{date_field}' 找到 {len(posts_in_range)} 条2025年的帖子:")
                        for i, post in enumerate(posts_in_range, 1):
                            title = post.get('title', '无标题')[:30] + '...' if len(post.get('title', '')) > 30 else post.get('title', '无标题')
                            print(f"  {i}. {title} (日期: {post.get(date_field, '无日期')})")
                        break
                except Exception as e:
                    print(f"❌ 使用日期字段 '{date_field}' 查询失败: {e}")
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")

if __name__ == "__main__":
    test_comment_crawler()