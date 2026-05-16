// Mocking the environment window for assets/data.js
if (typeof window !== 'undefined') {
  window.CONSTANTS = window.CONSTANTS || {};
}

function syncData() {
  const elements = document.querySelectorAll('[data-const]');
  elements.forEach(el => {
    const key = el.dataset.const;
    if (window.CONSTANTS && window.CONSTANTS[key]) {
      el.innerText = window.CONSTANTS[key];
    }
  });
}

document.addEventListener('DOMContentLoaded', syncData);
// Also hook into Reveal.js slide changes to ensure dynamic updates
if (typeof Reveal !== 'undefined') {
  Reveal.on('ready', syncData);
  Reveal.on('slidechanged', syncData);
}
