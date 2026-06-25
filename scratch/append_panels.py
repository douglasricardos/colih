import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

panels = """
  <!-- ─── ABA: COLIH MEDICOS ───────────────────────────────────── -->
  <section class="tab-panel" id="tab-colih-medicos">
    <div class="panel-header" style="background: linear-gradient(135deg, rgba(255, 170, 0, 0.1), transparent); border-bottom: 1px solid rgba(255, 170, 0, 0.2);">
      <h1>🤝 Cooperadores COLIH</h1>
      <p>Lista de médicos cadastrados na base de dados da COLIH. Atualizada a partir do sistema oficial.</p>
    </div>
    <div class="search-bar">
      <input type="text" id="busca-colih-medico" placeholder="Filtrar cooperadores..." onkeyup="renderColihMedicos()">
    </div>
    <div class="results-grid" id="colih-medicos-grid" style="grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));"></div>
  </section>

  <!-- ─── ABA: COLIH MEMBROS ───────────────────────────────────── -->
  <section class="tab-panel" id="tab-colih-membros">
    <div class="panel-header" style="background: linear-gradient(135deg, rgba(255, 170, 0, 0.1), transparent); border-bottom: 1px solid rgba(255, 170, 0, 0.2);">
      <h1>👥 Membros COLIH</h1>
      <p>Membros do comitê com validação de geolocalização para mapa de prospectos.</p>
    </div>
    <div class="search-bar">
      <input type="text" id="busca-colih-membro" placeholder="Filtrar membros..." onkeyup="renderColihMembros()">
    </div>
    <div id="alerta-coords-membros" style="display:none; background:rgba(239,68,68,0.1); color:#ef4444; padding:12px; border-radius:8px; margin-top:16px; border:1px solid #ef4444; font-weight:600;">
      ⚠️ Há membros pendentes de validação de coordenadas. Acesse o arquivo CSV para corrigir.
    </div>
    <div class="results-grid" id="colih-membros-grid" style="grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); margin-top:20px;"></div>
  </section>
"""

if 'id="tab-colih-medicos"' not in content:
    content = content.replace('<!-- ─── ABA: ESTATÍSTICAS ────────────────────────────────────── -->', panels + '\n  <!-- ─── ABA: ESTATÍSTICAS ────────────────────────────────────── -->')
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('COLIH panels added.')
else:
    print('COLIH panels already exist.')
