import requests, re, urllib3
urllib3.disable_warnings()
from dotenv import load_dotenv
import os
load_dotenv('backend/.env')
COLIH_USER = os.getenv('COLIH_USER')
COLIH_PASS = os.getenv('COLIH_PASS')

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})
r=s.get('https://salvador.colih.med.br', verify=False)
c=re.search(r'name="_token"[^>]+value="([^"]+)"', r.text)
csrf = c.group(1) if c else re.search(r'name="csrf-token" content="([^"]+)"', r.text).group(1)

s.post('https://salvador.colih.med.br/auth/login', data={'_token': csrf, 'username': COLIH_USER, 'password': COLIH_PASS}, verify=False)
m=s.get('https://salvador.colih.med.br/panel/users', verify=False)
with open('scratch/users_page.html', 'w', encoding='utf-8') as f:
    f.write(m.text)
