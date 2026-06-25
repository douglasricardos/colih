import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_download = """    print(f"   Iniciando download do ZIP (~1.5GB)...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as res:
        # Lê os primeiros 4 bytes para validar se é um ZIP ('PK\\x03\\x04')
        first_chunk = res.read(4)
        if not first_chunk or not first_chunk.startswith(b'PK'):
            raise Exception(f"Arquivo não disponível no Servlet (Competência {competencia} não publicada ainda)")
            
        total_size = int(res.getheader('Content-Length') or 1.5 * 1024 * 1024 * 1024)
        downloaded = 4
        
        import time
        start_time = time.time()
        last_update = start_time
        
        with open(zip_path, "wb") as f:
            f.write(first_chunk)
            while True:
                chunk = res.read(8192 * 4) # 32KB chunks
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                
                now = time.time()
                if now - last_update > 1.0:
                    speed = downloaded / (now - start_time) / (1024*1024)
                    eta_sec = (total_size - downloaded) / (speed * 1024 * 1024) if speed > 0 else 0
                    eta_str = f"{int(eta_sec//60)}m {int(eta_sec%60)}s" if speed > 0 else "Calculando..."
                    pct = int((downloaded / total_size) * 100 * 0.99)
                    det = f"Baixando ZIP principal... {downloaded/1024/1024:.1f} MB de ~1500 MB\\nVelocidade: {speed:.1f} MB/s | ETA: {eta_str}"
                    save_sync_status("verificando", [], progresso=pct, detalhes=det, url_fonte=url)
                    last_update = now
                    
    print(f"   Download concluído. Tamanho: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")"""

new_download = """    zip_path = Path(r"c:\\Users\\e333638\\Desktop\\Projetos AntiGravity\\COLIH_Captacao\\backend\\data\\BASE_CNES.zip")
    print(f"   Iniciando leitura do ZIP Local (~1.5GB)...")"""

if old_download in code:
    code = code.replace(old_download, new_download)
    with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\scripts\atualizar_cache.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("DOWNLOAD BYPASSED")
else:
    print("BYPASS FAILED")
