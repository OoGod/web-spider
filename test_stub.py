# -*- coding: utf-8 -*-
import os
import requests
import time
from lxml import html


def parse_url(url, port=7890, referer=None):
    headers = {
        "headers" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36", 
        "Referer": referer
    }
    proxy = '127.0.0.1:%s' % port
    response = requests.get(url, headers = headers, proxies={"http": "http://{}".format(proxy)})
    return response
