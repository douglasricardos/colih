import urllib.parse
import urllib.request
import json

qs = urllib.parse.urlencode({
    'hospital': 'Hospital Santo Antonio',
    'especialidade': 'Anestesiologia'
})
url = 'http://127.0.0.1:8000/api/medicos?' + qs
print("Requesting URL:", url)
with urllib.request.urlopen(url) as response:
    res = json.loads(response.read().decode('utf-8'))
    print('Total returned:', res['total'])
    if res['total'] > 0:
        print('First match:', res['medicos'][0]['nome'])
