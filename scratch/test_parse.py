import requests, re, pandas as pd, urllib3
urllib3.disable_warnings()
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})
r=s.get('https://salvador.colih.med.br', verify=False)
c=re.search(r'name="_token"[^>]+value="([^"]+)"', r.text)
csrf = c.group(1) if c else re.search(r'name="csrf-token" content="([^"]+)"', r.text).group(1)
s.post('https://salvador.colih.med.br/auth/login', data={'_token': csrf, 'username': 'suporte@colihsalvador.com', 'password': 'colihsalvador'}, verify=False)
m=s.get('https://salvador.colih.med.br/panel/users/export?type=xls&region=12&isMultipleRegions=1&moreFilters=0&name=&tipo=1&sortOrder=nm', verify=False)
with open('scratch/members.xlsx','wb') as f:
    f.write(m.content)
df=pd.read_excel('scratch/members.xlsx')
print('Columns:', df.columns.tolist())
print('First row:', df.iloc[0].to_dict())
