import requests, re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})
r = session.get('https://salvador.colih.med.br', verify=False)
c = re.search(r'name="_token"[^>]+value="([^"]+)"', r.text)
if not c:
    c = re.search(r'name="csrf-token" content="([^"]+)"', r.text)
csrf = c.group(1)

login = session.post(
    'https://salvador.colih.med.br/auth/login',
    data={'_token': csrf, 'username': 'suporte@colihsalvador.com', 'password': 'colihsalvador'},
    verify=False, allow_redirects=True
)

panel = session.get('https://salvador.colih.med.br/panel/members', verify=False)
print('Members status:', panel.status_code)
export_links = re.findall(r'href="([^"]*export[^"]*)"', panel.text)
print('Export links on members page:', export_links)

# Also let's check the HTML of the members page to see if we can parse it
with open('backend/data/members_page.html', 'w', encoding='utf-8') as f:
    f.write(panel.text)
print('Saved to backend/data/members_page.html')
