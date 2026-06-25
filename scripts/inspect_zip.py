import urllib.request
import zipfile
import os

print("Baixando CNES ZIP...")
url = "ftp://ftp.datasus.gov.br/cnes/BASE_DE_DADOS_CNES_202402.ZIP"
urllib.request.urlretrieve(url, "temp_cnes.zip")

print("Analisando ZIP...")
with zipfile.ZipFile("temp_cnes.zip", 'r') as z:
    for f in z.namelist():
        if f.endswith('.csv'):
            with z.open(f) as csv_file:
                header = csv_file.readline().decode('iso-8859-1').strip()
                print(f"FILE: {f}")
                print(f"HEADER: {header}\n")
