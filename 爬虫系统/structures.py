class WebPage:
    def __init__(self, url, keywords, crawl_datetime, content, storage_location):
        """
        网页的结构化存储
        """
        self.url = url  # 网址
        self.keywords = keywords  # 关键词（这里直接使用<a>标签的文本信息代替）
        self.crawl_datetime = crawl_datetime  # 爬取时间
        self.content = content  # 原url内容
        self.storage_location = storage_location  # 网页存储位置，不太理解这个存储位置是指什么，我的理解是去掉url开头之后在服务器上的资源路径