import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('<section class="tab-panel" id="tab-config-hlc" style="display:none;">', '<section class="tab-panel" id="tab-config-hlc">')
text = text.replace('<section class="tab-panel" id="tab-config-cnes" style="display:none;">', '<section class="tab-panel" id="tab-config-cnes">')
text = text.replace('<section class="tab-panel" id="tab-config-apoio" style="display:none;">', '<section class="tab-panel" id="tab-config-apoio">')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Config tabs inline style removed.')
