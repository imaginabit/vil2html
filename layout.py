"""Ferris Sweep physical layout (34 keys, split).

.vil layer structure: 8 groups x 5 slots
  Groups 0-2 : left half rows top->bottom, left->right
  Group  3   : left thumbs  [outer, inner, -1, -1, -1]
  Groups 4-6 : right half rows, stored RIGHT<-LEFT (need reversal for display)
  Group  7   : right thumbs [outer, inner, -1, -1, -1] (same convention as rows)

Physical view after transform::

    [Q][W][E][R][T]   [Y][U][I][O][P]
    [A][S][D][F][G]   [H][J][K][L][;]
    [Z][X][C][V][B]   [N][M][,][.][/]
           [Ent][Tab] [Spc][Bsp]
"""

import html

from keycodes import parse

# Layout dimensions (pixels)
KEY_SIZE = 60
KEY_GAP = 6
KEY_UNIT = KEY_SIZE + KEY_GAP            # 66 px per slot
COL_STAGGER = [12, 6, 0, 6, 12]          # column stagger px (0 = highest, center)


def key_html(raw):
    """Generate the HTML element for a single key."""
    tap, hold, cls = parse(raw)
    raw_str = html.escape(str(raw))

    if cls == 'none':
        return f'<div class="key none" data-raw="{raw_str}"></div>'

    hold_h = f'<span class="hold">{html.escape(hold)}</span>' if hold else ''
    tap_h = f'<span class="tap">{html.escape(tap)}</span>'
    return (f'<div class="key {cls}" data-raw="{raw_str}" title="{raw_str}">'
            f'{tap_h}{hold_h}</div>')


def half_html(rows, thumbs, side):
    """Generate HTML for the left or right keyboard half.

    Args:
        rows:   3 lists of 5 keys in left->right physical order.
        thumbs: 2 keys in left->right order for this half.
        side:   ``'left'`` or ``'right'``.
    """
    items = []

    # Main key grid
    for r, row in enumerate(rows):
        for c, k in enumerate(row):
            x = c * KEY_UNIT
            y = r * KEY_UNIT + COL_STAGGER[c]
            items.append(
                f'<div class="pk" style="left:{x}px;top:{y}px">{key_html(k)}</div>'
            )

    # Thumb cluster positioning
    base_y = 3 * KEY_UNIT + max(COL_STAGGER) + 14

    if side == 'left':
        # Outer thumb (Enter) under col 2, inner (Tab) under col 3.
        # Outer is slightly lower to mimic the physical arc.
        thumb_positions = [(2 * KEY_UNIT, base_y + 7), (3 * KEY_UNIT, base_y)]
    else:
        # Inner thumb under col 1 (closer to the split gap),
        # outer thumb under col 2. Outer sits slightly lower to mimic the arc.
        thumb_positions = [(1 * KEY_UNIT, base_y), (2 * KEY_UNIT, base_y + 7)]

    for (x, y), k in zip(thumb_positions, thumbs):
        items.append(
            f'<div class="pk thumb" style="left:{x}px;top:{y}px">{key_html(k)}</div>'
        )

    return '<div class="half">\n    ' + '\n    '.join(items) + '\n  </div>'


def layer_html(layer):
    """Generate HTML for a single keymap layer (both halves)."""
    left_rows = [layer[0], layer[1], layer[2]]
    left_thumbs = [layer[3][0], layer[3][1]]

    # Right rows are stored right<-left: reverse each for visual left->right display.
    # Right thumbs follow the same convention (slot 0 = outer, slot 1 = inner),
    # so swap them too -- inner thumb has to render closer to the keyboard gap.
    right_rows = [list(reversed(layer[4])),
                  list(reversed(layer[5])),
                  list(reversed(layer[6]))]
    right_thumbs = [layer[7][1], layer[7][0]]

    lh = half_html(left_rows, left_thumbs, 'left')
    rh = half_html(right_rows, right_thumbs, 'right')
    return f'<div class="keyboard">\n  {lh}\n  {rh}\n</div>'
