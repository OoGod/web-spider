## web-spider

* 可配合搭建文件服务器使用[filebrowser/filebrowser](https://github.com/filebrowser/filebrowser)

### header 
```
def parse_url(url, port=7890, referer=None):
    headers = {
        "headers" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Referer": referer
    }
    ### 填写对应代理地址
    proxy = '127.0.0.1:%s' % port
    response = requests.get(url, headers = headers, proxies={"http": "http://{}".format(proxy)})
    return response
```
- 代理池[jhao104/proxy_pool](https://github.com/jhao104/proxy_pool)

### 当前代码结构
- 根据下一页标识，解析当前页面的所有子页面
- 读取子页面，获取每一页的专辑页面
- 从专辑页面，获取图片的下载链接
- 整体顺序为，
```python
for page in all_page: 
    all_album = [album for album in page]
    [down(image) for album in all_album for image in album]
```

### future
- 将会引入数据库，解析，下载分离
- 引入多线程/多进程/异步等进行下载
- 增加几种规则，提高解析的可用性；引入机器学习，探索页面结构，获取解析规则；
- 增加下载失败重试；已下载自动跳过；
- 增加日志记录并存储
- 图片表结构为
```sql
uuid: 
url: img_url
name: name
album:  
tags: []
refer: host
```
