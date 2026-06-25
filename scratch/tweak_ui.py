import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Add lucide script if not present
if 'unpkg.com/lucide' not in text:
    text = text.replace('</head>', '  <script src="https://unpkg.com/lucide@latest"></script>\n</head>')

# Ensure toggleGroup uses the new class structure properly
# It's already fixed in app.js, so just fixing the HTML tab
text = text.replace('class="menu-item active" onclick="openTab(\'hospitais\'', 'class="menu-item" onclick="openTab(\'hospitais\'')
text = text.replace('class="menu-item" onclick="openTab(\'stats\'', 'class="menu-item active" onclick="openTab(\'stats\'')

text = text.replace('<section class="tab-panel active" id="tab-hospitais">', '<section class="tab-panel" id="tab-hospitais">')
text = text.replace('<section class="tab-panel" id="tab-stats">', '<section class="tab-panel active" id="tab-stats">')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

# Also fix CSS to compress sidebar items
with open('frontend/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

css = re.sub(r'\.menu-item\s*\{.*?\}', '.menu-item {\n    padding: 6px 12px;\n    margin: 2px 8px;\n    border-radius: 6px;\n    cursor: pointer;\n    display: flex;\n    align-items: center;\n    gap: 8px;\n    color: #94a3b8;\n    transition: 0.2s;\n    font-size: 12px;\n}', css, flags=re.DOTALL)

css = re.sub(r'\.menu-group\s*\{.*?\}', '.menu-group {\n    padding: 8px 12px 4px 12px;\n    font-size: 10px;\n    text-transform: uppercase;\n    font-weight: 700;\n    color: #475569;\n    letter-spacing: 0.5px;\n}', css, flags=re.DOTALL)

css = re.sub(r'\.sidebar\s*\{.*?\}', '.sidebar {\n    width: 240px;\n    background-color: #0f172a;\n    color: #f8fafc;\n    display: flex;\n    flex-direction: column;\n    box-shadow: 2px 0 5px rgba(0,0,0,0.1);\n    z-index: 1000;\n    font-size: 12px;\n    overflow-y: auto;\n}', css, flags=re.DOTALL)

with open('frontend/style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print('UI compressed and Lucide added.')
