# AGENTS.md — Public website repository

## Navigation is derived from page order (required)
- The physical DOM order of eligible sections in `index.html` is the single source of truth for **both** the desktop Jump to sidebar and mobile Reading Compass. Never manually sort or regroup navigation links.
- Every `<section id="...">` containing a visible `<h2>` participates in navigation unless explicitly marked `data-nav-exclude="true"`. A short label may be supplied with `data-nav-label`; otherwise the first h2 supplies the label.
- A nested subsection (e.g. the Whisper training disclosure) is indexed **only** when it has a unique `id`, `data-nav-item`, and `data-nav-label`. It appears at its actual position immediately after its containing section, never in an unrelated group.
- Optional `data-nav-group` on the first section of a contiguous cluster creates a *visual heading only*. Group labels do **not** change document or link order.
- There must be exactly one `#compass-links` list. Its contents are GENERATED. Do not edit the `<li>` elements by hand.
- After adding, removing, renaming, reordering or nesting sections, run:
  ```sh
  python scripts/sync_navigation.py --fix
  python scripts/sync_navigation.py --check
  python -m unittest discover -s tests -p "test_*.py"
  ```
- Both mobile and desktop render the **same** navigation links, in document order. No duplicate IDs, broken anchors, missing navigable sections, or navigation links that resolve to more than one target. The website must remain usable without JavaScript.

## Quality gate
- All pull requests and pushes must pass the GitHub Actions navigation check and negative regression tests. Do not bypass the check or claim it passes without running it.
- Whenever a section is moved, verify the generated order, keyboard/focus access, mobile pill morph and wide-screen static sidebar.
- Keep the public website free of personal/private data and internal source links. Do not publish private project artifacts.
- Preserve existing OET pages, research image, workstation photo and existing video IDs unless explicitly requested otherwise.
- Commit focused changes separately and avoid replacing the whole page when a narrow edit suffices.
