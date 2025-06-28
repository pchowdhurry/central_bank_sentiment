import os 
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re as re 
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any 
from tqdm import tqdm 
import time 

json_address = 'https://www.bis.org/api/document_lists/cbspeeches.json'

class ScrapeBIS: 
    def __init__(self, workers=4, dir="bis_data", use_codes={22, 24}):
        self.json_link = json_address
        self.use_codes = use_codes
        self.base_link = 'https://www.bis.org/' 
        self.num_workers = workers 
        
        # Set up directory
        curr_dir = os.getcwd()
        root = os.path.dirname(curr_dir)
        self.dir = os.path.join(root, 'data', dir)
        
        # Create directory if it doesn't exist
        os.makedirs(self.dir, exist_ok=True)
        print(f"Download directory: {self.dir}")
        
    
    def collect_links(self):
        req = requests.get(json_address)
        data = req.json()
        
        # The data is nested under "list" key
        if 'list' not in data:
            print("Error: 'list' key not found in JSON response")
            return []
            
        list_data = data['list']
        total_docs = []
        
        for path, info in list_data.items():
            # Check if info is not None and has required fields
            if info is not None and isinstance(info, dict):
                # Check if this document has the institutions we want
                institutions = info.get('institutions', [])
                if self.use_codes.intersection(institutions):
                    total_docs.append({
                        'title': info.get('short_title', 'Untitled'),
                        "date": info.get("publication_start_date", "no_date"),
                        "url": self.base_link + path + '.pdf',
                        "inst_ids": institutions,
                        "path": path
                    })
        
        print(f"Found {len(total_docs)} documents matching institution codes {self.use_codes}")
        return total_docs
    
    def __pdf_download_helper(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Downloading a single pdf given a doc that includes the link"""
        try: 
            time.sleep(0.2)
            req = requests.get(doc['url'], timeout=10)
            req.raise_for_status()

            title = doc['title'] or 'none'
            date = doc['date'] or 'no_date'
            
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
            safe_title = safe_title[:100] 
            file_name = f'{safe_title}-{date}.pdf'
            file_path = os.path.join(self.dir, file_name)
            
            with open(file_path, 'wb') as file: 
                file.write(req.content)
            
            return {
                **doc,
                'file_name': file_name,
                'file_path': file_path,
                'size_bytes': len(req.content),
                'status': 'success'
            }
        except Exception as e: 
            return {
                **doc,
                'file_name': '',
                'file_path': '',
                'size_bytes': 0,
                'status': f'error: {str(e)}'
            }

    def download_pdfs(self):
        """Download all PDFs using threading"""
        links = self.collect_links()
        if not links:
            print("No documents found to download!")
            return []
            
        print(f'Found {len(links)} files to download')
        result = []
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as pool: 
            future_doc = {
                pool.submit(self.__pdf_download_helper, doc): doc for doc in links 
            }
            
            with tqdm(total=len(links), desc='Download PDFs') as progress: 
                for future in as_completed(future_doc):
                    curr_result = future.result()
                    result.append(curr_result)
                    progress.update(1)
                    
                    num_success = sum(1 for r in result if r['status'] == 'success')
                    progress.set_description(f'Downloaded: {num_success}/{len(result)}')
        
        return result
                
                    
if __name__ == "__main__":
    scraper = ScrapeBIS(workers=4)
    results = scraper.download_pdfs()
    
    # Print summary
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"\nDownloaded {successful}/{len(results)} PDFs successfully")

    
            
    


                
                

