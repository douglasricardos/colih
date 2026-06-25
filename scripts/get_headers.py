import urllib.request
import zipfile
import tempfile
from pathlib import Path
import os

url = "https://cnes.datasus.gov.br/EstatisticasServlet?path=BASE_DE_DADOS_CNES_202605.ZIP"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

with tempfile.TemporaryDirectory() as td:
    zip_path = Path(td) / "BASE.zip"
    print("Baixando ZIP gigante...", flush=True)
    with urllib.request.urlopen(req) as res, open(zip_path, "wb") as f:
        while True:
            chunk = res.read(8192 * 1024)
            if not chunk: break
            f.write(chunk)
    
    print("Extraindo e lendo headers...", flush=True)
    with zipfile.ZipFile(zip_path, 'r') as z:
        for name in z.namelist():
            if name.endswith(".csv"):
                with z.open(name) as f:
                    header = f.readline().decode('iso-8859-1').strip()
                    print(f"[{name}] {header}")
    print("CONCLUIDO")
