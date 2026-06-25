import requests, re
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})
resp = session.get('https://salvador.colih.med.br', timeout=30)
csrf = re.search(r'name="_token"[^>]+value="([^"]+)"', resp.text)
if not csrf: csrf = re.search(r'name="csrf-token" content="([^"]+)"', resp.text)
session.post('https://salvador.colih.med.br/auth/login', data={'_token': csrf.group(1), 'username': 'lmc.colihba@gmail.com', 'password': 'Svc@colih26'}, headers={'Referer': 'https://salvador.colih.med.br/auth/login'})
users_page = session.get('https://salvador.colih.med.br/panel/users')
export_links = re.findall(r'href="([^"]*export[^"]*)"', users_page.text, re.IGNORECASE)
print('Exports on users page:', export_links)
if export_links:
    r = session.get(export_links[0])
    print('Export HTTP code:', r.status_code, len(r.content), 'bytes')
