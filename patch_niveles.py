import re

# ============================================================
# 1. models.py
# ============================================================
with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'cycle_month' not in content:
    content = content.replace(
        "    qr_secret = db.Column(db.String(64), unique=True)",
        "    qr_secret = db.Column(db.String(64), unique=True)\n    cycle_month = db.Column(db.String(7), nullable=True)"
    )
    print("✅ Columna cycle_month agregada al modelo")
else:
    print("ℹ️ cycle_month ya existía en el modelo")

if 'def check_monthly_reset' not in content:
    anchor = "    def get_level(self):"
    method_code = '''    def check_monthly_reset(self):
        current_month = date.today().strftime('%Y-%m')
        if self.cycle_month != current_month:
            self.cycle_month = current_month
            self.visits = 0
            self.points = 0
            self.breakfast_count = 0
            self.free_breakfast_available = False
            self.scratch_available = False
            self.scratch_used = False
            self.scratch_reward = None
            self.scratch_visits_used = 0
            db.session.commit()

    def get_tier_index(self):
        if self.visits <= 0:
            return 0
        return min((self.visits - 1) // 10, 3)

    def get_tier_name(self):
        tiers = ['BRONCE', 'PLATA', 'ORO', 'DIAMANTE']
        return tiers[self.get_tier_index()]

    def get_cycle_progress(self):
        if self.visits <= 0:
            return 0
        return ((self.visits - 1) % 10) + 1

'''
    content = content.replace(anchor, method_code + anchor)
    print("✅ Métodos de nivel/ciclo agregados")
else:
    print("ℹ️ check_monthly_reset ya existía")

old_add_visit_start = "    def add_visit(self, product_type='BREAKFAST', employee_id=None):\n        from config import Config"
new_add_visit_start = "    def add_visit(self, product_type='BREAKFAST', employee_id=None):\n        from config import Config\n        self.check_monthly_reset()"
if "self.check_monthly_reset()" not in content:
    content = content.replace(old_add_visit_start, new_add_visit_start)
    print("✅ add_visit ahora llama check_monthly_reset")
else:
    print("ℹ️ add_visit ya llamaba check_monthly_reset")

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(content)

# ============================================================
# 2. app.py
# ============================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

old_card_route = "@app.route('/card')\ndef card():\n    client = get_client_from_session()\n    if not client:\n        return redirect(url_for('login'))"
if "client.check_monthly_reset()" not in app_content:
    new_card_route = old_card_route + "\n    client.check_monthly_reset()"
    app_content = app_content.replace(old_card_route, new_card_route)
    print("✅ Ruta /card ahora verifica el reinicio mensual")
else:
    print("ℹ️ /card ya llamaba check_monthly_reset")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)

# ============================================================
# 3. templates/client/card.html
# ============================================================
with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    card_content = f.read()

old_front = '                <div class="card-front">\n                    <div class="premium-card">'
new_front = '                <div class="card-front">\n                    <div class="premium-card tier-{{ client.get_tier_name()|lower }}">'
if 'tier-{{' not in card_content:
    card_content = card_content.replace(old_front, new_front)
    print("✅ Clase de nivel agregada a la tarjeta frontal")
else:
    print("ℹ️ La tarjeta ya tenía clase de nivel")

old_status = '''                                <div class="client-status">
                                    <span class="dot"></span> MIEMBRO ACTIVO
                                </div>'''
new_status = '''                                <div class="client-status">
                                    <span class="dot"></span> MIEMBRO ACTIVO · {{ client.get_tier_name() }}
                                </div>'''
if '· {{ client.get_tier_name() }}' not in card_content:
    card_content = card_content.replace(old_status, new_status)
    print("✅ Etiqueta de nivel agregada junto a Miembro Activo")
else:
    print("ℹ️ La etiqueta de nivel ya existía")

old_vasos = '''                            <div class="vasos-grid" id="vasosGrid">
                                {% for i in range(1, 11) %}
                                    {% set is_completed = i <= client.visits %}'''
new_vasos = '''                            <div class="vasos-grid" id="vasosGrid">
                                {% set cycle_progress = client.get_cycle_progress() %}
                                {% for i in range(1, 11) %}
                                    {% set is_completed = i <= cycle_progress %}'''
if 'cycle_progress' not in card_content:
    card_content = card_content.replace(old_vasos, new_vasos)
    print("✅ Jarritas usando el progreso del ciclo actual")
else:
    print("ℹ️ Las jarritas ya usaban el progreso del ciclo")

old_count = '''                            <div class="progress-text">
                                Visitas: <span class="count" id="visitsCount">{{ client.visits }}</span> / 10
                            </div>'''
new_count = '''                            <div class="progress-text">
                                Visitas: <span class="count" id="visitsCount">{{ cycle_progress }}</span> / 10
                            </div>'''
if 'id="visitsCount">{{ cycle_progress }}' not in card_content:
    card_content = card_content.replace(old_count, new_count)
    print("✅ Contador de visitas usando el progreso del ciclo")
else:
    print("ℹ️ El contador ya usaba el progreso del ciclo")

tier_css = '''
        /* ===== NIVELES POR CICLO MENSUAL ===== */
        .tier-plata .vaso.destapado {
            background: linear-gradient(145deg, #c7d0d8, #98a5b0);
            box-shadow: 0 4px 16px rgba(140,152,163,0.25), inset 0 -3px 8px rgba(0,0,0,0.05), inset 0 3px 8px rgba(255,255,255,0.25);
        }
        .tier-oro .vaso.destapado {
            background: linear-gradient(145deg, #f5d060, #d4a017);
            box-shadow: 0 4px 16px rgba(212,160,23,0.25), inset 0 -3px 8px rgba(0,0,0,0.05), inset 0 3px 8px rgba(255,255,255,0.25);
        }
        .tier-diamante .vaso.destapado {
            background: linear-gradient(145deg, #9fd8ff, #4aa8e8);
            box-shadow: 0 4px 16px rgba(74,168,232,0.25), inset 0 -3px 8px rgba(0,0,0,0.05), inset 0 3px 8px rgba(255,255,255,0.25);
        }
        .tier-plata .client-status { color: #7a8894; }
        .tier-plata .client-status .dot { background: #8e9aa6; }
        .tier-oro .client-status { color: #b8860b; }
        .tier-oro .client-status .dot { background: #d4a017; }
        .tier-diamante .client-status { color: #2f7fb8; }
        .tier-diamante .client-status .dot { background: #4aa8e8; }
    </style>'''
if 'NIVELES POR CICLO MENSUAL' not in card_content:
    card_content = card_content.replace('    </style>', tier_css, 1)
    print("✅ Estilos de color por nivel agregados")
else:
    print("ℹ️ Los estilos de nivel ya existían")

with open('templates/client/card.html', 'w', encoding='utf-8') as f:
    f.write(card_content)

print("\nListo. Revisa los mensajes de arriba: todos deben decir ✅ o ℹ️, ninguno debe fallar.")
