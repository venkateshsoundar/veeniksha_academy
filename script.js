const $=(s,c=document)=>c.querySelector(s), $$=(s,c=document)=>[...c.querySelectorAll(s)];

const menu=$('.menu-toggle'), nav=$('.nav-links');
menu?.addEventListener('click',()=>{const open=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(open));});
$$('.nav-links a').forEach(a=>a.addEventListener('click',()=>nav.classList.remove('open')));

const reveals=$$('.reveal');
if('IntersectionObserver' in window){
  const io=new IntersectionObserver(entries=>entries.forEach(entry=>{
    if(entry.isIntersecting){entry.target.classList.add('visible');io.unobserve(entry.target);}
  }),{threshold:.12});
  reveals.forEach(el=>io.observe(el));
}else{reveals.forEach(el=>el.classList.add('visible'));}

// Student feedback: horizontal mouse-wheel, trackpad, drag and touch scrolling.
const storySlider=$('#storySlider');
storySlider?.addEventListener('wheel',e=>{
  if(Math.abs(e.deltaY)>Math.abs(e.deltaX)){
    e.preventDefault();
    storySlider.scrollBy({left:e.deltaY,behavior:'smooth'});
  }
},{passive:false});
let isDown=false,startX=0,startScroll=0;
storySlider?.addEventListener('pointerdown',e=>{isDown=true;startX=e.clientX;startScroll=storySlider.scrollLeft;storySlider.setPointerCapture?.(e.pointerId);});
storySlider?.addEventListener('pointermove',e=>{if(isDown)storySlider.scrollLeft=startScroll-(e.clientX-startX);});
['pointerup','pointercancel','pointerleave'].forEach(evt=>storySlider?.addEventListener(evt,()=>{isDown=false;}));

const form=$('#registrationForm'), status=$('#formStatus');
const APPS_SCRIPT_URL='YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL';
form?.addEventListener('submit',async e=>{
  e.preventDefault();
  status.className='form-status';
  if(form.website.value)return;
  if(!form.checkValidity()){
    form.reportValidity();
    status.textContent='Please complete the required fields.';
    status.classList.add('error');
    return;
  }
  const btn=$('.submit-btn',form),old=btn.innerHTML;
  btn.disabled=true; btn.textContent='Sending registration…';
  const payload=Object.fromEntries(new FormData(form).entries());
  payload.source='veeniksha-website'; payload.submittedAt=new Date().toISOString();
  if(APPS_SCRIPT_URL.startsWith('YOUR_')){
    status.textContent='Registration UI is ready; Google Apps Script must be connected before live submission.';
    status.classList.add('error'); btn.disabled=false; btn.innerHTML=old; return;
  }
  try{
    await fetch(APPS_SCRIPT_URL,{method:'POST',mode:'no-cors',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify(payload)});
    form.reset(); status.textContent='Thank you — your registration has been received.'; status.classList.add('success');
  }catch(err){
    status.textContent='We could not submit right now. Please try again or contact Veeniksha on WhatsApp.'; status.classList.add('error');
  }finally{btn.disabled=false;btn.innerHTML=old;}
});