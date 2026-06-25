import re

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# We want to replace the existing forceSyncUpdateMultiple function
# Wait, I previously appended it at the end. So I can just do a regex replace from `async function forceSyncUpdateMultiple` to the end.

new_logic = """
// ─── SYNC & HLC CONFIG LOGIC ──────────────────────────────────────────────────
async function forceSyncUpdateMultiple() {
    const doCnes = document.getElementById('syncCheckCnes')?.checked;
    const doColih = document.getElementById('syncCheckColih')?.checked;
    
    if(!doCnes && !doColih) {
        alert('Selecione ao menos uma fonte para sincronizar.');
        return;
    }
    
    document.getElementById('btnForceSync').disabled = true;
    document.getElementById('btnForceSync').innerHTML = 'Iniciando...';
    document.getElementById('syncColihPreviewArea').style.display = 'none';
    
    try {
        if(doCnes) {
            await fetchAPI('/sync', { method: 'POST' });
            alert('Sincronização CNES iniciada em segundo plano.');
        }
        
        if(doColih) {
            document.getElementById('btnForceSync').innerHTML = 'Gerando Preview COLIH...';
            const res = await fetchAPI('/colih/sync?action=preview', { method: 'POST' });
            if (res && res.preview_ready) {
                // Show Preview
                const diff = res.diff;
                let diffHtml = `<strong>Médicos:</strong> +${diff.docs_added.length}, -${diff.docs_removed.length}<br>`;
                diffHtml += `<strong>Membros:</strong> +${diff.mem_added.length}, -${diff.mem_removed.length}<br><br>`;
                
                if (diff.docs_added.length > 0) diffHtml += `<em>Médicos Adicionados:</em> ${diff.docs_added.join(', ')}<br>`;
                if (diff.docs_removed.length > 0) diffHtml += `<em>Médicos Removidos:</em> ${diff.docs_removed.join(', ')}<br>`;
                if (diff.mem_added.length > 0) diffHtml += `<em>Membros Adicionados:</em> ${diff.mem_added.join(', ')}<br>`;
                if (diff.mem_removed.length > 0) diffHtml += `<em>Membros Removidos:</em> ${diff.mem_removed.join(', ')}<br>`;
                
                if(diff.docs_added.length === 0 && diff.docs_removed.length === 0 && diff.mem_added.length === 0 && diff.mem_removed.length === 0) {
                    diffHtml += "Nenhuma alteração detectada. Você pode confirmar ou descartar.";
                }
                
                document.getElementById('syncColihDiff').innerHTML = diffHtml;
                document.getElementById('syncColihPreviewArea').style.display = 'block';
            } else {
                alert('Erro ao gerar preview COLIH: ' + (res.error || 'Desconhecido'));
            }
        }
        
        if (doCnes && !doColih) {
            document.getElementById('syncStatusModal').style.display = 'none';
        }
        
        carregarStatusSync();
    } catch(e) {
        alert('Erro ao iniciar sincronização.');
    } finally {
        document.getElementById('btnForceSync').disabled = false;
        document.getElementById('btnForceSync').innerHTML = '<i class="fas fa-sync-alt"></i> Forçar Sincronização';
    }
}

async function commitColihSync() {
    try {
        const btn = document.querySelector('#syncColihPreviewArea .btn-primary');
        btn.disabled = true;
        btn.innerHTML = "Aplicando...";
        const res = await fetchAPI('/colih/sync?action=commit', { method: 'POST' });
        if(res && res.success) {
            alert(res.message || 'Aplicado com sucesso');
            document.getElementById('syncStatusModal').style.display = 'none';
            document.getElementById('syncColihPreviewArea').style.display = 'none';
        } else {
            alert('Erro ao aplicar: ' + (res.error || ''));
        }
        btn.disabled = false;
        btn.innerHTML = "Confirmar e Aplicar COLIH";
    } catch(e) {
        alert('Erro ao confirmar.');
    }
}

async function discardColihSync() {
    try {
        await fetchAPI('/colih/sync?action=discard', { method: 'POST' });
        document.getElementById('syncColihPreviewArea').style.display = 'none';
    } catch(e) {}
}
"""

# Replace the old forceSyncUpdateMultiple with the new one
pattern = r'// ─── SYNC & HLC CONFIG LOGIC ──────────────────────────────────────────────────\nasync function forceSyncUpdateMultiple.*?Forçar Sincronização\';\n    }\n}'
if re.search(pattern, text, re.DOTALL):
    text = re.sub(pattern, new_logic, text, flags=re.DOTALL)
    with open('frontend/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print('app.js successfully updated with preview logic.')
else:
    print('Pattern not found in app.js')
