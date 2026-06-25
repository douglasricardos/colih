import requests

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

# Step 1: Get login page + CSRF token
print("Step 1: Getting login page...")
resp = session.get('https://salvador.colih.med.br', timeout=30)
print(f"  Status: {resp.status_code}, URL: {resp.url}")

# Extract CSRF token
import re
csrf_match = re.search(r'<input[^>]+name="_token"[^>]+value="([^"]+)"', resp.text)
if not csrf_match:
    csrf_match = re.search(r'name="csrf-token" content="([^"]+)"', resp.text)
if csrf_match:
    csrf_token = csrf_match.group(1)
    print(f"  CSRF token: {csrf_token[:20]}...")
else:
    print("  ERROR: CSRF token not found!")
    print("  Response snippet:", resp.text[:500])
    exit()

# Step 2: Login
print("\nStep 2: Logging in...")
login_resp = session.post(
    'https://salvador.colih.med.br/auth/login',
    data={
        '_token': csrf_token,
        'username': 'lmc.colihba@gmail.com',
        'password': 'Svc@colih26',
    },
    headers={
        'Referer': 'https://salvador.colih.med.br/auth/login',
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    allow_redirects=True,
    timeout=30
)
print(f"  Status: {login_resp.status_code}, Final URL: {login_resp.url}")
logged_in = 'panel' in login_resp.url or 'dashboard' in login_resp.url or 'painel' in login_resp.url
if not logged_in:
    print("  Response snippet:", login_resp.text[:500])
    print("  WARNING: May not be logged in!")
else:
    print("  SUCCESS: Logged in!")

# Step 3: Try to find export URL
print("\nStep 3: Looking for export/CSV endpoint...")
# Try direct export URL patterns common in PHP/Laravel apps
export_urls = [
    'https://salvador.colih.med.br/panel/doctors/export',
    'https://salvador.colih.med.br/panel/doctors/excel',
    'https://salvador.colih.med.br/panel/doctors/download',
    'https://salvador.colih.med.br/panel/medicos/export',
    'https://salvador.colih.med.br/export/doctors',
    'https://salvador.colih.med.br/panel/doctors?export=excel',
]

for url in export_urls:
    r = session.get(url, timeout=15, allow_redirects=True)
    ct = r.headers.get('content-type', '')
    print(f"  {url} -> {r.status_code} ({ct[:60]})")
    if r.status_code == 200 and ('excel' in ct or 'spreadsheet' in ct or 'csv' in ct or 'octet-stream' in ct):
        print(f"  => FOUND EXPORT at: {url}")
        with open('doctors_export.xlsx', 'wb') as f:
            f.write(r.content)
        print("  File saved as doctors_export.xlsx")
        break

# Also check panel page for export button
print("\nStep 4: Checking panel/doctors page for export links...")
panel = session.get('https://salvador.colih.med.br/panel/doctors', timeout=30)
print(f"  Status: {panel.status_code}")
export_links = re.findall(r'href="([^"]*export[^"]*)"', panel.text, re.IGNORECASE)
export_links += re.findall(r'href="([^"]*excel[^"]*)"', panel.text, re.IGNORECASE)
export_links += re.findall(r'href="([^"]*download[^"]*)"', panel.text, re.IGNORECASE)
export_links += re.findall(r'href="([^"]*csv[^"]*)"', panel.text, re.IGNORECASE)
if export_links:
    print(f"  Export links found: {export_links}")
else:
    # Look for any button with export-like text
    btn_matches = re.findall(r'<(?:a|button)[^>]*>.*?(?:export|excel|baixar|download|exportar).*?</(?:a|button)>', panel.text, re.IGNORECASE | re.DOTALL)
    if btn_matches:
        print(f"  Export buttons: {btn_matches[:3]}")
    else:
        print("  No obvious export links found.")
    
    # Dump for manual inspection
    with open('panel_doctors.html', 'w', encoding='utf-8') as f:
        f.write(panel.text)
    print("  Saved panel HTML to panel_doctors.html for inspection")
