import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
import jieba
import string

def chinese_segmentation(text):
    # 使用全模式进行分词，可能会输出冗余词汇，但是根据冗余词汇检索比骄方便
    # 如果是空的字符串则会返回[]
    seg_list = jieba.cut(text, cut_all=True)
    chinese_punctuation = set("，。！？&#8203;``【oaicite:0】``&#8203;（）《》")  # 中文标点符号
    return [word for word in seg_list if word not in string.punctuation and word not in chinese_punctuation]

# 定义函数：下载网页并存储
def download_page(url):
    try:
        response = requests.get(url, timeout=3)  # 3秒get不到就滚
        response.raise_for_status()  # 检查请求是否成功
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None
    
# 定义函数：下载网页并解析内容，返回<p>整体内容的一个string
def download_content(url):
    html_content = download_page(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    contents = soup.find_all('p')
    s = ""
    for c in contents:
        s += c.text
    return s

# 定义函数：解析网页内容，提取词条和链接
def parse_page(html_content, seed_urls):
    """    
    在 HTML 中，<a> 标签通常是用于创建超链接的标签，而 href 属性是该标签的核心属性，指定了链接的目标地址。
    按照 HTML 规范，<a> 标签应该带有 href 属性，以确保提供了目标地址。
    但是为了防止不规范的情况出现，这里需要过滤那些没有href属性的标签

    比如：<a class="cy" href="//www.baidu.com/duty/">使用百度前必读</a>     。这就是一个标签

    a指定这是一个超链接，比如p是段落标签，h1~h6是标题标签等等
    class用于指定元素类名的属性。元素的类名通常用于将样式应用到一个或多个元素
    href就是超链接的URL，有时候这里给出的是完整的绝对链接，有时则是给出的相对链接
        相对链接就像例子一样，href="//www.baidu.com/duty/"，缺少了开头的http
        这表示相对于当前页面使用的协议，即如果当前页面是 http，则链接是 http:...；如果是 https，则是 https:...
        同时href还有一种特殊写法，即href="javascript:void(0);"或者href="#"
        这种写法通常用于创建一个无操作的链接，即点击链接时不会触发任何实际的页面导航或跳转。
        在过滤这种href的时候，我直接判断了href是否是javascript:开头的方式来简单粗暴的进行判断
        因为javascript:开头的不是传统URL，除了这种void(0)的情况，也有可能对应js点击事件的链接，但需要模拟浏览器行为，这里不做考虑
    "使用百度前必读"是包含在标签的开始标签和结束标签之间的部分的文本内容，在BeautifulSoup中使用.text读取
    某些还会有target="_blank"的属性，这是让它在新页面打开xxx，默认不说明则是本页打开xxx
    """
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 初始化一个空列表，用于存储提取的词条和链接
    entries = []

    # 提取所有的链接（<a>标签）信息
    links = soup.find_all('a', href=True)
    

    # 遍历每个找到的链接
    for link in links:
        # 构建绝对URL，使用urljoin确保URL的正确性
        url = urljoin(seed_urls[0], link['href'])
        # 使用 urlparse 检查链接的格式
        parsed_url = urlparse(url)
        
        # 判断链接是否是无效url，如果是则跳过
        if link['href'].startswith('javascript:') or link['href'].startswith('Javascript:') or link['href'].startswith('javascri6pt:') or link['href'].startswith('mail') or link['href'].startswith('#') or link['href'].startswith('..'):
            continue

        # 判断是否是有效的 URL
        if parsed_url.scheme and parsed_url.netloc:
            # 创建一个字典，存储每个链接的词条和URL
            entry = {
                'title': link.text.strip(),  # 获取链接文本，去除首尾空白
                'url': url,  
            }
            # 将这个字典添加到entries列表中
            entries.append(entry)
            if not entry['url'].startswith('http'):
                print(f"[WARNING] ODD ENTRY ADDED: {entry['url']}")
            # print(f"{len(entries)} ENTRYS ADDED")

    # 返回包含词条和链接信息的列表
    return entries
