(() => {
  "use strict";

  /* The bands that drift sideways on the home page: the athletes, and the
     company marks below them running the other way.

     Each ships as one plain row that wraps like ordinary content — complete and
     readable standing still. This clones that row until the track can loop
     without a gap, then switches it to a single non-wrapping line and starts it
     moving. Scripts off, this file failing, or "reduce motion" all leave the
     wrapped row, which is a finished thing rather than a fallback. */

  const bands = Array.from(document.querySelectorAll("[data-marquee]"));
  if (!bands.length) return;

  // Reduce motion asks for less movement, not less content: the rows are
  // already there and already readable, so nothing needs to happen.
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const SPEED = 50;   // px per second — a drift, not a ticker

  function measure(band) {
    const view = band.querySelector(".marquee__viewport");
    const track = band.querySelector(".marquee__track");
    const group = band.querySelector(".marquee__group");
    if (!view || !track || !group) return;

    // Measure on one unwrapped line — the width that matters is the width the
    // row will have once it is rolling, not the wrapped height it has now.
    band.classList.add("is-rolling");

    // The gap belongs to the track, so a group's share of the loop is its own
    // width plus one gap; translating by exactly that puts the next copy where
    // this one started and the seam is invisible.
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    const span = group.getBoundingClientRect().width + gap;
    if (!span) {
      band.classList.remove("is-rolling");
      return;
    }

    // Enough copies to cover the visible strip twice. That also covers the
    // worst case for either direction — the track has to outlast one full
    // span plus a screenful — since copies * span >= 2 * view implies
    // copies * span >= span + view whether span is the larger term or not.
    const want = Math.max(2, Math.ceil((view.clientWidth * 2) / span));
    for (let i = track.children.length; i < want; i++) {
      const copy = group.cloneNode(true);
      // one voice, not five: a screen reader reads the original row only
      copy.setAttribute("aria-hidden", "true");
      copy.querySelectorAll("img").forEach((im) => { im.alt = ""; });
      track.appendChild(copy);
    }

    track.style.setProperty("--marquee-span", span + "px");
    track.style.animationDuration = span / SPEED + "s";
  }

  function start(band) {
    measure(band);
    // The row's width is not settled for good: the marks are lazy-loaded and
    // can arrive after this runs, and the window can be resized or turned.
    // Either changes what one loop is worth, and a stale figure makes the seam
    // jump, so re-derive it whenever the row actually changes size.
    const group = band.querySelector(".marquee__group");
    if (group && "ResizeObserver" in window) {
      let last = Math.round(group.getBoundingClientRect().width);
      new ResizeObserver(() => {
        const now = Math.round(group.getBoundingClientRect().width);
        if (now && now !== last) {
          last = now;
          measure(band);
        }
      }).observe(group);
    }
  }

  // Wait for the marks themselves: an image that has not loaded contributes no
  // width, and below the fold on a phone that is the normal case at load. A
  // group measured then comes out short and the loop lands in the wrong place.
  function whenMarksReady(done) {
    const imgs = bands.flatMap((b) => Array.from(b.querySelectorAll("img")));
    const pending = imgs.filter((im) => !im.complete || !im.naturalWidth);
    if (!pending.length) return done();
    let left = pending.length;
    // Lazy images below the fold may never load until scrolled to, so this is
    // a head start, not a gate: the ResizeObserver above corrects the span
    // whenever they do arrive.
    const timer = window.setTimeout(done, 1200);
    const tick = () => {
      if (--left) return;
      window.clearTimeout(timer);
      done();
    };
    pending.forEach((im) => {
      im.addEventListener("load", tick, { once: true });
      im.addEventListener("error", tick, { once: true });
    });
  }

  const startAll = () => whenMarksReady(() => bands.forEach(start));

  if (document.readyState === "complete") startAll();
  else window.addEventListener("load", startAll);
})();
