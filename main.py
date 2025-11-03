#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富股吧爬虫 - Apify Actor 版本
使用 Playwright 进行数据爬取
"""

import asyncio
import logging
import re
from datetime import datetime
from urllib.parse import urljoin

from playwright.async_api import async_playwright
from apify import Actor


class EastMoneyCrawler:
    """东方财富股吧爬虫"""

    def __init__(self, stock_code, stock_name, max_posts=10, headless=True):
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.max_posts = max_posts
        self.headless = headless
        self.base_url = f"https://guba.eastmoney.com/list,{stock_code}.html"
        self.logger = logging.getLogger(__name__)

        # 存储数据
        self.posts_data = []
        self.comments_data = []

    async def crawl_post_list(self, page):
        """爬取帖子列表"""
        try:
            self.logger.info(f"开始爬取股票 {self.stock_name}({self.stock_code}) 的帖子...")

            # 访问页面
            await page.goto(self.base_url, wait_until='domcontentloaded', timeout=45000)
            await asyncio.sleep(3)

            # 检查页面是否正确加载
            title = await page.title()
            if title and ("东方财富" in title or "股吧" in title):
                self.logger.info(f"✅ 页面加载成功: {title}")
            else:
                self.logger.warning(f"页面标题异常: {title}")
                return 0

            # 等待页面完全加载
            await asyncio.sleep(3)

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
                    elements = await page.query_selector_all(selector)
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
                content = await page.content()

                # 使用正则表达式提取帖子信息
                title_pattern = r'<a[^>]*title="([^"]*)"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
                matches = re.findall(title_pattern, content)

                self.logger.info(f"通过正则表达式找到 {len(matches)} 个标题链接")

                count = 0
                for title, href, text in matches[:self.max_posts]:
                    if self.stock_code in href or "guba.eastmoney.com" in href:
                        post_url = href if href.startswith('http') else f"https://guba.eastmoney.com{href}"

                        post_data = {
                            'title': title or text,
                            'author': f'用户{count+1}',
                            'post_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'read_count': '0',
                            'reply_count': '0',
                            'post_url': post_url,
                            'stock_code': self.stock_code,
                            'stock_name': self.stock_name,
                            'crawl_time': datetime.now().isoformat()
                        }

                        self.posts_data.append(post_data)
                        count += 1
                        self.logger.info(f"帖子 {count}: {title[:50]}...")

                return len(self.posts_data)

            # 处理找到的帖子元素
            for i, element in enumerate(post_elements[:self.max_posts]):
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

    async def crawl_comments(self, page, post_url, max_comments=5):
        """爬取单个帖子的评论"""
        try:
            self.logger.info(f"正在爬取帖子评论: {post_url}")

            await page.goto(post_url, wait_until='domcontentloaded', timeout=45000)
            await asyncio.sleep(3)

            # 尝试多种选择器来找到评论
            comment_selectors = [
                '.reply-item',
                '.comment-item',
                '.stock-comment',
                '[class*="comment"]',
                '[class*="reply"]'
            ]

            comment_elements = []
            for selector in comment_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        self.logger.info(f"使用选择器 '{selector}' 找到 {len(elements)} 个评论")
                        comment_elements = elements
                        break
                except:
                    continue

            for i, element in enumerate(comment_elements[:max_comments]):
                try:
                    # 提取评论内容
                    content = await element.inner_text()

                    comment_data = {
                        'author': f'评论用户{i+1}',
                        'content': content.strip()[:500] if content else '',
                        'comment_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'floor_number': i+1,
                        'post_url': post_url,
                        'stock_code': self.stock_code,
                        'crawl_time': datetime.now().isoformat()
                    }

                    self.comments_data.append(comment_data)

                except Exception as e:
                    self.logger.error(f"处理评论 {i+1} 时出错: {e}")
                    continue

            return len(comment_elements[:max_comments])

        except Exception as e:
            self.logger.error(f"爬取评论失败: {e}")
            return 0


async def main() -> None:
    """主函数 - Apify Actor 入口"""
    async with Actor:
        # 设置日志
        Actor.log.info("🚀 东方财富股吧爬虫启动...")

        # 获取输入参数
        actor_input = await Actor.get_input() or {}
        stock_code = actor_input.get('stockCode', '002001')
        stock_name = actor_input.get('stockName', '新和成')
        max_posts = actor_input.get('maxPosts', 10)
        crawl_comments = actor_input.get('crawlComments', False)
        headless = actor_input.get('headless', True)

        Actor.log.info(f"输入参数: 股票代码={stock_code}, 股票名称={stock_name}, 最大帖子数={max_posts}")
        Actor.log.info(f"爬取评论: {crawl_comments}, 无头模式: {headless}")

        # 创建爬虫实例
        crawler = EastMoneyCrawler(
            stock_code=stock_code,
            stock_name=stock_name,
            max_posts=max_posts,
            headless=headless
        )

        # 启动 Playwright
        Actor.log.info("正在启动 Playwright 浏览器...")

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )

            context = await browser.new_context()
            page = await context.new_page()

            # 设置超时时间
            page.set_default_timeout(60000)
            page.set_default_navigation_timeout(60000)

            Actor.log.info("✅ Playwright 浏览器初始化成功")

            # 爬取帖子列表
            posts_count = await crawler.crawl_post_list(page)
            Actor.log.info(f"✅ 成功爬取 {posts_count} 个帖子")

            # 将帖子数据推送到 Apify 数据集
            if crawler.posts_data:
                await Actor.push_data(crawler.posts_data)
                Actor.log.info(f"✅ 已将 {len(crawler.posts_data)} 个帖子推送到数据集")

            # 如果需要爬取评论
            if crawl_comments and crawler.posts_data:
                Actor.log.info("开始爬取帖子评论...")

                for i, post in enumerate(crawler.posts_data[:5]):  # 限制只爬取前5个帖子的评论
                    if post.get('post_url'):
                        Actor.log.info(f"爬取第 {i+1}/{min(5, len(crawler.posts_data))} 个帖子的评论")
                        comments_count = await crawler.crawl_comments(page, post['post_url'])
                        Actor.log.info(f"找到 {comments_count} 条评论")
                        await asyncio.sleep(2)  # 避免请求过快

                # 将评论数据推送到 Apify 数据集
                if crawler.comments_data:
                    await Actor.push_data(crawler.comments_data)
                    Actor.log.info(f"✅ 已将 {len(crawler.comments_data)} 条评论推送到数据集")

            # 关闭浏览器
            await browser.close()

        # 输出统计信息
        Actor.log.info("=== 爬取完成 ===")
        Actor.log.info(f"总帖子数: {len(crawler.posts_data)}")
        Actor.log.info(f"总评论数: {len(crawler.comments_data)}")
        Actor.log.info("🎉 任务完成！")


if __name__ == '__main__':
    asyncio.run(main())
