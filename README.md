# vil2html

> Turn a Vial `.vil` keymap into a self-contained, printable HTML visualizer
> for the **Ferris Sweep** (34-key split keyboard).

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.8+-3776AB?logo=python&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
  <img alt="No dependencies" src="https://img.shields.io/badge/dependencies-stdlib%20only-success">
  <img alt="Keyboard" src="https://img.shields.io/badge/keyboard-Ferris%20Sweep%2034--key-blueviolet">
</p>

---

## What it does

`vil2html` reads a [Vial](https://get.vial.today/) `.vil` keymap export and
emits a **single, self-contained HTML file** — no build step, no external
assets, no JavaScript framework. Just open it in any browser.

The output renders every layer of your keymap as an interactive split
keyboard, color-coded by key kind (normal / modifier / mod-tap / layer-tap /
combo / transparent), with live **OS layout switching** so the labels
match what your operating system will actually type.

```
┌─────────────────────────────────────────────────────────────┐
│  ⌨ ferrys-sweep — Keymap                                    │
│  Ferris Sweep · 34 keys · 4 active layers of 7              │
│                                                             │
│  [ Layer 0 ] [ Layer 1 ] [ Layer 2 ] [ Layer 3 ]            │
│                                                             │
│  OS Layout:  🇺🇸 US  🇪🇸 ES  🇬🇧 UK  🇩🇪 DE  🇫🇷 FR          │
│                                                             │
│   ┌──┬──┬──┬──┬──┐   ┌──┬──┬──┬──┬──┐                       │
│   │Q │W │E │R │T │   │Y │U │I │O │P │                       │
│   ├──┼──┼──┼──┼──┤   ├──┼──┼──┼──┼──┤                       │
│   │A │S │D │F │G │   │H │J │K │L │; │                       │
│   ├──┼──┼──┼──┼──┤   ├──┼──┼──┼──┼──┤                       │
│   │Z │X │C │V │B │   │N │M │, │. │/ │                       │
│   └──┴──┴──┴──┴──┘   └──┴──┴──┴──┴──┘                       │
│           ┌──┬──┐   ┌──┬──┐                                 │
│           │↩ │Tb│   │Sp│⌫ │                                 │
│           └──┴──┘   └──┴──┘                                 │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **Zero dependencies.** Pure Python 3 standard library.
- **One file out.** CSS + JS are inlined — share it, host it on GitHub Pages,
  or open it locally.
- **Multi-layer.** Tabs for every non-empty layer; empty layers are skipped.
- **Smart key parsing.** Handles `LALT_T(...)`, `LT2(...)`, `LSFT(...)`,
  `C_S(...)`, modifier wrappers and plain keycodes.
- **Live OS layout switching.** US ANSI · ES · UK · DE · FR — labels update
  instantly so shifted/AltGr characters reflect *your* system.
- **Print-friendly.** Dedicated `@media print` stylesheet with all layers
  on one page, light background, page-break protection.
- **Dark / light aware.** Follows `prefers-color-scheme`.

## Install

There's nothing to install. Clone or download the repo:

```bash
git clone https://github.com/imaginabit/vil2html.git
cd vil2html
```

You need **Python 3.8+** — that's it.

## Usage

```bash
python3 vil2html.py path/to/keymap.vil [output.html]
```

If you omit the output path, the HTML is written next to the input with the
same stem (`keymap.vil` → `keymap.html`).

### Try the bundled example

```bash
python3 vil2html.py examples/ferrys-sweep.vil
xdg-open examples/ferrys-sweep.html   # or just double-click
```

## Project structure

```
vil2html/
├── vil2html.py        # CLI entry point
├── keycodes.py        # Keycode mappings & parsing (no HTML)
├── layout.py          # Ferris Sweep physical layout + key/half HTML
├── renderer.py        # Full HTML document assembly
├── assets/
│   ├── styles.css     # Inlined into the output <style>
│   └── script.js      # Inlined into the output <script>
├── examples/
│   ├── ferrys-sweep.vil
│   └── ferrys-sweep.html
└── README.md
```

Each module has a single job:

| Module         | Responsibility                                              |
| -------------- | ----------------------------------------------------------- |
| `keycodes.py`  | `KC_*` → label table, mod-tap / layer-tap / combo parsing.  |
| `layout.py`    | Physical key positioning (stagger, thumb arc, split halves).|
| `renderer.py`  | Tabs, legend, layout selector, full HTML document.          |
| `assets/*`     | The CSS and JS embedded in every generated file.            |
| `vil2html.py`  | Argument parsing, file I/O.                                 |

## How the `.vil` is interpreted

A Ferris Sweep `.vil` layer is `8 groups × 5 slots`:

| Group  | Meaning                                                              |
| :----: | -------------------------------------------------------------------- |
| 0–2    | Left half rows (top → bottom, left → right)                          |
| 3      | Left thumbs: `[outer, inner, -1, -1, -1]`                            |
| 4–6    | Right half rows — stored **right ← left**, reversed for display      |
| 7      | Right thumbs: `[outer, inner, -1, -1, -1]` — same convention as rows |

Slots holding `-1` are dead positions and rendered transparent.

> **Note on the right half.** Everything on the right half — rows *and*
> thumbs — is stored outer-to-inner (pinky-side first, index-side last).
> The renderer reverses both so the inner thumb ends up next to the split
> gap, matching the physical keyboard.

## OS layout support

Layouts only override keys that differ from US ANSI. Add a new one by
extending the `LAYOUTS` table in [`assets/script.js`](assets/script.js):

```js
const LAYOUTS = {
  XX: {
    name: 'My Layout',
    plain: { KC_GRAVE: '…' },
    shift: { KC_2: '…' },
    altgr: { KC_E: '€' },
  },
};
```

Then add a button next to the others in [`renderer.py`](renderer.py):

```html
<button class="layout-btn" onclick="applyLayout('XX')" id="layout-XX">🏳 XX</button>
```

## License

MIT
