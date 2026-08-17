with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_body = '''        body {
            font-family: 'Inter', -apple-system, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;'''
new_body = '''        body {
            font-family: 'Inter', -apple-system, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding: 16px;
            padding-top: 8px;'''

n = content.count(old_body)
if n == 1:
    content = content.replace(old_body, new_body, 1)
    print("✅ El contenido ahora empieza desde arriba, sin espacio vacío grande")
else:
    print(f"⚠️ No coincide (encontrado {n} veces)")

with open('templates/client/card.html', 'w', encoding='utf-8') as f:
    f.write(content)
