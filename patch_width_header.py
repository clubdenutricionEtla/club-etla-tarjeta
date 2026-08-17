with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Arreglar el ancho: dar 100% de ancho explícito a las vistas
old_appview = '''        .app-view { display: none; }'''
new_appview = '''        .app-view { display: none; width: 100%; }'''
n1 = content.count(old_appview)
if n1 == 1:
    content = content.replace(old_appview, new_appview, 1)
    print("✅ Ancho corregido: la tarjeta ahora usa todo el espacio disponible")
else:
    print(f"⚠️ No coincide .app-view (encontrado {n1} veces)")

# 2. Etiqueta "★ MI TARJETA" - hacerla legible sobre fondo claro
old_tag = '''        .premium-header .tag {
            font-size: 10px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 3px;
            text-transform: uppercase;
            background: rgba(0,0,0,0.15);
            padding: 4px 16px;
            border-radius: 20px;
            display: inline-block;
            backdrop-filter: blur(4px);
        }'''
new_tag = '''        .premium-header .tag {
            font-size: 10px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 3px;
            text-transform: uppercase;
            background: rgba(45,74,26,0.85);
            padding: 4px 16px;
            border-radius: 20px;
            display: inline-block;
            backdrop-filter: blur(4px);
        }'''
n2 = content.count(old_tag)
if n2 == 1:
    content = content.replace(old_tag, new_tag, 1)
    print("✅ Etiqueta MI TARJETA con fondo sólido oscuro (legible)")
else:
    print(f"⚠️ No coincide .tag (encontrado {n2} veces)")

# 3. "MI CLUB" - texto oscuro en vez de blanco
old_club = '''        .premium-header .title-row .club {
            font-size: 30px;
            font-weight: 900;
            color: #ffffff;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 20px rgba(0,0,0,0.10);
        }'''
new_club = '''        .premium-header .title-row .club {
            font-size: 30px;
            font-weight: 900;
            color: #1a1a1a;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 12px rgba(255,255,255,0.4);
        }'''
n3 = content.count(old_club)
if n3 == 1:
    content = content.replace(old_club, new_club, 1)
    print("✅ MI CLUB en color oscuro (legible)")
else:
    print(f"⚠️ No coincide .club (encontrado {n3} veces)")

# 4. Subtítulo "CLUB DE NUTRICIÓN ETLA" - texto oscuro
old_sub = '''        .premium-header .sub {
            font-size: 10px;
            color: rgba(255,255,255,0.6);
            letter-spacing: 2.5px;
            text-transform: uppercase;
            margin-top: 2px;
            font-weight: 400;
        }'''
new_sub = '''        .premium-header .sub {
            font-size: 10px;
            color: rgba(30,30,30,0.55);
            letter-spacing: 2.5px;
            text-transform: uppercase;
            margin-top: 2px;
            font-weight: 600;
        }'''
n4 = content.count(old_sub)
if n4 == 1:
    content = content.replace(old_sub, new_sub, 1)
    print("✅ Subtítulo en color oscuro (legible)")
else:
    print(f"⚠️ No coincide .sub (encontrado {n4} veces)")

with open('templates/client/card.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nProceso completo. Revisa que todo diga ✅.")
