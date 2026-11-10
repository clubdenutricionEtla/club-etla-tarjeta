(function(){
var P=document.querySelector('#cardWrapper .card-front .premium-card');
if(P){
var box=document.createElement('div');box.className='hq-front';
['.front-logo-wrap','.qr-wrapper','.qr-hint'].forEach(function(sel){
var el=P.querySelector(':scope > '+sel);
if(el)box.appendChild(el);
});
var ref=P.querySelector(':scope > .client-info-row');
P.insertBefore(box,ref?ref.nextSibling:P.firstChild);
}
var h=document.querySelector('#cardWrapper .back-hours');
if(h){h.innerHTML='<span class="ico">🕒</span><span class="hrs">7:00 AM – 3:00 PM<br>6:00 PM – 10:00 PM</span>';}
})();
