import sys
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    data = f.read()

target = '<span id="colih-coop-count" style="font-weight:600;">Verificando...</span>\n          </div>'
replacement = '<span id="colih-coop-count" style="font-weight:600;">Verificando...</span>\n          </div>\n          <div style="margin-top: 10px; border-top: 1px solid var(--border-color); padding-top: 15px;">\n             <button class="btn btn-primary" onclick="document.getElementById(\'colihDetailsModal\').style.display=\'none\'; document.getElementById(\'syncCheckCnes\').checked=false; document.getElementById(\'syncCheckColih\').checked=true; document.getElementById(\'syncStatusModal\').style.display=\'flex\';" style="width:100%;"><i data-lucide="refresh-cw"></i> Forçar Sincronização</button>\n          </div>'
if target in data:
    data = data.replace(target, replacement)
    with open('frontend/index.html', 'w', encoding='utf-8', newline='') as f:
        f.write(data)
    print('Fixed COLIH button')
else:
    print('Target not found')
