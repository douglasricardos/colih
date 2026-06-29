import requests, re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})
resp = session.get('https://salvador.colih.med.br', verify=False)
csrf_match = re.search(r'name="_token"[^>]+value="([^"]+)"', resp.text)
if not csrf_match:
    csrf_match = re.search(r'name="csrf-token" content="([^"]+)"', resp.text)
csrf = csrf_match.group(1)

login = session.post(
    'https://salvador.colih.med.br/auth/login',
    data={'_token': csrf, 'username': 'suporte@colihsalvador.com', 'password': 'colihsalvador'},
    headers={'Referer': 'https://salvador.colih.med.br/auth/login'},
    verify=False, allow_redirects=True
)
print('Login URL:', login.url)

m_resp = session.get('https://salvador.colih.med.br/panel/members/export?type=xls', verify=False)
print('Members export status:', m_resp.status_code)
if m_resp.status_code == 200:
    print('Content type:', m_resp.headers.get('Content-Type'))
    print('Length:', len(m_resp.content))
