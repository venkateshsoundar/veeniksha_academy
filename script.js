const menuButton=document.querySelector('.menu-toggle');
const navLinks=document.querySelector('.nav-links');
menuButton?.addEventListener('click',()=>{const open=navLinks.classList.toggle('open');menuButton.setAttribute('aria-expanded',String(open));});
document.querySelectorAll('.nav-links a').forEach(a=>a.addEventListener('click',()=>{navLinks.classList.remove('open');menuButton?.setAttribute('aria-expanded','false');}));

// Use the clean, high-resolution image supplied by the user.
const approvedImage='assets/monisha-clean.jpg?v=20260823-2013';
document.querySelectorAll('.image-frame img,.guru-photo img').forEach(img=>{
  img.src=approvedImage;
  img.removeAttribute('srcset');
  img.style.display='block';
  img.style.opacity='1';
  img.style.filter='none';
  img.style.imageRendering='auto';
  img.addEventListener('error',()=>{
    const holder=img.parentElement;
    img.style.display='none';
    if(holder && !holder.querySelector('.image-load-fallback')){
      const fallback=document.createElement('div');
      fallback.className='image-load-fallback';
      fallback.textContent='Veeniksha · Veena Music';
      fallback.style.cssText='min-height:320px;display:grid;place-items:center;color:#f1bf60;background:linear-gradient(135deg,#0b2348,#071b3a);font-family:serif;font-size:28px;text-align:center;padding:24px;';
      holder.appendChild(fallback);
    }
  },{once:true});
});

const revealEls=document.querySelectorAll('.reveal');
if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target);}});},{threshold:.12});revealEls.forEach(el=>observer.observe(el));}else{revealEls.forEach(el=>el.classList.add('visible'));}
document.querySelectorAll('.faq-list details').forEach(item=>item.addEventListener('toggle',()=>{if(item.open){document.querySelectorAll('.faq-list details').forEach(other=>{if(other!==item)other.open=false;});}}));
