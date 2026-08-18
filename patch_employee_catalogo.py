with open('templates/employee/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_menu = '''            <div class="menu-grid">
                <a href="/employee/scan" class="menu-item">
                    <span class="icon">📷</span>
                    <span class="label">Escanear QR</span>
                </a>
            </div>'''
new_menu = '''            <div class="menu-grid">
                <a href="/employee/scan" class="menu-item">
                    <span class="icon">📷</span>
                    <span class="label">Escanear QR</span>
                </a>
                <a href="/admin/products" class="menu-item">
                    <span class="icon">🛍️</span>
                    <span class="label">Catálogo</span>
                </a>
            </div>'''

n = content.count(old_menu)
if n == 1:
    content = content.replace(old_menu, new_menu, 1)
    with open('templates/employee/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Botón de Catálogo agregado al panel de empleado")
else:
    print(f"⚠️ Panel de empleado: no coincide (encontrado {n} veces)")
