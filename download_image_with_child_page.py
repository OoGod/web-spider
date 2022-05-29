from lxml import html
import time, os
import test_stub

start_url = 'http://baidu.com/'
host_url = start_url.split('/')
host_url = host_url[0] + '//' + host_url[2] + '/'
download_path = '/home/share/filebrower/test/'

def get_page_urls(start_url):
    response = test_stub.parse_url(start_url, referer=start_url)
    page_urls = []
    page_urls.append(start_url)
    parsed_body = html.fromstring(response.text)
    next_url = parsed_body.xpath('//div[@class="text-center"]//@href')
    print('next_url: ', next_url)
    if not next_url or next_url[-1][-1] > '10':
        return page_urls
    last_page = next_url[-2].split('=')[-1]
    page_info = next_url[-2][:-len(last_page)]
    host_url = start_url.split('/')
    host_url = host_url[0] + '//' + host_url[2] + '/'
    for i in range(2, int(last_page)+1):
        next_url = host_url + page_info + str(i)
        page_urls.append(next_url)
    return page_urls

def get_album_list(page_url):
    response = test_stub.parse_url(page_url, referer=start_url)
    parsed_body = html.fromstring(response.text)
    album_titles = parsed_body.xpath('//div[@class="album-item row"]//h2//text()')
    album_urls = parsed_body.xpath('//div[@class="album-item row"]//div[@class="album-grid"]//a[1]/@href')
    album_urls = [host_url[:-1] + url for url in album_urls]
    if len(album_titles) != len(album_urls):
        print('title and url do not match, xpath rule need to update')
        return None
    album_list  = [{'title': title, 'url': url} for title, url in zip(album_titles, album_urls)]
    return album_list

def parse_image_urls(album_list):
    for album in album_list:
        response = test_stub.parse_url(album['url'], referer=start_url)
        parsed_body = html.fromstring(response.text)
        if not album.get('title'):
            album['title'] = parsed_body.xpath('//div[@class="photos"]//img/@title')[0]
        album['image_urls'] = parsed_body.xpath('//div[@class="photos"]//img/@src | //div[@class="photos"]//img/@delay')
    print("get_imagee_urls done!!!")
    return album_list

def download_images(album_list, path=download_path):
    for album in album_list:
        album_path = path + album['title']
        if not os.path.exists(album_path):
            os.makedirs(album_path)
        #print('image_urls: %s' % album['image_urls'])
        for url in album['image_urls']:
            with open(album_path + '/' + url.split('/')[-1], 'wb') as f:
                image = test_stub.parse_url(url, referer=start_url)
                f.write(image.content)
        print('title: %s, %s pics downloaded' % (album['title'], len(album['image_urls'])))

def test():
    page_urls = get_page_urls(start_url)
    start_time = time.time()
    for page_url in page_urls:
        print('page_url: %s' % page_url)
        album_list = get_album_list(page_url)
        album_list = parse_image_urls(album_list)
        print("album number: %s" % len(album_list))
        download_images(album_list)
        elapsed_time = time.time() - start_time
        print("elasped %s seconds" % elapsed_time)

test()
