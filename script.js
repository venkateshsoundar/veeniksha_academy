const menuButton=document.querySelector('.menu-toggle');
const navLinks=document.querySelector('.nav-links');
menuButton?.addEventListener('click',()=>{const open=navLinks.classList.toggle('open');menuButton.setAttribute('aria-expanded',String(open));});
document.querySelectorAll('.nav-links a').forEach(a=>a.addEventListener('click',()=>{navLinks.classList.remove('open');menuButton?.setAttribute('aria-expanded','false');}));

const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target);}});},{threshold:.12});
document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));

// Replace this value once with the Web App URL produced by the Google Apps Script
// included in /google-apps-script/Code.gs. The page will then save registrations
// to the Google Sheet and send the confirmation email automatically.
const APPS_SCRIPT_URL='PASTE_GOOGLE_APPS_SCRIPT_WEB_APP_URL_HERE';

const form=document.getElementById('registrationForm');
const statusBox=document.getElementById('formStatus');
const submitBtn=document.getElementById('submitBtn');

function showStatus(message,type='info'){
  if(!statusBox)return;
  statusBox.textContent=message;
  statusBox.className=`form-status show ${type}`;
}

function isConfigured(){
  return APPS_SCRIPT_URL.startsWith('https://script.google.com/macros/s/');
}

form?.addEventListener('submit',async event=>{
  event.preventDefault();
  if(!form.checkValidity()){
    form.reportValidity();
    showStatus('Please complete all required fields before registering.','error');
    return;
  }

  const data=Object.fromEntries(new FormData(form).entries());
  if(data.website){return;}
  delete data.website;
  data.source='Veeniksha Website';
  data.submittedAt=new Date().toISOString();

  if(!isConfigured()){
    showStatus('The new website form is ready, but the Google Sheet connection needs its one-time Apps Script deployment URL. Until that is connected, please use the original Google Form link below so your registration is not lost.','info');
    return;
  }

  submitBtn.disabled=true;
  submitBtn.querySelector('span')?.replaceChildren(document.createTextNode('Registering…'));
  showStatus('Submitting your registration…','info');

  try{
    const response=await fetch(APPS_SCRIPT_URL,{
      method:'POST',
      headers:{'Content-Type':'text/plain;charset=utf-8'},
      body:JSON.stringify(data),
      redirect:'follow'
    });
    if(!response.ok)throw new Error('Submission failed');
    const result=await response.json();
    if(result.ok!==true)throw new Error(result.message||'Submission failed');
    const firstName=(data.fullName||'').trim().split(/\s+/)[0]||'there';
    showStatus(`Thank you, ${firstName}. Your registration has been received and a confirmation email has been sent to ${data.email}. We will contact you shortly.`, 'success');
    form.reset();
  }catch(error){
    console.error(error);
    showStatus('We could not submit the registration right now. Please use the original Google Form link below or contact Veeniksha on WhatsApp.','error');
  }finally{
    submitBtn.disabled=false;
    submitBtn.querySelector('span')?.replaceChildren(document.createTextNode('Register Now'));
  }
});
