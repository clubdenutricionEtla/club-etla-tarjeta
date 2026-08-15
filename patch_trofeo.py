with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

extra_css = '''
        .tier-plata .vaso.trofeo {
            background: linear-gradient(135deg, #b8c2cc, #8e9aa6);
            border-color: rgba(142,154,166,0.3);
            box-shadow: 0 4px 24px rgba(142,154,166,0.25);
        }
        .tier-oro .vaso.trofeo {
            background: linear-gradient(135deg, #d4a017, #f5d060);
            border-color: rgba(212,160,23,0.3);
            box-shadow: 0 4px 24px rgba(212,160,23,0.25);
        }
        .tier-diamante .vaso.trofeo {
            background: linear-gradient(135deg, #4aa8e8, #9fd8ff);
            border-color: rgba(74,168,232,0.3);
            box-shadow: 0 4px 24px rgba(74,168,232,0.25);
        }
    </style>'''

if 'tier-oro .vaso.trofeo' not in content:
    content = content.replace('    </style>', extra_css, 1)
    print("✅ Colores de trofeo por nivel agregados")
else:
    print("ℹ️ Ya existían")

with open('templates/client/card.html', 'w', encoding='utf-8') as f:
    f.write(content)
