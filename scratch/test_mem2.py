import requests, re, pandas as pd
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})
resp = session.get('https://salvador.colih.med.br', timeout=30, verify=False)
csrf = re.search(r'name="_token"[^>]+value="([^"]+)"', resp.text)
if not csrf: csrf = re.search(r'name="csrf-token" content="([^"]+)"', resp.text)
session.post('https://salvador.colih.med.br/auth/login', data={'_token': csrf.group(1), 'username': 'lmc.colihba@gmail.com', 'password': 'Svc@colih26'}, headers={'Referer': 'https://salvador.colih.med.br/auth/login'}, verify=False)

mem_url = 'https://salvador.colih.med.br/panel/users/export?type=xls&region=All&isMultipleRegions=1&moreFilters=0&name=&sortOrder=nm'
r = session.get(mem_url, verify=False)
with open('test_mem2.xlsx', 'wb') as f: f.write(r.content)
try:
    df = pd.read_excel('test_mem2.xlsx', engine='openpyxl')
    print('Members with region=All:', len(df))
except Exception as e:
    print('Failed to read:', e)
