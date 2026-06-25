import json, unicodedata
def norm(s):
    if not s: return ''
    s = str(s).replace('ǭ','a').replace('Ǹ','e').replace('','a')
    return unicodedata.normalize('NFD', s).encode('ascii','ignore').decode('utf-8').lower().strip()

with open('backend/bairros_distritos.json', 'r', encoding='utf-8', errors='replace') as f:
    bd = {norm(k): v for k, v in json.load(f).items()}

with open('backend/data/estab_cache.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

s = set()
count = 0
for h in data['estabelecimentos']:
    mun = h.get('municipio', '').upper()
    if mun == 'SALVADOR' or mun == '292740':
        bairro = h['raw'].get('NO_BAIRRO', '')
        b_norm = norm(bairro)
        if bd.get(b_norm, 'Não Informado') == 'Não Informado':
            s.add(bairro)
            count += 1

print(f'Total hospitais com bairro não mapeado em Salvador: {count}')
print(f'Total bairros distintos não mapeados: {len(s)}')
print('Amostra:', list(s)[:30])
