import os 
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re as re 
import threading 
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver import Chrome 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
SPEECH_URL = "https://www.ecb.europa.eu/press/pubbydate/html/index.en.html?name_of_publication=Speech"


class ECB_Scraper : 
    def __init__(self, years: List[int], scroll_num=None):
        self.base_url = "https://www.ecb.europa.eu"
        self.speech_url = SPEECH_URL
        self.years = years
        self.driver = None 
        self.curr_page = 0 
        self.scroll_num = scroll_num 

    def __get_speech_page(self, scroll_num = None):
        if not self.driver: 
            self.driver = Chrome()
        
        try: 
            self.driver.get(self.speech_url)
            wait  = WebDriverWait(self.driver, 30)
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.title > a")))
            time.sleep(5)
            prev_height = self.driver.execute_script("return document.body.scrollHeight")

            if not scroll_num : 
                while True : 
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    # if we are done scrolling to the end fo the page 
                    if prev_height==new_height: 
                        break 
                    else : 
                        prev_height = new_height 
                        self.curr_page += 1 
                return self.driver.page_source 
            elif scroll_num>0:
                for k in range(scroll_num):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if prev_height==new_height: 
                        break 
                    else : 
                        prev_height = new_height 
                        self.curr_page += 1 
                return self.driver.page_source 
            else : 
                raise ValueError("scroll number must be an integer")
        except Exception as e: 
            print(f'inputted scroll number {scroll_num} is not an integer')
        finally: 
            self.driver.quit()

    def get_speech_links(self ):
        # getting the page source 
        page = self.__get_speech_page(self.scroll_num)
        print(page)
        # will store the links of the speeches along with title
        speeches = {}
        if not page:
            print(f'no page source found for linked page {self.speech_url}')
            return None 
        
        soup = BeautifulSoup(page, 'lxml') 
        links = soup.select('div.title > a')
        for link in links : 
            href = link.get('href')
            title = link.text 
            speeches[title] = href 
        return speeches 


