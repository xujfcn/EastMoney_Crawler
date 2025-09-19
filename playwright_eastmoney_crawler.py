#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用原生Playwright的东方财富爬虫
避开AgentQL兼容性问题
"""

import asyncio
import logging
import json
from datetime import datetime
import re

class PlaywrightEastMoneyCrawler:
    """使用原生Playwright的东方财富爬虫"""
    
    def __init__(self, stock_code="002001", stock_name="新和成"):
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.base_url = f"https://guba.eastmoney.com/list,{stock_code}.html"
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('playwright_crawler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 存储数据
        self.posts_data = []
        self.comments_data = []
    
    async def init_browser(self):
        """初始化浏览器"""
        try:
            from playwright.async_api import async_playwright
            
            self.logger.info("正在初始化Playwright浏览器...")
            
            # 启动Playwright
            self.playwright = await async_playwright().start()
            
            # 启动浏览器
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # 显示浏览器便于调试
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            # 创建页面
            self.page = await self.browser.new_page()
            
            # 设置超时时间
            self.page.set_default_timeout(60000)
            self.page.set_default_navigation_timeout(60000)
            
            self.logger.info("✅ Playwright浏览器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 浏览器初始化失败: {e}")
            return False
    
    async def safe_goto(self, url, max_retries=3):
        """安全的页面导航"""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"尝试访问页面 (第{attempt+1}次): {url}")
                
                await self.page.goto(url, wait_until='domcontentloaded', timeout=45000)
                await asyncio.sleep(3)
                
                # 检查页面是否正确加载
                title = await self.page.title()
                if title and ("东方财富" in title or "股吧" in title):
                    self.logger.info(f"✅ 页面加载成功: {title}")
                    return True
                else:
                    self.logger.warning(f"页面标题异常: {title}")
                    
            except Exception as e:
                self.logger.warning(f"第{attempt+1}次访问失败: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                else:
                    self.logger.error("所有访问尝试都失败了")
                    return False
        
        return False
    
    async def crawl_posts(self):
        """爬取帖子列表"""
        try:
            self.logger.info(f"开始爬取股票 {self.stock_name}({self.stock_code}) 的帖子...")
            
            # 访问页面
            if not await self.safe_goto(self.base_url):
                return 0
            
            # 等待页面完全加载
            await asyncio.sleep(5)
            
            # 尝试多种选择器来找到帖子列表
            selectors = [
                'tr.listitem',
                'tr[class*="listitem"]',
                '.articleh',
                '.normal_post',
                'tbody tr'
            ]
            
            post_elements = []
            for selector in selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        self.logger.info(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                        post_elements = elements
                        break
                except Exception as e:
                    self.logger.debug(f"选择器 '{selector}' 失败: {e}")
                    continue
            
            if not post_elements:
                self.logger.warning("未找到帖子元素，尝试获取页面内容进行分析")
                
                # 获取页面HTML进行分析
                content = await self.page.content()
                
                # 使用正则表达式提取帖子信息
                title_pattern = r'<a[^>]*title="([^"]*)"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
                matches = re.findall(title_pattern, content)
                
                self.logger.info(f"通过正则表达式找到 {len(matches)} 个标题链接")
                
                for i, (title, href, text) in enumerate(matches[:10]):
                    if self.stock_code in href or "guba.eastmoney.com" in href:
                        post_url = href if href.startswith('http') else f"https://guba.eastmoney.com{href}"
                        
                        post_data = {
                            'title': title or text,
                            'author': f'用户{i+1}',
                            'post_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'read_count': '0',
                            'reply_count': '0',
                            'post_url': post_url,
                            'stock_code': self.stock_code,
                            'stock_name': self.stock_name,
                            'crawl_time': datetime.now().isoformat()
                        }
                        
                        self.posts_data.append(post_data)
                        self.logger.info(f"帖子 {len(self.posts_data)}: {title[:50]}...")
                
                return len(self.posts_data)
            
            # 处理找到的帖子元素
            for i, element in enumerate(post_elements[:10]):
                try:
                    # 尝试提取标题
                    title_element = await element.query_selector('a[title]')
                    if not title_element:
                        title_element = await element.query_selector('a')
                    
                    if title_element:
                        title = await title_element.get_attribute('title')
                        if not title:
                            title = await title_element.inner_text()
                        
                        href = await title_element.get_attribute('href')
                        post_url = href if href and href.startswith('http') else f"https://guba.eastmoney.com{href}" if href else ""
                    else:
                        title = f"帖子{i+1}"
                        post_url = ""
                    
                    # 尝试提取其他信息
                    author = "未知用户"
                    try:
                        author_element = await element.query_selector('.author, .username, [class*="author"]')
                        if author_element:
                            author = await author_element.inner_text()
                    except:
                        pass
                    
                    post_data = {
                        'title': title.strip() if title else f"帖子{i+1}",
                        'author': author.strip() if author else f"用户{i+1}",
                        'post_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'read_count': '0',
                        'reply_count': '0',
                        'post_url': post_url,
                        'stock_code': self.stock_code,
                        'stock_name': self.stock_name,
                        'crawl_time': datetime.now().isoformat()
                    }
                    
                    self.posts_data.append(post_data)
                    self.logger.info(f"帖子 {i+1}: {post_data['title'][:50]}...")
                    
                except Exception as e:
                    self.logger.error(f"处理帖子 {i+1} 时出错: {e}")
                    continue
            
            return len(self.posts_data)
            
        except Exception as e:
            self.logger.error(f"爬取帖子失败: {e}")
            return 0
    
    async def save_data(self):
        """保存数据到JSON文件"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 保存帖子数据
            posts_file = f"playwright_posts_{self.stock_code}_{timestamp}.json"
            with open(posts_file, 'w', encoding='utf-8') as f:
                json.dump(self.posts_data, f, ensure_ascii=False, indent=2)
            
            # 保存评论数据
            comments_file = f"playwright_comments_{self.stock_code}_{timestamp}.json"
            with open(comments_file, 'w', encoding='utf-8') as f:
                json.dump(self.comments_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ 数据已保存:")
            self.logger.info(f"   帖子数据: {posts_file}")
            self.logger.info(f"   评论数据: {comments_file}")
            
            return posts_file, comments_file
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            return None, None
    
    async def run(self):
        """运行爬虫"""
        try:
            self.logger.info("=== 开始Playwright爬虫任务 ===")
            
            # 初始化浏览器
            if not await self.init_browser():
                return False
            
            # 爬取帖子
            posts_count = await self.crawl_posts()
            
            if posts_count > 0:
                self.logger.info(f"成功爬取 {posts_count} 个帖子")
                
                # 保存数据
                await self.save_data()
                
                # 输出统计信息
                self.logger.info("=== 爬取完成 ===")
                self.logger.info(f"总帖子数: {len(self.posts_data)}")
                self.logger.info(f"总评论数: {len(self.comments_data)}")
                
                return True
            else:
                self.logger.error("未能爬取到任何帖子")
                return False
                
        except Exception as e:
            self.logger.error(f"爬虫运行失败: {e}")
            return False
        
        finally:
            # 清理资源
            try:
                if hasattr(self, 'browser'):
                    await self.browser.close()
                if hasattr(self, 'playwright'):
                    await self.playwright.stop()
                self.logger.info("浏览器资源已清理")
            except Exception as e:
                self.logger.error(f"清理资源时出错: {e}")

async def main():
    """主函数"""
    print("=== Playwright东方财富爬虫 ===")
    
    # 检查依赖
    try:
        import playwright
        print("✅ Playwright依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少Playwright依赖: {e}")
        print("请运行: pip install playwright")
        print("然后运行: playwright install")
        return
    
    # 创建爬虫实例
    crawler = PlaywrightEastMoneyCrawler()
    
    # 运行爬虫
    success = await crawler.run()
    
    if success:
        print("🎉 爬虫任务完成！")
    else:
        print("❌ 爬虫任务失败，请查看日志文件")

if __name__ == "__main__":
    asyncio.run(main())