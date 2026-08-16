import re

# ============================================================
# 1. app.py - decidir el premio de bienvenida ANTES de mostrar la página
# ============================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

pattern = re.compile(
    r"(if not has_welcome and not has_normal:\s*\n\s*return redirect\(url_for\('card'\)\)\s*\n)(\s*return render_template\('client/scratch\.html')"
)
if 'select_scratch_reward()' not in app_content.split("def scratch()")[1].split("def ")[0] if "def scratch()" in app_content else True:
    new_app_content, n = pattern.subn(
        r"\1    if has_welcome and not client.scratch_reward:\n        client.select_scratch_reward()\n        db.session.commit()\n\2",
        app_content
    )
    if n > 0:
        app_content = new_app_content
        print(f"✅ Ruta /scratch actualizada ({n} reemplazo)")
    else:
        print("⚠️ No se encontró el patrón de la ruta /scratch (revisar manualmente)")
else:
    print("ℹ️ La ruta /scratch ya tenía la lógica de selección previa")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)

# ============================================================
# 2. templates/client/scratch.html
# ============================================================
with open('templates/client/scratch.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 2.1 - Reemplazar el catálogo REWARDS del JS + agregar las constantes del servidor
rewards_pattern = re.compile(r"const REWARDS = \{.*?\};", re.DOTALL)
new_rewards_block = """const REWARDS = {
        'CUPCAKE': { name: '🧁 Cupcake Gratis', icon: '🧁' },
        'COFFEE': { name: '☕ Café Herbalife Individual', icon: '☕' },
        'TEA': { name: '🍵 Té Individual', icon: '🍵' },
        'ALOE': { name: '🌿 Aloe Individual', icon: '🌿' },
        'PROTEIN': { name: '💪 Porción de Proteína Extra', icon: '💪' }
    };
    const SERVER_REWARD = "{{ client.scratch_reward or '' }}";
    const IS_WELCOME = {{ 'true' if is_welcome else 'false' }};"""

content, n1 = rewards_pattern.subn(new_rewards_block, content, count=1)
print(f"✅ Catálogo REWARDS + constantes del servidor agregadas ({n1} reemplazo)" if n1 else "⚠️ No se encontró el bloque REWARDS")

# 2.2 - Usar el premio del servidor en vez de elegir al azar
old_pick = "const rewardKey = keys[Math.floor(Math.random() * keys.length)];"
new_pick = "const rewardKey = (SERVER_REWARD && REWARDS[SERVER_REWARD]) ? SERVER_REWARD : keys[0];"
if old_pick in content:
    content = content.replace(old_pick, new_pick)
    print("✅ El premio ahora viene del servidor, no se elige al azar en el navegador")
else:
    print("⚠️ No se encontró la línea de selección aleatoria del premio")

# 2.3 - Llamar al endpoint correcto según sea rascadita de bienvenida o de ciclo
old_fetch = "fetch('/api/scratch/welcome/claim', {"
new_fetch = "fetch(IS_WELCOME ? '/api/scratch/welcome/claim' : '/api/scratch/claim', {"
if old_fetch in content:
    content = content.replace(old_fetch, new_fetch)
    print("✅ El endpoint de canje ahora depende de si es rascadita de bienvenida o de ciclo")
else:
    print("⚠️ No se encontró la línea del fetch a welcome/claim")

# 2.4 - Mensaje distinto si es bienvenida vs rascadita de ciclo
old_desc = "document.getElementById('resultDesc').textContent = '¡Bienvenido al Club de Nutrición Etla!';"
new_desc = "document.getElementById('resultDesc').textContent = IS_WELCOME ? '¡Bienvenido al Club de Nutrición Etla!' : '¡Gracias por tu visita número 5!';"
if old_desc in content:
    content = content.replace(old_desc, new_desc)
    print("✅ Mensaje de resultado diferenciado por tipo de rascadita")
else:
    print("⚠️ No se encontró la línea del mensaje de bienvenida")

with open('templates/client/scratch.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nProceso completo. Revisa que todo diga ✅, ninguno debe decir ⚠️")
