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

  // Dynamic percentage circles
  function updateProgressCircles() {
    // Find all progress circles in the statistics section
    const progressCircles = document.querySelectorAll('.progress-circle circle:last-child');

    progressCircles.forEach(function(circle) {
      const svg = circle.closest('svg');
      const percentageText = svg.parentElement.querySelector('p:first-of-type');
      if (!percentageText) return;

      const percentage = parseInt(percentageText.textContent.replace('%', ''));
      if (isNaN(percentage)) return;

      // Check if this is the main statistics circle (larger radius)
      const isMainCircle = svg.classList.contains('main-stat-circle');
      const radius = isMainCircle ? 85 : 60; // Main circle has radius 85, others have 60
      const circumference = 2 * Math.PI * radius;

      // Calculate the dash array based on percentage
      const dashArray = (percentage / 100) * circumference;
      const gap = circumference - dashArray;

      // Update the stroke-dasharray
      circle.style.strokeDasharray = `${dashArray} ${gap}`;
    });
  }

  // Initial update of progress circles
  updateProgressCircles();

  // Optional: Add mutation observer to watch for changes in percentage text
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'childList' || mutation.type === 'characterData') {
        updateProgressCircles();
      }
    });
  });

  // Observe changes in the statistics section
  const statsSection = document.querySelector('.projects-grid');
  if (statsSection) {
    observer.observe(statsSection, {
      childList: true,
      subtree: true,
      characterData: true
    });
  }

  // Function to manually update percentage (can be called from console or other scripts)
  window.updatePercentageCircle = function(cardIndex, newPercentage) {
    // Handle main statistics circle (index 0 is now the main circle)
    if (cardIndex === 0) {
      const mainCard = document.querySelector('.main-stat-circle');
      if (!mainCard) return;
      
      const percentageText = mainCard.parentElement.querySelector('p:first-of-type');
      const circle = mainCard.querySelector('circle:last-child');
      
      if (!percentageText || !circle) return;
      
      // Update the text
      percentageText.textContent = newPercentage + '%';
      
      // Update the circle (main circle has radius 85)
      const radius = 85;
      const circumference = 2 * Math.PI * radius;
      const dashArray = (newPercentage / 100) * circumference;
      const gap = circumference - dashArray;
      
      circle.style.strokeDasharray = `${dashArray} ${gap}`;
      return;
    }
    
    // Handle specific tool cards (now indices 1, 2, 3 instead of 0, 1, 2)
    const actualIndex = cardIndex - 1;
    const cards = document.querySelectorAll('.projects-grid .card');
    if (actualIndex < 0 || actualIndex >= cards.length) return;

    const card = cards[actualIndex];
    const percentageText = card.querySelector('p:first-of-type');
    const circle = card.querySelector('svg circle:last-child');

    if (!percentageText || !circle) return;

    // Update the text
    percentageText.textContent = newPercentage + '%';

    // Update the circle
    const radius = 60;
    const circumference = 2 * Math.PI * radius;
    const dashArray = (newPercentage / 100) * circumference;
    const gap = circumference - dashArray;

    circle.style.strokeDasharray = `${dashArray} ${gap}`;
  };
});