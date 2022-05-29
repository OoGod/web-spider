from lxml import html
import time, os
import re
import test_stub
import threading
from tld import get_tld

start_url = 'http://baidu.com/'
host_url = start_url.split('/')
host_url = host_url[0] + '//' + host_url[2] + '/'
download_path = '/home/share/filebrower/test2/'

def get_page_list(page):
    response = test_stub.parse_url(page['url'], referer=page['url'])
    parsed_body = html.fromstring(response.text)
    if page.get('title'):
        page_info = parsed_body.xpath('//dd[@class="page"]//@href')[-1].split('.')[0]
        page_number = page_info.split('_')[-1]
        page_urls = [page['url'] + page_info[:-len(page_number)] + str(i) + '.html' for i in range(2, int(page_number)+1)]
    else:
        page_urls = parsed_body.xpath('//div[@class="main"]//li[@class="column-title public-title"]//@href')
    if not page.get('title'):
        page_titles = parsed_body.xpath('//div[@class="main"]//li[@class="column-title public-title"]/span/text()')
    else:
        page_titles = [page['title'] for i in range(len(page_urls))]
    if len(page_titles) != len(page_urls):
        print('title and url do not match, xpath rule need to update')
    page_list  = [{'title': title, 'url': url} for title, url in zip(page_titles, page_urls)]
    print('if have page title, it has been classified, that is, it is subpage')
    if page.get('title'):
        print('page_list: ', len(page_list))
        page_list = [page] + page_list
        print('page_list: ', len(page_list))
    return page_list

def get_album_list(page, referer):
    response = test_stub.parse_url(page['url'], referer=referer)
    parsed_body = html.fromstring(response.text)
    album_titles = parsed_body.xpath('//dl[@class="list-left public-box"]//dd[not(@class)]/a/text()')
    album_urls = parsed_body.xpath('//dl[@class="list-left public-box"]//dd[not(@class)]/a/@href')
    if len(album_titles) != len(album_urls):
        print('title and url do not match, xpath rule need to update')
        return None
    album_list  = [{'title': title, 'url': url, 'referer': referer, 'type': page['title']} for title, url in zip(album_titles, album_urls)]
    return album_list

def parse_album_list(album_list):
    def update_album_image(album):
        response = test_stub.parse_url(album['url'], referer=album['referer'])
        parsed_body = html.fromstring(response.text)
        number =  parsed_body.xpath('//span[@class="page-ch"]/text()')[0]
        number = re.findall(r'\d+', number)[0]
        page_info = parsed_body.xpath('//a[@class="page-ch"]/@href')[0].split('_')[0]
        if not album.get('image_main_urls'):
            album['image_main_urls'] = [album['url']]
            album['image_main_urls'].extend([album['referer'] + page_info + '_' + str(i) + '.html' for i in range(2, int(number)+1)]) 
            print("get_image_main_urls done!!! number: %s" % len(album['image_main_urls']))
        else:
            album['image_urls'] = []
            for url in album['image_main_urls']:
                #print('url: %s, referer: %s' % (url, album['referer']))
                response = test_stub.parse_url(url, referer=album['referer']) 
                parsed_body = html.fromstring(response.text)
                album['image_urls'].extend(parsed_body.xpath('//div[@class="content-pic"]//@src'))
            print("get_image_urls done!!! %s " % (len(album['image_urls'])))
    threads = [threading.Thread(target=update_album_image, args=(album,)) for album in album_list]
    [t.start() for t in threads]
    [t.join() for t in threads]
    return album_list

def download_images(album_list, path=download_path):
    def download_imgs(album):
        album_path = path + "/" + album['type'] + "/" + album['title']
        if not os.path.exists(album_path):
            os.makedirs(album_path)
        print('image_urls: %s' % album['image_urls'])
        for url in album['image_urls']:
            with open(album_path + '/' + url.split('/')[-1], 'wb') as f:
                image = test_stub.parse_url(url, referer=start_url)
                f.write(image.content)
        print('title: %s, %s pics downloaded' % (album['title'], len(album['image_urls'])))
    threads = [threading.Thread(target=download_imgs, args=(album,)) for album in album_list]
    [t.start() for t in threads]
    [t.join() for t in threads]

def test():
    page = {'url': start_url}
    pages = get_page_list(page)
    print("web分类: %s" % pages)
    pages = get_page_list(pages[0])
    start_time = time.time()
    def down_album_imgs(album):
        album_list = [album]
        album_list = parse_album_list(album_list)
        album_list = parse_album_list(album_list)
        download_images(album_list)
        
    for page in pages:
        print('page_url: %s' % page['url'])
        print('page_url: %s' % page)
        album_list = get_album_list(page, referer=pages[0]['url'])
        print("album number: %s" % len(album_list))
        threads = [threading.Thread(target=down_album_imgs, args=(album,)) for album in album_list[2:]]
        [t.start() for t in threads]
        [t.join() for t in threads]
        elapsed_time = time.time() - start_time
        print("elasped %s seconds" % elapsed_time)


test()
