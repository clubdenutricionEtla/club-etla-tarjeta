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
