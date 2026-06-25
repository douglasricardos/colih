import requests, re
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})
resp = session.get('https://salvador.colih.med.br', timeout=30)
csrf = re.search(r'name="_token"[^>]+value="([^"]+)"', resp.text)
if not csrf:
    csrf = re.search(r'name="csrf-token" content="([^"]+)"', resp.text)
csrf_token = csrf.group(1)

session.post('https://salvador.colih.med.br/auth/login', data={'_token': csrf_token, 'username': 'lmc.colihba@gmail.com', 'password': 'Svc@colih26'}, headers={'Referer': 'https://salvador.colih.med.br/auth/login'})
dash = session.get('https://salvador.colih.med.br/panel/dashboard')
links = re.findall(r'href="([^"]+)"', dash.text)
for l in sorted(set(links)):
    if '/panel/' in l: print(l)
