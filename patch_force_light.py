with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_meta = '''    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />'''
new_meta = '''    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <meta name="color-scheme" content="light only" />'''
if 'color-scheme' not in content:
    n = content.count(old_meta)
    if n == 1:
        content = content.replace(old_meta, new_meta, 1)
        print("✅ Meta tag color-scheme agregado")
    else:
        print(f"⚠️ No coincide el meta viewport (encontrado {n} veces)")
else:
    print("ℹ️ color-scheme ya existía")

old_style = '''        * { margin: 0; padding: 0; box-sizing: border-box; }'''
new_style = '''        :root { color-scheme: light only; }
        html { color-scheme: light only; background: #e0ece0; }
        * { margin: 0; padding: 0; box-sizing: border-box; }'''
if 'color-scheme: light only; }' not in content.split('<style>')[1].split('</style>')[0] if '<style>' in content else True:
    n2 = content.count(old_style)
    if n2 == 1:
        content = content.replace(old_style, new_style, 1)
        print("✅ Regla CSS color-scheme agregada")
    else:
        print(f"⚠️ No coincide el bloque de reset CSS (encontrado {n2} veces)")
else:
    print("ℹ️ La regla CSS ya existía")

with open('templates/client/card.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nProceso completo.")
