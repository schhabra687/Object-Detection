#pip install selenium - in conda prompt
from selenium import webdriver
import time
import argparse
import itertools
import logging
import os
import uuid
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup


def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('[%(asctime)s %(levelname)s %(module)s]: %(message)s'))
    logger.addHandler(handler)
    return logger

logger = configure_logging()

REQUEST_HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}


def get_soup(url, header):
    response = urlopen(Request(url, headers=header))
    return BeautifulSoup(response, 'html.parser')

def get_query_url(query):
    return "https://duckduckgo.com/?q=%s&va=z&t=hk&iax=images&ia=images" % query

def extract_images_from_soup(soup,query):
    extensions = {"jpg","jpeg","keys"}
    #install chromedriver.exe - https://chromedriver.chromium.org/downloads
    driver = webdriver.Chrome('chromedriver.exe')
    driver.get(get_query_url(query))
    html = driver.page_source.split('["')
    #to debug html code
    with open("sample4.txt", "w", encoding="utf-8") as f:
        f.write("stark".join(html))
    #debug - end
    #print(html)
    img_count = 1
    imges = []
    while img_count < 2: #this counter for number of scrolls
        img_count = img_count+1
        for i in html:
            if i.startswith('http'): #and i.split('"')[0].split('.')[-1] in extensions:
                imges.append(i.split('"')[0])
        time.sleep(3) #wait for 3 seconds
        driver.execute_script("window.scrollTo(0, window.scrollY + 500)")
    print(imges)
    #return imges

def extract_images(query, num_images):
    url = get_query_url(query)
    logger.info("Souping")
    soup = get_soup(url, REQUEST_HEADER)
    logger.info("Extracting image urls")
    link_type_records = extract_images_from_soup(soup,query)
    return itertools.islice(link_type_records, num_images)

def get_raw_image(url):
    req = Request(url, headers=REQUEST_HEADER)
    resp = urlopen(req)
    return resp.read()

def save_image(raw_image, image_type, save_directory):
    file_name = uuid.uuid4().hex
    save_path = os.path.join(save_directory, file_name)
    save_path = save_path + '.jpg'
    with open(save_path, 'wb') as image_file:
        image_file.write(raw_image)

def download_images_to_dir(images, save_directory, num_images):
    for i, (url) in enumerate(images):
        try:
            logger.info("Making request (%d/%d): %s", i, num_images, url)
            raw_image = get_raw_image(url)
            image_type = 'jpg'
            save_image(raw_image, image_type, save_directory)
        except Exception as e:
            logger.exception(e)

def run(query, save_directory, num_images=100):
    query = '+'.join(query.split())
    logger.info("Extracting image links")
    images = extract_images(query, num_images)
    logger.info("Downloading images")
    download_images_to_dir(images, save_directory, num_images)
    logger.info("Finished")

def main():
    parser = argparse.ArgumentParser(description='Scrape Google images')
    parser.add_argument('-s', '--search', default='keys', type=str, help='search term')
    parser.add_argument('-n', '--num_images', default=100, type=int, help='num images to save')
    parser.add_argument('-d', '--directory', default='E:/Images', type=str, help='save directory')
    args = parser.parse_args()
    run(args.search, args.directory, args.num_images)
    
if __name__ == '__main__':
    main()


