with open('frontend/index.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'id="syncStatusModal"' in line:
            print(f'Found modal at {i+1}')
