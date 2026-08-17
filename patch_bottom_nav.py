with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_start = '''    <div class="container">
        <div class="premium-header">'''
new_start = '''    <div id="view-inicio" class="app-view active">
    <div class="container">
        <div class="premium-header">'''

old_end = '''                </div>
            </div>
        </div>
    </div>
    <div class="notification" id="notification">'''
new_end = '''                </div>
            </div>
        </div>
    </div>
    </div>

    <!-- ===== CATÁLOGO ===== -->
    <div id="view-catalogo" class="app-view">
        <div class="container">
            <div class="premium-header">
                <div class="tag">★ MI TARJETA</div>
                <div class="title-row">
                    <span class="club">MI CLUB</span>
                    <span class="etla">ETLA</span>
                </div>
                <div class="sub">CATÁLOGO DE PRODUCTOS</div>
            </div>
            <div class="premium-card" style="min-height:auto;">
                {% if products %}
                <div class="catalogo-grid">
                    {% for p in products %}
                    <div class="catalogo-item">
                        {% if p.image_url %}
                            <img src="{{ p.image_url }}" alt="{{ p.name }}">
                        {% else %}
                            <div class="catalogo-no-image">🥤</div>
                        {% endif %}
                        <div class="catalogo-info">
                            <div class="catalogo-name">{{ p.name }}</div>
                            {% if p.description %}<div class="catalogo-desc">{{ p.description }}</div>{% endif %}
                            {% if p.price %}<div class="catalogo-price">${{ '%.2f'|format(p.price) }}</div>{% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="catalogo-empty">🛍️ Muy pronto verás aquí nuestros productos</div>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- ===== PERFIL ===== -->
    <div id="view-perfil" class="app-view">
        <div class="container">
            <div class="premium-header">
                <div class="tag">★ MI TARJETA</div>
                <div class="title-row">
                    <span class="club">MI CLUB</span>
                    <span class="etla">ETLA</span>
                </div>
                <div class="sub">MI PERFIL</div>
            </div>
            <div class="premium-card tier-{{ client.get_tier_name()|lower }}" style="min-height:auto;">
                <div class="client-info-row" style="margin-top:8px;">
                    <div class="client-avatar">{{ client.name[0]|upper }}</div>
                    <div>
                        <div class="client-name">{{ client.name }}</div>
                        <div class="client-status">
                            <span class="dot"></span> {{ client.get_tier_name() }}
                        </div>
                    </div>
                </div>
                <div class="info-grid" style="margin-top:16px;">
                    <div class="info-card">
                        <div class="label">WhatsApp</div>
                        <div class="value" style="font-size:14px;">{{ client.whatsapp }}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Cumpleaños</div>
                        <div class="value" style="font-size:14px;">{% if client.birthday %}{{ client.birthday.strftime('%d/%m') }}{% else %}No registrado{% endif %}</div>
                    </div>
                </div>
                <div class="info-grid">
                    <div class="info-card">
                        <div class="label">Código de Referido</div>
                        <div class="value">{{ client.referral_code or '---' }}</div>
                    </div>
                    <div class="info-card">
                        <div class="label">Referidos Válidos</div>
                        <div class="value green">{{ client.referrals_valid or 0 }}</div>
                    </div>
                </div>
                <a href="https://wa.me/?text={{ ('¡Únete al Club de Nutrición Etla! Usa mi código ' + (client.referral_code or '')) | urlencode }}" target="_blank" class="whatsapp-share-btn">📱 Compartir mi código por WhatsApp</a>
            </div>
        </div>
    </div>

    <!-- ===== BARRA DE NAVEGACIÓN INFERIOR ===== -->
    <nav class="bottom-nav">
        <button class="nav-btn active" data-view="inicio" onclick="switchView('inicio')">
            <span class="nav-icon">🏠</span>
            <span class="nav-label">Inicio</span>
        </button>
        <button class="nav-btn" data-view="catalogo" onclick="switchView('catalogo')">
            <span class="nav-icon">🛍️</span>
            <span class="nav-label">Catálogo</span>
        </button>
        <button class="nav-btn" data-view="perfil" onclick="switchView('perfil')">
            <span class="nav-icon">👤</span>
            <span class="nav-label">Perfil</span>
        </button>
    </nav>

    <div class="notification" id="notification">'''

n_start = content.count(old_start)
n_end = content.count(old_end)

if old_start in content and old_end in content:
    content = content.replace(old_start, new_start, 1)
    content = content.replace(old_end, new_end, 1)
    print("✅ Barra de navegación y vistas Catálogo/Perfil insertadas")
else:
    print(f"⚠️ No coincide (start found={n_start}, end found={n_end}) - revisar manualmente")

nav_css = '''
        /* ===== NAVEGACIÓN INFERIOR ===== */
        body { padding-bottom: 90px; }
        .app-view { display: none; }
        .app-view.active { display: block; animation: fadeUp 0.3s ease; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .catalogo-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; position: relative; z-index: 1; }
        .catalogo-item { background: rgba(255,255,255,0.5); border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.3); }
        .catalogo-item img { width: 100%; height: 100px; object-fit: cover; display: block; }
        .catalogo-no-image { width: 100%; height: 100px; display: flex; align-items: center; justify-content: center; font-size: 32px; background: rgba(0,0,0,0.03); }
        .catalogo-info { padding: 10px; }
        .catalogo-name { font-size: 13px; font-weight: 800; color: #000000; }
        .catalogo-desc { font-size: 11px; color: #000000; opacity: 0.5; margin-top: 2px; }
        .catalogo-price { font-size: 14px; font-weight: 700; color: #2d7a2d; margin-top: 4px; }
        .catalogo-empty { text-align: center; padding: 30px 10px; opacity: 0.4; font-size: 14px; position: relative; z-index: 1; }
        .whatsapp-share-btn {
            display: block; text-align: center; margin-top: 16px; padding: 14px;
            background: linear-gradient(135deg, #25D366, #128C7E); color: #fff;
            border-radius: 14px; text-decoration: none; font-weight: 700; font-size: 14px;
            position: relative; z-index: 1;
        }
        .bottom-nav {
            position: fixed; bottom: 0; left: 0; width: 100%;
            display: flex; justify-content: space-around;
            background: rgba(252,248,244,0.92);
            backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border-top: 1px solid rgba(212,160,23,0.15);
            box-shadow: 0 -8px 30px rgba(0,0,0,0.06);
            padding: 8px 0 max(8px, env(safe-area-inset-bottom));
            z-index: 500;
        }
        .nav-btn {
            background: none; border: none; display: flex; flex-direction: column;
            align-items: center; gap: 2px; padding: 6px 18px; cursor: pointer;
            color: rgba(0,0,0,0.35); border-radius: 12px; transition: all 0.25s;
        }
        .nav-btn .nav-icon { font-size: 20px; }
        .nav-btn .nav-label { font-size: 10px; font-weight: 700; letter-spacing: 0.3px; }
        .nav-btn.active { color: #d4a017; background: rgba(212,160,23,0.08); }
    </style>'''

if 'NAVEGACIÓN INFERIOR' not in content:
    content = content.replace('    </style>', nav_css, 1)
    print("✅ Estilos de la barra de navegación agregados")
else:
    print("ℹ️ Ya existían los estilos de navegación")

switch_js = '''
        // ============================================================
        // NAVEGACIÓN INFERIOR
        // ============================================================
        function switchView(viewName) {
            document.querySelectorAll('.app-view').forEach(v => v.classList.remove('active'));
            document.getElementById('view-' + viewName).classList.add('active');
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.querySelector('.nav-btn[data-view="' + viewName + '"]').classList.add('active');
            window.scrollTo(0, 0);
        }
'''
if 'function switchView' not in content:
    content = content.replace('    <script>\n', '    <script>\n' + switch_js, 1)
    print("✅ Función switchView agregada")
else:
    print("ℹ️ switchView ya existía")

with open('templates/client/card.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nProceso completo. Revisa que todo diga ✅, ninguno debe decir ⚠️")
