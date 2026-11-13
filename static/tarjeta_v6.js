(function(){
var qr=document.querySelector('#cardWrapper .qr-wrapper');
if(!qr)return;
qr.addEventListener('click',function(e){
e.stopPropagation();
var img=qr.querySelector('img');
if(!img||document.getElementById('qrBig'))return;
var nm=document.querySelector('#cardWrapper .v6-name');
var o=document.createElement('div');o.id='qrBig';
var t=document.createElement('p');t.textContent='MUESTRA ESTE CÓDIGO';t.style.cssText='letter-spacing:3px;font-size:12px;color:#8a6410';
var im=document.createElement('img');im.src=img.src;
var n=document.createElement('p');n.textContent=nm?nm.textContent:'';n.style.cssText='font-size:20px;font-weight:700';
var c=document.createElement('p');c.textContent='Toca para cerrar';c.style.cssText='font-size:12px;color:#888';
o.appendChild(t);o.appendChild(im);o.appendChild(n);o.appendChild(c);
o.addEventListener('click',function(ev){ev.stopPropagation();o.remove();});
document.body.appendChild(o);
});
})();
(function(){
document.querySelectorAll('#cardWrapper a[href]').forEach(function(a){
a.addEventListener('click',function(e){e.stopPropagation();});
});
})();
(function(){
['click','touchstart','touchend','pointerdown','pointerup','mousedown','mouseup'].forEach(function(t){
document.addEventListener(t,function(e){
if(e.target.closest&&e.target.closest('#cardWrapper .v6 a[href]'))e.stopPropagation();
},true);
});
})();
(function(){
function pn(){var n=document.querySelector('#cardWrapper .v6-name');var t=n?n.textContent.trim().split(/\s+/)[0]:'';return t?t.charAt(0).toUpperCase()+t.slice(1).toLowerCase():'';}
var el=document.getElementById('v6Hi');
if(el){
var h=new Date().getHours(),n=pn();
var s=h<12?'Buenos días':(h<19?'Buenas tardes':'Buenas noches');
var P=['Qué gusto tenerte en la familia Etla 💚','Gracias por ser parte de este club 🌿','Tu constancia nos inspira ✨','Aquí siempre eres bienvenido 😊','Qué bonito verte cuidar de ti 💪','Cada visita tuya nos alegra el día 🥤','Estamos muy orgullosos de ti 🌟','Hoy es un gran día para tu bienestar 💚'];
var x=P[Math.floor(Math.random()*P.length)];
el.textContent='¡'+s+(n&&Math.random()<0.4?', '+n:'')+'! '+x;
}
document.querySelectorAll('#cardWrapper .v6-soc a, #cardWrapper .v6-wa').forEach(function(a){
a.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();window.open(a.href,'_blank','noopener');},true);
});
})();
(function(){
var tag=document.querySelector('#view-inicio .premium-header .tag');
if(!tag)return;
tag.innerHTML='<div class="v6-tk"><span id="v6TkTxt"></span></div>';
var box=tag.firstChild,sp=document.getElementById('v6TkTxt');
var F=['💚 Tu bienestar es lo que más importa','✨ Cada paso cuenta, sigue así','🥤 Nutrición en cada vaso','🌿 Hoy es un buen día para cuidarte','💪 La constancia da resultados','😊 Qué gusto que seas parte del club','🌟 Pequeños hábitos, grandes cambios','🍎 Tu mejor versión se construye hoy','💚 Gracias por ser parte de la familia Etla','🔥 ¡Tú puedes con todo!','🌞 Empieza el día con energía','🏆 Cada visita te acerca a tu premio'];
for(var i=F.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=F[i];F[i]=F[j];F[j]=t;}
var promos=[],fi=0,pi=0,c=0;
function fmt(m){var h=Math.floor(m/60),mi=m%60,ap=h>=12?'PM':'AM';h=h%12||12;return h+':'+(mi<10?'0':'')+mi+' '+ap;}
function hora(){var d=new Date(),m=d.getHours()*60+d.getMinutes(),n=fmt(m);
if(m>=420&&m<900)return '🕒 '+n+' · Abierto hasta las 3:00 PM';
if(m>=900&&m<1020)return '🕒 '+n+' · Reabrimos a las 5:00 PM';
if(m>=1020&&m<1320)return '🕒 '+n+' · Abierto hasta las 10:00 PM';
if(m<420)return '🕒 '+n+' · Abrimos a las 7:00 AM';
return '🕒 '+n+' · Mañana abrimos a las 7:00 AM';}
function next(){c++;
if(promos.length&&c%3===0){var p=promos[pi++%promos.length];return p.charCodeAt(0)<128?'🎁 '+p:p;}
if(c%5===0)return hora();
return F[fi++%F.length];}
var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function show(){
var txt=next();
sp.textContent=txt;
sp.style.transition='none';sp.style.transform='translateX(110%)';sp.style.opacity='0';
void sp.offsetWidth;
if(reduce){sp.style.transform='none';sp.style.opacity='1';}
else{sp.style.transition='transform .45s ease, opacity .45s ease';sp.style.transform='translateX(0)';sp.style.opacity='1';}
var over=Math.max(0,sp.offsetWidth-box.clientWidth);
var dwell=2000+(over>0?over*22+900:0);
if(over>0){setTimeout(function(){sp.style.transition='transform '+(over/45)+'s linear';sp.style.transform='translateX(-'+over+'px)';},800);}
setTimeout(function(){
if(!reduce){sp.style.transition='transform .4s ease, opacity .4s ease';sp.style.transform='translateX(-110%)';sp.style.opacity='0';}
setTimeout(show,reduce?0:450);
},450+dwell);
}
fetch('/api/ticker',{credentials:'same-origin'}).then(function(r){return r.ok?r.json():null;}).then(function(j){if(j&&j.items)promos=j.items.map(function(x){return String(x.text||x).trim();}).filter(Boolean);}).catch(function(){});
show();
})();
