#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入是否修复成功
"""

print("🔍 测试模块导入...")

try:
    print("1. 测试导入 PostCrawler...")
    from crawler import PostCrawler
    print("   ✅ PostCrawler 导入成功")
    
    print("2. 测试导入 CommentCrawler...")
    from crawler import CommentCrawler
    print("   ✅ CommentCrawler 导入成功")
    
    print("3. 测试创建 PostCrawler 实例...")
    crawler = PostCrawler("000002")
    print("   ✅ PostCrawler 实例创建成功")
    
    print("4. 测试导入 parser 模块...")
    import parser as builtin_parser
    print("   ✅ 内置 parser 模块正常")
    
    print("5. 测试导入本地 parser...")
    from parser import PostParser
    print("   ✅ 本地 PostParser 导入成功")
    
    print("\n🎉 所有导入测试通过！问题已修复！")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")