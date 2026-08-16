with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Nuevo catálogo de premios con probabilidades
old_rewards = '''    def get_scratch_rewards(self):
        return {
            'ALOE': {'name': 'Aloe Individual', 'icon': '🌿'},
            'TEA': {'name': 'Té NRG Individual', 'icon': '🍵'},
            'PANCAKE': {'name': 'Panquecito Individual', 'icon':
'🥞'},
            'COFFEE': {'name': 'Café Herbalife Individual', 'icon': '☕ '}
        }'''
new_rewards = '''    def get_scratch_rewards(self):
        return {
            'CUPCAKE': {'name': 'Cupcake Gratis', 'icon': '🧁', 'weight': 50},
            'COFFEE': {'name': 'Café Herbalife Individual', 'icon': '☕', 'weight': 12.5},
            'TEA': {'name': 'Té Individual', 'icon': '🍵', 'weight': 12.5},
            'ALOE': {'name': 'Aloe Individual', 'icon': '🌿', 'weight': 12.5},
            'PROTEIN': {'name': 'Porción de Proteína Extra', 'icon': '💪', 'weight': 12.5}
        }

    def select_scratch_reward(self):
        rewards = self.get_scratch_rewards()
        codes = list(rewards.keys())
        weights = [rewards[c]['weight'] for c in codes]
        chosen = random.choices(codes, weights=weights, k=1)[0]
        self.scratch_reward = chosen
        return chosen'''

if old_rewards in content:
    content = content.replace(old_rewards, new_rewards)
    print("✅ Catálogo de premios actualizado con nuevas probabilidades")
else:
    print("⚠️ No se encontró el bloque exacto de get_scratch_rewards (revisar manualmente)")

# 2. claim_welcome_scratch: usar selección ponderada en vez de random.choice uniforme
old_welcome = '''    def claim_welcome_scratch(self):
        if not self.welcome_scratch_used:
            rewards = list(self.get_scratch_rewards().keys())
            reward = random.choice(rewards)
            self.welcome_scratch_used = True
            self.points += 5
            db.session.commit()
            return reward
        return None'''
new_welcome = '''    def claim_welcome_scratch(self):
        if not self.welcome_scratch_used:
            reward = self.select_scratch_reward()
            self.welcome_scratch_used = True
            self.points += 5
            db.session.commit()
            return reward
        return None'''
if old_welcome in content:
    content = content.replace(old_welcome, new_welcome)
    print("✅ Rascadita de bienvenida usando selección ponderada")
else:
    print("⚠️ No se encontró el bloque exacto de claim_welcome_scratch")

# 3. claim_scratch: el premio ya fue elegido antes (en la visita 5), aquí solo se revela
old_claim = '''    def claim_scratch(self):
        if self.scratch_available and not self.scratch_used:
            rewards = list(self.get_scratch_rewards().keys())
            reward = random.choice(rewards)
            self.scratch_reward = reward
            self.scratch_used = True
            self.scratch_available = False
            self.scratch_visits_used += 5
            db.session.commit()
            return reward
        return None'''
new_claim = '''    def claim_scratch(self):
        if self.scratch_available and not self.scratch_used:
            reward = self.scratch_reward
            self.scratch_used = True
            self.scratch_available = False
            self.scratch_visits_used += 5
            db.session.commit()
            return reward
        return None'''
if old_claim in content:
    content = content.replace(old_claim, new_claim)
    print("✅ claim_scratch ahora solo revela el premio ya asignado (no lo vuelve a sortear)")
else:
    print("⚠️ No se encontró el bloque exacto de claim_scratch")

# 4. add_visit: el premio se sortea y se guarda en la visita 5 de cada ciclo de 10
old_trigger = '''        if self.visits % 5 == 0 and not self.scratch_available and not self.scratch_used:
            self.scratch_available = True'''
new_trigger = '''        cycle_progress = self.get_cycle_progress()
        if cycle_progress == 5 and not self.scratch_available:
            self.select_scratch_reward()
            self.scratch_available = True
            self.scratch_used = False'''
if old_trigger in content:
    content = content.replace(old_trigger, new_trigger)
    print("✅ El premio de la rascadita ahora se sortea en la visita 5 de cada ciclo de 10")
else:
    print("⚠️ No se encontró el bloque exacto del disparador de rascadita en add_visit")

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nProceso completo. Revisa que todo diga ✅, ninguno debe decir ⚠️")
