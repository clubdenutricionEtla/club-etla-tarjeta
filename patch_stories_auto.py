with open('templates/client/card.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_fill_css = '''        .story-progress .segment .fill {
            height: 100%; width: 0%; background: #fff;
        }'''
new_fill_css = '''        .story-progress .segment .fill {
            height: 100%; width: 0%; background: #fff;
            transition: width linear;
        }'''
n1 = content.count(old_fill_css)
if n1 == 1:
    content = content.replace(old_fill_css, new_fill_css, 1)
    print("✅ Transición animada de la barra de progreso agregada")
else:
    print(f"⚠️ No coincide el CSS del fill (encontrado {n1} veces)")

old_js = '''        let storyIndex = 0;
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

new_js = '''        let storyIndex = 0;
        let storyTimer = null;
        const storySlides = document.querySelectorAll('.story-slide');
        const storySegments = document.querySelectorAll('.story-progress .segment');
        const storyCount = storySlides.length;
        const STORY_DURATION = 4000;

        function showStory(i) {
            storySlides.forEach((s, idx) => s.classList.toggle('active', idx === i));
            storySegments.forEach((seg, idx) => {
                const fill = seg.querySelector('.fill');
                fill.style.transition = 'none';
                if (idx < i) {
                    fill.style.width = '100%';
                } else if (idx > i) {
                    fill.style.width = '0%';
                } else {
                    fill.style.width = '0%';
                }
            });
            storyIndex = i;

            clearTimeout(storyTimer);
            if (storyCount > 0) {
                const currentFill = storySegments[i].querySelector('.fill');
                requestAnimationFrame(() => {
                    currentFill.style.transition = 'width ' + STORY_DURATION + 'ms linear';
                    currentFill.style.width = '100%';
                });
                storyTimer = setTimeout(nextStory, STORY_DURATION);
            }
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

n2 = content.count(old_js)
if n2 == 1:
    content = content.replace(old_js, new_js, 1)
    print("✅ Avance automático de historias agregado")
else:
    print(f"⚠️ No coincide el bloque JS (encontrado {n2} veces)")

with open('templates/client/card.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nProceso completo.")
