from lib2to3.pgen2 import driver
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from lxml import etree
from time import sleep

def init_selenium(chromedriver_path="/opt/homebrew/bin/chromedriver"):
    global driver
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)
    return driver

def init_parser():
    """Open main page and check for captcha
    if show captcha wait for user to resolve it"""
    url = "http://yad2.co.il/"
    driver.get(url)
    page_source = driver.page_source
    html = BeautifulSoup(page_source, features="lxml")
    if html.title.text == "ShieldSquare Captcha":
        logging.info("Website request captcha, resolve")
        sleep(120)
        page_source = driver.page_source
    return page_source
    


def get_page_realestate(page_num):
    """Get realestate listing page"""
    url = "https://www.yad2.co.il/realestate/rent?page={page_num}".format(page_num=page_num)
    driver.get(url)
    return driver.page_source

def get_max_page():
    """Get maximum number of pages"""
    url = "https://www.yad2.co.il/realestate/rent"
    driver.get(url)
    html = BeautifulSoup(driver.page_source, features="lxml")
    dom = etree.HTML(str(html))
    max_page = int(dom.xpath("//button[@class='page-num']")[0].text.strip())
    logging.info("Maimum page number: {max_page}".format(max_page=max_page))
    return max_page

def get_all_pages(max_page):
    """Get all pages"""
    for page_num in range(1,max_page):
        out_fn = 'stage/re_pages/{page_num}.html'.format(page_num=page_num)
        logging.info("Get page: {page_num}".format(page_num=page_num))
        if os.path.exists(out_fn):
            cache_file_size = os.path.getsize(out_fn)
            if cache_file_size > 10000:
                logging.info("Found cached verison, skip")
                continue

        page_source = get_page_realestate(page_num)
        with open(out_fn, 'w') as f:
            f.write(page_source)
        sleep(1)