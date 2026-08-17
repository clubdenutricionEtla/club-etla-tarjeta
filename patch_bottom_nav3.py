with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_start = '''    <div class="container">

        <div class="premium-header">'''
new_start = '''    <div id="view-inicio" class="app-view active">
    <div class="container">

        <div class="premium-header">'''

n_start = content.count(old_start)
print(f"Coincidencias encontradas para el inicio: {n_start}")

if n_start == 1:
    content = content.replace(old_start, new_start, 1)
    with open('templates/client/card.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Etiqueta de apertura view-inicio insertada correctamente")
else:
    print("⚠️ Todavía no coincide, hace falta revisar más de cerca")
