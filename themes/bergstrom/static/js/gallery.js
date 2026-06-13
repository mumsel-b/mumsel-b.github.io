(function () {
  'use strict';

  // ---- Lightbox ----
  var lightbox = document.getElementById('lightbox');
  var lbImg = document.getElementById('lightbox-img');
  var lbTitle = document.getElementById('lightbox-title');
  var lbMeta = document.getElementById('lightbox-meta');
  var lbCollection = document.getElementById('lightbox-collection');

  var currentDeck = [];
  var currentIndex = 0;

  function openLightbox(deck, index) {
    currentDeck = deck;
    currentIndex = index;
    var d = deck[index];
    lbImg.src = d.full;
    lbImg.alt = d.title || '';
    lbTitle.textContent = d.title || '';
    lbMeta.textContent = d.meta || '';
    lbCollection.textContent = d.collection || '';
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
    openLightbox(currentDeck, (currentIndex + 1) % currentDeck.length);
  }

  function showPrev() {
    openLightbox(currentDeck, (currentIndex - 1 + currentDeck.length) % currentDeck.length);
  }

  function setupLightboxControls() {
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

  // ---- Painting gallery ----
  function initGallery() {
    var cards = Array.from(document.querySelectorAll('.painting-card[data-full]'));
    if (!cards.length) return;

    var deck = cards.map(function (card) {
      return {
        full: card.dataset.full,
        title: card.dataset.title || '',
        meta: card.dataset.meta || '',
        collection: card.dataset.collection || ''
      };
    });

    cards.forEach(function (card, i) {
      card.addEventListener('click', function () { openLightbox(deck, i); });
      card.setAttribute('tabindex', '0');
      card.setAttribute('role', 'button');
      card.setAttribute('aria-label', 'View painting: ' + (card.dataset.title || ''));
      card.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openLightbox(deck, i);
        }
      });
    });
  }

  // ---- Content photo galleries ----
  function initContentGallery() {
    var galleries = document.querySelectorAll('.content-gallery');
    galleries.forEach(function (gallery) {
      var imgs = Array.from(gallery.querySelectorAll('img'));
      if (!imgs.length) return;

      var deck = imgs.map(function (img) {
        return { full: img.dataset.full || img.src, title: img.alt || '', meta: '', collection: '' };
      });

      imgs.forEach(function (img, i) {
        img.addEventListener('click', function () {
          openLightbox(deck, i);
        });
      });
    });
  }

  // ---- Publication book covers ----
  function initPubGallery() {
    var imgs = Array.from(document.querySelectorAll('.pub-item img[data-full]'));
    imgs.forEach(function (img) {
      img.style.cursor = 'zoom-in';
      img.addEventListener('click', function () {
        openLightbox([{ full: img.dataset.full, title: img.alt || '', meta: '', collection: '' }], 0);
      });
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

    nav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  function run() {
    try { setupLightboxControls(); } catch(e) {}
    try { initGallery(); } catch(e) {}
    try { initContentGallery(); } catch(e) {}
    try { initPubGallery(); } catch(e) {}
    try { initSlideshow(); } catch(e) {}
    try { initNav(); } catch(e) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
