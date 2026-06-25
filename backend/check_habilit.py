import json
import pprint

f = open('data/estab_cache.json', encoding='utf-8')
d = json.load(f)
hospitais = d['estabelecimentos']

# The data from the API has habilitacoes separately - let's check the CNES API
# Check what comissoes has
print("=== COMISSOES SAMPLE ===")
for h in hospitais[:30]:
    comissoes = h.get('comissoes', [])
    if comissoes:
        print(f"Hospital: {h.get('nome','')}")
        pprint.pprint(comissoes[:5])
        break

# Check atendimentoPrestado more deeply  
print("\n=== ATENDIMENTO PRESTADO SAMPLE ===")
for h in hospitais[:30]:
    atend = h.get('atendimentoPrestado', {})
    if isinstance(atend, dict) and atend:
        print(f"Hospital: {h.get('nome','')}")
        pprint.pprint(atend)
        break
    elif isinstance(atend, list) and atend:
        print(f"Hospital: {h.get('nome','')} - LIST")
        pprint.pprint(atend[:3])
        break

# Count hospitals with various atendimento types
tipos_atend = {}
for h in hospitais:
    atend = h.get('atendimentoPrestado', {})
    if isinstance(atend, dict):
        for k in atend.keys():
            tipos_atend[k] = tipos_atend.get(k, 0) + 1
    elif isinstance(atend, list):
        for item in atend:
            tipos_atend[str(item)] = tipos_atend.get(str(item), 0) + 1

print("\n=== ATENDIMENTO TYPES ===")
pprint.pprint(sorted(tipos_atend.items(), key=lambda x: -x[1])[:20])

# Find a hospital with ALTA COMPLEXIDADE in its services
print("\n=== LOOKING FOR ALTA COMPLEXIDADE KEYWORD ===")
for h in hospitais:
    servs = h.get('servicosEspecializados', [])
    for s in servs:
        if 'ALTA' in str(s).upper() or 'COMPLEX' in str(s).upper() or 'CARDIOVAS' in str(s).upper() or 'TRANSPLAN' in str(s).upper():
            print(f"Hospital: {h.get('nome','')}")
            print(f"Service: {s}")
            break
