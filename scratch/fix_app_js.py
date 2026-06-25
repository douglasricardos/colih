import re

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove user select population logic
text = re.sub(r'async function carregarUsuarios\(\).*?\}', 'async function carregarUsuarios() {}', text, flags=re.DOTALL)

# Add lucide.createIcons() to init or end of file
if 'lucide.createIcons' not in text:
    text = text.replace('async function init() {', 'async function init() {\n  if(window.lucide) window.lucide.createIcons();')

# Fix fetchSyncStatus interval if it's missing
if 'setInterval(fetchSyncStatus' not in text:
    text += '\nsetInterval(fetchSyncStatus, 5000);\nsetTimeout(fetchSyncStatus, 500);\n'

with open('frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('app.js updated with lucide and removed user select')
