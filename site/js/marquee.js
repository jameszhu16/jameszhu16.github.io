(() => {
  "use strict";

  /* The band of company marks on the home page scrolls slowly and endlessly.

     The markup ships one plain row of logos — complete and correct on its own.
     This clones that row until the track is wide enough to loop seamlessly and
     starts it moving. Scripts off, this file failing, or "reduce motion" all
     leave the single row, which is a finished thing rather than a fallback. */

  const marquee = document.querySelector("[data-marquee]");
  if (!marquee) return;

  const view = marquee.querySelector(".marquee__viewport");
  const track = marquee.querySelector(".marquee__track");
  const group = marquee.querySelector(".marquee__group");
  if (!view || !track || !group) return;

  // Reduce motion asks for less movement, not less content: the logos are
  // already there, so nothing needs to happen.
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const SPEED = 50;   // px per second — a drift, not a ticker

  function start() {
    // The gap belongs to the track, so a group's share of the loop is its own
    // width plus one gap; translating by exactly that puts the next copy where
    // this one started and the seam is invisible.
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    const span = group.getBoundingClientRect().width + gap;
    if (!span) return;

    // Enough copies to cover the visible strip twice: one screen's worth is on
    // show while the next is queued off to the right, so the loop never runs
    // out of logos before it restarts.
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
    marquee.classList.add("is-rolling");
  }

  // Measure once the logos have their real widths; before that a group can
  // measure short and the loop would jump at the seam.
  if (document.readyState === "complete") start();
  else window.addEventListener("load", start);
})();
