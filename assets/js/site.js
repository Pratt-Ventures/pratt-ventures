/* Pratt Ventures — interaction layer. Progressive enhancement only. */
(function () {
  'use strict';

  /* Sticky header */
  var hdr = document.querySelector('.hdr');
  if (hdr) {
    var stuck = false;
    var onScroll = function () {
      var should = window.scrollY > 24;
      if (should !== stuck) { stuck = should; hdr.classList.toggle('is-stuck', should); }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* Mobile drawer */
  var burger = document.querySelector('.burger');
  var drawer = document.getElementById('drawer');
  if (burger && drawer) {
    var links = drawer.querySelectorAll('a');
    var setOpen = function (open) {
      burger.setAttribute('aria-expanded', String(open));
      drawer.classList.toggle('is-open', open);
      document.body.classList.toggle('is-locked', open);
      drawer.setAttribute('aria-hidden', String(!open));
      if (open) {
        links.forEach(function (a, i) { a.style.animationDelay = (0.05 + i * 0.032) + 's'; });
      }
    };
    burger.addEventListener('click', function () {
      setOpen(burger.getAttribute('aria-expanded') !== 'true');
    });
    drawer.addEventListener('click', function (e) { if (e.target.tagName === 'A') setOpen(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') { setOpen(false); burger.focus(); }
    });
  }

  /* Scroll reveal */
  var targets = document.querySelectorAll('.rv');
  if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    targets.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -9% 0px', threshold: 0.08 });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* Current year */
  var y = document.querySelectorAll('[data-year]');
  y.forEach(function (el) { el.textContent = String(new Date().getFullYear()); });
})();
