# -*- coding: utf-8 -*-

import json
import random
import time
import datetime
import requests
from loguru import logger
from lxml import etree
import re

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
    # # Prevent requests from being too fast
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
    with open(f"D:\*\*\*\{filename}", "wb") as f:
        f.write(image)

base_url = '*'
content_base_url = '*'
entry_base_url = '*'
entry_dynamic_base_url = '*'
image_base = "*"

strokes = [*]

flags = [*]

amounts = [*]


refer = '*'


def crawl():
    image_id = 0
    for stroke, flag, amount in zip(strokes, flags, amounts):
        # Heading to the pages sorted by strokes
            url = base_url.format(flag, stroke)
            res = httget(url)
            if res.status_code == 200:
                logger.info(f"get {stroke}")
                for i in range(0, amount, 20):
                    content_url = content_base_url.format(flag, i)
                    res_itemcode = httget(content_url)
                    if res_itemcode.status_code == 200:
                        words = re.findall('"itemtitle":"(.*?)"', res_itemcode.text)
                        for word in words:
                            entry_url = entry_base_url.format(word)
                            res_entry = httget(entry_url)
                            img = etree.HTML(res_entry.text)
                            img_url_base = "".join(img.xpath("//img/@src")).strip()
                            img_url = ""
                            if len(img_url_base) != 0:
                                try:
                                    img_url = re.findall('\"/CRFDPIC/(.*?)(\\\)"/', img_url_base)[0][0]
                                except Exception as e:
                                    logger.error(e)
                            interpretations = re.findall('"annotations":"(.*?)"', res_entry.text)
                            sources = re.findall('"booktitle":"(.*?)"', res_entry.text)
                            bookids = re.findall('"bookid":"(.*?)"',res_entry.text)
                            entryids = re.findall('"id":"(.*?)"', res_entry.text)
                            for source, interpretation, bookid, entryid in zip(sources, interpretations, bookids, entryids):
                                data={}
                                data["word"] = word
                                data["interpretation"] = interpretation
                                data["source"] = source
                                data["image_url"] = ""
                                data["image_id"] = ""
                                if len(img_url) != 0:
                                    image_id += 1
                                    image = image_base.format(img_url)
                                    try:
                                        image_format = re.findall('\..{3}$',image)[0]
                                    except Exception as e:
                                        logger.error(e)
                                    data["image_url"] = image
                                    data["image_id"] = image_id
                                    image_name = f"{image_id}{image_format}"
                                    saveimage(httget(image).content, image_name)
                                    logger.info(f"image{image_id} downloaded")
                                data["url"] = entry_dynamic_base_url.format(entryid, bookid)
                                data["crawledTime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                savedata(data)
                                logger.info(f"{word} saved")
                    else:
                        break
            else:
                break


crawl()
