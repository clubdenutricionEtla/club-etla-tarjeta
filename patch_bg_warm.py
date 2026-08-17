with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_body_bg = '''            background:
                radial-gradient(ellipse 120% 80% at 20% 20%, rgba(30,80,30,0.30) 0%, transparent 60%),
                radial-gradient(ellipse 100% 70% at 80% 80%, rgba(20,60,20,0.25) 0%, transparent 50%),
                radial-gradient(ellipse 80% 60% at 50% 50%, rgba(60,100,50,0.10) 0%, transparent 40%),
                radial-gradient(ellipse 100% 100% at 50% 50%, #e0ece0 0%, #c8dcc8 100%);'''
new_body_bg = '''            background:
                radial-gradient(ellipse 120% 80% at 20% 20%, rgba(212,160,23,0.20) 0%, transparent 60%),
                radial-gradient(ellipse 100% 70% at 80% 80%, rgba(190,140,50,0.16) 0%, transparent 50%),
                radial-gradient(ellipse 80% 60% at 50% 50%, rgba(220,180,90,0.10) 0%, transparent 40%),
                radial-gradient(ellipse 100% 100% at 50% 50%, #fbf3e6 0%, #f2e2c4 100%);'''
n1 = content.count(old_body_bg)
if n1 == 1:
    content = content.replace(old_body_bg, new_body_bg, 1)
    print("✅ Fondo principal cambiado a tonos cálidos crema/dorado")
else:
    print(f"⚠️ No coincide el fondo principal (encontrado {n1} veces)")

old_before = '''            background:
                radial-gradient(ellipse 150% 100% at 20% 30%, rgba(255,255,255,0.10) 0%, transparent 50%),
                radial-gradient(ellipse 130% 80% at 75% 60%, rgba(200,255,200,0.06) 0%, transparent 45%);'''
new_before = '''            background:
                radial-gradient(ellipse 150% 100% at 20% 30%, rgba(255,255,255,0.15) 0%, transparent 50%),
                radial-gradient(ellipse 130% 80% at 75% 60%, rgba(255,215,120,0.10) 0%, transparent 45%);'''
n2 = content.count(old_before)
if n2 == 1:
    content = content.replace(old_before, new_before, 1)
    print("✅ Destellos de fondo ajustados a tono cálido")
else:
    print(f"⚠️ No coincide el overlay de destellos (encontrado {n2} veces)")

old_html_fallback = '''        html { color-scheme: light only; background: #e0ece0; }'''
new_html_fallback = '''        html { color-scheme: light only; background: #fbf3e6; }'''
n3 = content.count(old_html_fallback)
if n3 == 1:
    content = content.replace(old_html_fallback, new_html_fallback, 1)
    print("✅ Color de respaldo (html) actualizado")
elif n3 == 0 and 'html { color-scheme: light only;' not in content:
    print("ℹ️ No se encontró la regla de respaldo (puede que no se haya aplicado el parche anterior, no es grave)")
else:
    print(f"⚠️ No coincide el fallback de html (encontrado {n3} veces)")

with open('templates/client/card.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nProceso completo.")
