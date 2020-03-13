#pip install selenium - in conda prompt
from selenium import webdriver
import os, os.path
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
    return "https://www.google.co.in/search?q=%s&source=lnms&tbm=isch" % query

def extract_images_from_soup(soup,query):
    extensions = {"jpg","jpeg"}
    #install chromedriver.exe - https://chromedriver.chromium.org/downloads
    driver = webdriver.Chrome('chromedriver.exe')
    driver.get(get_query_url(query))
    # to debug html code
    html = driver.page_source.split('["')
    #text_file = open("sample.txt", "w")
    #n = text_file.write("stark".join(html))
    #text_file.close()
    # debug - end
    img_count = 1
    imges = []
    #after n number of attempts - driver page gets stuck at "Show More Images"
    # 1. Manually click on Show More Images tab to load driver content - Works Well
    # 2. Write proper code - To be added later
    while img_count < 15: #this counter for number of scrolls
        img_count = img_count+1
        for i in html:
            if i.startswith('http') and i.split('"')[0].split('.')[-1] in extensions:
                imges.append(i.split('"')[0])
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, window.scrollY + 500)")
        time.sleep(3) #wait for page to load further
    return imges

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

def save_image(raw_image, image_type, save_directory,count):
    file_name = "keys_" + str(count)
    save_path = os.path.join(save_directory, file_name)
    save_path = save_path + '.jpg'
    with open(save_path, 'wb') as image_file:
        image_file.write(raw_image)

def download_images_to_dir(images, save_directory, num_images):
    #check how many files are there in the directory
    num_images_present = (len([name for name in os.listdir(save_directory) if os.path.isfile(os.path.join(save_directory, name))]))
    count = num_images_present + 1 #no need to initalize now at every run
    for i, (url) in enumerate(images):
        count = count+1
        try:
            logger.info("Making request (%d/%d): %s", i, num_images, url)
            raw_image = get_raw_image(url)
            image_type = 'jpg'
            save_image(raw_image, image_type, save_directory,count)
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
    parser.add_argument('-s', '--search', default='door keys', type=str, help='search term')
    parser.add_argument('-n', '--num_images', default=1000, type=int, help='num images to save')
    parser.add_argument('-d', '--directory', default='E:/Images', type=str, help='save directory')
    args = parser.parse_args()
    run(args.search, args.directory, args.num_images)
    
if __name__ == '__main__':
    main()

