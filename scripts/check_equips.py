import json

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\backend\data\estab_cache.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

hospitals = []
for estab in data.get('estabelecimentos', []):
    equipamentos = estab.get('equipamentos', [])
    relevant_equips = []
    for eq in equipamentos:
        nome = (eq.get('nome') or '').lower()
        if 'circulacao extracorporea' in nome or 'aferese' in nome or 'hemoderivados' in nome:
            relevant_equips.append(f"• {eq.get('nome')} (Quantidade: {eq.get('quantidade')})")
    
    if relevant_equips:
        hospitals.append({
            'nome': estab.get('nome') or estab.get('fantasia'),
            'cnes': estab.get('cnes'),
            'equips': relevant_equips
        })

for h in hospitals:
    print(f"🏥 {h['nome']} (CNES: {h['cnes']})")
    for eq in h['equips']:
        print(f"   {eq}")
