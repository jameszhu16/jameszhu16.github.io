(() => {
  "use strict";

  /* The stat numbers roll up like an odometer when the strip scrolls into view.

     The markup ships the finished text ("200K+"), and the reels are built here
     and taken back down when they finish. So scripts off, this file failing to
     load, or "reduce motion" all leave the real number on the page with nothing
     to fall back to — and once the roll is over the DOM is exactly what it was,
     which matters because the font-size is a clamp() and a reel measured at one
     viewport width would sit wrong at another. */

  const cells = Array.from(document.querySelectorAll(".strip .stat b"));
  if (!cells.length) return;

  // Reduce motion asks for less movement, not less content: the numbers are
  // already on the page, so there is simply nothing to do.
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const SPIN = 1000;       // ms for one revolution
  const DIGIT_STEP = 80;   // ms between digits within one number, left to right
  const CELL_STEP = 120;   // ms between the three numbers
  const EASE = "cubic-bezier(0.16, 1, 0.3, 1)";

  /* Build the reels for one number and return a function that starts them.
     Splitting build from start matters: everything must be laid out and
     measured before the first transition, or the first digit jumps.

     Both halves run at trigger time, never at load. Building early would leave
     the 0-9 ladders sitting in the page for anyone who never scrolls this far. */
  function build(el, cellIndex) {
    const value = el.textContent;
    if (!/[0-9]/.test(value)) return null;

    const reel = document.createElement("span");
    reel.className = "num";
    reel.setAttribute("aria-hidden", "true");

    // A screen reader should hear "200K+", never the 0-9 ladder behind it.
    const spoken = document.createElement("span");
    spoken.className = "sr-only";
    spoken.textContent = value;

    const cols = [];
    for (const ch of value) {
      if (ch < "0" || ch > "9") {
        const flat = document.createElement("span");
        flat.textContent = ch;
        reel.appendChild(flat);
        continue;
      }
      const win = document.createElement("span");
      win.className = "num__d";
      const col = document.createElement("span");
      col.className = "num__col";
      // 0 through 9 and then the target again: every digit travels exactly one
      // revolution, so three digits share one rhythm instead of the target
      // value deciding how far each one runs.
      for (let i = 0; i <= 9; i++) col.appendChild(digit(String(i)));
      col.appendChild(digit(ch));
      win.appendChild(col);
      reel.appendChild(win);
      cols.push({ win, col });
    }

    el.textContent = "";
    el.append(reel, spoken);

    // Measure after insertion. The window height cannot be assumed to be 1em:
    // line-height is 1 here and the type is set with clamp(), so a guess clips
    // the tops of the digits at some widths and not others.
    const step = cols[0].col.firstChild.getBoundingClientRect().height;
    cols.forEach(({ win }) => { win.style.height = step + "px"; });

    return () => cols.forEach(({ col }, i) => {
      col.style.transition = `transform ${SPIN}ms ${EASE}`;
      col.style.transitionDelay = cellIndex * CELL_STEP + i * DIGIT_STEP + "ms";
      col.style.transform = `translateY(${-10 * step}px)`;
    });

    function digit(ch) {
      const d = document.createElement("i");
      d.textContent = ch;
      return d;
    }
  }

  // Put the numbers back to plain text once the last reel has landed, so the
  // markup ends up where it started.
  const restore = () => cells.forEach((el) => {
    const spoken = el.querySelector(".sr-only");
    if (spoken) el.textContent = spoken.textContent;
  });

  const roll = () => {
    const starters = cells.map(build).filter(Boolean);
    if (!starters.length) return;
    // Start on the next frame so the reels are laid out at their zero position
    // first; setting the transform in the same frame they are inserted gives
    // the browser nothing to animate from and the digits simply appear.
    requestAnimationFrame(() => {
      starters.forEach((start) => start());
      const last = (cells.length - 1) * CELL_STEP + 2 * DIGIT_STEP + SPIN;
      window.setTimeout(restore, last + 120);
    });
  };

  const strip = document.querySelector(".strip");

  if (!("IntersectionObserver" in window)) {
    roll();
    return;
  }

  // Same trigger geometry as the reveal fade in js/main.js, so the numbers
  // start rolling on the very frame the strip starts fading in — one movement,
  // not two. It runs once; scrolling back does not replay it.
  const io = new IntersectionObserver((entries) => {
    if (!entries.some((e) => e.isIntersecting)) return;
    io.disconnect();
    roll();
  }, { threshold: 0, rootMargin: "0px 0px -12% 0px" });
  io.observe(strip);
})();
