import os 
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.federalreserve.gov"
SPEECH_URL = 'https://www.federalreserve.gov/newsevents/speeches.htm'

