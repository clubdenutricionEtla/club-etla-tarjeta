(function(){
var box=document.querySelector('#cardWrapper .hq-front');
if(box){var lw=box.querySelector('.front-logo-wrap');if(lw)box.parentNode.insertBefore(lw,box);}
var bc=document.querySelector('#cardWrapper .card-back .back-content');
if(bc&&!bc.querySelector('.hq-back')){
var logo=bc.querySelector(':scope > .back-logo');
var panel=document.createElement('div');panel.className='hq-back';
Array.prototype.slice.call(bc.children).forEach(function(el){if(el!==logo)panel.appendChild(el);});
bc.appendChild(panel);
}
})();
