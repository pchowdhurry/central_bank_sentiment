import os
import sys 
import numpy as np 
import pandas as pd 
from pathlib import Path 
import pickle 
from typing import List, Dict, Any

# current file 
current = Path(__file__).resolve()
#parent directory 
root = current.parent.parent
# creating import path 
print(root)
sys.path.append(str(root))

from scraper_py.fed_scraper import FedScraper

# TODO: Specify years for collecting speeches
collection_years = [int(i) for i in range(2025)]

def collect_speech_text(years:List[int], write_to_file:bool =False, workers: int = 4) -> dict:
    scraper = FedScraper(years)
    speech_dict = scraper.get_speech_texts(workers= workers)
    data = []
    for year, speech in speech_dict.items():
          for text in speech: 
                data.append((year, text))
    speech_df = pd.DataFrame(data=data)
    
    if write_to_file == True:
            file_name = f"data/{years[0]}-{years[-1]}_speeches.pkl"
            with open(file_name, 'wb') as file:
                  pickle.dump(speech_df, file)
            return speech_df
    elif write_to_file == False:
          return speech_dict


def collect_policy_reports(years: List[int], write_to_file: bool = False) -> dict:
      scraper = FedScraper(years)
      testimony, reports = scraper.get_policy_texts()

      # Initialize empty lists for both types of data
      report_data = []
      testimony_data = []

      # Handle testimony data - checking if it's a list of tuples
      if testimony:  # Check if testimony is not empty
            for year, words in testimony:
                  for report in words:
                        testimony_data.append((year, report))

      # Handle reports data
      if reports:  # Check if reports is not empty
            for year, report_list in reports.items():
                  for report in report_list:
                        report_data.append((year, report))

      # Create DataFrames with column names
      report_df = pd.DataFrame(data=report_data, columns=['year', 'text'])
      testimony_df = pd.DataFrame(data=testimony_data, columns=['year', 'text'])

      if write_to_file:
            # Create data directory if it doesn't exist
            data_dir = Path("data")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Save reports
            report_file = data_dir / f"{years[0]}-{years[-1]}_reports.pkl"
            with open(report_file, 'wb') as file:
                  pickle.dump(report_df, file)
            
            # Save testimony
            testimony_file = data_dir / f"{years[0]}-{years[-1]}_testimony.pkl"
            with open(testimony_file, 'wb') as file:
                  pickle.dump(testimony_df, file)
            
            return testimony_df, report_df
      else:
            return testimony_df, report_df


if __name__ == '__main__':
      testimony_df, report_df = collect_policy_reports(collection_years, True)
      speeches = collect_speech_text(collection_years, True, 8)
      
      print("Speeches shape:", speeches.shape)
      print("Testimony shape:", testimony_df.shape)
      print("Reports shape:", report_df.shape)
      


        
