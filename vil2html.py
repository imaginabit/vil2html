#!/usr/bin/env python3
"""
vil2html.py — Ferris Sweep .vil → HTML keymap visualizer
Usage: python3 vil2html.py input.vil [output.html]
"""

import json, sys, re, html
from pathlib import Path

# ─── Key name translations ────────────────────────────────────────────────────

KC_MAP = {
    'KC_TRNS': '▽',  'KC_NO': '',
    'KC_SPACE': 'Space', 'KC_SPC': 'Space',
    'KC_BSPACE': '⌫',  'KC_BSPC': '⌫',
    'KC_ENTER': '↩',   'KC_ENT': '↩',
    'KC_TAB': 'Tab',   'KC_ESC': 'Esc',  'KC_GESC': 'Esc',
    'KC_DELETE': 'Del', 'KC_DEL': 'Del',
    'KC_LSFT': 'Shift', 'KC_RSFT': 'Shift',
    'KC_LALT': 'Alt',   'KC_RALT': 'AltGr',
    'KC_LCTL': 'Ctrl',  'KC_RCTL': 'Ctrl',
    'KC_LGUI': '⊞',    'KC_RGUI': '⊞',
    'KC_LEFT': '←', 'KC_RIGHT': '→', 'KC_UP': '↑', 'KC_DOWN': '↓',
    'KC_HOME': 'Home', 'KC_END': 'End',
    'KC_PGUP': 'PgUp', 'KC_PGDOWN': 'PgDn', 'KC_PGDN': 'PgDn',
    'KC_SCOLON': ';',  'KC_SCLN': ';',
    'KC_COMMA': ',',   'KC_COMM': ',',
    'KC_DOT': '.',     'KC_SLASH': '/',   'KC_SLSH': '/',
    'KC_MINUS': '-',   'KC_MINS': '-',
    'KC_EQUAL': '=',   'KC_EQL': '=',
    'KC_LBRACKET': '[', 'KC_LBRC': '[',
    'KC_RBRACKET': ']', 'KC_RBRC': ']',
    'KC_BSLASH': '\\', 'KC_BSLS': '\\',
    'KC_QUOTE': "'",   'KC_QUOT': "'",
    'KC_GRAVE': '`',   'KC_GRV': '`',
    'KC_NONUS_BSLASH': '<',
    'KC_VOLU': 'Vol+', 'KC_VOLD': 'Vol-', 'KC_MUTE': 'Mute',
    'KC_KP_SLASH': 'KP/',
    'KC_PSCREEN': 'PrtSc', 'KC_PSCR': 'PrtSc',
    'KC_COPY': 'Copy', 'KC_PSTE': 'Paste', 'KC_CUT': 'Cut',
    **{f'KC_F{i}': f'F{i}' for i in range(1, 25)},
    **{f'KC_{i}': str(i) for i in range(10)},
}

MOD_SHORT = {
    'LALT': 'Alt', 'RALT': 'Ag', 'LSFT': 'Sft', 'RSFT': 'Sft',
    'LCTL': 'Ctl', 'RCTL': 'Ctl', 'LGUI': '⊞',  'RGUI': '⊞',
}


def kc(code):
    return KC_MAP.get(code, re.sub(r'^KC_', '', code))


def parse(raw):
    """Return (tap, hold, css_class)."""
    if raw == -1:        return '',  '',   'none'
    if raw == 'KC_TRNS': return '▽', '',   'trns'
    if raw == 'KC_NO':   return '',  '',   'empty'

    # Mod-tap:  LALT_T(KC_F)
    m = re.fullmatch(r'([A-Z]+)_T\((.+)\)', raw)
    if m:
        return kc(m[2]), MOD_SHORT.get(m[1], m[1]), 'modtap'

    # Layer-tap:  LT2(KC_SPACE)
    m = re.fullmatch(r'LT(\d+)\((.+)\)', raw)
    if m:
        return kc(m[2]), f'L{m[1]}', 'layertap'

    # Ctrl+Shift:  C_S(KC_P)
    m = re.fullmatch(r'C_S\((.+)\)', raw)
    if m:
        return f'C+S {kc(m[1])}', '', 'combo'

    # One-modifier wrapper:  LSFT(KC_1), RALT(KC_GRAVE), RCTL(KC_J) …
    m = re.fullmatch(r'([A-Z]+)\((.+)\)', raw)
    if m:
        pfx = {'LSFT': '⇧', 'RSFT': '⇧', 'RALT': 'Ag+', 'LALT': 'Al+',
               'RCTL': 'C+', 'LCTL': 'C+', 'RGUI': '⊞+', 'LGUI': '⊞+'}.get(m[1], m[1] + '+')
        return f'{pfx}{kc(m[2])}', '', 'combo'

    # Plain keycode
    label = kc(raw)
    if raw in ('KC_LSFT','KC_RSFT','KC_LALT','KC_RALT','KC_LCTL','KC_RCTL','KC_LGUI','KC_RGUI'):
        return label, '', 'modifier'
    if re.match(r'KC_F\d+$', raw):
        return label, '', 'func'
    if raw in {'KC_SPACE','KC_SPC','KC_BSPACE','KC_BSPC','KC_ENTER','KC_ENT',
               'KC_TAB','KC_ESC','KC_GESC','KC_DELETE','KC_DEL'}:
        return label, '', 'special'
    return label, '', 'normal'


def key_html(raw):
    tap, hold, cls = parse(raw)
    raw_str = html.escape(str(raw))
    if cls == 'none':
        return f'<div class="key none" data-raw="{raw_str}"></div>'
    hold_h = f'<span class="hold">{html.escape(hold)}</span>' if hold else ''
    tap_h  = f'<span class="tap">{html.escape(tap)}</span>'
    return (f'<div class="key {cls}" data-raw="{raw_str}" title="{raw_str}">'
            f'{tap_h}{hold_h}</div>')


# ─── Ferris Sweep physical layout ─────────────────────────────────────────────
#
# .vil layer structure: 8 groups × 5 slots
#   Groups 0–2 : left half rows top→bottom, left→right
#   Group  3   : left thumbs  [outer(Enter), inner(Tab), -1, -1, -1]
#   Groups 4–6 : right half rows, stored RIGHT→LEFT (need reversal for display)
#   Group  7   : right thumbs [inner(Space), outer(Bsp), -1, -1, -1]
#
# Physical view after transform:
#   [Q][W][E][R][T]   [Y][U][I][O][P]
#   [A][S][D][F][G]   [H][J][K][L][;]
#   [Z][X][C][V][B]   [N][M][,][.][/]
#          [Ent][Tab] [Spc][⌫]

SZ  = 60                      # key size px
GAP = 6                       # gap between keys px
U   = SZ + GAP                # 66 px per key slot
STAGGER = [12, 6, 0, 6, 12]  # column stagger px (0 = highest, at middle finger)


def half_html(rows, thumbs, side):
    """
    rows:   3 lists of 5 keys in left→right physical order
    thumbs: 2 keys in left→right order for this half
    side:   'left' | 'right'
    """
    items = []

    for r, row in enumerate(rows):
        for c, k in enumerate(row):
            x = c * U
            y = r * U + STAGGER[c]
            items.append(
                f'<div class="pk" style="left:{x}px;top:{y}px">{key_html(k)}</div>'
            )

    base_y = 3 * U + max(STAGGER) + 14  # thumb cluster Y baseline

    if side == 'left':
        # Outer thumb (Enter) under col 2, inner (Tab) under col 3
        # Outer is slightly lower — mimics the physical arc
        positions = [(2 * U, base_y + 7), (3 * U, base_y)]
    else:
        # Inner thumb (Space) under col 1, outer (Bsp) under col 2
        positions = [(1 * U, base_y), (2 * U, base_y + 7)]

    for (x, y), k in zip(positions, thumbs):
        items.append(
            f'<div class="pk thumb" style="left:{x}px;top:{y}px">{key_html(k)}</div>'
        )

    return '<div class="half">\n    ' + '\n    '.join(items) + '\n  </div>'


def layer_html(layer):
    left_rows   = [layer[0], layer[1], layer[2]]
    left_thumbs = [layer[3][0], layer[3][1]]           # [outer=Enter, inner=Tab]

    # Right rows stored right→left — reverse each for visual left→right display
    right_rows   = [list(reversed(layer[4])),
                    list(reversed(layer[5])),
                    list(reversed(layer[6]))]
    right_thumbs = [layer[7][0], layer[7][1]]           # [inner=Space, outer=Bsp]

    lh = half_html(left_rows,  left_thumbs,  'left')
    rh = half_html(right_rows, right_thumbs, 'right')
    return f'<div class="keyboard">\n  {lh}\n  {rh}\n</div>'


# ─── Styles ────────────────────────────────────────────────────────────────────

CSS = """\
/* ── CSS variables: dark mode (default) ── */
:root {
  --bg:           #0f0f1a;
  --bg-kb:        #0a0a14;
  --border-kb:    #1e1e34;
  --text:         #ccd;
  --h1:           #90cbf0;
  --sub:          #556;
  --legend-sep:   #1e1e2e;
  --legend-h3:    #445;
  --legend-text:  #557;

  --tab-bg:       #1a1a2e;
  --tab-border:   #343460;
  --tab-text:     #778;
  --tab-hov-bg:   #22223c;
  --tab-hov-text: #bbc;
  --tab-act-bg:   #2a2a7a;
  --tab-act-bdr:  #5858cc;

  --btn-bg:       #1e3a1e;
  --btn-border:   #2e6a2e;
  --btn-text:     #80d880;
  --btn-hov-bg:   #274a27;
  --btn-hov-text: #a0f0a0;

  --k-normal-bg:  #212138; --k-normal-bdr: #383868; --k-normal-txt: #d8d8ff;
  --k-special-bg: #182f50; --k-special-bdr: #28609a; --k-special-txt: #8cd4f8;
  --k-mod-bg:     #361650; --k-mod-bdr:    #5e2c9a; --k-mod-txt:    #d0a0f8;
  --k-func-bg:    #122e22; --k-func-bdr:   #20663c; --k-func-txt:   #80eea0;
  --k-mt-bg:      #243318; --k-mt-bdr:     #4a6c24; --k-mt-txt:     #c4e490;
  --k-lt-bg:      #163434; --k-lt-bdr:     #245e5e; --k-lt-txt:     #80e4e4;
  --k-combo-bg:   #33230f; --k-combo-bdr:  #6b5020; --k-combo-txt:  #f0c480;
  --k-trns-bg:    #0d0d1c; --k-trns-bdr:   #252540; --k-trns-txt:   #303055;
  --k-empty-bg:   #090912; --k-empty-bdr:  #181826; --k-empty-txt:  #202030;

  --hold-txt:     #99a;
  --hold-mt-txt:  #b4d864;
  --hold-lt-txt:  #64d8d8;
  --hold-bg:      rgba(0,0,0,.45);
  --shadow-kb:    0 8px 40px rgba(0,0,0,.6);
  --shadow-key:   0 5px 20px rgba(0,0,0,.7);
}

/* ── CSS variables: light mode ── */
@media (prefers-color-scheme: light) {
  :root {
    --bg:           #f0f0f8;
    --bg-kb:        #e4e4f2;
    --border-kb:    #c0c0d8;
    --text:         #223;
    --h1:           #1a4a80;
    --sub:          #558;
    --legend-sep:   #c8c8dc;
    --legend-h3:    #558;
    --legend-text:  #446;

    --tab-bg:       #e0e0f0;
    --tab-border:   #b0b0d0;
    --tab-text:     #448;
    --tab-hov-bg:   #d4d4ec;
    --tab-hov-text: #224;
    --tab-act-bg:   #3838a0;
    --tab-act-bdr:  #2828c0;

    --btn-bg:       #d8f0d8;
    --btn-border:   #50a050;
    --btn-text:     #1a5a1a;
    --btn-hov-bg:   #c8e8c8;
    --btn-hov-text: #0e3a0e;

    --k-normal-bg:  #dde; --k-normal-bdr: #99c; --k-normal-txt: #113;
    --k-special-bg: #cde; --k-special-bdr: #68a; --k-special-txt: #024;
    --k-mod-bg:     #dcd; --k-mod-bdr:    #a6c; --k-mod-txt:    #302;
    --k-func-bg:    #cec; --k-func-bdr:   #6a8; --k-func-txt:   #030;
    --k-mt-bg:      #deecc8; --k-mt-bdr:  #7aa040; --k-mt-txt:  #1a3a08;
    --k-lt-bg:      #c8ecea; --k-lt-bdr:  #409898; --k-lt-txt:  #033030;
    --k-combo-bg:   #fde8c0; --k-combo-bdr: #c09040; --k-combo-txt: #3a1800;
    --k-trns-bg:    #ebebf4; --k-trns-bdr: #c8c8dc; --k-trns-txt: #aaa;
    --k-empty-bg:   #e8e8f0; --k-empty-bdr: #d0d0e0; --k-empty-txt: #bbb;

    --hold-txt:     #446;
    --hold-mt-txt:  #2a6010;
    --hold-lt-txt:  #106060;
    --hold-bg:      rgba(0,0,0,.08);
    --shadow-kb:    0 4px 20px rgba(0,0,0,.15);
    --shadow-key:   0 3px 12px rgba(0,0,0,.2);
  }
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Segoe UI', system-ui, sans-serif;
  padding: 32px 24px;
}

h1 { font-size: 1.65rem; color: var(--h1); margin-bottom: 5px; }
.sub { color: var(--sub); font-size: .82rem; margin-bottom: 24px; letter-spacing: .03em; }

/* ── Tabs ── */
.tabs { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 18px; }
.tab {
  padding: 7px 18px;
  background: var(--tab-bg);
  border: 1px solid var(--tab-border);
  border-radius: 7px;
  color: var(--tab-text);
  cursor: pointer;
  font-size: .8rem;
  transition: all .12s;
}
.tab:hover  { background: var(--tab-hov-bg); color: var(--tab-hov-text); }
.tab.active { background: var(--tab-act-bg); border-color: var(--tab-act-bdr); color: #fff; font-weight: 600; }

/* ── Panels ── */
.panel { display: none; }
.panel.active { display: block; }

/* ── Keyboard container ── */
.keyboard {
  display: flex;
  gap: 44px;
  padding: 28px 24px;
  background: var(--bg-kb);
  border: 1px solid var(--border-kb);
  border-radius: 16px;
  width: fit-content;
  box-shadow: var(--shadow-kb);
}

/* ── Each half ── */
.half {
  position: relative;
  width: 324px;
  height: 310px;
}

/* ── Key slot ── */
.pk { position: absolute; }

/* ── Keys ── */
.key {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: default;
  border: 2px solid transparent;
  transition: transform .1s, box-shadow .1s;
  padding: 3px;
  user-select: none;
}
.key:hover { transform: scale(1.10); z-index: 10; box-shadow: var(--shadow-key); }

.key.normal   { background: var(--k-normal-bg);  border-color: var(--k-normal-bdr);  color: var(--k-normal-txt); }
.key.special  { background: var(--k-special-bg); border-color: var(--k-special-bdr); color: var(--k-special-txt); }
.key.modifier { background: var(--k-mod-bg);     border-color: var(--k-mod-bdr);     color: var(--k-mod-txt); }
.key.func     { background: var(--k-func-bg);    border-color: var(--k-func-bdr);    color: var(--k-func-txt); }
.key.modtap   { background: var(--k-mt-bg);      border-color: var(--k-mt-bdr);      color: var(--k-mt-txt); }
.key.layertap { background: var(--k-lt-bg);      border-color: var(--k-lt-bdr);      color: var(--k-lt-txt); }
.key.combo    { background: var(--k-combo-bg);   border-color: var(--k-combo-bdr);   color: var(--k-combo-txt); }
.key.trns     { background: var(--k-trns-bg);    border-color: var(--k-trns-bdr);    color: var(--k-trns-txt); }
.key.empty    { background: var(--k-empty-bg);   border-color: var(--k-empty-bdr);   color: var(--k-empty-txt); }
.key.none     { background: transparent; border: none; pointer-events: none; }

/* Key labels */
.tap  { font-size: .78rem; font-weight: 700; line-height: 1.15; text-align: center; }
.hold {
  font-size: .55rem;
  color: var(--hold-txt);
  margin-top: 4px;
  background: var(--hold-bg);
  padding: 1px 5px;
  border-radius: 3px;
  line-height: 1;
}
.key.modtap  .hold { color: var(--hold-mt-txt); }
.key.layertap .hold { color: var(--hold-lt-txt); }

/* ── Print button ── */
.print-btn {
  margin-bottom: 18px;
  padding: 8px 20px;
  background: var(--btn-bg);
  border: 1px solid var(--btn-border);
  border-radius: 7px;
  color: var(--btn-text);
  cursor: pointer;
  font-size: .82rem;
  transition: all .12s;
}
.print-btn:hover { background: var(--btn-hov-bg); color: var(--btn-hov-text); }

/* ── Legend ── */
.legend {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid var(--legend-sep);
}
.legend h3 {
  color: var(--legend-h3);
  font-size: .72rem;
  text-transform: uppercase;
  letter-spacing: .07em;
  margin-bottom: 12px;
}
.legend-row {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
  font-size: .72rem;
  color: var(--legend-text);
}
.legend-row .key {
  width: auto;
  min-width: 46px;
  height: 34px;
  padding: 2px 8px;
  border-radius: 5px;
  flex-shrink: 0;
}
.legend-row .tap  { font-size: .65rem; }
.legend-row .hold { font-size: .50rem; }

/* ── Layout selector ── */
.layout-row { display:flex; align-items:center; gap:8px; margin-bottom:16px; flex-wrap:wrap; }
.layout-label { font-size:.72rem; color:var(--sub); white-space:nowrap; font-weight:600; }
.layout-btn {
  padding: 5px 13px;
  background: var(--tab-bg);
  border: 1px solid var(--tab-border);
  border-radius: 5px;
  color: var(--tab-text);
  cursor: pointer;
  font-size: .76rem;
  transition: all .12s;
}
.layout-btn:hover  { background: var(--tab-hov-bg); color: var(--tab-hov-text); }
.layout-btn.active { background: var(--tab-act-bg); border-color: var(--tab-act-bdr); color: #fff; font-weight: 600; }

/* ── Print styles ── */
@media print {
  body { background: #fff !important; color: #000; padding: 10px; }
  h1   { color: #000 !important; font-size: 1.2rem; }
  .sub { color: #555; }
  .tabs, .print-btn { display: none !important; }
  .panel { display: block !important; page-break-inside: avoid; margin-bottom: 28px; }
  .panel::before {
    content: attr(data-label);
    display: block;
    font-size: .8rem;
    font-weight: 700;
    color: #333;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: .05em;
  }
  .keyboard { background: #f5f5f5 !important; border: 1px solid #ccc; box-shadow: none; gap: 28px; padding: 16px; }
  .half { height: 300px; }
  .key { border-width: 1px !important; }
  .key.normal   { background: #eef !important; border-color: #99c !important; color: #112 !important; }
  .key.special  { background: #def !important; border-color: #79c !important; color: #024 !important; }
  .key.modifier { background: #ede !important; border-color: #a6c !important; color: #302 !important; }
  .key.func     { background: #dfd !important; border-color: #6a9 !important; color: #020 !important; }
  .key.modtap   { background: #efd !important; border-color: #8b6 !important; color: #130 !important; }
  .key.layertap { background: #dff !important; border-color: #6aa !important; color: #023 !important; }
  .key.combo    { background: #fec !important; border-color: #b8a !important; color: #302 !important; }
  .key.trns     { background: #f9f9f9 !important; border-color: #ccc !important; color: #aaa !important; }
  .key.empty    { background: #f0f0f0 !important; border-color: #ddd !important; color: #ccc !important; }
  .tap  { color: inherit; }
  .hold { background: rgba(0,0,0,.08); color: #444; }
  .legend { border-top: 1px solid #ccc; }
  .legend h3    { color: #666; }
  .legend-row   { color: #555; }
}
"""

SCRIPT = r"""
/* ── US baseline keycode → display label ── */
const US_KC = {
  KC_TRNS:'▽', KC_NO:'',
  KC_SPACE:'Space', KC_SPC:'Space', KC_BSPACE:'⌫', KC_BSPC:'⌫',
  KC_ENTER:'↩', KC_ENT:'↩', KC_TAB:'Tab', KC_ESC:'Esc', KC_GESC:'Esc',
  KC_DELETE:'Del', KC_DEL:'Del',
  KC_LSFT:'Shift', KC_RSFT:'Shift', KC_LALT:'Alt', KC_RALT:'AltGr',
  KC_LCTL:'Ctrl', KC_RCTL:'Ctrl', KC_LGUI:'⊞', KC_RGUI:'⊞',
  KC_LEFT:'←', KC_RIGHT:'→', KC_UP:'↑', KC_DOWN:'↓',
  KC_HOME:'Home', KC_END:'End', KC_PGUP:'PgUp', KC_PGDOWN:'PgDn', KC_PGDN:'PgDn',
  KC_SCOLON:';', KC_SCLN:';', KC_COMMA:',', KC_COMM:',',
  KC_DOT:'.', KC_SLASH:'/', KC_SLSH:'/',
  KC_MINUS:'-', KC_MINS:'-', KC_EQUAL:'=', KC_EQL:'=',
  KC_LBRACKET:'[', KC_LBRC:'[', KC_RBRACKET:']', KC_RBRC:']',
  KC_BSLASH:'\\', KC_BSLS:'\\', KC_QUOTE:"'", KC_QUOT:"'",
  KC_GRAVE:'`', KC_GRV:'`', KC_NONUS_BSLASH:'<',
  KC_VOLU:'Vol+', KC_VOLD:'Vol-', KC_MUTE:'Mute', KC_KP_SLASH:'KP/',
  KC_PSCREEN:'PrtSc', KC_PSCR:'PrtSc', KC_COPY:'Copy', KC_PSTE:'Paste',
};
for (let i=1;i<=12;i++) US_KC['KC_F'+i]='F'+i;
for (let i=0;i<=9;i++) US_KC['KC_'+i]=String(i);

/* ── US shifted characters (for LSFT combos) ── */
const US_SHIFT = {
  KC_GRAVE:'~', KC_MINUS:'_', KC_EQUAL:'+',
  KC_LBRACKET:'{', KC_RBRACKET:'}', KC_BSLASH:'|',
  KC_SCOLON:':', KC_QUOTE:'"', KC_SLASH:'?', KC_NONUS_BSLASH:'>',
  KC_1:'!', KC_2:'@', KC_3:'#', KC_4:'$', KC_5:'%',
  KC_6:'^', KC_7:'&', KC_8:'*', KC_9:'(', KC_0:')',
  KC_COMMA:'<', KC_DOT:'>',
};

/* ── Layout override tables ── */
const LAYOUTS = {
  US: { name:'US ANSI',       plain:{}, shift:{}, altgr:{} },
  ES: {
    name:'Español (ES)',
    plain: {
      KC_GRAVE:'º',   KC_MINUS:"'",  KC_EQUAL:'¡',
      KC_LBRACKET:'`',KC_RBRACKET:'+',KC_BSLASH:'ç',
      KC_SCOLON:'ñ',  KC_QUOTE:'´',  KC_NONUS_BSLASH:'<', KC_SLASH:'-',
    },
    shift: {
      KC_GRAVE:'ª',   KC_MINUS:'?',  KC_EQUAL:'¿',
      KC_LBRACKET:'^',KC_RBRACKET:'*',KC_BSLASH:'Ç',
      KC_SCOLON:'Ñ',  KC_QUOTE:'¨',  KC_NONUS_BSLASH:'>',KC_SLASH:'_',
      KC_2:'"', KC_3:'·', KC_6:'&', KC_7:'/', KC_8:'(', KC_9:')', KC_0:'=',
    },
    altgr: {
      KC_GRAVE:'\\',  KC_LBRACKET:'[',KC_RBRACKET:']',
      KC_BSLASH:'}',  KC_QUOTE:'{',   KC_NONUS_BSLASH:'|',
      KC_1:'|', KC_2:'@', KC_3:'#',   KC_4:'~',
    },
  },
  UK: {
    name:'UK',
    plain: { KC_NONUS_BSLASH:'\\', KC_BSLASH:'#' },
    shift: { KC_2:'"', KC_3:'£',   KC_BSLASH:'~', KC_NONUS_BSLASH:'|' },
    altgr: { KC_4:'€' },
  },
  DE: {
    name:'Deutsch (DE)',
    plain: {
      KC_Y:'z',      KC_Z:'y',
      KC_GRAVE:'^',  KC_MINUS:'ß',  KC_EQUAL:'´',
      KC_LBRACKET:'ü',KC_RBRACKET:'+',KC_BSLASH:'#',
      KC_SCOLON:'ö', KC_QUOTE:'ä',  KC_NONUS_BSLASH:'<', KC_SLASH:'-',
    },
    shift: {
      KC_Y:'Z',      KC_Z:'Y',
      KC_GRAVE:'°',  KC_MINUS:'?',  KC_EQUAL:'`',
      KC_LBRACKET:'Ü',KC_RBRACKET:'*',KC_BSLASH:"'",
      KC_SCOLON:'Ö', KC_QUOTE:'Ä',  KC_NONUS_BSLASH:'>',KC_SLASH:'_',
      KC_2:'"', KC_3:'§', KC_6:'&', KC_7:'/', KC_8:'(', KC_9:')', KC_0:'=',
    },
    altgr: {
      KC_Q:'@', KC_E:'€', KC_2:'²', KC_3:'³',
      KC_7:'{', KC_8:'[', KC_9:']', KC_0:'}',
      KC_MINUS:'\\', KC_RBRACKET:'~', KC_NONUS_BSLASH:'|',
    },
  },
  FR: {
    name:'Français (FR)',
    plain: {
      KC_GRAVE:'²',
      KC_1:'&', KC_2:'é', KC_3:'"',  KC_4:"'", KC_5:'(', KC_6:'-',
      KC_7:'è', KC_8:'_', KC_9:'ç',  KC_0:'à', KC_MINUS:')', KC_EQUAL:'=',
      KC_Q:'a', KC_W:'z', KC_LBRACKET:'^',KC_RBRACKET:'$',
      KC_A:'q', KC_SCOLON:'m', KC_QUOTE:'ù', KC_BSLASH:'*',
      KC_NONUS_BSLASH:'<',
      KC_Z:'w', KC_M:',', KC_COMMA:';', KC_DOT:':', KC_SLASH:'!',
    },
    shift: {
      KC_1:'1', KC_2:'2', KC_3:'3',  KC_4:'4', KC_5:'5', KC_6:'6',
      KC_7:'7', KC_8:'8', KC_9:'9',  KC_0:'0', KC_MINUS:'°', KC_EQUAL:'+',
      KC_Q:'A', KC_W:'Z', KC_LBRACKET:'¨',KC_RBRACKET:'£',
      KC_A:'Q', KC_SCOLON:'M', KC_QUOTE:'%', KC_BSLASH:'µ',
      KC_NONUS_BSLASH:'>',
      KC_Z:'W', KC_M:'?', KC_COMMA:'.', KC_DOT:'/', KC_SLASH:'§',
    },
    altgr: {
      KC_0:'@', KC_3:'#', KC_4:'{', KC_5:'[', KC_6:'|',
      KC_7:'`', KC_8:'\\', KC_9:'^', KC_MINUS:']', KC_EQUAL:'}', KC_E:'€',
    },
  },
};

const MOD_J = {
  LALT:'Alt', RALT:'Ag', LSFT:'Sft', RSFT:'Sft',
  LCTL:'Ctl', RCTL:'Ctl', LGUI:'⊞',  RGUI:'⊞',
};
const SPECIALS = new Set(['KC_SPACE','KC_SPC','KC_BSPACE','KC_BSPC','KC_ENTER','KC_ENT','KC_TAB','KC_ESC','KC_GESC','KC_DELETE','KC_DEL']);
const MODKEYS  = new Set(['KC_LSFT','KC_RSFT','KC_LALT','KC_RALT','KC_LCTL','KC_RCTL','KC_LGUI','KC_RGUI']);

function kcLabel(code, lid) {
  const p = LAYOUTS[lid]?.plain;
  if (p && p[code] !== undefined) return p[code];
  return US_KC[code] !== undefined ? US_KC[code] : code.replace(/^KC_/,'');
}
function shiftOf(code, lid) {
  const s = LAYOUTS[lid]?.shift;
  if (s && s[code] !== undefined) return s[code];
  if (US_SHIFT[code] !== undefined) return US_SHIFT[code];
  const plain = kcLabel(code, lid);
  return /^[a-zA-Z]$/.test(plain) ? plain.toUpperCase() : '⇧'+plain;
}
function altgrOf(code, lid) {
  const a = LAYOUTS[lid]?.altgr;
  return (a && a[code] !== undefined) ? a[code] : null;
}

function parseKey(raw, lid) {
  if (raw === '-1' || raw === -1) return {tap:'', hold:'', cls:'none'};
  if (raw === 'KC_TRNS') return {tap:'▽', hold:'', cls:'trns'};
  if (raw === 'KC_NO')   return {tap:'',  hold:'', cls:'empty'};

  let m;
  // Mod-tap
  if ((m = raw.match(/^([A-Z]+)_T\((.+)\)$/)))
    return {tap: kcLabel(m[2],lid), hold: MOD_J[m[1]]||m[1], cls:'modtap'};
  // Layer-tap
  if ((m = raw.match(/^LT(\d+)\((.+)\)$/)))
    return {tap: kcLabel(m[2],lid), hold:'L'+m[1], cls:'layertap'};
  // Ctrl+Shift
  if ((m = raw.match(/^C_S\((.+)\)$/)))
    return {tap:'C+S '+kcLabel(m[1],lid), hold:'', cls:'combo'};
  // Single modifier wrapper
  if ((m = raw.match(/^([A-Z]+)\((.+)\)$/))) {
    const [,fn,inner] = m;
    if (fn==='LSFT'||fn==='RSFT') return {tap: shiftOf(inner,lid), hold:'', cls:'combo'};
    if (fn==='RALT'||fn==='LALT') {
      const ag = altgrOf(inner,lid);
      return {tap: ag!==null ? ag : 'Ag+'+kcLabel(inner,lid), hold:'', cls:'combo'};
    }
    const pfx = {RCTL:'C+',LCTL:'C+',RGUI:'⊞+',LGUI:'⊞+'}[fn]||fn+'+';
    return {tap: pfx+kcLabel(inner,lid), hold:'', cls:'combo'};
  }
  // Plain
  const label = kcLabel(raw, lid);
  const cls = MODKEYS.has(raw) ? 'modifier' : /^KC_F\d+$/.test(raw) ? 'func' : SPECIALS.has(raw) ? 'special' : 'normal';
  return {tap: label, hold:'', cls};
}

function applyLayout(lid) {
  document.querySelectorAll('.layout-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('layout-'+lid);
  if (btn) btn.classList.add('active');

  document.querySelectorAll('.key[data-raw]').forEach(el => {
    const raw = el.dataset.raw;
    if (!raw) return;
    const {tap, hold, cls} = parseKey(raw, lid);
    el.className = 'key ' + cls;

    let te = el.querySelector('.tap');
    if (!te) { te = document.createElement('span'); te.className='tap'; el.prepend(te); }
    te.textContent = tap;

    let he = el.querySelector('.hold');
    if (hold) {
      if (!he) { he = document.createElement('span'); he.className='hold'; el.appendChild(he); }
      he.textContent = hold;
    } else if (he) { he.remove(); }
  });
}

function show(n) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('p'+n).classList.add('active');
  document.getElementById('t'+n).classList.add('active');
}
"""

LEGEND = [
    ('normal',   'A',    '',     'Normal'),
    ('special',  '↩',   '',     'Special'),
    ('modifier', 'Shift','',     'Modifier'),
    ('func',     'F1',  '',     'Function'),
    ('modtap',   'F',   'Alt',  'Mod-Tap (tap / hold)'),
    ('layertap', 'Tab', 'L1',   'Layer-Tap'),
    ('combo',    'C+V', '',     'Combo'),
    ('trns',     '▽',  '',     'Transparent'),
]


def legend_key(cls, tap, hold):
    hold_h = f'<span class="hold">{html.escape(hold)}</span>' if hold else ''
    return f'<div class="key {cls}"><span class="tap">{html.escape(tap)}</span>{hold_h}</div>'


# ─── HTML assembly ─────────────────────────────────────────────────────────────

def build_html(vil, name):
    layers = vil['layout']
    tabs   = ''
    panels = ''

    first = True
    for i, layer in enumerate(layers):
        real_keys = [k for row in layer for k in row if k not in ('KC_TRNS', -1)]
        if not real_keys:
            continue
        active = 'active' if first else ''
        first  = False
        tabs   += f'<button class="tab {active}" onclick="show({i})" id="t{i}">Layer {i}</button>\n    '
        panels += f'<div class="panel {active}" id="p{i}" data-label="Layer {i}">{layer_html(layer)}</div>\n'

    legend_row = '\n    '.join(
        f'{legend_key(c, t, h)}<span>{html.escape(label)}</span>'
        for c, t, h, label in LEGEND
    )

    total_layers = len(layers)
    used_layers  = sum(
        1 for layer in layers
        if any(k not in ('KC_TRNS', -1) for row in layer for k in row)
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(name)} — Keymap</title>
  <style>
{CSS}
  </style>
</head>
<body>
  <h1>⌨ {html.escape(name)}</h1>
  <p class="sub">Ferris Sweep · 34 keys · {used_layers} active layers of {total_layers}</p>

  <button class="print-btn" onclick="window.print()">🖨 Imprimir / Print</button>

  <div class="tabs">
    {tabs}
  </div>

  <div class="layout-row">
    <span class="layout-label">OS Layout:</span>
    <button class="layout-btn active" onclick="applyLayout('US')" id="layout-US">🇺🇸 US</button>
    <button class="layout-btn" onclick="applyLayout('ES')" id="layout-ES">🇪🇸 ES</button>
    <button class="layout-btn" onclick="applyLayout('UK')" id="layout-UK">🇬🇧 UK</button>
    <button class="layout-btn" onclick="applyLayout('DE')" id="layout-DE">🇩🇪 DE</button>
    <button class="layout-btn" onclick="applyLayout('FR')" id="layout-FR">🇫🇷 FR</button>
  </div>

  <div class="panels">
{panels}
  </div>

  <div class="legend">
    <h3>Legend</h3>
    <div class="legend-row">
      {legend_row}
    </div>
  </div>

  <script>
{SCRIPT}
  </script>
</body>
</html>"""


# ─── Entry point ───────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(f'Usage: {Path(sys.argv[0]).name} input.vil [output.html]', file=sys.stderr)
        sys.exit(1)

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix('.html')

    try:
        vil = json.loads(src.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f'Error reading {src}: {e}', file=sys.stderr)
        sys.exit(1)

    out = build_html(vil, src.stem)
    dst.write_text(out, encoding='utf-8')
    print(f'✓  {dst}')


if __name__ == '__main__':
    main()
