import requests, re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

# Get CSRF and Login
resp = session.get('https://salvador.colih.med.br', timeout=30)
csrf = re.search(r'name="_token"[^>]+value="([^"]+)"', resp.text)
if not csrf:
    csrf = re.search(r'name="csrf-token" content="([^"]+)"', resp.text)
csrf_token = csrf.group(1)

session.post(
    'https://salvador.colih.med.br/auth/login',
    data={'_token': csrf_token, 'username': 'lmc.colihba@gmail.com', 'password': 'Svc@colih26'},
    headers={'Referer': 'https://salvador.colih.med.br/auth/login'},
    allow_redirects=True, timeout=30
)
print("Logged in!")

# Test Members Export
members = session.get('https://salvador.colih.med.br/panel/members', timeout=30)
print(f"Members page: {members.status_code}")

export_links = re.findall(r'href="([^"]*export[^"]*)"', members.text, re.IGNORECASE)
export_links += re.findall(r'href="([^"]*excel[^"]*)"', members.text, re.IGNORECASE)
print(f"Found export links on members page: {export_links}")

# Try direct urls
for url in [
    'https://salvador.colih.med.br/panel/members/export?type=xls',
    'https://salvador.colih.med.br/panel/members/export',
    'https://salvador.colih.med.br/panel/people/export?type=xls'
]:
    r = session.get(url, timeout=15)
    print(f"{url} -> {r.status_code} ({r.headers.get('content-type', '')}) {len(r.content)} bytes")
    if r.status_code == 200 and len(r.content) > 1000:
        with open('members_export_test.xls', 'wb') as f:
            f.write(r.content)
        print("Saved to members_export_test.xls")
        break
