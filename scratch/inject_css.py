with open('frontend/css/style.css', 'a', encoding='utf-8') as f:
    f.write("""

/* ─── SIDEBAR & MAIN LAYOUT (GLPI Style) ────────────────────────── */
body {
    display: flex;
    margin: 0;
    padding: 0;
    height: 100vh;
    overflow: hidden;
}

.sidebar {
    width: 250px;
    background-color: #1e293b;
    color: #f8fafc;
    display: flex;
    flex-direction: column;
    box-shadow: 2px 0 5px rgba(0,0,0,0.2);
    z-index: 1000;
    transition: width 0.3s ease;
}

.sidebar-header {
    padding: 20px;
    font-size: 1.25rem;
    font-weight: 800;
    text-align: center;
    background-color: #0f172a;
    border-bottom: 1px solid #334155;
    letter-spacing: 1px;
}

.sidebar-menu {
    list-style: none;
    padding: 0;
    margin: 0;
    flex: 1;
    overflow-y: auto;
}

.sidebar-menu::-webkit-scrollbar {
    width: 6px;
}
.sidebar-menu::-webkit-scrollbar-thumb {
    background: #475569;
    border-radius: 4px;
}

.menu-group {
    padding: 15px 20px 5px;
    font-size: 0.75rem;
    text-transform: uppercase;
    color: #94a3b8;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.menu-item {
    padding: 12px 20px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.95rem;
    color: #cbd5e1;
}

.menu-item i {
    width: 20px;
    text-align: center;
    font-size: 1.1rem;
}

.menu-item:hover {
    background-color: #334155;
    color: #fff;
    border-left: 4px solid #3b82f6;
    padding-left: 16px;
}

.menu-item.active {
    background-color: #2563eb;
    color: #fff;
    border-left: 4px solid #60a5fa;
    padding-left: 16px;
}

.main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    background-color: #0f172a; /* Match existing dark theme */
    padding: 0;
}

/* Adjust top bar (formerly navbar) */
.topbar {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding: 10px 20px;
    background-color: rgba(30, 41, 59, 0.8);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

.tab-panel {
    padding: 20px;
}

/* Hide old horizontal navbar elements if any remain */
.navbar {
    display: none !important;
}
""")
print('CSS styles added for sidebar')
