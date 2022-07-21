# -*- coding: utf-8 -*-
import ast
import asyncio
import json
import queue
import random
import time
import datetime
import requests
# from loguru import logger
from loguru import logger
import re

from lxml.html import html5parser, tostring
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

requests.packages.urllib3.disable_warnings()

headers = {
    'authority': '*',
    'user-agent': '*',
    'accept': '*',
    'referer': '*',
    'accept-language': '*'
}
# proxy

proxyHost = "*"
proxyPort = "*"

# Proxy tunnel authentication information
proxyUser = "*"
proxyPass = "*"

proxyServer = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
}
proxies = {
    "http": proxyServer,
    "https": proxyServer,
}


def httget(url):
    # Prevent requests from being too fast
    # time.sleep(random.randint(3, 5))
    for i in range(10):
        try:
            body = requests.get(url=url, headers=headers, timeout=60, verify=False, proxies=proxies)
            body.encoding = "utf-8"
            if body.status_code == 200 or body.status_code == 404:
                return body
            else:
                logger.error(f"status_code {body.status_code}")
                time.sleep(random.randint(3, 5))
        except Exception as e:
            logger.error(e)
            time.sleep(2)
    return None


def savedata(data):
    with open("*.json", "a+", encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False))
        f.write("\n")


def saveimage(image, filename):
    with open(f"D:\*\*\*\{filename}.jpg", "wb") as f:
        f.write(image)

F = open('test.txt', encoding='utf-8')
total = 67104
num = 0

url_base = "*"
img_base = "*"
js = "let ele = document.evaluate(\"//a[@data-value='Img_Count|1']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;dropList.handleItemclick(ele);"
opt = webdriver.FirefoxOptions()
opt.headless = True
browser = webdriver.Firefox(proxy=proxies, options=opt)
image_id = 0
for key_init in F:
    key = key_init.replace("\n", "")
    num += 1
    url = url_base.format(key)
    browser.get(url=url)
    browser.execute_script(js)
    logger.info(f"{key} crawling {num}/{total}")
    # need time to execute Javascript
    time.sleep(6)
    text = browser.page_source.replace("\u2002", "").replace(" ", "")
    # Convert multiple lines of text to single line. It is easier to use re to match required fields. 
    with open('*.txt', 'w', encoding='utf-8') as f:
        f.write(text)
        f.close()
    with open('*.txt', encoding='utf-8') as f:
        t = f.readlines()
        f.close()
    text1 = ''
    for line in t:
        text1 += line.rstrip()
    word = key
    img_url = []
    b = 0
    img_url_init = re.findall("<li><imgsrc=\"/CRFDPIC/(.*?)\"", text1)
    # Check whether the current keyword has results in required condition
    if len(img_url_init) != 0:
        for x in img_url_init:
            img_url.append(img_base + x)
        img_judge = []
        # There are many cases in which "the number of pictures" field does not match the actual number of pictures shown on the website， 
        # so I have to calculate the amount of pictures by RE
        a = re.findall("<ulclass=\"pic-list\"><li><imgsrc=\"(.*?)</li></ul>", text1)
        for i in range(len(a)):
            a[i] = a[i].replace("</li>", "").replace("<li>", "").replace(">", "").replace("<imgsrc=\"", "")
        for i in a:
            img_judge.append(i.count("\"/") + 1)
        source_init = re.findall(".html\">(.*)</a>\.(.*)\.(\d{1,4})", text)
        source = []
        for a in img_judge:
            b += int(a)
        if True: # Meaningless，
            # dealing with conditions that multiple pictures derive from same sources. 
            for (i, j, k), num in zip(source_init, img_judge):
                for _ in range(int(num)):
                        source.append(i+"."+j+"."+k)
            # Save
            for i in range(len(img_url)):
                image_id += 1
                data = {}
                data['image_id'] = image_id
                data['word'] = word
                data['source'] = source[i]
                data['url'] = img_url[i]
                data['crawl_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                savedata(data)
                logger.info(f"{word}-{image_id} saved")
                saveimage(httget(data['url']).content, data['image_id'])
                logger.info(f"image{image_id} saved")
    else:
        continue
