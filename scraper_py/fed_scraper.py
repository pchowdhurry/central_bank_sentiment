import os 
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re as re 
import threading 
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from tqdm import tqdm

# Base URLs for Federal Reserve website
BASE_URL = "https://www.federalreserve.gov"
SPEECH_URL = "https://www.federalreserve.gov/newsevents/speeches.htm"
MPR_URL = 'https://www.federalreserve.gov/monetarypolicy/publications/mpr_default.htm'

class FedScraper:
    """
    Class that is used to scrape speech texts from the website of the U.S Federal 
    Reserve on a year-by-year basis. Can be used to extract text of speeches by year 
    along with the dates of speeches. Can be used to ouput those speeches into 
    txt file.
    """

    def __init__(self, years:List[int]):
        """
        Initialize the scraper with specific years to scrape.
        
        Args:
            years (List[int]): List of years to scrape speeches for
        """
        self.base_url = BASE_URL
        self.speech_url = SPEECH_URL
        self.years = years 
    
    def get_link(self):
        """
        Gets links by year from the main speeches page.
        
        Returns:
            List[str]: List of URLs for yearly speech pages
        """
        req = requests.get(self.speech_url) 
        soup = BeautifulSoup(req.text, 'lxml')
        year_links = [
            urljoin(BASE_URL, a["href"])
            for a in soup.find_all("a", href=True)
            if re.fullmatch(r"/newsevents/speech/\d{4}-speeches\.htm", a["href"])]

        final_links = [urljoin(BASE_URL, link) for link in year_links]
        return final_links
    
    def get_speech_links(self):
        """
        Gets all individual speech links for each year.
        
        Returns:
            dict: Dictionary with years as keys and lists of speech URLs as values
        """
        master_links = {}
        for link in self.get_link(): 
            req = requests.get(link)
            soup = BeautifulSoup(req.text, 'lxml')

            # Extract year from the URL
            year = int(re.search(r"(\d{4})-speeches", link).group(1))
            # Find all speech event elements
            hdr = soup.find_all(class_='col-xs-9 col-md-10 eventlist__event')
            if not hdr:
                continue 
            sublink = []

            # Extract individual speech links
            for el in hdr:
                link_tag = el.find('a', href=True)
                link = link_tag['href']
                url = urljoin(BASE_URL, link)
                sublink.append(url)
                
            master_links[year] = sublink
        return master_links
    
    def thread_parse(self, link: str) -> str:
        """
        Parse a single speech page to extract its content.
        
        Args:
            link (str): URL of the speech to parse
            
        Returns:
            str: Formatted speech text with date, or empty string if parsing fails
        """
        try:
            req = requests.get(link)
            soup = BeautifulSoup(req.text, 'lxml')
            # Find main content and date
            text_tag = soup.find(class_='col-xs-12 col-sm-8 col-md-8')
            date_tag = soup.find('p', class_='article__time')
            date = date_tag.get_text(strip=True)
            print(date)
            text = text_tag.find_all('p')
            speech: str = date + "\n"
            for para in text:
                speech += para.get_text(strip=True)
            return speech  
            
        except AttributeError:
            return ""

    def get_speech_texts(self, workers: int):
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
        master_dict = self.get_speech_links()
        shortlist = {}
        count = 0 
        # Filter links for requested years
        for val in self.years: 
            links = master_dict[val]
            if not links: 
                print(f'Could not find links for year {val}')
                return 0
            else: 
                shortlist[val] = links 
        
        # Process speeches in parallel
        master_results = {}
        for year, links in shortlist.items():
            result = [None] * len(links)
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(self.thread_parse, link):i 
                          for i, link in enumerate(links)}

                for future in tqdm(as_completed(futures), 
                                 total=len(futures), 
                                 desc="Scraper Results"):
                    index = futures[future]
                    try:
                        result[index] = future.result()
                    except Exception as e:
                        print(f'Error with link: {links[index]}: {e}')
                        result[index] = "" 
            
            master_results[year] = result
        return master_results
    
    def __write_helper(self, file_name, speeches):
        """
        Helper method to write speeches to a file.
        
        Args:
            file_name (str): Name of the file to write to
            speeches (List[str]): List of speeches to write
        """
        with open(file_name, 'w', encoding='utf-8') as file:
            for speech in speeches:
                file.write(speech + "\n")

    def write_to_file(self, speech_dict: dict, num_workers):
        """
        Write all speeches to separate files by year.
        
        Args:
            speech_dict (dict): Dictionary of speeches by year
            num_workers (int): Number of worker threads to use
        """
        titles = []
        year_speech = []
        for year, speeches in speech_dict.items():
            titles.append(f'{year}_fed_speeches.txt')
            year_speech.append(speeches)
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor: 
            executor.map(self.__write_helper, titles, year_speech)

    def get_policy_report_links(self):
        """
        Get links to Monetary Policy Reports and testimonies.
        
        Returns:
            tuple: (List of MPR links, List of testimony links)
        """
        mpr_report = []
        testimony_links = []
        request = requests.get(MPR_URL)
        soup = BeautifulSoup(request.text, 'lxml')
        
        # Find all links and categorize them
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/newsevents/testimony'):
                testimony_links.append(urljoin(BASE_URL, href))
            elif href.startswith('/monetarypolicy'):
                mpr_report.append(urljoin(BASE_URL, href))
        
        return mpr_report, testimony_links

    def get_policy_texts(self):
        """
        Extract text from Monetary Policy Reports and testimonies.
        
        Returns:
            tuple: (Dictionary of testimonies by date, Dictionary of MPR texts by date)
        """
        mpr_links, testimony_links = self.get_policy_report_links()
        all_testimony = {}
        mpr_texts = {}
        
        # Process testimonies
        for link in testimony_links:
            try:
                request = requests.get(link)
                soup = BeautifulSoup(request.text, 'lxml')
                
                # Find date - using select_one for more reliable selection
                date_tag = soup.select_one('p.article__time')
                if not date_tag:
                    print(f"No date found for {link}")
                    continue
                    
                date = date_tag.get_text(strip=True)
                print(f"Processing testimony from {date}")
                
                # Find content - using select for more reliable selection
                content_div = soup.select_one('div.col-xs-12.col-sm-8.col-md-8')
                if not content_div:
                    print(f"No content found for {link}")
                    continue
                    
                # Get all paragraphs from the content
                paras = content_div.select('p')
                testimony = '\n'.join(p.get_text(strip=True) for p in paras)
                
                if testimony:
                    all_testimony[date] = testimony
                
            except Exception as e:
                print(f"Error processing testimony {link}: {str(e)}")
                continue
        
        # Process MPR reports
        for link in mpr_links:
            try:
                request = requests.get(link)
                soup = BeautifulSoup(request.text, 'lxml')
                
                # Find navigation links
                nav_div = soup.select_one('div.t4_nav.list-group.sticky#t4_nav')
                if nav_div:
                    links = nav_div.select('a[href]')
                    
                    for url in links:
                        href = url['href']
                        new_url = urljoin(BASE_URL, href)
                        req = requests.get(new_url)
                        sub_soup = BeautifulSoup(req.text, 'lxml')
                        
                        expression = re.fullmatch(r"https://www\.federalreserve\.gov/monetarypolicy/(\d{4})-(\d{2})-mpr-[\w\-]+\.htm", new_url)
                        if not expression : 
                            print(f'error : {new_url}')
                        if expression : 
                            year = expression.group(1)
                            month = expression.group(2)
                            date = f'{year}-{month}'
                        
                            content_div = sub_soup.select_one('div.col-xs-12.col-md-9')
                            if not content_div:
                                continue
                                
                            paras = content_div.select('p')
                            text = '\n'.join(p.get_text(strip=True) for p in paras)
                            print(text)
                            
                            if text:
                                mpr_texts[date] = text
                        
            except Exception as e:
                print(f"Error processing MPR {link}: {str(e)}")
                continue
            
        return all_testimony, mpr_texts
            

            