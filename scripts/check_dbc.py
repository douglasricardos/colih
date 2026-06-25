import ftplib
import os
import pyreaddbc
from dbfread import DBF

ftp_host = "ftp.datasus.gov.br"

def check(tipo):
    caminho_ftp = f"/dissemin/publicos/CNES/200508_/Dados/{tipo}/{tipo}BA2605.dbc"
    destino = f"{tipo}BA2605.dbc"
    try:
        with ftplib.FTP(ftp_host, timeout=20) as ftp:
            ftp.login()
            with open(destino, "wb") as f:
                ftp.retrbinary(f"RETR {caminho_ftp}", f.write)
        pyreaddbc.dbc2dbf(destino, destino.replace('.dbc', '.dbf'))
        table = DBF(destino.replace('.dbc', '.dbf'), encoding='iso-8859-1')
        print(tipo, "Columns:", table.field_names)
    except Exception as e:
        print(tipo, "Failed:", e)

for t in ["EQ", "LT", "ST", "IN", "SR"]:
    check(t)
