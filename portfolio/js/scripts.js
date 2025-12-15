// Minimal JS pour toggles et menu mobile
document.addEventListener('DOMContentLoaded', function(){
  // Toggle projets - afficher/masquer code
  document.querySelectorAll('[data-toggle]').forEach(function(btn){
    btn.addEventListener('click', function(){
      var id = btn.getAttribute('data-toggle');
      var el = document.getElementById(id);
      if(!el) return;
      el.style.display = (el.style.display === 'block') ? 'none' : 'block';
    });
  });

  // Mobile nav toggle simple
  var navToggle = document.getElementById('navToggle');
  if(navToggle){
    navToggle.addEventListener('click', function(){
      var nav = document.querySelector('.nav');
      if(!nav) return;
      nav.style.display = (nav.style.display === 'flex') ? 'none' : 'flex';
      nav.style.flexDirection = 'column';
      nav.style.background = 'linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))';
      nav.style.position = 'absolute';
      nav.style.right = '1rem';
      nav.style.top = '60px';
      nav.style.padding = '0.8rem';
      nav.style.borderRadius = '8px';
    });
  }

  // Contact form: open mail client with prefilled fields (fallback for static site)
  var contactForm = document.getElementById('contactForm');
  if(contactForm){
    contactForm.addEventListener('submit', function(e){
      e.preventDefault();
      var name = (contactForm.querySelector('[name=name]') || {}).value || '';
      var email = (contactForm.querySelector('[name=email]') || {}).value || '';
      var message = (contactForm.querySelector('[name=message]') || {}).value || '';
      var subject = encodeURIComponent('Contact portfolio - ' + name);
      var body = encodeURIComponent('Nom: ' + name + '\nEmail: ' + email + '\n\n' + message);
      // Remplacer votre.email@example.com par votre adresse
      window.location.href = 'mailto:votre.email@example.com?subject=' + subject + '&body=' + body;
    });
  }
});