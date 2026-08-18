with open('templates/admin/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

floating_btn = '''
<a href="/admin/products" style="position:fixed; bottom:24px; right:20px; z-index:9999; background:linear-gradient(135deg,#00ff87,#00d4ff); color:#0a0a0a; padding:14px 22px; border-radius:30px; font-weight:800; font-family:sans-serif; text-decoration:none; box-shadow:0 8px 30px rgba(0,255,135,0.35); display:flex; align-items:center; gap:8px;">🛍️ Catálogo</a>
</body>'''

n = content.count('</body>')
if n == 1 and '🛍️ Catálogo' not in content:
    content = content.replace('</body>', floating_btn, 1)
    with open('templates/admin/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Botón flotante de Catálogo agregado al panel de administrador")
elif '🛍️ Catálogo' in content:
    print("ℹ️ El botón ya existía")
else:
    print(f"⚠️ Panel de admin: </body> encontrado {n} veces (revisar manualmente)")
