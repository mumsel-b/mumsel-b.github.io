(function () {
  'use strict';

  // ---- Lightbox ----
  var lightbox = document.getElementById('lightbox');
  var lbImg = document.getElementById('lightbox-img');
  var lbTitle = document.getElementById('lightbox-title');
  var lbMeta = document.getElementById('lightbox-meta');
  var lbCollection = document.getElementById('lightbox-collection');

  var cards = [];
  var currentIndex = 0;

  function openLightbox(index) {
    currentIndex = index;
    var card = cards[index];
    lbImg.src = card.dataset.full;
    lbImg.alt = card.dataset.title || '';
    lbTitle.textContent = card.dataset.title || '';
    lbMeta.textContent = card.dataset.meta || '';
    lbCollection.textContent = card.dataset.collection || '';
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
    lightbox.focus();
  }

  function closeLightbox() {
    lightbox.classList.remove('open');
    document.body.style.overflow = '';
    lbImg.src = '';
  }

  function showNext() {
    openLightbox((currentIndex + 1) % cards.length);
  }

  function showPrev() {
    openLightbox((currentIndex - 1 + cards.length) % cards.length);
  }

  function initGallery() {
    cards = Array.from(document.querySelectorAll('.painting-card[data-full]'));
    if (!cards.length) return;

    cards.forEach(function (card, i) {
      card.addEventListener('click', function () { openLightbox(i); });
      card.setAttribute('tabindex', '0');
      card.setAttribute('role', 'button');
      card.setAttribute('aria-label', 'View painting: ' + (card.dataset.title || ''));
      card.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openLightbox(i);
        }
      });
    });

    lightbox.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
    lightbox.querySelector('.lightbox-next').addEventListener('click', showNext);
    lightbox.querySelector('.lightbox-prev').addEventListener('click', showPrev);

    lightbox.addEventListener('click', function (e) {
      if (e.target === lightbox) closeLightbox();
    });

    document.addEventListener('keydown', function (e) {
      if (!lightbox.classList.contains('open')) return;
      if (e.key === 'Escape') closeLightbox();
      if (e.key === 'ArrowRight') showNext();
      if (e.key === 'ArrowLeft') showPrev();
    });
  }

  // ---- Hero Slideshow ----
  function initSlideshow() {
    var slides = document.querySelectorAll('.hero-slide');
    var dots = document.querySelectorAll('.hero-dot');
    if (!slides.length) return;

    var current = 0;
    var interval;

    function goTo(n) {
      slides[current].classList.remove('active');
      slides[current].setAttribute('aria-hidden', 'true');
      dots[current].classList.remove('active');
      current = n % slides.length;
      slides[current].classList.add('active');
      slides[current].setAttribute('aria-hidden', 'false');
      dots[current].classList.add('active');
    }

    function next() { goTo((current + 1) % slides.length); }

    function startAuto() { interval = setInterval(next, 4000); }
    function stopAuto() { clearInterval(interval); }

    dots.forEach(function (dot, i) {
      dot.addEventListener('click', function () {
        stopAuto();
        goTo(i);
        startAuto();
      });
    });

    startAuto();
  }

  // ---- Mobile Nav Toggle ----
  function initNav() {
    var toggle = document.querySelector('.nav-toggle');
    var nav = document.querySelector('.site-nav');
    if (!toggle || !nav) return;

    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    // Close nav when a link is clicked
    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initGallery();
    initSlideshow();
    initNav();
  });
})();
