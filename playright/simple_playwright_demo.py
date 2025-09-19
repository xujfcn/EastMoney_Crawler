#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简单的Playwright示例
展示Playwright的核心功能和优势
"""

import asyncio
from playwright.async_api import async_playwright

async def simple_demo():
    """最基础的Playwright演示"""
    print("🚀 启动Playwright演示...")
    
    # 启动Playwright
    async with async_playwright() as p:
        # 1. 启动浏览器 (比Selenium更快)
        print("📱 启动浏览器...")
        browser = await p.chromium.launch(
            headless=False,  # 显示浏览器窗口
            args=['--no-sandbox']
        )
        
        # 2. 创建新页面
        page = await browser.new_page()
        
        # 3. 访问网页
        print("🌐 访问百度首页...")
        await page.goto("https://www.baidu.com")
        
        # 4. 获取页面标题
        title = await page.title()
        print(f"📄 页面标题: {title}")
        
        # 5. 截图功能 (Playwright内置)
        print("📸 截图保存...")
        await page.screenshot(path="playright/baidu_screenshot.png")
        
        # 6. 查找元素并输入文本
        print("🔍 在搜索框输入文本...")
        search_box = page.locator("#kw")  # 百度搜索框
        await search_box.fill("Playwright自动化测试")
        
        # 7. 点击搜索按钮
        print("🖱️ 点击搜索...")
        search_btn = page.locator("#su")  # 百度搜索按钮
        await search_btn.click()
        
        # 8. 等待页面加载
        await page.wait_for_load_state("networkidle")
        
        # 9. 获取搜索结果
        print("📊 获取搜索结果...")
        results = await page.locator(".result").all()
        print(f"找到 {len(results)} 个搜索结果")
        
        # 10. 提取第一个结果的标题
        if results:
            first_result = results[0]
            title_element = first_result.locator("h3 a")
            if await title_element.count() > 0:
                first_title = await title_element.text_content()
                print(f"第一个结果: {first_title}")
        
        # 11. 再次截图
        await page.screenshot(path="playright/search_results.png")
        print("📸 搜索结果截图已保存")
        
        # 等待3秒让用户看到结果
        await asyncio.sleep(3)
        
        # 关闭浏览器
        await browser.close()
        print("✅ 演示完成!")

async def eastmoney_simple_demo():
    """东方财富网站的简单演示"""
    print("\n🏢 东方财富网站演示...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 访问东方财富股吧
        print("🌐 访问东方财富万科A股吧...")
        await page.goto("https://guba.eastmoney.com/list,000002.html")
        
        # 等待页面加载
        await page.wait_for_load_state("networkidle")
        
        # 获取页面标题
        title = await page.title()
        print(f"📄 页面标题: {title}")
        
        # 查找帖子列表
        print("📝 获取帖子列表...")
        posts = await page.locator("tr.listitem").all()
        print(f"找到 {len(posts)} 个帖子")
        
        # 提取前3个帖子的信息
        for i, post in enumerate(posts[:3], 1):
            try:
                # 获取帖子标题
                title_element = post.locator("td:nth-child(1) a")
                if await title_element.count() > 0:
                    title = await title_element.text_content()
                    print(f"帖子{i}: {title.strip()}")
                
                # 获取作者
                author_element = post.locator("td:nth-child(2) a")
                if await author_element.count() > 0:
                    author = await author_element.text_content()
                    print(f"  作者: {author.strip()}")
                
                # 获取发布时间
                time_element = post.locator("td:nth-child(4)")
                if await time_element.count() > 0:
                    post_time = await time_element.text_content()
                    print(f"  时间: {post_time.strip()}")
                
                print("-" * 50)
                
            except Exception as e:
                print(f"  获取帖子{i}信息失败: {e}")
        
        # 截图保存
        await page.screenshot(path="playright/eastmoney_posts.png")
        print("📸 东方财富页面截图已保存")
        
        await asyncio.sleep(2)
        await browser.close()
        print("✅ 东方财富演示完成!")

def show_playwright_features():
    """展示Playwright的主要功能特点"""
    print("\n" + "="*60)
    print("🎭 Playwright 核心功能和优势")
    print("="*60)
    
    features = [
        "🚀 启动速度快 - 比Selenium快2-3倍",
        "🎯 元素定位准确 - 支持多种定位策略",
        "📱 多浏览器支持 - Chrome、Firefox、Safari、Edge",
        "📸 内置截图功能 - 无需额外配置",
        "🔄 异步处理 - 支持并发操作",
        "🛡️ 反爬虫能力强 - 更难被检测",
        "⏱️ 智能等待 - 自动等待元素加载",
        "📊 网络拦截 - 可以拦截和修改请求",
        "🎬 录制功能 - 可以录制操作生成代码",
        "📱 移动端模拟 - 支持移动设备模拟"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n" + "="*60)
    print("🆚 Playwright vs Selenium 对比")
    print("="*60)
    
    comparison = [
        ("启动速度", "Playwright: 2-3秒", "Selenium: 5-8秒"),
        ("内存占用", "Playwright: 较低", "Selenium: 较高"),
        ("反爬虫", "Playwright: 强", "Selenium: 中等"),
        ("API设计", "Playwright: 现代异步", "Selenium: 传统同步"),
        ("截图功能", "Playwright: 内置", "Selenium: 需要额外库"),
        ("等待机制", "Playwright: 智能等待", "Selenium: 手动等待"),
        ("学习曲线", "Playwright: 中等", "Selenium: 简单")
    ]
    
    for item, pw, sel in comparison:
        print(f"  {item:10} | {pw:20} | {sel}")
    
    print("\n" + "="*60)

async def main():
    """主函数"""
    show_playwright_features()
    
    print("\n请选择演示:")
    print("1. 基础功能演示 (百度搜索)")
    print("2. 东方财富网站演示")
    print("3. 两个都运行")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == "1":
        await simple_demo()
    elif choice == "2":
        await eastmoney_simple_demo()
    elif choice == "3":
        await simple_demo()
        await eastmoney_simple_demo()
    else:
        print("❌ 无效选择")
        return
    
    print("\n🎉 所有演示完成!")
    print("📁 截图文件保存在 playright/ 目录下")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        print("💡 请确保已安装Playwright:")
        print("   pip install playwright")
        print("   playwright install chromium")