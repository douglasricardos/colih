import urllib.request
import zipfile
import tempfile
import shutil
from pathlib import Path

url = "https://cnes.datasus.gov.br/EstatisticasServlet?path=BASE_DE_DADOS_CNES_202605.ZIP"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
zip_path = Path(r"c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\backend\data\BASE_CNES.zip")
extract_dir = Path(r"c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\backend\data\dicts")
extract_dir.mkdir(exist_ok=True)

if not zip_path.exists() or zip_path.stat().st_size < 1000000:
    print("Baixando ZIP gigante permanentemente...", flush=True)
    with urllib.request.urlopen(req) as res, open(zip_path, "wb") as f:
        while True:
            chunk = res.read(8192 * 1024)
            if not chunk: break
            f.write(chunk)
else:
    print("ZIP já existe. Pulando download.")

print("Extraindo dicionarios...", flush=True)
with zipfile.ZipFile(zip_path, 'r') as z:
    for name in z.namelist():
        if name.startswith("tb") and ("Equip" in name or "Leito" in name or "Jurid" in name or "Instal" in name or "Serv" in name or "Comiss" in name or "Atend" in name):
            z.extract(name, path=extract_dir)
            print(f"Extraido: {name}")

print("SUCESSO")
