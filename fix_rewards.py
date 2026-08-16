with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_rewards = """    def get_scratch_rewards(self):
        return {
            'ALOE': {'name': 'Aloe Individual', 'icon': '🌿'},
            'TEA': {'name': 'Té NRG Individual', 'icon': '🍵'},
            'PANCAKE': {'name': 'Panquecito Individual', 'icon': '🥞'},
            'COFFEE': {'name': 'Café Herbalife Individual', 'icon': '☕ '}
        }"""

new_rewards = """    def get_scratch_rewards(self):
        return {
            'CUPCAKE': {'name': 'Cupcake Gratis', 'icon': '🧁', 'weight': 50},
            'COFFEE': {'name': 'Café Herbalife Individual', 'icon': '☕', 'weight': 12.5},
            'TEA': {'name': 'Té Individual', 'icon': '🍵', 'weight': 12.5},
            'ALOE': {'name': 'Aloe Individual', 'icon': '🌿', 'weight': 12.5},
            'PROTEIN': {'name': 'Porción de Proteína Extra', 'icon': '💪', 'weight': 12.5}
        }"""

if old_rewards in content:
    content = content.replace(old_rewards, new_rewards)
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Catálogo de premios actualizado")
else:
    print("❌ Todavía no coincide, hace falta revisar manualmente")
