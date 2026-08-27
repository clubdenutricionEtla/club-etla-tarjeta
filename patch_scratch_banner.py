# ============================================================
# 1. card.html - aviso de rascadita disponible
# ============================================================
with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_qr_wrapper = '''                <div class="card-front">
                    <div class="premium-card tier-{{ client.get_tier_name()|lower }}">
                        <div class="qr-wrapper">'''
new_qr_wrapper = '''                <div class="card-front">
                    <div class="premium-card tier-{{ client.get_tier_name()|lower }}">
                        {% if client.has_welcome_scratch() or (client.scratch_available and not client.scratch_used) %}
                        <a href="/scratch" style="display:block; text-align:center; background:linear-gradient(135deg,#d4a017,#f5d060); color:#3a2500; font-weight:800; font-size:13px; padding:10px 14px; border-radius:14px; text-decoration:none; margin-bottom:12px; position:relative; z-index:2;">
                            🎁 ¡Tienes una rascadita disponible! Tócala aquí
                        </a>
                        {% endif %}
                        <div class="qr-wrapper">'''

n1 = content.count(old_qr_wrapper)
if n1 == 1:
    content = content.replace(old_qr_wrapper, new_qr_wrapper, 1)
    print("✅ Aviso de rascadita disponible agregado a la tarjeta")
else:
    print(f"⚠️ No coincide en card.html (encontrado {n1} veces)")

with open('templates/client/card.html', 'w', encoding='utf-8') as f:
    f.write(content)

# ============================================================
# 2. register.html - prefijo de país por defecto
# ============================================================
with open('templates/register.html', 'r', encoding='utf-8') as f:
    reg_content = f.read()

old_input = '''<input type="tel" id="whatsapp" name="whatsapp" placeholder="WhatsApp: +5215512345678" value="{{ phone }}" required autocomplete="tel" />'''
new_input = '''<input type="tel" id="whatsapp" name="whatsapp" placeholder="WhatsApp: +5215512345678" value="{{ phone if phone else '+52' }}" required autocomplete="tel" />'''

n2 = reg_content.count(old_input)
if n2 == 1:
    reg_content = reg_content.replace(old_input, new_input, 1)
    print("✅ Prefijo +52 agregado por defecto (editable para otros países)")
else:
    print(f"⚠️ No coincide en register.html (encontrado {n2} veces)")

with open('templates/register.html', 'w', encoding='utf-8') as f:
    f.write(reg_content)

print("\nProceso completo. Revisa que todo diga ✅.")
