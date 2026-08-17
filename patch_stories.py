with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Reemplazar el grid del catálogo por el visor tipo historias
old_catalogo = '''            <div class="premium-card" style="min-height:auto;">
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
            </div>'''

new_catalogo = '''            <div class="premium-card" style="min-height:auto; padding: 12px;">
                {% if products %}
                <div class="story-container" id="storyContainer">
                    <div class="story-progress" id="storyProgress">
                        {% for p in products %}
                        <div class="segment"><div class="fill"></div></div>
                        {% endfor %}
                    </div>
                    {% for p in products %}
                    <div class="story-slide {% if loop.first %}active{% endif %}" data-index="{{ loop.index0 }}">
                        {% if p.image_url %}
                            <img src="{{ p.image_url }}" alt="{{ p.name }}">
                        {% else %}
                            <div class="catalogo-no-image" style="height:100%;">🥤</div>
                        {% endif %}
                        <div class="story-caption">
                            <div class="story-name">{{ p.name }}</div>
                            {% if p.price %}<div class="story-price">${{ '%.2f'|format(p.price) }}</div>{% endif %}
                            {% if p.description %}<div class="story-desc">{{ p.description }}</div>{% endif %}
                        </div>
                    </div>
                    {% endfor %}
                    <div class="story-tap-zone left" onclick="prevStory()"></div>
                    <div class="story-tap-zone right" onclick="nextStory()"></div>
                </div>
                {% else %}
                <div class="catalogo-empty">🛍️ Muy pronto verás aquí nuestros productos</div>
                {% endif %}
            </div>'''

n1 = content.count(old_catalogo)
if n1 == 1:
    content = content.replace(old_catalogo, new_catalogo, 1)
    print("✅ Catálogo convertido a visor tipo historias")
else:
    print(f"⚠️ No coincide el bloque del catálogo (encontrado {n1} veces)")

# 2. CSS del visor de historias
old_css_end = '''        .nav-btn.active { color: #d4a017; background: rgba(212,160,23,0.08); }
    </style>'''
new_css_end = '''        .nav-btn.active { color: #d4a017; background: rgba(212,160,23,0.08); }

        /* ===== HISTORIAS DE PRODUCTOS ===== */
        .story-container {
            position: relative;
            width: 100%;
            max-width: 380px;
            aspect-ratio: 9 / 19.5;
            margin: 0 auto;
            border-radius: 20px;
            overflow: hidden;
            background: #111;
            box-shadow: 0 20px 60px rgba(0,0,0,0.20);
        }
        .story-progress {
            position: absolute; top: 8px; left: 8px; right: 8px;
            display: flex; gap: 4px; z-index: 5;
        }
        .story-progress .segment {
            flex: 1; height: 3px; border-radius: 2px;
            background: rgba(255,255,255,0.3); overflow: hidden;
        }
        .story-progress .segment .fill {
            height: 100%; width: 0%; background: #fff;
        }
        .story-progress .segment.completed .fill { width: 100%; }
        .story-slide {
            position: absolute; inset: 0; display: none;
        }
        .story-slide.active { display: block; }
        .story-slide img { width: 100%; height: 100%; object-fit: cover; display: block; }
        .story-slide .story-caption {
            position: absolute; bottom: 0; left: 0; right: 0;
            padding: 24px 16px 16px;
            background: linear-gradient(to top, rgba(0,0,0,0.80), transparent);
            color: #fff; z-index: 2;
        }
        .story-slide .story-name { font-size: 18px; font-weight: 800; }
        .story-slide .story-price { font-size: 15px; font-weight: 700; color: #ffd700; margin-top: 2px; }
        .story-slide .story-desc { font-size: 12px; opacity: 0.85; margin-top: 4px; }
        .story-tap-zone { position: absolute; top: 0; bottom: 0; width: 50%; z-index: 4; }
        .story-tap-zone.left { left: 0; }
        .story-tap-zone.right { right: 0; }
    </style>'''

n2 = content.count(old_css_end)
if n2 == 1:
    content = content.replace(old_css_end, new_css_end, 1)
    print("✅ Estilos del visor de historias agregados")
else:
    print(f"⚠️ No coincide el final del CSS (encontrado {n2} veces)")

# 3. JS de navegación de historias
old_js_end = '''            window.scrollTo(0, 0);
        }'''
new_js_end = '''            window.scrollTo(0, 0);
        }

        // ============================================================
        // HISTORIAS DE PRODUCTOS (CATÁLOGO)
        // ============================================================
        let storyIndex = 0;
        const storySlides = document.querySelectorAll('.story-slide');
        const storySegments = document.querySelectorAll('.story-progress .segment');
        const storyCount = storySlides.length;

        function showStory(i) {
            storySlides.forEach((s, idx) => s.classList.toggle('active', idx === i));
            storySegments.forEach((seg, idx) => {
                seg.classList.toggle('completed', idx <= i);
            });
            storyIndex = i;
        }
        function nextStory() {
            if (storyCount === 0) return;
            showStory((storyIndex + 1) % storyCount);
        }
        function prevStory() {
            if (storyCount === 0) return;
            showStory((storyIndex - 1 + storyCount) % storyCount);
        }
        if (storyCount > 0) showStory(0);'''

n3 = content.count(old_js_end)
if n3 == 1:
    content = content.replace(old_js_end, new_js_end, 1)
    print("✅ Navegación de historias (JS) agregada")
else:
    print(f"⚠️ No coincide el final del JS (encontrado {n3} veces)")

with open('templates/client/card.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nProceso completo. Revisa que todo diga ✅.")
