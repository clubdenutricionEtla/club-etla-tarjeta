with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_dom = '''        document.addEventListener('DOMContentLoaded', function() {
            const visits = parseInt(document.getElementById('visitsCount')?.textContent || '0');
            if (visits === 0) {
                setTimeout(() => {
                    lanzarConfeti();
                    mostrarNotificacion('🎉 ¡Bienvenido al Club!', '✨');
                }, 800);
            }
        });'''
new_dom = '''        document.addEventListener('DOMContentLoaded', function() {
            const visits = parseInt(document.getElementById('visitsCount')?.textContent || '0');
            const clientId = "{{ client.id }}";
            const waffleKey = 'waffle_' + clientId + '_' + "{{ client.cycle_month or '' }}" + '_' + "{{ client.get_tier_index() }}";

            if (visits === 0) {
                setTimeout(() => {
                    lanzarConfeti();
                    mostrarNotificacion('🎉 ¡Bienvenido al Club!', '✨');
                }, 800);
            } else if (visits === 10 && !localStorage.getItem(waffleKey)) {
                localStorage.setItem(waffleKey, '1');
                setTimeout(() => {
                    lanzarConfeti();
                    mostrarNotificacion('🧇 ¡Lo lograste! Tu waffle es gratis.', '🎉');
                    setTimeout(() => lanzarConfeti(), 700);
                }, 800);
            }
        });'''

n = content.count(old_dom)
if n == 1:
    content = content.replace(old_dom, new_dom, 1)
    print("✅ Celebración de waffle gratis (visita 10) agregada")
else:
    print(f"⚠️ No coincide el bloque DOMContentLoaded (encontrado {n} veces)")

with open('templates/client/card.html', 'w', encoding='utf-8') as f:
    f.write(content)
