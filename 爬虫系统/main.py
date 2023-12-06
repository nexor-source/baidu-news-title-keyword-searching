import time
import json
from queue import Queue
from datetime import datetime

from structures import *
from utils import *


# 设置种子URL和相关参数
seed_urls = ["https://news.baidu.com/"]
MAX_DEPTH = 2  # 设置最大爬取深度
visited_urls = set()  # 存储已访问的URL
visited_urls_hash = set()  # 存储已访问的URL的html_content的hash值，进行双重判断去重
downloaded_pages = {}  # 存储已下载的结构化网页数据 key = url, value = 结构化数据
MY_SEARCH_KEYWORD = "游戏"  #设置关键词，如果不需要关键词则设置为None
FILE_SAVE_DIRECTORY = "./"  # 设置最终文件保存的路径

# 创建待抓取URL队列和初始深度队列
url_queue = Queue()
depth_queue = Queue()

# 将种子URL添加到待抓取队列
for seed_url in seed_urls:
    url_queue.put(seed_url)
    depth_queue.put(0)


try:
    # 主循环
    while not url_queue.empty():
        current_url = url_queue.get()
        current_depth = depth_queue.get()

        # 打印当前正在处理的URL
        # print(f"Processing {current_url} at depth {current_depth}")

        # 检查是否达到最大深度
        if current_depth > MAX_DEPTH:
            continue

        # 下载网页 + 第一步去重：访问过的URL我不会再访问
        if current_url not in visited_urls:
            # html_content = downloaded_pages[current_url]['raw_content'] if current_url in downloaded_pages else download_page(current_url)  # 得到完全是字符串形式的html_content
            html_content = download_page(current_url)  # 得到完全是字符串形式的html_content
            html_content_hash = hash(html_content)
            # 解析 + 第二步去重：访问过的内容我不会再解析
            if html_content and html_content_hash not in visited_urls_hash:
                # 存储已下载的网页内容
                visited_urls.add(current_url)
                visited_urls_hash.add(html_content_hash)
                
                # 解析网页内容，提取词条和链接，得到 entries = [{'title'=...,'url'=...},...]
                entries = parse_page(html_content, seed_urls)
                for entry in entries:
                    
                    # 关键词过滤
                    keywords = chinese_segmentation(entry['title'])
                    if MY_SEARCH_KEYWORD == None or MY_SEARCH_KEYWORD in keywords:
                        # 将新的URL添加到待抓取队列和深度队列
                        next_url = entry['url']
                        url_queue.put(next_url)
                        depth_queue.put(current_depth + 1)
                        # 打印过滤后得到的搜索结果
                        print(f"FOUND {entry['title']}")
                        # 存储
                        crawl_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        storage_location = f"{current_url.replace('https://', '').replace('http://', '')}.html"
                        # webpage = WebPage(url=entry['url'], keywords=keywords, crawl_datetime=crawl_datetime, content=download_page(entry['url']), storage_location=storage_location)
                        downloaded_pages[entry['url']] = {
                            'url':entry['url'],
                            'keywords':keywords,
                            'title':entry['title'],
                            'crawl_datetime':crawl_datetime,
                            # 'raw_content':download_page(entry['url']),
                            'storage_location':storage_location}
        
        # 添加延迟，以减轻对服务器的访问压力
        time.sleep(0.2)
finally:
    print(f"运行结束，共爬取到{len(downloaded_pages)}篇相关结果")
    # 保存为 JSON 文件
    with open(FILE_SAVE_DIRECTORY + 'data.json', 'w') as json_file:
        json.dump(downloaded_pages, json_file)
    print(f"结果已保存到{FILE_SAVE_DIRECTORY + 'data.json'}")