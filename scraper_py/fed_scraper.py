import os 
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re as re 
import threading 
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from tqdm import tqdm
BASE_URL = "https://www.federalreserve.gov"
SPEECH_URL = "https://www.federalreserve.gov/newsevents/speeches.htm"

class Speech_Scraper:
    """
    Class that is used to scrape speech texts from the website of the U.S Federal 
    Reserve on a year-by-year basis. Can be used to extract text of speeches by year 
    along with the dates of speeches. Can be used to ouput those speeches into 
    txt file.
    """

    def __init__(self, years:List[int]):
        self.base_url = BASE_URL
        self.speech_url = SPEECH_URL
        self.years = years 
    

    def __get_link(self):
        """
        Gets links by year
        """
        req = requests.get(self.speech_url) 
        soup = BeautifulSoup(req.text, 'lxml')
        year_links = [
        urljoin(BASE_URL, a["href"])
        for a in soup.find_all("a", href=True)
        if re.fullmatch(r"/newsevents/speech/\d{4}-speeches\.htm", a["href"])]

        final_links = [urljoin(BASE_URL, link) for link in year_links ]

        return final_links
    
    def __get_speech_links(self):
        master_links = {}
        for link in self.__get_link(): 
            req = requests.get(link)
            soup = BeautifulSoup(req.text, 'lxml')

            year = int(re.search(r"(\d{4})-speeches", link).group(1))
            hdr = soup.find(class_ ='col-xs-9 col-md-10 eventlist__event')
            if not hdr:
                continue 
            i +=1 

            link_tags = hdr.find_all('a', href=True)
            sublink = []
            for el in link_tags:
                link = el['href']
                url = urljoin(BASE_URL, link)
                sublink.append(url)
            master_links[year] = sublink
        return master_links
    
    def thread_parse(self, link :str) -> str:
        try:
            req = requests.get(link)
            soup = BeautifulSoup(req.text, 'lxml')
            text_tag = soup.find(class_ = 'col-xs-12 col-sm-8 col-md-8')
            date_tag = soup.find('p', class_= 'article__time')
            date = date_tag.get_text(strip=True)
            print(date)
            text = text_tag.find_all('p')
            speech:str = ''
            for para in text:
                speech += para.get_text(strip=True)
            return speech  
            
        except AttributeError:
            return ""
        

        
    def parse_year_speeches(self, years: List[int], workers:int) :
        """ 
        Function that returns the text of speeches by year and saves them 
        to a text file. 
      
        Args : 
        years: List of years as integers for whom we want to scrape speeches for 
        file_name : the name of the txt file that will store the text of the speeches 
        workers : number of threads active 
        Returns: 
        int : The number of files that were parsed. 0 if there was an error
        """
        
        master_dict = self.__get_speech_links()
        # getting the links by year 
        shortlist = {}
        count = 0 
        for val in years : 
            links  = master_dict[val]
            if links == None : 
                print(f'Could not find links for year {val}')
                return 0
            else : 
                shortlist[val] = links 
        master_results = {}
        for year, links in enumerate(shortlist):
            result = [None] * len(links)
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(self.thread_parse, link):i for i, link in enumerate(links)}

                for future in tqdm(as_completed(futures), total = len(futures), desc="Scraper Results"):
                    index = futures[future]
                
                    try:
                        result[index] = future.result()
                    except Exception as e :
                        print(f'Error with link: {links[index]}: {e}')
                        result[index] = "" 
            
            master_results[year] = result
        return master_results



