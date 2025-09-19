#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from crawler import CommentCrawler

def test_simple():
    print("开始测试评论爬虫...")
    
    # 创建评论爬虫实例
    comment_crawler = CommentCrawler("600438")
    
    # 测试按ID范围查找（这样可以避免日期字段的问题）
    print("测试按ID范围查找帖子...")
    comment_crawler.find_by_id(1, 100)  # 查找前100条帖子
    
    # 如果找到了帖子，尝试爬取评论
    if not comment_crawler.post_df.empty:
        print("找到帖子，开始爬取评论...")
        comment_crawler.crawl_comment_info()
    else:
        print("没有找到帖子，尝试按日期查找...")
        comment_crawler.find_by_date('2025-08-01', '2025-12-31')
        
        if not comment_crawler.post_df.empty:
            print("按日期找到帖子，开始爬取评论...")
            comment_crawler.crawl_comment_info()
        else:
            print("仍然没有找到帖子")

if __name__ == "__main__":
    test_simple()