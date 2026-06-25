with open('frontend/index.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'id="tab-stats"' in line:
            print(f'Found stats at {i+1}')
