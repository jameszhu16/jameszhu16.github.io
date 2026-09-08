(() => {
  "use strict";

  /* Footer year */
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* Reveal on scroll — anything already on screen fades in at once, the rest
     as it scrolls into view.

     Elements arriving together are staggered rather than shown in the same
     frame: a whole screen appearing at once reads as no animation at all. The
     delay is capped so the last element in a batch never waits long. */
  const STEP = 70;        // ms between neighbours in a batch
  const STEP_MAX = 6;     // 420ms of stagger at most

  const revealEls = Array.from(document.querySelectorAll(".reveal"));
  const pending = new Set(revealEls);

  // tells the inline script in the head that this file loaded, so it leaves
  // the hidden-until-revealed styling in place
  window.__reveal = true;

  const show = (el, order = 0) => {
    pending.delete(el);
    if (order > 0) {
      el.style.transitionDelay = Math.min(order, STEP_MAX) * STEP + "ms";
    }
    el.classList.add("is-visible");
  };

  // "on screen" for the first pass: a hair short of the fold, so an element
  // only just peeking over the bottom edge still gets to fade in on scroll
  const onScreen = (el) =>
    el.getBoundingClientRect().top < window.innerHeight * 0.88;

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      // stagger the batch that crossed together, in the order the elements sit
      // on the page rather than the order the observer happens to report them
      entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        .forEach((entry, i) => {
          show(entry.target, i);
          io.unobserve(entry.target);
        });
    }, {
      // A zero threshold with the root pulled up from the bottom fires as the
      // element's top edge rises into view. Asking instead for a fraction of
      // the element (threshold: 0.12) never fires for a section taller than
      // about eight screens, since that fraction is never on screen at once.
      threshold: 0,
      rootMargin: "0px 0px -12% 0px",
    });

    let onscreen = 0;
    revealEls.forEach((el) => {
      if (onScreen(el)) show(el, onscreen++);
      else io.observe(el);
    });

    /* Repair, not a blanket backstop. Layout moves after the first pass — the
       webfont swaps in, the hero photo lands — and an observer can in principle
       miss an element. This shows whatever *should already be visible* and
       leaves the rest to the scroll, because revealing the whole document on a
       timer is what made the scroll animation invisible in the first place:
       everything below the fold was already faded in before you got there. */
    const repair = () => {
      if (!pending.size) return;
      pending.forEach((el) => {
        if (onScreen(el)) {
          el.style.transitionDelay = "";
          show(el);
        }
      });
      if (!pending.size) window.removeEventListener("scroll", repair);
    };
    window.addEventListener("load", repair);
    window.addEventListener("scroll", repair, { passive: true });
    setTimeout(repair, 1200);
  } else {
    revealEls.forEach((el) => show(el));
  }
})();
