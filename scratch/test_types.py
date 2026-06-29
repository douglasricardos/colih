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

session.post(
    'https://salvador.colih.med.br/auth/login',
    data={'_token': csrf_token, 'username': COLIH_USER, 'password': COLIH_PASS},
    headers={'Referer': 'https://salvador.colih.med.br/auth/login'},
    allow_redirects=True, timeout=30, verify=False
)

mem_url_all = 'https://salvador.colih.med.br/panel/users/export?type=xls&region=12&isMultipleRegions=1&moreFilters=0&name=&sortOrder=nm'
mem_resp_all = session.get(mem_url_all, verify=False)
with open('scratch/mem_all.xlsx', 'wb') as f: f.write(mem_resp_all.content)

try:
    df_all = pd.read_excel('scratch/mem_all.xlsx')
    print("All members (tipo omitted):", len(df_all))
    print(df_all.head())
except Exception as e:
    print("All failed:", e)

mem_url_tipo2 = 'https://salvador.colih.med.br/panel/users/export?type=xls&region=12&isMultipleRegions=1&moreFilters=0&name=&tipo=2&sortOrder=nm'
mem_resp_2 = session.get(mem_url_tipo2, verify=False)
with open('scratch/mem_tipo2.xlsx', 'wb') as f: f.write(mem_resp_2.content)

try:
    df_2 = pd.read_excel('scratch/mem_tipo2.xlsx')
    print("Tipo 2 members:", len(df_2))
except Exception as e:
    print("Tipo 2 failed:", e)
