# 东方财富股吧爬虫 - Apify Actor 版本

## 项目介绍

该项目使用 Playwright 和 Apify SDK 构建的网页爬虫，用于抓取东方财富网股吧的 **发帖** 和 **评论** 数据。项目已适配为 Apify Actor，可以在 Apify 平台上运行，也支持本地 Docker 环境运行。

### 版本说明

- **v4.0 (当前版本)**: Apify Actor 版本，使用 Playwright + Apify SDK
- **v3.0**: 原生 Playwright 版本（见 [playwright_eastmoney_crawler.py](playwright_eastmoney_crawler.py)）
- **v2.0**: Selenium 版本（见 [crawler.py](crawler.py) 和 [main_old.py](main_old.py)）

## 主要功能

1. **爬取发帖信息**: 抓取指定股票股吧的帖子标题、作者、发帖时间、阅读数、回复数和帖子链接
2. **爬取评论信息** (可选): 抓取帖子下的评论内容、评论者、评论时间和楼层号
3. **数据输出**: 数据自动保存到 Apify 数据集，支持导出为 JSON、CSV、Excel 等格式
4. **灵活配置**: 通过输入参数轻松配置股票代码、爬取数量、是否爬取评论等选项

## 项目结构

```
EastMoney_Crawler/
├── .actor/
│   ├── actor.json              # Apify Actor 配置文件
│   └── INPUT_SCHEMA.json       # 输入参数定义
├── main.py                     # Apify Actor 主程序 (v4.0)
├── Dockerfile                  # Docker 构建文件
├── requirements.txt            # Python 依赖
├── .dockerignore              # Docker 忽略文件
├── .gitignore                 # Git 忽略文件
├── playwright_eastmoney_crawler.py  # 原生 Playwright 版本 (v3.0)
├── crawler.py                 # Selenium 版本爬虫 (v2.0)
├── main_old.py                # Selenium 版本主程序 (v2.0)
├── parser.py                  # 数据解析器 (v2.0)
├── mongodb.py                 # MongoDB 接口 (v2.0)
└── README.md                  # 项目文档
```

## 快速开始

### 方式一: 在 Apify 平台运行 (推荐)

1. 将项目推送到 GitHub
2. 在 Apify 控制台创建新 Actor
3. 连接 GitHub 仓库并选择分支
4. Apify 会自动读取 `.actor/actor.json` 配置并构建 Actor
5. 配置输入参数并运行

### 方式二: 本地运行 (需要 Apify CLI)

```bash
# 安装 Apify CLI
npm install -g apify-cli

# 登录 Apify 账户
apify login

# 在项目目录运行
apify run

# 或推送到 Apify 平台
apify push
```

### 方式三: 使用 Docker 本地运行

```bash
# 构建 Docker 镜像
docker build -t eastmoney-crawler .

# 创建输入文件 input.json
echo '{
  "stockCode": "002001",
  "stockName": "新和成",
  "maxPosts": 10,
  "crawlComments": false,
  "headless": true
}' > input.json

# 运行 Docker 容器
docker run -v $(pwd)/apify_storage:/app/apify_storage \
  -e APIFY_INPUT_FILE=/app/input.json \
  eastmoney-crawler
```

### 方式四: 本地 Python 运行 (不使用 Apify)

使用原生 Playwright 版本：

```bash
# 安装依赖
pip install playwright

# 安装浏览器
playwright install chromium

# 运行爬虫
python playwright_eastmoney_crawler.py
```

## 输入参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `stockCode` | string | 是 | "002001" | 股票代码 |
| `stockName` | string | 是 | "新和成" | 股票名称 |
| `maxPosts` | integer | 否 | 10 | 最大爬取帖子数 (1-100) |
| `crawlComments` | boolean | 否 | false | 是否爬取评论 |
| `headless` | boolean | 否 | true | 是否使用无头浏览器 |
| `proxyConfiguration` | object | 否 | - | 代理配置 |

## 输出数据格式

### 帖子数据示例

```json
{
  "title": "帖子标题",
  "author": "作者用户名",
  "post_time": "2025-01-15 10:30:00",
  "read_count": "1234",
  "reply_count": "56",
  "post_url": "https://guba.eastmoney.com/news,xxx.html",
  "stock_code": "002001",
  "stock_name": "新和成",
  "crawl_time": "2025-01-15T10:35:00.123456"
}
```

### 评论数据示例

```json
{
  "author": "评论用户",
  "content": "评论内容",
  "comment_time": "2025-01-15 11:00:00",
  "floor_number": 1,
  "post_url": "https://guba.eastmoney.com/news,xxx.html",
  "stock_code": "002001",
  "crawl_time": "2025-01-15T11:05:00.123456"
}
```

## 技术特点

### Apify Actor 版本优势 (v4.0)

- **云端运行**: 可在 Apify 平台上运行，无需本地环境
- **标准化输出**: 数据自动保存到 Apify 数据集，支持多种导出格式
- **容器化部署**: 使用 Docker 打包，环境一致性好
- **易于配置**: 通过 JSON Schema 定义输入参数，自动生成 UI
- **可扩展性**: 支持代理、调度任务等企业级功能

### Playwright 优势 (v3.0 & v4.0)

- **高性能**: 原生异步支持，执行效率高
- **稳定性强**: 更好的页面等待和错误处理机制
- **现代化**: 官方维护活跃，支持最新浏览器特性
- **无需驱动**: 不需要单独下载 ChromeDriver

### Selenium 版本 (v2.0)

如果需要使用旧版 Selenium + MongoDB 方案，请参考：
- [使用说明.md](使用说明.md) - Selenium 版本详细使用指南
- [项目总结.md](项目总结.md) - Selenium 版本技术总结

## 注意事项

1. **合规使用**: 请遵守网站的 robots.txt 和使用条款，仅用于学习研究
2. **频率控制**: 建议设置合理的爬取间隔，避免对服务器造成压力
3. **数据隐私**: 不要爬取和存储用户的敏感信息
4. **IP 限制**: 东方财富可能会限制频繁访问的 IP，建议使用代理或控制请求频率

## 常见问题

### Q: 如何部署到 Apify 平台？

A: 参考"快速开始"中的"方式一"，将代码推送到 GitHub 后在 Apify 控制台关联仓库即可。

### Q: 本地如何测试？

A: 使用 `apify run` 命令或直接运行 `python playwright_eastmoney_crawler.py`（不需要 Apify 环境）。

### Q: 数据保存在哪里？

A: Apify Actor 运行时数据保存在 Apify 数据集中；本地运行时保存为 JSON 文件。

### Q: 爬取失败怎么办？

A: 检查网络连接、目标网站是否可访问、是否被限制访问。可以尝试使用代理或降低爬取频率。

## 开发计划

- [ ] 支持更多股票论坛网站
- [ ] 添加数据清洗和分析功能
- [ ] 支持增量爬取和断点续爬
- [ ] 添加反爬虫策略优化
- [ ] 提供数据可视化面板

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目仅供学习研究使用，请勿用于商业用途。

## 致谢

- 感谢 [Apify](https://apify.com/) 提供优秀的 Actor 平台
- 感谢 [Playwright](https://playwright.dev/) 团队提供强大的浏览器自动化工具
- 感谢所有贡献者和使用者的反馈

