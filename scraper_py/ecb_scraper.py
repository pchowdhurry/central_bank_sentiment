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
BULLETIN_URL = 'https://www.ecb.europa.eu/press/economic-bulletin/articles/html/index.en.html'

class ECB_Scraper : 
    def __init__(self, years: List[int], scroll_num=None):
        self.base_url = "https://www.ecb.europa.eu"
        self.speech_url = SPEECH_URL
        self.years = years
        self.driver = None 
        self.curr_page = 0 
        self.scroll_num = scroll_num 
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def __get_speech_page(self, scroll_num = None, link = None):
        if not self.driver: 
            self.driver = Chrome()
        url = self.speech_url 
        if link != None : 
            url = link 
        try: 
            self.driver.get(url)
            wait  = WebDriverWait(self.driver, 30)
            if link == BULLETIN_URL:
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.lazy-load.loaded")))
            else : 
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.title > a")))
            time.sleep(5)
            prev_height = self.driver.execute_script("return document.body.scrollHeight")
            prev_count = 0
            i = 0 
            if not scroll_num : 
                while True : 
                    self.driver.execute_script("window.scrollBy(0, 1500);")
                    time.sleep(5)
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    # if we are done scrolling to the end fo the page 
                    curr_count = len(self.driver.find_elements(By.CSS_SELECTOR, "div.lazy-load.loaded"))
                    print(f"Scroll {i+1}: {curr_count} containers loaded")
                    if prev_height==new_height: 
                        break 
                    else : 
                        prev_height = new_height 
                        self.curr_page += 1 
                return self.driver.page_source 
            elif scroll_num>0:
                for i in range(scroll_num):
                    self.driver.execute_script("window.scrollBy(0, 1500);")
                    time.sleep(5)
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    curr_count = len(self.driver.find_elements(By.CSS_SELECTOR, "div.lazy-load.loaded"))
                    print(f"Scroll {i+1}: {curr_count} containers loaded")
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
            speeches[title] = urljoin(self.base_url, href) 
        return speeches 

    def thread_parse(self, link: str) -> tuple:
        """Parse a single speech page."""
        # Skip PDFs
        if link.endswith('.pdf'):
            return None, None
            
        try:
            req = requests.get(link, headers=self.headers)
            if req.status_code != 200:
                print(f'Failed to get page for {link}: status code {req.status_code}')
                return None, None
                
            soup = BeautifulSoup(req.text, 'lxml')
            
            # Extract date from URL
            date_match = re.search(r'/date/(\d{4})/', link)
            if not date_match:
                # Find the main content
                date_match = re.search(r'/articles/(\d{4})/', link)
                date = date_match.group(1)
                print(date)
                content = ""
                
                # Try different content selectors
                section = soup.select('div.section > p')
                print(section)
                
            
                for text in section:
                    content += text.get_text(strip=True)
                return  date, content
            else: 
                
                date = date_match.group(1)
                
                # Find the main content
                content = ""
                
                # Try different content selectors
                section = soup.select('div.section > p')
                print(section)
                
            
                for text in section:
                    content += text.get_text(strip=True)
                return date, content
            
        except Exception as e:
            print(f'Error parsing {link}: {str(e)}')
            return None, None

    def get_speech_text(self, links: dict, num_workers: int = 4) -> dict:
        """Get text content from speech links using multiple threads."""
        results = {}
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for title, url in links.items():
                futures.append(executor.submit(self.thread_parse, url))
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Scraper Results"):
                date, content = future.result()
                if date and content:
                    if date not in results:
                        results[date] = [content]
                    else : 
                        results[date].append(content)
        
        return results
    
    def get_econ_bulletin_links(self, years: List[int]): 
        link_types = 'https://www.ecb.europa.eu/press/economic-bulletin/articles/{}/html/index_include.en.html'
        all_links = []
        for year in years : 
            link = link_types.format(year)
            all_links.append(link)
            print(link)
        
        links ={}
        
        for url in all_links :
            req = requests.get(url, headers=self.headers)
        
            soup = BeautifulSoup(req.text, 'lxml')
            link_elements = soup.select("div.title")
            print(link_elements[0])

            
            
            for container in link_elements : 
                try:    
                    title = container.text.strip()
                    link = container.select_one("a")["href"]
                  
                    links[title] = urljoin(self.base_url, link)
                    print(urljoin(self.base_url, link))

                except Exception as e: 
                    print(f'Could not find link for speech')
                    continue
        return links 
    
    def get_buletin_texts(self, links): 
        return self.get_speech_text(links)
            
        




