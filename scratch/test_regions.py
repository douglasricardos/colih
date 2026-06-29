import os, tempfile
from pathlib import Path
import pandas as pd
import requests
import re
import urllib3
urllib3.disable_warnings()
from dotenv import load_dotenv

load_dotenv('backend/.env')
COLIH_USER = os.getenv('COLIH_USER')
COLIH_PASS = os.getenv('COLIH_PASS')

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})
resp = session.get('https://salvador.colih.med.br', timeout=30, verify=False)
csrf = re.search(r'name="_token"[^>]+value="([^"]+)"', resp.text)
if not csrf: csrf = re.search(r'name="csrf-token" content="([^"]+)"', resp.text)
csrf_token = csrf.group(1)

login_resp = session.post(
    'https://salvador.colih.med.br/auth/login',
    data={'_token': csrf_token, 'username': COLIH_USER, 'password': COLIH_PASS},
    headers={'Referer': 'https://salvador.colih.med.br/auth/login'},
    allow_redirects=True, timeout=30, verify=False
)

mem_url_1 = 'https://salvador.colih.med.br/panel/users/export?type=xls&region=1&isMultipleRegions=1&moreFilters=0&name=&tipo=1&sortOrder=nm'
mem_resp_1 = session.get(mem_url_1, verify=False)

mem_url_12 = 'https://salvador.colih.med.br/panel/users/export?type=xls&region=12&isMultipleRegions=1&moreFilters=0&name=&tipo=1&sortOrder=nm'
mem_resp_12 = session.get(mem_url_12, verify=False)

with open('scratch/mem1.xlsx', 'wb') as f: f.write(mem_resp_1.content)
with open('scratch/mem12.xlsx', 'wb') as f: f.write(mem_resp_12.content)

try:
    df1 = pd.read_excel('scratch/mem1.xlsx')
    print("Region 1 members:", len(df1))
except Exception as e:
    print("Region 1 failed:", e)

try:
    df12 = pd.read_excel('scratch/mem12.xlsx')
    print("Region 12 members:", len(df12))
except Exception as e:
    print("Region 12 failed:", e)
