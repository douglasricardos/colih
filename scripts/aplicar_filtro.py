import json
import pandas as pd
import unicodedata
from pathlib import Path

BASE_DIR = Path(r"C:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao")
DATA_DIR = BASE_DIR / "backend" / "data"

def normalize_str(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\ufffd", "")
    s = unicodedata.normalize("NFD", str(s))
    s = s.encode("ascii", "ignore").decode("utf-8")
    return s.lower().strip()

# 1. Read CSV
csv_path = r"c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Salvador\Cópia de BA Salvador- Municípios.csv"
df = pd.read_csv(csv_path)

municipios_nomes_norm = set()
formatted_list = []
for _, row in df.iterrows():
    codigo = str(row['CD_MUN'])
    nome = str(row['NM_MUN'])
    municipios_nomes_norm.add(normalize_str(nome))
    formatted_list.append(f"{codigo} - {nome}")

# 2. Write sync_config.json
config = {
    "uf": "BA",
    "descricao": "COLIH Salvador - 96 Municípios",
    "municipios_especificos": formatted_list
}
with open(DATA_DIR / "sync_config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"Created sync_config.json with {len(formatted_list)} municipalities.")

# 3. Filter estab_cache.json
estab_path = DATA_DIR / "estab_cache.json"

if estab_path.exists():
    print("Filtering estab_cache.json...")
    with open(estab_path, "r", encoding="utf-8") as f:
        estab_data = json.load(f)
    
    original_len = len(estab_data.get("estabelecimentos", []))
    new_estabs = []
    
    valid_cnes = set()
    
    for h in estab_data.get("estabelecimentos", []):
        mun_nome = normalize_str(str(h.get("municipio", "")))
        
        if mun_nome in municipios_nomes_norm:
            new_estabs.append(h)
            valid_cnes.add(str(h.get("cnes")))
            
    estab_data["estabelecimentos"] = new_estabs
    with open(estab_path, "w", encoding="utf-8") as f:
        json.dump(estab_data, f, ensure_ascii=False)
    
    print(f"estab_cache.json: {original_len} -> {len(new_estabs)}")
else:
    valid_cnes = set()
    print("estab_cache.json not found")

# 4. Filter medicos_cache.json
medicos_path = DATA_DIR / "medicos_cache.json"
if medicos_path.exists():
    print("Filtering medicos_cache.json...")
    with open(medicos_path, "r", encoding="utf-8") as f:
        medicos_data = json.load(f)
    
    original_len = len(medicos_data.get("medicos", []))
    new_medicos = []
    
    for m in medicos_data.get("medicos", []):
        has_valid_vinculo = False
        for v in m.get("vinculos", []):
            if str(v.get("cnes")) in valid_cnes:
                has_valid_vinculo = True
                break
        if has_valid_vinculo:
            new_medicos.append(m)
            
    medicos_data["medicos"] = new_medicos
    with open(medicos_path, "w", encoding="utf-8") as f:
        json.dump(medicos_data, f, ensure_ascii=False)
        
    print(f"medicos_cache.json: {original_len} -> {len(new_medicos)}")
else:
    print("medicos_cache.json not found")
