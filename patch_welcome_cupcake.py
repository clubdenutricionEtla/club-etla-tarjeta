# ============================================================
# 1. app.py - la rascadita de bienvenida siempre es Cupcake
# ============================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

old_welcome_select = '''    if has_welcome and not client.scratch_reward:
        client.select_scratch_reward()
        db.session.commit()'''
new_welcome_select = '''    if has_welcome and not client.scratch_reward:
        client.scratch_reward = 'CUPCAKE'
        db.session.commit()'''
n1 = app_content.count(old_welcome_select)
if n1 == 1:
    app_content = app_content.replace(old_welcome_select, new_welcome_select, 1)
    print("✅ Rascadita de bienvenida fijada siempre a Cupcake")
else:
    print(f"⚠️ No coincide en app.py (encontrado {n1} veces)")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)

# ============================================================
# 2. models.py - claim_welcome_scratch también siempre Cupcake
# ============================================================
with open('models.py', 'r', encoding='utf-8') as f:
    models_content = f.read()

old_claim_welcome = '''    def claim_welcome_scratch(self):
        if not self.welcome_scratch_used:
            reward = self.select_scratch_reward()
            self.welcome_scratch_used = True
            self.points += 5
            db.session.commit()
            return reward
        return None'''
new_claim_welcome = '''    def claim_welcome_scratch(self):
        if not self.welcome_scratch_used:
            self.scratch_reward = 'CUPCAKE'
            reward = 'CUPCAKE'
            self.welcome_scratch_used = True
            self.points += 5
            db.session.commit()
            return reward
        return None'''
n2 = models_content.count(old_claim_welcome)
if n2 == 1:
    models_content = models_content.replace(old_claim_welcome, new_claim_welcome, 1)
    print("✅ claim_welcome_scratch fijado siempre a Cupcake")
else:
    print(f"⚠️ No coincide en models.py (encontrado {n2} veces)")

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(models_content)

# ============================================================
# 3. scratch.html - mensaje invitando a visitar el club + umbral 15%
# ============================================================
with open('templates/client/scratch.html', 'r', encoding='utf-8') as f:
    scratch_content = f.read()

old_desc = '''document.getElementById('resultDesc').textContent = IS_WELCOME ? '¡Bienvenido al Club de Nutrición Etla!' : '¡Gracias por tu visita número 5!';'''
new_desc = '''document.getElementById('resultDesc').textContent = IS_WELCOME ? '¡Visita el Club de Nutrición Etla para reclamar tu cupcake! 🧁' : '¡Gracias por tu visita número 5!';'''
n3 = scratch_content.count(old_desc)
if n3 == 1:
    scratch_content = scratch_content.replace(old_desc, new_desc, 1)
    print("✅ Mensaje de invitación a visitar el club agregado")
else:
    print(f"⚠️ No coincide el mensaje en scratch.html (encontrado {n3} veces)")

old_threshold = '''if(percent > 15 && !isRevealed){'''
new_threshold = '''if(percent >= 15 && !isRevealed){'''
n4 = scratch_content.count(old_threshold)
if n4 == 1:
    scratch_content = scratch_content.replace(old_threshold, new_threshold, 1)
    print("✅ Umbral de revelado confirmado en 15%")
else:
    print(f"⚠️ No coincide el umbral (encontrado {n4} veces)")

with open('templates/client/scratch.html', 'w', encoding='utf-8') as f:
    f.write(scratch_content)

print("\nProceso completo. Revisa que todo diga ✅.")
