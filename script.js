const $=(s,c=document)=>c.querySelector(s), $$=(s,c=document)=>[...c.querySelectorAll(s)];

const menu=$('.menu-toggle'), nav=$('.nav-links');
menu?.addEventListener('click',()=>{const open=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(open));});
$$('.nav-links a').forEach(a=>a.addEventListener('click',()=>nav.classList.remove('open')));

const reveals=$$('.reveal');
if('IntersectionObserver' in window){const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target)}}),{threshold:.12});reveals.forEach(el=>io.observe(el));}else reveals.forEach(el=>el.classList.add('visible'));

let audioCtx=null,nodes=[],playing=false;
function startAmbience(){audioCtx=new(window.AudioContext||window.webkitAudioContext)();const master=audioCtx.createGain();master.gain.value=.035;master.connect(audioCtx.destination);nodes=[master];[130.81,196,261.63].forEach((f,i)=>{const o=audioCtx.createOscillator(),g=audioCtx.createGain(),lfo=audioCtx.createOscillator(),lg=audioCtx.createGain();o.type=i===1?'triangle':'sine';o.frequency.value=f;g.gain.value=i===0?.55:.18;lfo.frequency.value=.07+i*.025;lg.gain.value=1.2+i*.5;lfo.connect(lg);lg.connect(o.detune);o.connect(g);g.connect(master);o.start();lfo.start();nodes.push(o,g,lfo,lg)});playing=true}
function stopAmbience(){nodes.forEach(n=>{try{n.stop?.()}catch{}try{n.disconnect?.()}catch{}});audioCtx?.close?.();audioCtx=null;nodes=[];playing=false}
const soundBtn=$('#soundToggle');
soundBtn?.addEventListener('click',()=>{playing?stopAmbience():startAmbience();soundBtn.setAttribute('aria-pressed',String(playing));$('.sound-copy b',soundBtn).textContent=playing?'Ambience playing':'Veena ambience';$('.sound-copy small',soundBtn).textContent=playing?'Tap to pause':'Tap for a gentle meditative drone'});

// Student feedback: native horizontal scrolling for mouse wheel, trackpad and touch.
const storySlider=$('#storySlider');
storySlider?.addEventListener('wheel',e=>{if(Math.abs(e.deltaY)>Math.abs(e.deltaX)){e.preventDefault();storySlider.scrollBy({left:e.deltaY,behavior:'smooth'})}},{passive:false});
let isDown=false,startX=0,startScroll=0;
storySlider?.addEventListener('pointerdown',e=>{isDown=true;startX=e.clientX;startScroll=storySlider.scrollLeft;storySlider.setPointerCapture?.(e.pointerId)});
storySlider?.addEventListener('pointermove',e=>{if(isDown)storySlider.scrollLeft=startScroll-(e.clientX-startX)});
['pointerup','pointercancel','pointerleave'].forEach(evt=>storySlider?.addEventListener(evt,()=>{isDown=false}));

const form=$('#registrationForm'), status=$('#formStatus');
const APPS_SCRIPT_URL='YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL';
form?.addEventListener('submit',async e=>{e.preventDefault();status.className='form-status';if(form.website.value)return;if(!form.checkValidity()){form.reportValidity();status.textContent='Please complete the required fields.';status.classList.add('error');return}const btn=$('.submit-btn',form),old=btn.innerHTML;btn.disabled=true;btn.innerHTML='<span>Sending registration…</span><b>⏳</b>';const payload=Object.fromEntries(new FormData(form).entries());payload.source='veeniksha-website';payload.submittedAt=new Date().toISOString();if(APPS_SCRIPT_URL.startsWith('YOUR_')){status.textContent='Registration UI is ready; Google Apps Script must be connected before live submission.';status.classList.add('error');btn.disabled=false;btn.innerHTML=old;return}try{await fetch(APPS_SCRIPT_URL,{method:'POST',mode:'no-cors',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify(payload)});form.reset();status.textContent='Thank you — your registration has been received.';status.classList.add('success')}catch(err){status.textContent='We could not submit right now. Please try again or contact Veeniksha on WhatsApp.';status.classList.add('error')}finally{btn.disabled=false;btn.innerHTML=old}});