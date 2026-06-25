import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. We extract the header-meta block
header_meta_match = re.search(r'<div class="header-meta" id="header-meta">.*?</div>\s*</div>\s*</header>', text, re.DOTALL)
if header_meta_match:
    header_meta_html = header_meta_match.group(0).replace('</div>\n  </div>\n</header>', '</div>')
    
    # 2. We remove the entire <header class="app-header"> block
    text = re.sub(r'<!-- ═══════════════════════════════════════════════════════ HEADER -->\s*<header class="app-header">.*?</header>', '', text, flags=re.DOTALL)
    
    # 3. We insert the header_meta_html into the .topbar
    # We find `<div class="topbar">`
    replacement = f'''<div class="topbar" style="display:flex; justify-content:flex-end; align-items:center; padding:10px 20px; background-color: var(--bg-card); border-bottom: 1px solid var(--border-color); width: 100%;">
      {header_meta_html}
    '''
    text = text.replace('<div class="topbar">', replacement)
    
    # We should also remove the old sync-status btnOpenSyncModal because it's duplicated now
    text = re.sub(r'<!-- Sync Button -->\s*<div class="sync-status".*?</div>', '', text, flags=re.DOTALL)
    
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Header fixed!')
else:
    print('header-meta not found')
