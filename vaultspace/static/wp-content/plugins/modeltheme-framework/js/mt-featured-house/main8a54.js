;(function(window){'use strict';if(jQuery('#slideshow').length){var lastTime=0;var prefixes='webkit moz ms o'.split(' ');var requestAnimationFrame=window.requestAnimationFrame;var cancelAnimationFrame=window.cancelAnimationFrame;var prefix;for(var i=0;i<prefixes.length;i++){if(requestAnimationFrame&&cancelAnimationFrame){break;}
prefix=prefixes[i];requestAnimationFrame=requestAnimationFrame||window[prefix+'RequestAnimationFrame'];cancelAnimationFrame=cancelAnimationFrame||window[prefix+'CancelAnimationFrame']||window[prefix+'CancelRequestAnimationFrame'];}
if(!requestAnimationFrame||!cancelAnimationFrame){requestAnimationFrame=function(callback,element){var currTime=new Date().getTime();var timeToCall=Math.max(0,16-(currTime-lastTime));var id=window.setTimeout(function(){callback(currTime+timeToCall);},timeToCall);lastTime=currTime+timeToCall;return id;};cancelAnimationFrame=function(id){window.clearTimeout(id);};}
var support={animations:Modernizr.cssanimations,transitions:Modernizr.csstransitions,preserve3d:Modernizr.preserve3d},animEndEventNames={'WebkitAnimation':'webkitAnimationEnd','OAnimation':'oAnimationEnd','msAnimation':'MSAnimationEnd','animation':'animationend'},animEndEventName=animEndEventNames[Modernizr.prefixed('animation')],onEndAnimation=function(el,callback){var onEndCallbackFn=function(ev){if(support.animations){if(ev.target!=this)return;this.removeEventListener(animEndEventName,onEndCallbackFn);}
if(callback&&typeof callback==='function'){callback.call();}};if(support.animations){el.addEventListener(animEndEventName,onEndCallbackFn);}
else{onEndCallbackFn();}},transEndEventNames={'WebkitTransition':'webkitTransitionEnd','MozTransition':'transitionend','OTransition':'oTransitionEnd','msTransition':'MSTransitionEnd','transition':'transitionend'},transEndEventName=transEndEventNames[Modernizr.prefixed('transition')],onEndTransition=function(el,callback){var onEndCallbackFn=function(ev){if(support.transitions){if(ev.target!=this)return;this.removeEventListener(transEndEventName,onEndCallbackFn);}
if(callback&&typeof callback==='function'){callback.call(this);}};if(support.transitions){el.addEventListener(transEndEventName,onEndCallbackFn);}
else{onEndCallbackFn();}};function extend(a,b){for(var key in b){if(b.hasOwnProperty(key)){a[key]=b[key];}}
return a;}
function throttle(fn,delay){var allowSample=true;return function(e){if(allowSample){allowSample=false;setTimeout(function(){allowSample=true;},delay);fn(e);}};}
function getMousePos(e){var posx=0;var posy=0;if(!e)var e=window.event;if(e.pageX||e.pageY){posx=e.pageX;posy=e.pageY;}
else if(e.clientX||e.clientY){posx=e.clientX+document.body.scrollLeft
+document.documentElement.scrollLeft;posy=e.clientY+document.body.scrollTop
+document.documentElement.scrollTop;}
return{x:posx,y:posy}}
function Slideshow(el,options){if(!support.preserve3d){return false;}
this.el=el;this.options=extend({},this.options);extend(this.options,options);this.slides=[].slice.call(this.el.querySelectorAll('.slide'));this.slidesTotal=this.slides.length;this.items=[].slice.call(this.el.querySelectorAll('.item'));this.nav=this.el.querySelector('.nav');this.navCtrls=[].slice.call(this.nav.querySelectorAll('.nav__item'));this.titles=[].slice.call(this.el.querySelectorAll('.titles > .title'));this.current=0;this._init();}
Slideshow.prototype.options={movement:{rotateX:3,rotateY:5}};Slideshow.prototype._init=function(){this._updateCurrent();classie.add(this.currentSlide,'slide--current');classie.add(this.navCtrls[this.current],'nav__item--current');classie.add(this.titles[this.current],'title--current');this.items.forEach(function(item){var itemImg=item.querySelector('img');itemImg.style.WebkitTransform=itemImg.style.transform='translate3d(0,0,'+itemImg.getAttribute('data-transform-z')+'px)';});this._initEvents();};Slideshow.prototype._updateCurrent=function(){this.currentSlide=this.slides[this.current];this.currentScene=this.currentSlide.querySelector('.scene');this.slideSizes={width:this.currentSlide.offsetWidth,height:this.currentSlide.offsetHeight};};Slideshow.prototype._initEvents=function(){var self=this;this.navCtrls.forEach(function(navEl,pos){navEl.addEventListener('click',function(ev){ev.preventDefault();self._navigate(pos);var mousepos=getMousePos(ev);self._rotateSlide(mousepos);});});document.addEventListener('mousemove',function(ev){requestAnimationFrame(function(){if(self.lockedTilt)return;var mousepos=getMousePos(ev);self._rotateSlide(mousepos);});});document.addEventListener('keydown',function(ev){var keyCode=ev.keyCode||ev.which;if(keyCode!==37&&keyCode!==38&&keyCode!==39&&keyCode!==40)return;switch(keyCode){case 37:if(self.current-1>=0){self._navigate(self.current-1);}
break;case 39:if(self.current+1<self.slidesTotal){self._navigate(self.current+1);}
break;case 40:if(self.current+2<self.slidesTotal){self._navigate(self.current+2);}
break;case 38:if(self.current-2>=0){self._navigate(self.current-2);}
break;}
var mousepos={x:window.innerWidth/2,y:window.innerHeight/2};self._rotateSlide(mousepos);});window.addEventListener('resize',throttle(function(ev){self.slideSizes={width:self.currentSlide.offsetWidth,height:self.currentSlide.offsetHeight};},10));};Slideshow.prototype._openItem=function(item){if(this.isItemOpen){return false;}
this.isItemOpen=true;var view=item.parentNode;view.style.zIndex=10;var views=view.parentNode;classie.add(views,'view-open');this.lockedTilt=true;this.currentScene.style.WebkitTransform=this.currentScene.style.transform='rotate3d(1,1,0,0deg)';classie.add(item,'item--popup');var itemImg=item.querySelector('img');itemImg.style.WebkitTransform=itemImg.style.transform='translate3d(0,0,0) scale3d(1.3, 1.3, 1)';[].slice.call(views.querySelectorAll('.item > img')).forEach(function(img){if(itemImg!=img){img.style.WebkitTransform=img.style.transform='translate3d(0,0,0)';}});this.currentOpenItem=item;};Slideshow.prototype._closeItem=function(item){var item=item||this.currentOpenItem;this.isItemOpen=false;var view=item.parentNode,views=view.parentNode;classie.remove(views,'view-open');classie.remove(item,'item--popup');var itemImg=item.querySelector('img'),self=this;setTimeout(function(){itemImg.style.WebkitTransform=itemImg.style.transform='translate3d(0,0,'+itemImg.getAttribute('data-transform-z')+'px)';onEndTransition(itemImg,function(){view.style.zIndex=1;self.lockedTilt=false;});},60);[].slice.call(views.querySelectorAll('.item > img')).forEach(function(img){if(itemImg!=img){img.style.WebkitTransform=img.style.transform='translate3d(0,0,'+img.getAttribute('data-transform-z')+'px)';}});};Slideshow.prototype._navigate=function(pos){if(this.isAnimating||this.current===pos){return false;}
this.isAnimating=true;if(this.isItemOpen){this._closeItem();}
var direction=this._getNavDirection(pos);classie.remove(this.navCtrls[this.current],'nav__item--current');classie.add(this.navCtrls[pos],'nav__item--current');classie.remove(this.titles[this.current],'title--current');var currentSlide=this.slides[this.current],nextSlide=this.slides[pos];this.current=pos;this._updateCurrent();classie.add(currentSlide,'to-'+direction.out);classie.add(nextSlide,'from-'+direction.in);var self=this;onEndAnimation(nextSlide,function(){classie.remove(currentSlide,'to-'+direction.out);classie.remove(nextSlide,'from-'+direction.in);classie.remove(currentSlide,'slide--current');classie.add(nextSlide,'slide--current');classie.add(self.titles[pos],'title--current');self.isAnimating=false;});};Slideshow.prototype._rotateSlide=function(mousepos){var rotX=this.options.movement.rotateX?2*this.options.movement.rotateX/this.slideSizes.height*mousepos.y-this.options.movement.rotateX:0,rotY=this.options.movement.rotateY?2*this.options.movement.rotateY/this.slideSizes.width*mousepos.x-this.options.movement.rotateY:0;this.currentScene.style.WebkitTransform=this.currentScene.style.transform='rotate3d(1,0,0,'+rotX+'deg) rotate3d(0,1,0,'+rotY+'deg)';};Slideshow.prototype._getNavDirection=function(pos){var direction={},isEven=function(val){return(val%2==0);}
if(isEven(this.current)&&isEven(pos)||!isEven(this.current)&&!isEven(pos)){if(this.current<pos){direction.in='bottom';direction.out='top';}
else{direction.in='top';direction.out='bottom';}}
else if(isEven(this.current)){if(pos===this.current+1){direction.in='right';direction.out='left';}
else if(pos<this.current){direction.in='topright';direction.out='bottomleft';}
else{direction.in='bottomright';direction.out='topleft';}}
else{if(pos===this.current-1){direction.in='left';direction.out='right';}
else if(pos<this.current){direction.in='topleft';direction.out='bottomright';}
else{direction.in='bottomleft';direction.out='topright';}}
return direction;};window.Slideshow=Slideshow;(function(){var slideshow=new Slideshow(document.getElementById('slideshow'));})();}})(window);