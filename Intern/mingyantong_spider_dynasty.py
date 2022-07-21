# -*- coding: utf-8 -*-

import json
import random
import time
import datetime
import requests
from loguru import logger
from lxml import etree

requests.packages.urllib3.disable_warnings()
"""
名人名言 按朝代分类
"""
headers = {
    'authority': 'www.mingyantong.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'referer': 'https://www.mingyantong.com/',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'
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
            time.sleep(5)
    return None


def savedata(data):
    with open("dynasty.json", "a+", encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False))
        f.write("\n")


host = "https://www.mingyantong.com"
base_url = "https://www.mingyantong.com/dynasty/{}?page={}"
dynastys = ["先秦", "汉朝", "魏晋", "南北朝", "隋唐五代", "宋朝", "元朝", "明朝", "清朝", "近现代"]


def crawl():
    for dynasty in dynastys:
        # Assuming the number of total page is 1000，If not exist, return 404
        for page in range(0, 1000):
            url = base_url.format(dynasty, page)
            res = httget(url)
            if res.status_code == 200:
                logger.info(f"get {dynasty} page {page}")
                shtml = etree.HTML(res.text)
                # url for every entry
                for href in shtml.xpath("//div[@class='view-content.txt']//div[@class='views-field-name']/a/@href"):
                    if "http" not in href:
                        href = host + href
                    # content
                    for index_page in range(0, 1000):
                        index_url = href + "?page={}".format(index_page)
                        index_res = httget(index_url)
                        if index_res.status_code == 200:
                            logger.info(f"crawl index {page} {dynasty} {index_url}")
                            index_shtml = etree.HTML(index_res.text)
                            path = "-".join(index_shtml.xpath("//div[@id='breadcrumb']//text()")).strip()
                            for one in index_shtml.xpath(
                                    "//div[@class='view-content.txt']//div[@class='views-field-phpcode']"):
                                data = {}
                                content = "".join(one.xpath(".//div[@class='views-field-phpcode-1']//text()")).strip()
                                source = "".join(one.xpath(".//div[@class='xqjulistwafo']//text()")).strip()
                                like = "".join(one.xpath(".//span[@class='flag-action']//text()")).strip()
                                comment = "".join(one.xpath(".//a[@class='comment-link']//text()")).strip()
                                data["path"] = path
                                data["content.txt"] = content
                                data["source"] = source
                                data["like"] = like
                                data["comment"] = comment
                                savedata(data)

                        else:
                            break
            else:
                break


if __name__ == '__main__':
    crawl()
