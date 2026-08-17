with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_end = '''                        </div>
                    </div>
                </div>

            </div>
        </div>

    </div>

    <div class="notification" id="notification">'''
new_end = '''                        </div>
                    </div>
                </div>

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

n_end = content.count(old_end)
print(f"Coincidencias encontradas: {n_end}")

if n_end == 1:
    content = content.replace(old_end, new_end, 1)
    with open('templates/client/card.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Catálogo, Perfil y barra de navegación insertados correctamente")
else:
    print("⚠️ No coincide, hace falta revisar más de cerca")
