import sys

with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """  if (advData.equipamentos && advData.equipamentos.length) {
      const temCellSaver = advData.equipamentos.some(x => {
          const n = (x.nome || '').toLowerCase();
          return n.includes('circulacao extracorporea') || n.includes('aferese') || n.includes('hemoderivados');
      });
      if (temCellSaver) {
          cellSaverBadge = `<div style="background:var(--accent-red); color:white; padding:8px 12px; border-radius:6px; font-size:12px; font-weight:bold; margin-bottom:15px; display:flex; align-items:center; gap:8px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);">
              <span style="font-size:16px;">🩸</span> <span>ALERTA COLIH: Hospital possui equipamento compatível com Cell Saver / Recuperação Intraoperatória (Aférese / Circulação Extracorpórea)</span>
          </div>`;
      }
  }"""

new_block = """  if (advData.equipamentos && advData.equipamentos.length) {
      const isCellSaver = (n) => {
          const str = (n || '').toLowerCase();
          return str.includes('circulacao extracorporea') || str.includes('aferese');
      };
      const temCellSaver = advData.equipamentos.some(x => isCellSaver(x.nome));
      if (temCellSaver) {
          cellSaverBadge = `<div style="background:#ef4444; color:#ffffff; padding:12px; border-radius:6px; font-size:13px; font-weight:bold; margin-bottom:15px; display:flex; align-items:center; gap:10px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);">
              <span style="font-size:18px;">🩸</span> <span>ALERTA COLIH: Este hospital possui equipamento compatível com a Recuperação Intraoperatória (Ex: Circulação Extracorpórea / Aférese contínua)</span>
          </div>`;
      }
      advData.equipamentos.forEach(x => {
          if (isCellSaver(x.nome)) {
              x._highlight = true;
          }
      });
  }"""

old_equip_render = """  if (advData.equipamentos && advData.equipamentos.length) {
    offlineAdvanced += `
    <details style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px; cursor:pointer;">
        <summary style="font-size:13px; font-weight:600; color:var(--accent-purple); outline:none; user-select:none;">Equipamentos <span style="font-size:11px; font-weight:normal; color:var(--text-muted); float:right; margin-top:2px;">(Expandir/Recolher)</span></summary>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:12px; margin-top:12px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.05);">
            ${advData.equipamentos.map(x => `<div><strong style="color:var(--text-secondary)">${x.nome}</strong>: ${x.quantidade}</div>`).join('')}
        </div>
    </details>`;
  }"""

new_equip_render = """  if (advData.equipamentos && advData.equipamentos.length) {
    offlineAdvanced += `
    <details style="background:var(--bg-card); padding:12px; border-radius:6px; border:1px solid var(--border-color); margin-bottom:10px; cursor:pointer;">
        <summary style="font-size:13px; font-weight:600; color:var(--accent-purple); outline:none; user-select:none;">Equipamentos <span style="font-size:11px; font-weight:normal; color:var(--text-muted); float:right; margin-top:2px;">(Expandir/Recolher)</span></summary>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:12px; margin-top:12px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.05);">
            ${advData.equipamentos.map(x => x._highlight ? `<div style="color:#ef4444; font-weight:bold; background:rgba(239, 68, 68, 0.1); padding:4px; border-radius:4px;"><strong style="color:#ef4444;">${x.nome}</strong>: ${x.quantidade}</div>` : `<div><strong style="color:var(--text-secondary)">${x.nome}</strong>: ${x.quantidade}</div>`).join('')}
        </div>
    </details>`;
  }"""

if old_block in content and old_equip_render in content:
    content = content.replace(old_block, new_block)
    content = content.replace(old_equip_render, new_equip_render)
    with open(r'c:\Users\e333638\Desktop\Projetos AntiGravity\COLIH_Captacao\frontend\app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("UI FIXED!")
else:
    print("BLOCK NOT FOUND")
