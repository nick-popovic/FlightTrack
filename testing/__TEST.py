import json

import requests
from bs4 import BeautifulSoup

from requests_html import HTMLSession

from multiprocessing import Pool as ThreadPool

import re


url = 'https://flightaware.com/live/flight/ACA127/history/20200116/0110Z/CYYZ/CYVR'


session = HTMLSession()
r = session.get(url)
r.html.render(timeout=15, wait=5, retries=10)

soup = BeautifulSoup(r.html.html, 'html.parser')

print(r.html.html)
