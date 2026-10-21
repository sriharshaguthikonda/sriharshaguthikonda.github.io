# Website repair campaign — 2026-10-21

Full structural, layout, interaction and accessibility audit of `index.html`
and `styles.css`, executed as atomic local commits. All geometry numbers come
from Playwright/Chromium `getBoundingClientRect()` measured at 320-1280px
(including the 680/681 and 900/901 boundaries) before and after each fix.

## Confirmed and fixed

| ID | Severity | Evidence | Fix commit |
|----|----------|----------|------------|
| AUD-01 | high | `<ul>` directly inside `<ul>` in Employment (old lines 244-249) and Technical Skills (389-391); one `<li>` left unclosed around the electrophoresis figure | d3d90fe |
| AUD-02 | high | Key Skills and the featured video carried card chrome on the `section` while every other card is a nested `article`: 22px-per-side width mismatch ([311,1171] vs [333,1149] at 1280px) and a double border on `.video-frame` | fb1a76a |
| AUD-03 | high | `.section--active` added padding, margins and a border: +48px section height, following content pushed 48px at every viewport on each navigation click | cb9e425 |
| AUD-04 | medium | Two `<br>` spacers produced the 27.2px header-to-main gap and 28.2px in-main gap as text line-boxes | 9d46d77 |
| AUD-05 | medium | Poster lightbox not keyboard-operable (plain `img` with click only); focus never moved on open nor restored on close; generic iframe title | 4665063 |
| AUD-06 | low | Verbatim duplicate `u/b/em/strong` CSS block; research-poster card fully inline-styled; three empty showcase label `<p>` elements | (this commit) |
| AUD-07 | medium | `test_hero.py` asserted the retired two-line headline, so the baseline suite was red | 3c2c15f |

Post-fix measurements: all visible cards share identical edges at every
viewport ([333,1149] desktop, [17,413] at 430px); `.section--active`
geometry delta 0px; zero horizontal overflow everywhere.

## Investigated and rejected

- Compass pill hiding anchor targets: the pill is bottom-fixed while
  `block:'start'` scrolls targets to the top — no overlap exists.
- Focus restore after outside-click compass close: focus correctly follows
  the pointer target; forcing it back to the trigger would be worse.
- Horizontal overflow at any measured viewport: none found.

## Known, deliberately not changed

- Unused CSS families (story/chapter/map/life-story/indent paragraphs,
  `.cv__summary`): unused by index.html but kept for the in-progress
  Life_story page work that shares this stylesheet.
- Guarded dead JS (carousel block, `#private-contact` probe, the extra id
  in the video allowlist): provable no-ops whose removal is churn without
  user-visible gain.
- h2 inset differs between article-wrapped and plain sections: a
  pre-existing design duality, not a defect.
- Compass `preventScroll` focus nit when the docked list is scrolled:
  minor, deferred.

ACCEPT: cd C:/Domains/Website && python -m unittest discover -s tests -p 'test_*.py' says OK with at least 25 tests running; python scripts/sync_navigation.py --check says Navigation OK; file tests/test_layout_structure.py and docs/audit/2026-10-21-repair-campaign.md must NOT say CRLF. Do not run git.
