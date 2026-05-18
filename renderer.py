"""HTML document assembly.

Loads CSS/JS from ``assets/`` and stitches together the full standalone
HTML page from a parsed ``.vil`` payload.
"""

import html
from pathlib import Path

from layout import layer_html

ASSETS_DIR = Path(__file__).parent / 'assets'

# Legend entries: (css_class, tap_label, hold_label, description)
LEGEND = [
    ('normal',   'A',     '',    'Normal'),
    ('special',  '↩',     '',    'Special'),
    ('modifier', 'Shift', '',    'Modifier'),
    ('func',     'F1',    '',    'Function'),
    ('modtap',   'F',     'Alt', 'Mod-Tap (tap / hold)'),
    ('layertap', 'Tab',   'L1',  'Layer-Tap'),
    ('combo',    'C+V',   '',    'Combo'),
    ('trns',     '▽',     '',    'Transparent'),
]


def _load_asset(name):
    return (ASSETS_DIR / name).read_text(encoding='utf-8')


def _legend_key(cls, tap, hold):
    """Generate HTML for a single legend key example."""
    hold_h = f'<span class="hold">{html.escape(hold)}</span>' if hold else ''
    return (f'<div class="key {cls}">'
            f'<span class="tap">{html.escape(tap)}</span>{hold_h}</div>')


def _count_active_layers(layers):
    """Count layers containing keys other than KC_TRNS or -1."""
    return sum(
        1 for layer in layers
        if any(k not in ('KC_TRNS', -1) for row in layer for k in row)
    )


def _build_tabs_and_panels(layers):
    """Generate tab buttons and layer panels for all non-empty layers."""
    tabs_parts = []
    panels_parts = []
    first = True

    for i, layer in enumerate(layers):
        real_keys = [k for row in layer for k in row if k not in ('KC_TRNS', -1)]
        if not real_keys:
            continue

        active_class = 'active' if first else ''
        first = False

        tabs_parts.append(
            f'<button class="tab {active_class}" onclick="show({i})" id="t{i}">Layer {i}</button>'
        )
        panels_parts.append(
            f'<div class="panel {active_class}" id="p{i}" data-label="Layer {i}">'
            f'{layer_html(layer)}</div>'
        )

    tabs = '\n    '.join(tabs_parts) + '\n    '
    panels = '\n'.join(panels_parts) + '\n'
    return tabs, panels


def _build_legend():
    items = '\n    '.join(
        f'{_legend_key(c, t, h)}<span>{html.escape(label)}</span>'
        for c, t, h, label in LEGEND
    )
    return f"""<div class="legend">
    <h3>Legend</h3>
    <div class="legend-row">
      {items}
    </div>
  </div>"""


def build_html(vil, name):
    """Generate the complete HTML document from a parsed .vil payload."""
    layers = vil['layout']

    tabs, panels = _build_tabs_and_panels(layers)
    total_layers = len(layers)
    active_layers = _count_active_layers(layers)

    css = _load_asset('styles.css')
    script = _load_asset('script.js')
    legend = _build_legend()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(name)} — Keymap</title>
  <style>
{css}
  </style>
</head>
<body>
  <h1>⌨ {html.escape(name)}</h1>
  <p class="sub">Ferris Sweep · 34 keys · {active_layers} active layers of {total_layers}</p>

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

  {legend}

  <script>

{script}
  </script>
</body>
</html>"""
