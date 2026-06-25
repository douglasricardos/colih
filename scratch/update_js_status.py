import re

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace syncStatusText and Dot targets
text = text.replace('const text = document.getElementById("syncStatusText");', 'const text = document.getElementById("modal-cnes-status");\n        const compactText = document.getElementById("cnesStatusCompact");')
text = text.replace('const dot = document.getElementById("syncStatusDot");', 'const dot = document.getElementById("cnesStatusDot");')

# Update references to text in the fetchSyncStatus logic
text = text.replace('text.innerText = "Lendo base do MS...";', 'text.innerText = "Lendo base do MS..."; if(compactText) compactText.innerText = "Lendo...";')
text = text.replace('text.innerText = `Atualizado`;', 'text.innerText = `Atualizado`; if(compactText) compactText.innerText = "Online";')
text = text.replace('text.innerText = "Erro de Sync";', 'text.innerText = "Erro de Sync"; if(compactText) compactText.innerText = "Erro";')

text = text.replace('text.innerHTML = `Sincronizando: <span style="color:#ffaa00; font-weight:bold;">${status.progresso}%</span> <span style="color:#aaa; font-size:12px;">${etaStr}</span>`;', 'text.innerHTML = `Sincronizando: <span style="color:#ffaa00; font-weight:bold;">${status.progresso}%</span> <span style="color:#aaa; font-size:12px;">${etaStr}</span>`; if(compactText) compactText.innerText = `${status.progresso}%`;')

text = text.replace('document.getElementById("syncStatusText").innerText = "Status Indisponível";', 'if(document.getElementById("modal-cnes-status")) document.getElementById("modal-cnes-status").innerText = "Indisponível";\n        if(document.getElementById("cnesStatusCompact")) document.getElementById("cnesStatusCompact").innerText = "Offline";')

with open('frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('app.js status elements updated.')
