import re

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update loadColihData to call popularFiltrosColih
old_load = '''    if (alertEl) {
        alertEl.style.display = missingCoords ? 'block' : 'none';
    }
  } catch (e) {'''

new_load = '''    if (alertEl) {
        alertEl.style.display = missingCoords ? 'block' : 'none';
    }
    popularFiltrosColih();
  } catch (e) {'''
text = text.replace(old_load, new_load)

# 2. Replace renderColihMedicos
old_render_medicos = re.search(r'function renderColihMedicos\(\).*?grid\.innerHTML =.*?join\(\'\'\);\n\}', text, re.DOTALL).group(0)
new_render_medicos = '''function renderColihMedicos() {
    const term = (document.getElementById('busca-colih-medico')?.value || '').toLowerCase();
    const espFiltro = (document.getElementById('filtro-colih-especialidade')?.value || '').toLowerCase();
    const visitaFiltro = (document.getElementById('filtro-colih-visita')?.value || '');
    
    const grid = document.getElementById('colih-medicos-grid');
    if (!grid) return;
    
    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
    
    const filtered = colihMedicosCache.filter(m => {
        const textMatch = (m.nome || '').toLowerCase().includes(term) || (m.especialidade_1_colih || '').toLowerCase().includes(term);
        const espMatch = !espFiltro || (m.especialidade_1_colih || '').toLowerCase() === espFiltro;
        
        let visitMatch = true;
        let isDefasado = false;
        
        if (m.ultima_visita) {
            const visitDate = new Date(m.ultima_visita.replace(' ', 'T'));
            if (!isNaN(visitDate)) {
                if (visitDate < sixMonthsAgo) isDefasado = true;
            } else {
                isDefasado = true; // Data inválida considera antigo
            }
        } else {
            isDefasado = true; // Sem data considera antigo
        }
        m._isDefasado = isDefasado;
        
        if (visitaFiltro === 'recentes') visitMatch = !isDefasado;
        if (visitaFiltro === 'antigos') visitMatch = isDefasado;
        
        return textMatch && espMatch && visitMatch;
    });
    
    grid.innerHTML = filtered.map(m => {
        const borderCol = m._isDefasado ? '#ef4444' : '#10b981';
        const bgCol = m._isDefasado ? 'rgba(239,68,68,0.05)' : 'var(--bg-card)';
        
        return `
        <div class="medico-card" style="border-left: 4px solid ${borderCol}; padding: 16px; background: ${bgCol}; border-radius: 8px; border-right: 1px solid var(--border-color); border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="font-weight:700; font-size:16px; color:var(--text-primary); margin-bottom:4px;">${m.nome}</div>
            <div style="font-size:13px; color:var(--text-muted); margin-bottom:8px;">${m.especialidade_1_colih || ''} ${m.especialidade_2_colih ? ' / ' + m.especialidade_2_colih : ''}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Colaboração:</strong> ${m.colaboracao || '-'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Membro Resp:</strong> ${m.membro_resp || '-'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Celular:</strong> ${m.celular || '-'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Atende SUS:</strong> ${m.atende_sus || '-'}</div>
            <div style="font-size:12px; color:${m._isDefasado ? '#ef4444' : 'var(--text-muted)'}; margin-top:8px; font-weight:${m._isDefasado ? 'bold' : 'normal'};"><em>Última visita: ${m.ultima_visita || 'Nunca'} ${m._isDefasado ? ' (Mais de 6 meses)' : ''}</em></div>
        </div>
    `}).join('');
}
'''
text = text.replace(old_render_medicos, new_render_medicos)

# 3. Replace renderColihMembros
old_render_membros = re.search(r'function renderColihMembros\(\).*?grid\.innerHTML =.*?join\(\'\'\);\n\}', text, re.DOTALL).group(0)
new_render_membros = '''function renderColihMembros() {
    const term = (document.getElementById('busca-colih-membro')?.value || '').toLowerCase();
    const regiaoFiltro = (document.getElementById('filtro-colih-regiao')?.value || '').toLowerCase();
    
    const grid = document.getElementById('colih-membros-grid');
    if (!grid) return;
    
    const filtered = colihMembrosCache.filter(m => {
        const textMatch = (m.nome || '').toLowerCase().includes(term) || (m.funcao || '').toLowerCase().includes(term);
        const regiaoMatch = !regiaoFiltro || (m.regiao || '').toLowerCase() === regiaoFiltro;
        return textMatch && regiaoMatch;
    });
    
    grid.innerHTML = filtered.map(m => {
        const hasCoords = m.lat && m.lon;
        const borderStyle = hasCoords ? 'border-left: 4px solid #3b82f6;' : 'border-left: 4px solid #ef4444; background: rgba(239,68,68,0.05);';
        return `
        <div class="medico-card" style="${borderStyle} padding: 16px; border-radius: 8px; border-right: 1px solid var(--border-color); border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div style="font-weight:700; font-size:16px; color:var(--text-primary); margin-bottom:4px;">${m.nome}</div>
                    <div style="font-size:13px; color:var(--accent-blue); font-weight:600; margin-bottom:2px;">${m.funcao || 'Membro'}</div>
                    <div style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">Região: ${m.regiao || 'Não definida'}</div>
                </div>
                <button onclick="abrirModalCoords(${m.id})" style="background:var(--bg-input); border:1px solid var(--border-color); color:var(--text-primary); padding:6px 10px; border-radius:6px; cursor:pointer; font-size:12px; display:flex; align-items:center; gap:4px;">
                    📍 Editar
                </button>
            </div>
            
            <div style="font-size:12px; margin-bottom:4px;"><strong>Telefone:</strong> ${m.telefone || '-'}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Hospital:</strong> ${m.hospital || '-'}</div>
            <div style="font-size:12px; margin-top:8px;">
                <strong>Geolocalização:</strong> 
                ${hasCoords ? '<span style="color:#10b981; font-weight:600;">Validada</span>' : '<span style="color:#ef4444; font-weight:bold;">Pendente</span>'}
            </div>
            <div style="font-size:11px; color:var(--text-muted); margin-top:4px;">${m.endereco_atual || 'Sem endereço registrado'}</div>
        </div>
    `}).join('');
}
'''
text = text.replace(old_render_membros, new_render_membros)

# 4. Add popularFiltrosColih and Coords functions at the end of the file
new_funcs = '''

// ─── COLIH AUXILIARY FUNCTIONS ───────────────────────────────────────────────

function popularFiltrosColih() {
    const especialidades = new Set();
    colihMedicosCache.forEach(m => {
        if(m.especialidade_1_colih) especialidades.add(m.especialidade_1_colih.trim());
    });
    
    const regioes = new Set();
    colihMembrosCache.forEach(m => {
        if(m.regiao) regioes.add(m.regiao.trim());
    });
    
    const selEsp = document.getElementById('filtro-colih-especialidade');
    if(selEsp) {
        selEsp.innerHTML = '<option value="">Todas as Especialidades</option>';
        Array.from(especialidades).sort().forEach(e => {
            selEsp.innerHTML += `<option value="${e}">${e}</option>`;
        });
    }
    
    const selReg = document.getElementById('filtro-colih-regiao');
    if(selReg) {
        selReg.innerHTML = '<option value="">Todos os Grupos (Regiões)</option>';
        Array.from(regioes).sort().forEach(r => {
            selReg.innerHTML += `<option value="${r}">${r}</option>`;
        });
    }
}

let coordsMembroAtual = null;

function abrirModalCoords(id) {
    const membro = colihMembrosCache.find(m => m.id === id);
    if(!membro) return;
    coordsMembroAtual = membro;
    
    document.getElementById('coord-membro-id').value = membro.id;
    document.getElementById('coord-membro-nome').value = membro.nome;
    document.getElementById('coord-lat').value = membro.lat || '';
    document.getElementById('coord-lon').value = membro.lon || '';
    document.getElementById('coord-endereco').value = membro.endereco_atual || '';
    
    document.getElementById('modal-coords').classList.add('open');
}

async function salvarCoordenadasMembro() {
    if(!coordsMembroAtual) return;
    
    const latRaw = document.getElementById('coord-lat').value;
    const lonRaw = document.getElementById('coord-lon').value;
    const endereco = document.getElementById('coord-endereco').value;
    
    const lat = latRaw ? parseFloat(latRaw) : null;
    const lon = lonRaw ? parseFloat(lonRaw) : null;
    
    const payload = {
        lat: lat,
        lon: lon,
        endereco_atual: endereco
    };
    
    try {
        const btn = document.querySelector('#modal-coords .btn-primary');
        const oldText = btn.innerText;
        btn.innerText = 'Salvando...';
        btn.disabled = true;
        
        const res = await fetchAPI(`/colih/membros/${coordsMembroAtual.id}/coords`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        btn.innerText = oldText;
        btn.disabled = false;
        
        if(res.success) {
            coordsMembroAtual.lat = lat;
            coordsMembroAtual.lon = lon;
            coordsMembroAtual.endereco_atual = endereco;
            fecharModal('modal-coords');
            renderColihMembros();
            alert('Coordenadas salvas com sucesso no banco de dados!');
        } else {
            alert('Erro ao salvar: ' + res.error);
        }
    } catch(e) {
        alert('Erro de rede ao salvar coordenadas.');
    }
}
'''

text = text + new_funcs

with open('frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('app.js updated successfully.')
